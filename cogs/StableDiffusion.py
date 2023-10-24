import asyncio
import base64
import io
import json
import os
import re
import time

import aiohttp
import requests
from discord import File
from discord.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")

localizedStrings = {
    'en':
        {
            'downloading': "🕑 Downloading **{0}**: {1}% at {2}kb/s..."
        },
    'ru':
        {
            'downloading': "🕑 Скачиваю **{0}**: {1}% со скоростью {2}кб/с..."
        },
}


class StableDiffusion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url = "http://127.0.0.1:7860"  # 7861 for nowebui and 7860 when with ui
        self.defaultSampler = "Euler"
        self.enableHiRes = True

    @commands.is_nsfw()
    @commands.max_concurrency(number=1, per=commands.BucketType.default, wait=True)
    @commands.command(pass_context=True, brief="Generate 1280*1280 (~14sec)")
    async def gen(self, ctx, *, _prompt: str = ""):
        await self._gen(ctx, _prompt, 512, 512, self.defaultSampler)

    @commands.is_nsfw()
    @commands.max_concurrency(number=1, per=commands.BucketType.default, wait=True)
    @commands.command(pass_context=True, brief="Generate 1280*1920 (portrait, ~27sec)")
    async def genp(self, ctx, *, _prompt: str = ""):
        await self._gen(ctx, _prompt, 512, 768, self.defaultSampler)

    @commands.is_nsfw()
    @commands.max_concurrency(number=1, per=commands.BucketType.default, wait=True)
    @commands.command(pass_context=True, brief="Generate 1920*1280 (landscape, ~27sec)")
    async def genl(self, ctx, *, _prompt: str = ""):
        await self._gen(ctx, _prompt, 768, 512, self.defaultSampler)

    async def _gen(self, ctx, _prompt, _width, _height, _sampler):
        _seed = -1
        if "seed:" in _prompt:
            _seed = int(re.sub("\D", "", _prompt.partition("seed:")[2].partition(",")[0]))
        # await ctx.message.add_reaction('🕑')
        cleanPrompt = _prompt \
            .replace(" loli", "") \
            .replace(" child", "") \
            .replace(" porn", "") \
            .replace(" kid", "") \
            .replace(" gore", "") \
            .replace(" baby", "")
        additions = ""
        try:
            await ctx.message.delete()
        except Exception as error:
            pass
        message = await ctx.send(f"🕑 Generating request from **{ctx.message.author.display_name}**:\n>>> " + cleanPrompt)
        sdStart = time.time()
        payload = {
            "prompt": cleanPrompt + additions + ", (masterpiece, extremely detailed)",
            "enable_hr": self.enableHiRes,
            "hr_upscaler": "4x_fatal_Anime_500000_G",
            "hr_scale": 1.5,
            "hr_second_pass_steps": 10,

            "steps": 30,
            "sampler_name": _sampler,
            "cfg_scale": 10,
            "width": _width,
            "height": _height,
            "denoising_strength": 0.5,
            "seed": _seed,
            "subseed": _seed,
            "save_images": False,
            "restore_faces": False,
            "tiling": False,
            "do_not_save_samples": True,
            "do_not_save_grid": True,
            "alwayson_scripts": {
                "ADetailer": {
                    "args": [
                        {
                            "ad_model": "face_yolov8m.pt"
                        },
                        {
                            "ad_model": "hand_yolov8s.pt",
                            "ad_prompt": "perfect hands",
                            "ad_negative_prompt": "extra fingers, (extra fingers, deformed hands:1.5), (badHands3, verybadimagenegative_v1.3:0.7)",
                        }
                    ]
                }
            },
            "negative_prompt": "(badHands3, verybadimagenegative_v1.3:0.7),"
                               "(extra fingers, deformed hands, deformed iris, deformed pupils, bad eyes, polydactyl:1.5),"
                               "(Worst Quality, Low Quality:1.3),"
                               "(Blurry, Blur:1.2),"
                               "(artist name, watermark, signature:1.3),"
                               "(loli, children, child, baby, baby face:1.333)"
        }
        text = "**Request from** <@" + str(ctx.message.author.id) + ">"
        resultFile = None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=f'{self.url}/sdapi/v1/txt2img', json=payload, ssl=False) as response:
                    respJSON = await response.json()
                    if 'errors' in respJSON.keys():
                        text += f"\n🚫 **Error occurred in StableDiffusion:**\n`{str(respJSON['errors'])}`"
                    else:
                        _fp = io.BytesIO(base64.b64decode(respJSON['images'][0].split(",", 1)[0]))
                        resultFile = File(filename=str(str(json.loads(respJSON['info'])['seed']) + ".png"), fp=_fp)
                        text += f"\nModel: {str(respJSON['info']).partition('Model: ')[2].partition(',')[0]}" \
                                f"\n✅ Done in {str(round((time.time() - sdStart), 2))}s"
                await session.close()
            await ctx.channel.send(content=text + f"\n>>> {cleanPrompt[:666]}", file=resultFile)
        except aiohttp.ClientConnectorError as error:
            await ctx.channel.send("🚫 I am sorry, " + self.bot.user_title(ctx.message.author.id) + "!\nBut StableDiffusion is currently offline.\n"
                                   + "Maybe Master <@!560867880632320020> would be so kind to launch it?")
        finally:
            await message.delete()

    @commands.cooldown(rate=1, per=24 * 3600)  # 1 day
    @commands.is_nsfw()
    @commands.command(pass_context=True, brief="Download a new model from civit.ai by modelID (once per 24hrs)")
    async def sddlmodel(self, ctx, *, modelid: int):
        # TODO: better links parsing that users send here
        try:
            await ctx.message.delete()
        except Exception as error:
            pass
        assert modelid >= 0, "modelid has to be a positive integer"
        modelName = ""
        filename = ""
        link = ""
        m1 = None
        respJSON = requests.get(f"https://civitai.com/api/v1/models/{modelid}").json()
        modelName = respJSON['name']
        filename = respJSON['modelVersions'][0]['files'][0]['name']
        link = respJSON['modelVersions'][0]['downloadUrl']
        text1 = "🕑 Downloading **" + filename + "**..."
        m1 = await ctx.send(text1)
        downloadStart = time.time()
        try:
            async with aiohttp.ClientSession(headers={'content-disposition': f'filename="{filename}"'}) as session:
                async with session.get(link, timeout=None) as response:
                    if response.status != 200:
                        await ctx.reply(f"Error {response.status}")
                        return
                    total_size = int(response.headers.get('Content-Length')) // 1024
                    with open("G:/AI Art Generator/stable-diffusion-webui/models/Stable-diffusion/" + filename, mode='wb') as file:
                        update_task = asyncio.create_task(
                            self.update_progress(m1, file, filename, total_size, 5))
                        async for data in response.content.iter_any():
                            file.write(data)
            await session.close()
        except Exception as error:
            await ctx.send("🚫 Downloading model ID " + str(modelid) + " file:**" + filename + f"**: FAILED! <@" + ctx.author.id + ">")
            return
        finally:
            update_task.cancel()
            await m1.delete()
        if requests.post(url=f'{self.url}/sdapi/v1/refresh-checkpoints').status_code == 200:
            models = []
            for item in requests.get(url=f'{self.url}/sdapi/v1/sd-models').json():
                models.append(item)
            models.sort(key=lambda x: x['model_name'])
            i = 1
            text = "✅ Successfully downloaded **" + modelName + f"** model in {str(round((time.time() - downloadStart), 2))}s!" \
                   + "\n**Updated models list:**\n"
            for model in models:
                text += str(i) + ') `' + model['model_name'] + '`\n'
                i += 1
            await ctx.send(content=text)
        else:
            await ctx.send("🚫 Failed to refresh checkpoints...")

    async def update_progress(self, msg, file, filename, total_bytes, update_interval):
        last_update_time = 0
        last_bytes = 0
        while True:
            downloaded_bytes = file.tell() // 1024
            percentage = downloaded_bytes * 100 // total_bytes
            current_time = time.time()
            if current_time - last_update_time > update_interval:
                await msg.edit(content="🕑 Downloading **" + filename + f"**: {percentage}% at {((downloaded_bytes - last_bytes) / 5):,} kb/s...".replace(",", ' '))
                last_update_time = current_time
                last_bytes = downloaded_bytes
            await asyncio.sleep(update_interval)

    @commands.cooldown(rate=1, per=60 * 5)
    @commands.command(pass_context=True, brief="Select model by number (once per 5min)")
    async def sdmodel(self, ctx, _model: int):
        try:
            await ctx.message.delete()
        except Exception as error:
            pass

        models = []
        for item in requests.get(url=f'{self.url}/sdapi/v1/sd-models').json():
            models.append(item)
        models.sort(key=lambda x: x['model_name'])
        newModel = models[_model - 1]['model_name']
        modelStart = time.time()
        mm1 = await ctx.send("🕑 Loading `" + newModel + "` model...")
        try:
            response = requests.post(url=f'{self.url}/sdapi/v1/options', json={"sd_model_checkpoint": models[_model - 1]['title']})
            if response.status_code == 200:
                try:
                    await mm1.delete()
                except Exception as error:
                    pass
                await ctx.send("✅ Successfully loaded `" + newModel + f"` model in {str(round((time.time() - modelStart), 2))}s!")
        except Exception as error:
            await ctx.channel.send("🚫 I am sorry, " + self.bot.user_title(ctx.message.author.id) + "!\nBut StableDiffusion is currently offline.\n"
                                   + "Maybe Master <@!560867880632320020> would be so kind to launch it?")

    @commands.command(pass_context=True, brief="Show models list")
    async def sdmodels(self, ctx):
        try:
            await ctx.message.delete()
        except Exception as error:
            pass
        models = []
        try:
            for item in requests.get(url=f'{self.url}/sdapi/v1/sd-models').json():
                models.append(item)
        except Exception as error:
            await ctx.channel.send("🚫 I am sorry, " + self.bot.user_title(ctx.message.author.id) + "!\nBut StableDiffusion is currently offline.\n"
                                   + "Maybe Master <@!560867880632320020> would be so kind to launch it?")
            return
        models.sort(key=lambda x: x['model_name'])
        i = 1
        text = ""
        for model in models:
            text += str(i) + ') `' + model['model_name'] + '`\n'
            i += 1
        await ctx.send(text)

    @commands.command(pass_context=True, brief="Show loras list")
    async def sdloras(self, ctx):
        try:
            await ctx.message.delete()
        except Exception as error:
            pass
        models = []
        try:
            for item in requests.get(url=f'{self.url}/sdapi/v1/loras').json():
                models.append(item)
        except Exception as error:
            await ctx.channel.send("🚫 I am sorry, " + self.bot.user_title(ctx.message.author.id) + "!\nBut StableDiffusion is currently offline.\n"
                                   + "Maybe Master <@!560867880632320020> would be so kind to launch it?")
            return
        models.sort(key=lambda x: x['name'])
        i = 1
        text = ""
        for model in models:
            text += str(i) + ') `' + model['name'] + '`\n'
            i += 1
        await ctx.send(text)

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True, brief="Show upscalers list")
    async def sdupscalers(self, ctx):
        try:
            await ctx.message.delete()
        except Exception as error:
            pass
        models = []
        try:
            for item in requests.get(url=f'{self.url}/sdapi/v1/upscalers').json():
                models.append(item)
        except Exception as error:
            await ctx.channel.send("🚫 I am sorry, " + self.bot.user_title(ctx.message.author.id) + "!\nBut StableDiffusion is currently offline.\n"
                                   + "Maybe Master <@!560867880632320020> would be so kind to launch it?")
            return
        models.sort(key=lambda x: x['name'])
        i = 1
        text = ""
        for model in models:
            text += str(i) + ') `' + model['name'] + '`\n'
            i += 1
        await ctx.send(text)

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def sdrm(self, ctx):
        try:
            await ctx.message.delete()
        except Exception as error:
            pass
        if requests.post(url=f'{self.url}/sdapi/v1/refresh-checkpoints').status_code == 200:
            models = []
            for item in requests.get(url=f'{self.url}/sdapi/v1/sd-models').json():
                models.append(item)
            models.sort(key=lambda x: x['model_name'])
            i = 1
            text = "**Updated models list:**\n"
            for model in models:
                text += str(i) + ') `' + model['model_name'] + '`\n'
                i += 1
            await ctx.send(text)

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def sdrl(self, ctx):
        try:
            await ctx.message.delete()
        except Exception as error:
            pass
        if requests.post(url=f'{self.url}/sdapi/v1/refresh-loras').status_code == 200:
            models = []
            for item in requests.get(url=f'{self.url}/sdapi/v1/loras').json():
                models.append(item)
            models.sort(key=lambda x: x['model_name'])
            i = 1
            text = "**Updated loras list:**\n"
            for model in models:
                text += str(i) + ') `' + model['model_name'] + '`\n'
                i += 1
            await ctx.send(text)

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def sdrl(self, ctx):
        try:
            await ctx.message.delete()
        except Exception as error:
            pass
        if requests.post(url=f'{self.url}/sdapi/v1/refresh-loras').status_code == 200:
            models = []
            for item in requests.get(url=f'{self.url}/sdapi/v1/loras').json():
                models.append(item)
            models.sort(key=lambda x: x['name'])
            i = 1
            text = "**Updated loras list:**\n"
            for model in models:
                text += str(i) + ') `' + model['name'] + '`\n'
                i += 1
            await ctx.send(text)

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def sdhr(self, ctx, _on: bool):
        self.enableHiRes = _on
        await ctx.message.add_reaction('✅')

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def sdgeto(self, ctx):
        import pprint
        await ctx.send(pprint.pformat(requests.get(url=f'{self.url}/sdapi/v1/options').json())[:1900])
        await ctx.send(pprint.pformat(requests.get(url=f'{self.url}/sdapi/v1/options').json())[1900:3700])
        await ctx.send(pprint.pformat(requests.get(url=f'{self.url}/sdapi/v1/options').json())[3700:])

    @commands.is_nsfw()
    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True)
    async def sdtest(self, ctx):
        text = localizedStrings['en']['downloading'] + '\n' + localizedStrings['ru']['downloading']
        await ctx.send(text)


async def setup(bot):
    await bot.add_cog(StableDiffusion(bot))
