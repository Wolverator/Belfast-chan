import asyncio
import os
import random
from io import BytesIO

import discord
from PIL import Image
from discord.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")
description_pattern = "test description\n" \
                      + "Health: **{0}/{1}**\nMoney: **{2}**GC **{3}**SS **{4}**P\nEncumb.: **{5}/{6}**"


class Testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def tesetColor(self, ctx, _w=50, _y=50):
        width = 500
        height = 100
        color_red = (255, 0, 0, 255)
        color_green = (0, 255, 0, 255)
        color_blue = (0, 0, 255, 255)
        img = Image.new(mode="RGB", size=(width, height))
        pixels = img.load()

        for w in range(width):
            for h in range(height):
                pixels[w, h] = random.choices([color_blue, color_green], [15, 1])[0]
        buffer = BytesIO()
        img.save(buffer, "png")
        buffer.seek(0)
        await ctx.send(file=discord.File(buffer, filename="teset.png"))
        while self.bot.is_ready():
            chat = self.bot.get_guild(566171342953512963).get_channel(570041633261879306)
            await chat.send("lul?")
            await asyncio.sleep(5)


def setup(bot):
    bot.add_cog(Testing(bot))
