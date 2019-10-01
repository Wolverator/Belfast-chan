import asyncio
import codecs
import configparser
import datetime
import os
import time
import discord

from platform import python_version
from colorama import Fore
from discord.ext import commands
from discord.utils import find

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")
time_start = time.time()


def logtime(): return str(datetime.datetime.now().time()).partition('.')[0] + " "


class BelfastUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def process_guilds(self):
        for guild in self.bot.guilds:
            guild_conf = configparser.ConfigParser()
            print(logtime() + "Guild connected: " + Fore.GREEN + guild.name)
            guild_conf.add_section(str(guild.id))
            guild_conf.set(str(guild.id), "Name", guild.name)
            guild_conf.add_section("Roles")
            for Role in guild.roles:
                guild_conf.set("Roles", str(Role.id), str(Role.name))
            guild_conf.add_section("Channels")
            for Channel in guild.channels:
                guild_conf.set("Channels", str(Channel.id), str(Channel.name))
            guild_conf.add_section("Members")
            for Member in guild.members:
                guild_conf.set("Members", str(Member.id), str(Member))
            with codecs.open(dir_path + "config/" + str(guild.id) + ".ini", mode="w", encoding="utf-8") as guild_file:
                guild_conf.write(guild_file)
            path = dir_path + "servers/" + str(guild.id)
            try:
                if not os.path.exists(path):
                    os.mkdir(path)
                    print(logtime() + "Успешно создана директория %s " % path)
            except OSError:
                print(logtime() + "Создать директорию %s не удалось" % path)

    def get_user(self, guild: discord.Guild, some_user: str):
        user = find(lambda m: m.name == some_user, guild.members)
        if user is None:
            user = find(lambda m: m.display_name == some_user, guild.members)
        if user is None:
            user = find(lambda m: str(m) == some_user, guild.members)
        if user is None and some_user.strip("@<>!").isdigit():
            user = find(lambda m: m.id == int(some_user.strip("@<>!")), guild.members)
        return user

    @commands.command(pass_context=True, aliases=['ava', 'mypp'], brief="Show your or other user's avatar")
    @commands.guild_only()
    async def avatar(self, ctx, *, some_user="placeholderLVL99999"):
        await ctx.channel.trigger_typing()
        if some_user == "placeholderLVL99999":
            some_user = str(ctx.author.id)
        user = self.get_user(ctx.guild, some_user)
        if user is not None:
            resultEmbed = discord.Embed()
            resultEmbed.set_author(name=str(user))
            resultEmbed.set_image(url=user.avatar_url)
            await ctx.send(embed=resultEmbed)
        else:
            await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nUser with predicate **" + some_user + "** not found on this server.")

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
        author = self.bot.get_user(self.bot.owner_id)
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
        msg = await ctx.send(embed=resultEmbed)
        await asyncio.sleep(45)
        await msg.delete()

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def bots(self, ctx):
        text = ""
        for member in self.bot.users:
            if member.bot:
                text += str(member) + "\n"
        msg = await ctx.send("```" + text + "```")
        await asyncio.sleep(15)
        await msg.delete()

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def users(self, ctx):
        text = ""
        for member in self.bot.users:
            if not member.bot:
                text += str(member) + "\n"
        msg = await ctx.send("```" + text + "```")
        await asyncio.sleep(15)
        await msg.delete()


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
