import datetime
import os

import discord
from discord.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")


def logtime(): return str(datetime.datetime.now().time()).partition('.')[0] + " "


class BelfastUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['parse'], hidden=True)
    @commands.is_owner()
    async def parsemessage(self, ctx, *, message_id: int):
        # self.bot.loop.create_task(self.teset(ctx))
        await self.parse_message(ctx, message_id)

    async def parse_message(self, ctx, message_id: int):
        msg_to_parse = await ctx.channel.fetch_message(message_id)
        emb = discord.Embed()
        text = ""
        if msg_to_parse:
            if msg_to_parse.author:
                text += "**Message author:** " + str(msg_to_parse.author) + "\n"
                text += "**Message author.id:** " + str(msg_to_parse.author.id) + "\n\n"
            if msg_to_parse.clean_content:
                text += "**Message clean_content:** " + str(msg_to_parse.clean_content) + "\n\n"
            if msg_to_parse.system_content:
                text += "**Message system_content:** " + str(msg_to_parse.system_content) + "\n\n"
            if msg_to_parse.type:
                text += "**Message type:** " + str(msg_to_parse.type) + "\n\n"
            if msg_to_parse.reference:
                text += "**Message reference:** " + str(msg_to_parse.reference) + "\n\n"
            for embed_ in msg_to_parse.embeds:
                text += "**Embed title:** " + str(embed_.title) + "\n"
                text += "**Embed color:** " + str(embed_.color) + "\n"
                text += "**Embed footer:** " + str(embed_.footer) + "\n"
                text += "**Embed author:** " + str(embed_.author) + "\n"
                text += "**Embed description:** " + str(embed_.description) + "\n\n\n"
        emb.description = text
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def leaveguild(self, ctx, *, guild_id_str: str = "placeholder999999lvl"):
        if guild_id_str == "placeholderLVL99999":
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you forgot to specify guild's id.", delete_after=35)
            await ctx.message.delete(delay=15)
            return
        try:
            guild = self.bot.get_guild(int(guild_id_str))
        except Exception:
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\n"
                           + "But I couldn't find guild with given id.\n"
                           + "Please, make sure you wrote correct guild id as number.", delete_after=35)
            await ctx.message.delete(delay=15)
            return
        if guild:
            await guild.leave()
            await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def cogs(self, ctx):
        await ctx.send("\n".join(self.bot.extensions), delete_after=35)
        await ctx.message.delete(delay=15)


async def setup(bot):
    await bot.add_cog(BelfastUtils(bot))
