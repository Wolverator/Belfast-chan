import datetime
import os
import time
from platform import python_version

import discord
from discord.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")
time_start = time.time()


def logtime(): return str(datetime.datetime.now().time()).partition('.')[0] + " "


class BelfastUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['ava', 'mypp'], brief="Show your or other user's avatar")
    @commands.guild_only()
    async def avatar(self, ctx, *, some_user="placeholderLVL99999"):
        await ctx.channel.trigger_typing()
        if some_user == "placeholderLVL99999":
            some_user = ctx.author.id
        user = self.bot.get_user_from_guild(ctx.guild, some_user)
        if user is not None:
            resultEmbed = discord.Embed()
            resultEmbed.set_author(name=str(user))
            resultEmbed.set_image(url=user.avatar_url)
            await ctx.send(embed=resultEmbed)
        else:
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nUser with predicate **" + some_user + "** not found on this server.")

    @commands.command(pass_context=True, hidden=True)
    async def stats(self, ctx):
        await ctx.channel.trigger_typing()
        text = "Bot online for: **" + str(datetime.timedelta(seconds=time.time() - time_start)).partition('.')[0] + "**\n"
        users = 0
        bots = 0
        for member in self.bot.users:
            if member.bot:
                bots += 1
            else:
                users += 1
        author = self.bot.get_user_from_guild(ctx.guild, str(self.bot.owner_id))
        scan_result = scan_dir(dir_path)
        resultEmbed = discord.Embed()
        resultEmbed.set_thumbnail(url=self.bot.user.avatar_url)
        resultEmbed.set_author(name=str(self.bot.user))
        resultEmbed.set_footer(text="Bot owner and author: " + str(author), icon_url=author.avatar_url)
        resultEmbed.timestamp = datetime.datetime.utcnow()
        resultEmbed.colour = discord.colour.Color.from_rgb(222, 222, 0)
        resultEmbed.title = "A bit of statistics:"

        text += "Guilds: **{0}**\n".format(len(self.bot.guilds))
        text += "Members: **{0}**\n".format(users)
        text += "Nearby bots: **{0}**\n".format(bots)
        text += "Files in folder: **{0}**\n".format(scan_result[0])
        text += "Code lines: **{0}**\n".format(scan_result[1])
        text += "Total files size: **{0}** MB\n".format(round(scan_result[2] / (1024 * 1024), 2))
        text += "Python version: **{0}**\n".format(str(python_version()))
        text += "Discord.py version: **{0}**\n".format(str(discord.__version__))

        resultEmbed.description = text
        await ctx.send(embed=resultEmbed, delete_after=45)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def bots(self, ctx):
        text = ""
        for member in self.bot.users:
            if member.bot:
                text += str(member) + "\n"
        await ctx.send("```" + text + "```", delete_after=15)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def users(self, ctx):
        text = ""
        for member in self.bot.users:
            if not member.bot:
                text += str(member) + "\n"
        await ctx.send("```" + text + "```", delete_after=15)


def scan_dir(path):
    count = 0
    code_lines = 0
    size = 0
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)):
            count += 1
            size += os.path.getsize(os.path.join(path, f))
            if os.path.join(path, f).endswith(".py"):
                # noinspection PyUnusedLocal
                code_lines += sum(1 for line in open(os.path.join(path, f), 'r'))
        elif os.path.join(path, f).count(".idea") == 0 and os.path.join(path, f).count("__pycache__") == 0:
            (c, c_l, s) = scan_dir(os.path.join(path, f))
            count += c
            code_lines += c_l
            size += s
    return count, code_lines, size


def setup(bot):
    bot.add_cog(BelfastUtils(bot))
