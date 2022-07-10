import asyncio
import codecs
import datetime
import os
import sys
import time
from datetime import datetime as d

import discord
from colorama import Fore
from dateutil.parser import parser
from discord.ext import commands

from cogs.BelfastUtils import logtime

DateParser = parser()
dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")
time_start = time.time()


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, brief="Get invite to my server")
    async def server(self, ctx):
        await ctx.channel.trigger_typing()
        await ctx.send("Join my Master's guild if you want or if you need some help:\nhttps://discord.gg/pbHMnTv5Pg")

    @commands.command(pass_context=True, brief="Check online time")
    async def online(self, ctx):
        await ctx.channel.trigger_typing()
        await ctx.send("I'm online for " + str(datetime.timedelta(seconds=time.time() - time_start)).partition('.')[0]
                       + " already, doing good.\nThanks for asking and may The Force be with you!", delete_after=15)
        await ctx.message.delete(delay=15)

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

    @commands.command(pass_context=True, brief="Invite me to your server")
    async def invite(self, ctx):
        await ctx.channel.trigger_typing()
        await ctx.send(
            "Let me join your guild too!\nhttps://discordapp.com/api/oauth2/authorize?client_id=568914197048459273"
            "&permissions=117824&scope=bot")

    @commands.command(name='ping', brief='Pong!')
    async def ping(self, ctx):
        start = d.timestamp(d.now())
        msg = await ctx.send(content='Pinging')
        await msg.edit(content=f'Thanks for asking!\nSeems like my ping is {str((d.timestamp(d.now()) - start) * 1000).partition(".")[0]}ms.', delete_after=15)
        await ctx.message.delete(delay=15)


    @commands.command(pass_context=True, aliases=['logout'], brief="[owner-only]Log out and exit program", hidden=True)
    @commands.is_owner()
    async def exit(self, ctx):
        await ctx.channel.trigger_typing()
        await asyncio.sleep(0.5)
        await ctx.send("Yes, Master! Logging out...", delete_after=15)
        await self.bot.change_presence(activity=None, status=discord.Status.offline)
        await ctx.message.delete(delay=15)
        await self.bot.get_cog('BelfastGame').save_world()
        await self.bot.logout()
        await self.bot.close()
        print(logtime() + Fore.YELLOW + "Logged out!")
        sys.exit()


def setup(bot):
    bot.add_cog(General(bot))
