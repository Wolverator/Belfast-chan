import asyncio
import codecs
import configparser
import datetime
import os
import time
import traceback

import discord
from colorama import init, Fore
from discord.ext import commands

from cogs.BelfastUtils import logtime
from cogs.Bingo import servers_with_games

init(autoreset=True)

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
print("path: " + dir_path)

description = "How can i help you, Commander?"
config = configparser.ConfigParser()
config.read(dir_path + "/config/config.ini")
prefixes = ['Bel ', 'Belfast ', 'Belfast-chan ', 'Bel-chan ', 'Belchan ', 'bel ', 'belfast ', 'belfast-chan ', 'bel-chan ', 'belchan ']

cogs = ['cogs.AzurLane', 'cogs.FinishedCommands', 'cogs.BelfastUtils', 'cogs.Testing', 'cogs.BelfastGame', 'cogs.Bingo']


# funcs
def get_prefix(client, message):
    bot_prefixes = prefixes
    if not message.guild:
        bot_prefixes = ['']
    return commands.when_mentioned_or(*bot_prefixes)(client, message)


def create_if_not_exists(path_to_file_or_dir: str):
    if path_to_file_or_dir.__contains__('.'):
        if not os.path.exists(dir_path + path_to_file_or_dir):
            with codecs.open(dir_path + path_to_file_or_dir, "w") as f:
                f.flush()
                f.close()
    else:
        if not os.path.exists(dir_path + path_to_file_or_dir):
            os.mkdir(dir_path + path_to_file_or_dir)


class BelfastBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, description=description, pm_help=None, help_attrs=dict(hidden=True))
        self.awake_time = datetime.datetime.utcnow()
        self.owner_id = 560867880632320020
        self.TigersMeadow = self.get_guild(566171342953512963)
        for extension in cogs:
            self.load_extension(extension)

    def _user(self, _id: int):
        if _id == self.owner_id:
            return "Master"
        else:
            return "Commander"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        else:
            guild = ""
            author = ""
            if message.guild:
                guild = Fore.GREEN + str(message.guild.name) + "|"
                author = "|" + Fore.CYAN + str(message.author)
            print(logtime() + guild + Fore.YELLOW + str(message.channel) + author + ":" + Fore.RESET + message.clean_content)
            if (message.clean_content.strip(" \n") == "@Belfast-chan#8997" and self.user in message.mentions) or (message.content + " ") in prefixes:
                await message.channel.trigger_typing()
                await asyncio.sleep(0.1)
                if await self.is_owner(message.author):
                    msg = await message.channel.send("Yes, Master?")
                    await asyncio.sleep(5)
                    await msg.delete()
                else:
                    msg = await message.channel.send("How can i help you, Commander?\nFor 'help' command, please write ``Bel info``.")
                    await asyncio.sleep(25)
                    await msg.delete()
            await self.process_commands(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            emojis = []
            for _reaction in reaction.message.reactions:
                if _reaction.me:
                    emojis.append(_reaction.emoji)
            if user != self.user and reaction.message.embeds and reaction.message.embeds[0].footer \
                    and str(reaction.message.embeds[0].footer.text) == str(user.id) and reaction.emoji in emojis:
                if reaction.emoji == "1⃣":
                    stat_type = 'base'
                elif reaction.emoji == "2⃣":
                    stat_type = '100'
                elif reaction.emoji == "3⃣":
                    stat_type = '120'
                elif reaction.emoji == "4⃣":
                    stat_type = '100r'
                elif reaction.emoji == "5⃣":
                    stat_type = '120r'
                else:
                    return
                try:
                    reaction.remove()
                except Exception:
                    ""
                await reaction.message.edit(
                    embed=self.get_cog('AzurLane').update_embed(reaction.message.embeds[0], stat_type))
            print(user.name + " reacted with " + str(reaction.emoji))

            print("1" + str(user != self.user))
            print("2" + str(reaction.emoji.id) + "///" + str(reaction.emoji.id == "<:AL:569511684650041364>"))
            print("3" + str(reaction.message.content.find("Azure Lane Bingo") != (-1)))
            print("4" + str(servers_with_games[reaction.message.guild.id].count(user.id) == 0))

            if user != self.user and str(reaction.emoji.id) == "569511684650041364" \
                    and reaction.message.content.find("Azure Lane Bingo") != (-1) \
                    and servers_with_games[reaction.message.guild.id].count(user.id) == 0:
                print(user.name + " reacted with " + str(reaction.emoji) + " and added to Bingo Game")
                servers_with_games[reaction.message.guild.id].append(user.id)
                await reaction.message.channel.send(user.name + " was added to upcoming game!")

    # guild events
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.get_cog('BelfastUtils').process_guilds()
        print(logtime() + Fore.CYAN + "New guild connected: " + Fore.GREEN + guild.name)
        if guild.system_channel is not None:
            try:
                await guild.system_channel.send(
                    "Hello there, Commanders!\nThanks for inviting me to your guild :wink:\nType 'Bel help' to see list "
                    "of available commands.\nAlso make sure you have 'belfast-chan-news' text channel to receive news from "
                    "my Master considering my online schedule or development!")
            except Exception:
                ""
        try:
            path = dir_path + "/servers/" + str(guild.id)
            if not os.path.exists(path):
                os.mkdir(path)
                print("Successfully created folder %s " % path)
        except OSError as error:
            path = dir_path + "/servers/" + str(guild.id)
            print("Failed making '%s' folder" % path)
            print(Fore.RED + error)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.get_cog('BelfastUtils').process_guilds()
        print(logtime() + Fore.YELLOW + "Guild lost: " + Fore.CYAN + guild.name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.get_cog('BelfastUtils').process_guilds()
        print(logtime() + Fore.CYAN + "New member " + Fore.GREEN + str(
            member) + Fore.CYAN + " has joined guild: " + Fore.GREEN + member.guild.name)
        if member.guild == self.TigersMeadow:
            await member.add_roles(self.TigersMeadow.get_role(569987757238386718))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member != self.user:
            self.get_cog('BelfastUtils').process_guilds()
            print(logtime() + Fore.YELLOW + "Member " + Fore.CYAN + str(
                member) + Fore.YELLOW + " has left guild: " + Fore.CYAN + member.guild.name)

    # connect events
    @commands.Cog.listener()
    async def on_connect(self):
        print(logtime() + Fore.GREEN + "Connected successfully!")
        await self.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game("loading..."))

    @commands.Cog.listener()
    async def on_disconnect(self):
        print(logtime() + Fore.YELLOW + "Connected lost!")
        await self.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game("loading..."))

    @commands.Cog.listener()
    async def on_resume(self):
        print(logtime() + Fore.GREEN + "Connected restored successfully!")
        await self.change_presence(status=discord.Status.online, activity=discord.Game("Azur Lane"))

    @commands.Cog.listener()
    async def on_ready(self):
        self.get_cog('BelfastUtils').process_guilds()
        await self.change_presence(status=discord.Status.online, activity=discord.Game("Azur Lane"))
        print(Fore.GREEN + logtime() + "Ready to serve my Master!")
        while self.is_ready():
            from cogs.FinishedCommands import mt_reminder
            await mt_reminder()
            await asyncio.sleep(180)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: discord.ext.commands.context, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            msg = await ctx.send("I am sorry, " + self._user(ctx.author.id) + "! :no_entry:\nBut this in unknown command.")
            await asyncio.sleep(15)
            await msg.delete()
            return
        elif isinstance(error, discord.ext.commands.errors.NotOwner):
            msg = await ctx.send("I am sorry, Commander! :no_entry:\nBut only my Master can give me this order.")
            await asyncio.sleep(15)
            await msg.delete()
            return
        else:
            error_log = str(type(error)) + "\n========================" + ''.join(traceback.format_tb(error.__traceback__))
            for arg in error.args:
                error_log += "-arg- = " + arg + "\n"
            text = "Encountered an error, gathering data...\n"
            text += "Discord guild: '" + ctx.message.guild.name + "'; channel: '" + ctx.message.channel.name + "'; Commander: '" + ctx.message.author.display_name + "'.\n"
            text += "Error-causing message text: '" + ctx.message.clean_content + "'.\n"
            text += "Logging...\n"
            filename = "/error_logs/error_log_" + str(time.time()) + ".txt"
            with codecs.open(os.path.abspath(dir_path + filename), encoding='utf-8', mode='w') as output_file:
                output_file.write(text + "\n\n" + str(error_log) + "\n")
                output_file.close()
            text += "Error log created: " + filename
            msg = await ctx.send(embed=discord.Embed(title=":bangbang:ERROR:bangbang:", description=text))
            owner = await self.fetch_user(self.owner_id)
            await owner.send(embed=discord.Embed(title=":bangbang:ERROR:bangbang:", description=text))
            await asyncio.sleep(25)
            await msg.delete()


if __name__ == '__main__':
    create_if_not_exists("/config")
    create_if_not_exists("/config/config.ini")
    create_if_not_exists("/config/last maintenance.txt")
    create_if_not_exists("/ALDB")
    create_if_not_exists("/ALDB/ships")
    create_if_not_exists("/servers")
    create_if_not_exists("/suggests")
    create_if_not_exists("/users")
    create_if_not_exists("/logs")
    create_if_not_exists("/error_logs")

    BelfastBot().run(config['Main']['token'], bot=True, reconnect=True)
