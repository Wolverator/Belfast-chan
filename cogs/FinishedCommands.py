import asyncio
import codecs
import datetime
import os
import time
from datetime import datetime as d
from platform import python_version

import discord
import pandas
from colorama import Fore
from dateutil.parser import parser
from discord.ext import commands
from pandas import DataFrame, ExcelWriter

from cogs.BelfastUtils import logtime

DateParser = parser()
dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, brief="Get invite to my server")
    async def server(self, ctx):
        await ctx.channel.typing()
        await ctx.send("Join my Master's guild if you want or if you need some help:\nhttps://discord.gg/pbHMnTv5Pg")

    @commands.command(pass_context=True, aliases=['ava'], brief="Show your or other user's avatar")
    @commands.guild_only()
    async def avatar(self, ctx, *, some_user="placeholderLVL99999"):
        await ctx.channel.typing()
        if some_user == "placeholderLVL99999":
            some_user = str(ctx.author.id)
        user = self.bot.get_user_from_guild(ctx.guild, some_user)
        if user is not None:
            resultEmbed = discord.Embed()
            resultEmbed.set_author(name=str(user))
            resultEmbed.set_image(url=user.avatar)
            await ctx.send(embed=resultEmbed)
            await ctx.message.delete(delay=15)
        else:
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nUser with predicate **" + some_user + "** not found on this server.")
            await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, brief="Check statistics")
    async def stats(self, ctx):
        await ctx.channel.typing()
        text = "Bot online for: **" + str(datetime.timedelta(seconds=time.time() - self.bot.botStartTime)).partition('.')[0] + "**\n"
        users = 0
        bots = 0

        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot:
                    bots += 1
                else:
                    users += 1
        author = self.bot.get_user_from_guild(ctx.guild, str(self.bot.owner_id))
        scan_result = self.scan_dir(dir_path)
        resultEmbed = discord.Embed()
        resultEmbed.set_thumbnail(url=self.bot.user.avatar)
        resultEmbed.set_author(name=str(self.bot.user))
        resultEmbed.set_footer(text="Bot owner and author: " + str(author), icon_url=author.avatar)
        resultEmbed.timestamp = datetime.datetime.utcnow()
        resultEmbed.colour = discord.colour.Color.from_rgb(222, 222, 0)
        resultEmbed.title = "A bit of statistics:"

        text += "Guilds: **{0}**\n".format(len(self.bot.guilds))
        text += "Nearby members: **{0}**\n".format(users)
        text += "Nearby bots: **{0}**\n".format(bots)
        text += "Files in folder: **{0}**\n".format(scan_result[0])
        text += "Code lines: **{0}**\n".format(scan_result[1])
        text += "Total files size: **{0}** MB\n".format(round(scan_result[2] / (1024 * 1024), 2))
        text += "Python version: **{0}**\n".format(str(python_version()))
        text += "Discord.py version: **{0}**\n".format(str(discord.__version__))

        resultEmbed.description = text
        await ctx.send(embed=resultEmbed, delete_after=45)
        await ctx.message.delete(delay=15)

    def scan_dir(self, path):
        count = 0
        code_lines = 0
        size = 0
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                count += 1
                size += os.path.getsize(os.path.join(path, f))
                if os.path.join(path, f).endswith(".py"):
                    # noinspection PyUnusedLocal
                    code_lines += sum(1 for line in open(file=os.path.join(path, f), mode='r', encoding="UTF-8"))
            elif os.path.join(path, f).count(".idea") == 0 and os.path.join(path, f).count("__pycache__") == 0:
                (c, c_l, s) = self.scan_dir(os.path.join(path, f))
                count += c
                code_lines += c_l
                size += s
        return count, code_lines, size

    @commands.command(pass_context=True, brief="Leave your suggestion")
    async def suggest(self, ctx, *, text: str):
        path_to_file = os.path.abspath("suggests/suggest by " + str(ctx.author) + " " + str(time.time()).replace('.', '_') + ".txt")
        with codecs.open(path_to_file, encoding='utf-8', mode='w') as output_file:
            output_file.write(text)
            output_file.close()
        await ctx.message.add_reaction('✅')
        print(str(datetime.datetime.utcnow().time()).partition('.')[0] + " " + Fore.CYAN + str(
            ctx.author) + Fore.RESET + " made a suggestion!")
        await ctx.message.delete(delay=15)

    @commands.command(name='ping', brief='Pong!')
    async def ping(self, ctx):
        start = d.timestamp(d.now())
        msg = await ctx.send(content='Pinging')
        await msg.edit(content=f'Thanks for asking!\nSeems like my ping is {str((d.timestamp(d.now()) - start) * 1000).partition(".")[0]}ms.', delete_after=15)
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, aliases=['logout'], hidden=True)
    @commands.is_owner()
    async def exit(self, ctx):
        await ctx.channel.typing()
        await asyncio.sleep(0.5)
        await ctx.send("Yes, Master! Logging out...", delete_after=15)
        await self.bot.change_presence(activity=None, status=discord.Status.offline)
        await ctx.message.delete(delay=15)
        # if self.bot.cogs.contains('cogs.BelfastGame'):
        #     await self.bot.get_cog('BelfastGame').save_world()
        await self.bot.close()
        print(logtime() + Fore.YELLOW + "Logged out!")
        exit()

    @commands.command(pass_context=True, brief="Grisaia1 translation status")
    async def ts(self, ctx):
        await ctx.message.add_reaction('🕑')
        path = "D:\\Misc\\VNs\\Grisaia 1 debug\\translate here\\clean texts"
        WRITE_TRANSLATION_HERE = "(write translation here)"
        com_total = 0
        com_trans = 0
        ama_total = 0
        ama_trans = 0
        mak_total = 0
        mak_trans = 0
        mic_total = 0
        mic_trans = 0
        sac_total = 0
        sac_trans = 0
        yum_total = 0
        yum_trans = 0

        com_filename = []
        com_total_lines = []
        com_translated_lines = []
        com_percent = []
        com_redacted_lines = []
        com_redacted_percent = []
        com_redacted_finished = []

        ama_filename = []
        ama_total_lines = []
        ama_translated_lines = []
        ama_percent = []
        ama_redacted_lines = []
        ama_redacted_percent = []
        ama_redacted_finished = []

        mak_filename = []
        mak_total_lines = []
        mak_translated_lines = []
        mak_percent = []
        mak_redacted_lines = []
        mak_redacted_percent = []
        mak_redacted_finished = []

        mic_filename = []
        mic_total_lines = []
        mic_translated_lines = []
        mic_percent = []
        mic_redacted_lines = []
        mic_redacted_percent = []
        mic_redacted_finished = []

        sac_filename = []
        sac_total_lines = []
        sac_translated_lines = []
        sac_percent = []
        sac_redacted_lines = []
        sac_redacted_percent = []
        sac_redacted_finished = []

        yum_filename = []
        yum_total_lines = []
        yum_translated_lines = []
        yum_percent = []
        yum_redacted_lines = []
        yum_redacted_percent = []
        yum_redacted_finished = []

        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            if os.path.isfile(file_path) and file_path.endswith(".xlsx") and "~" not in f:
                current_filename = f.replace('.xlsx', '')
                current_total = 0
                current_translated = 0
                xls = pandas.ExcelFile(file_path)
                df = xls.parse(0)
                text_lines = list(df[df.columns[2]]).copy()
                # result += "op.xlsx has " + str(f[:2]) + " lines"
                while len(text_lines) > 0:
                    text_lines.pop(0)
                    translated = 0
                    current_line = text_lines.pop(0)
                    if not str(current_line) in (WRITE_TRANSLATION_HERE, "None", 'nan'):
                        translated = 1

                    current_total += 1
                    current_translated += translated

                    match f[:2]:
                        case "op" | "co":
                            com_total += 1
                            com_trans += translated
                        case "am":
                            ama_total += 1
                            ama_trans += translated
                        case "ma":
                            mak_total += 1
                            mak_trans += translated
                        case "mi":
                            mic_total += 1
                            mic_trans += translated
                        case "sa":
                            sac_total += 1
                            sac_trans += translated
                        case "yu":
                            yum_total += 1
                            yum_trans += translated
                        case _:
                            pass
                match f[:2]:
                    case "op" | "co":
                        com_filename.append(current_filename)
                        com_total_lines.append(current_total)
                        com_translated_lines.append(current_translated)
                        com_percent.append(0)
                        com_redacted_lines.append(0)
                        com_redacted_percent.append(0)
                        com_redacted_finished.append(0)
                    case "am":
                        ama_filename.append(current_filename)
                        ama_total_lines.append(current_total)
                        ama_translated_lines.append(current_translated)
                        ama_percent.append(0)
                        ama_redacted_lines.append(0)
                        ama_redacted_percent.append(0)
                        ama_redacted_finished.append(0)
                    case "ma":
                        mak_filename.append(current_filename)
                        mak_total_lines.append(current_total)
                        mak_translated_lines.append(current_translated)
                        mak_percent.append(0)
                        mak_redacted_lines.append(0)
                        mak_redacted_percent.append(0)
                        mak_redacted_finished.append(0)
                    case "mi":
                        mic_filename.append(current_filename)
                        mic_total_lines.append(current_total)
                        mic_translated_lines.append(current_translated)
                        mic_percent.append(0)
                        mic_redacted_lines.append(0)
                        mic_redacted_percent.append(0)
                        mic_redacted_finished.append(0)
                    case "sa":
                        sac_filename.append(current_filename)
                        sac_total_lines.append(current_total)
                        sac_translated_lines.append(current_translated)
                        sac_percent.append(0)
                        sac_redacted_lines.append(0)
                        sac_redacted_percent.append(0)
                        sac_redacted_finished.append(0)
                    case "yu":
                        yum_filename.append(current_filename)
                        yum_total_lines.append(current_total)
                        yum_translated_lines.append(current_translated)
                        yum_percent.append(0)
                        yum_redacted_lines.append(0)
                        yum_redacted_percent.append(0)
                        yum_redacted_finished.append(0)
                    case _:
                        pass

        writer = ExcelWriter("D:\\Misc\\VNs\\Grisaia 1 debug\\translate here\\total_table.xlsx", engine='xlsxwriter')
        df_com = DataFrame({"Таблицы": com_filename,
                            "Всего строк": com_total_lines,
                            "Переведено": com_translated_lines,
                            "Процент перевода": com_percent,
                            "Подверглось редактуре": com_redacted_lines,
                            "Подверглось редактуре(%)": com_redacted_percent,
                            "Редактура": com_redacted_finished})
        df_com.to_excel(writer, sheet_name='Общий', index=False, na_rep='NaN')
        df_com = DataFrame({"Таблицы": ama_filename,
                            "Всего строк": ama_total_lines,
                            "Переведено": ama_translated_lines,
                            "Процент перевода": ama_percent,
                            "Подверглось редактуре": ama_redacted_lines,
                            "Подверглось редактуре(%)": ama_redacted_percent,
                            "Редактура": ama_redacted_finished})
        df_com.to_excel(writer, sheet_name='Амане', index=False, na_rep='NaN')
        df_com = DataFrame({"Таблицы": mak_filename,
                            "Всего строк": mak_total_lines,
                            "Переведено": mak_translated_lines,
                            "Процент перевода": mak_percent,
                            "Подверглось редактуре": mak_redacted_lines,
                            "Подверглось редактуре(%)": mak_redacted_percent,
                            "Редактура": mak_redacted_finished})
        df_com.to_excel(writer, sheet_name='Макина', index=False, na_rep='NaN')
        df_com = DataFrame({"Таблицы": mic_filename,
                            "Всего строк": mic_total_lines,
                            "Переведено": mic_translated_lines,
                            "Процент перевода": mic_percent,
                            "Подверглось редактуре": mic_redacted_lines,
                            "Подверглось редактуре(%)": mic_redacted_percent,
                            "Редактура": mic_redacted_finished})
        df_com.to_excel(writer, sheet_name='Мичиру', index=False, na_rep='NaN')
        df_com = DataFrame({"Таблицы": sac_filename,
                            "Всего строк": sac_total_lines,
                            "Переведено": sac_translated_lines,
                            "Процент перевода": sac_percent,
                            "Подверглось редактуре": sac_redacted_lines,
                            "Подверглось редактуре(%)": sac_redacted_percent,
                            "Редактура": sac_redacted_finished})
        df_com.to_excel(writer, sheet_name='Сачи', index=False, na_rep='NaN')
        df_com = DataFrame({"Таблицы": yum_filename,
                            "Всего строк": yum_total_lines,
                            "Переведено": yum_translated_lines,
                            "Процент перевода": yum_percent,
                            "Подверглось редактуре": yum_redacted_lines,
                            "Подверглось редактуре(%)": yum_redacted_percent,
                            "Редактура": yum_redacted_finished})
        df_com.to_excel(writer, sheet_name='Юмико', index=False, na_rep='NaN')
        writer.close()

        result = "**Прогресс перевода Grisaia no Kajitsu:**" \
                 + "\nОбщий: {0}/{1} строк, **{2}%**".format(com_trans, com_total, round((com_trans / com_total) * 100, 2))
        result += "\nАмане: {0}/{1} строк, **{2}%**".format(ama_trans, ama_total, round((ama_trans / ama_total) * 100, 2))
        result += "\nМакина: {0}/{1} строк, **{2}%**".format(mak_trans, mak_total, round((mak_trans / mak_total) * 100, 2))
        result += "\nМичиру: {0}/{1} строк, **{2}%**".format(mic_trans, mic_total, round((mic_trans / mic_total) * 100, 2))
        result += "\nСачи: {0}/{1} строк, **{2}%**".format(sac_trans, sac_total, round((sac_trans / sac_total) * 100, 2))
        result += "\nЮмико: {0}/{1} строк, **{2}%**".format(yum_trans, yum_total, round((yum_trans / yum_total) * 100, 2))
        sum_trans = ama_trans + com_trans + mak_trans + mic_trans + sac_trans + yum_trans
        sum_total = ama_total + com_total + mak_total + mic_total + sac_total + yum_total
        result += "\n\nИтого: {0}/{1} строк, **{2}%**".format(sum_trans, sum_total, round((sum_trans / sum_total) * 100, 2))

        result += "\nОбновлено: <t:{0}:f> (<t:{0}:R>)".format(
            # str(datetime.datetime.now()).split('.')[0],
            str(time.time()).split('.')[0])
        if ctx.channel.id == 1008380737294172253:
            message = await ctx.channel.fetch_message(1291474774832320522)
            await message.edit(content=result)
        else:
            await ctx.send(result)
        # await ctx.send(result)
        await ctx.message.remove_reaction('🕑', self.bot.user)
        await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, hidden=True, brief="Add translated file for Grisaia1")
    async def tladd(self, ctx):
        correctTableNames = 0
        for file in ctx.message.attachments:
            if file.filename in os.listdir("D:\\Misc\\VNs\\Grisaia 1 debug\\translate here\\clean texts"):
                correctTableNames += 1
        if correctTableNames > 0:
            for file in ctx.message.attachments:
                await file.save(fp="D:\\Misc\\VNs\\Grisaia 1 debug\\translation help\\" + file.filename)
                print(Fore.LIGHTGREEN_EX + "Получен файл перевода " + file.filename)

            await ctx.message.add_reaction('🕑')
            await ctx.message.remove_reaction('🕑', self.bot.user)
            await ctx.message.add_reaction('✅')
        else:
            await ctx.send("У сообщения с командой нет прикреплённых Excel таблиц с нужными названиями!", delete_after=15)
            await ctx.message.delete(delay=15)
            print(Fore.LIGHTGREEN_EX + "Что-то не получилось...")


async def setup(bot):
    await bot.add_cog(General(bot))
