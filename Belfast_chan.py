import asyncio
import codecs
import configparser
import datetime
import logging
import os
import time
import traceback

import discord
from colorama import init, Fore
from discord.ext import commands
from discord.utils import find

from cogs.BelfastUtils import logtime

init(autoreset=True)

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
print("path: " + dir_path)

description = "How can i help you, Commander?"
config = configparser.ConfigParser()
config.read(dir_path + "/config/config.ini")
prefixes = ['Bel ', 'bel ', 'Belfast ', 'belfast ']

cogs = ['cogs.FinishedCommands', 'cogs.BelfastUtils', 'cogs.Testing', 'cogs.Shikimori', 'cogs.StableDiffusion']


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
        super().__init__(command_prefix=get_prefix, description=description, pm_help=None, help_attrs=dict(hidden=True), member_cache_flags=discord.MemberCacheFlags.all(),
                         intents=discord.Intents().all())
        self.awake_time = datetime.datetime.utcnow()
        self.owner_id = 560867880632320020
        self.MyGuild = self.get_guild(566171342953512963)
        self.HangOut = self.get_guild(230774538579869708)
        self.silent_mode = False
        self.botStartTime = time.time()

    def process_guilds(self):
        for guild in self.guilds:
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
            with codecs.open(dir_path + "/config/" + str(guild.id) + ".ini", mode="w", encoding="utf-8") as guild_file:
                guild_conf.write(guild_file)
            path = dir_path + "/servers/" + str(guild.id)
            try:
                if not os.path.exists(path):
                    os.mkdir(path)
                    print(logtime() + "Успешно создана директория %s " % path)
            except OSError:
                print(logtime() + "Создать директорию %s не удалось" % path)

    def user_title(self, _id: int):
        if _id == self.owner_id:
            return "Master"
        else:
            return "Commander"

    def get_user_from_guild(self, guild: discord.Guild, some_user: str) -> discord.Member:
        user = find(lambda m: m.name == some_user, guild.members)
        if user is None:
            user = find(lambda m: m.display_name == some_user, guild.members)
        if user is None:
            user = find(lambda m: str(m) == some_user, guild.members)
        if user is None and not some_user.isdigit() and some_user.strip("@<>!").isdigit():
            user = find(lambda m: int(m.id) == int(some_user.strip("@<>!")), guild.members)
        if user is None:
            user = guild.get_member(int(some_user))
        return user

    @commands.Cog.listener()
    async def on_message(self, message):
        global cogs
        if message.author.id == 373267940008787969:
            # if it's Terminator - just type it
            guild = ""
            author = ""
            if message.guild:
                guild = Fore.GREEN + str(message.guild.name) + "|"
                author = "|" + Fore.CYAN + str(message.author)
            print(logtime() + guild + Fore.YELLOW + str(message.channel) + author + ":" + Fore.RESET + message.clean_content)
        elif not message.author.bot:
            # special commands from bot owner
            if message.author.id == self.owner_id:
                if str(message.clean_content).startswith("bel silentmode"):
                    guild = ""
                    author = ""
                    if message.guild:
                        guild = Fore.GREEN + str(message.guild.name) + "|"
                        author = "|" + Fore.CYAN + str(message.author)
                    print(logtime() + guild + Fore.YELLOW + str(message.channel) + author + ":" + Fore.RESET + message.clean_content)
                    if str(message.clean_content).endswith("on"):
                        self.silent_mode = True
                        await self.change_presence(activity=None, status=discord.Status.invisible)
                    elif str(message.clean_content).endswith("off"):
                        self.silent_mode = False

                        await self.change_presence(status=discord.Status.dnd, activity=discord.Game("Loading..."))
                        await asyncio.sleep(3)
                        await self.change_presence(status=discord.Status.online, activity=discord.Game("Azur Lane"))
                    return
                if str(message.clean_content).startswith("bel reload cogs"):
                    await message.add_reaction('🕑')
                    for extension in cogs:
                        await self.reload_extension(extension)

                    await message.remove_reaction('🕑', self.user)
                    await message.channel.send("Reloaded successfully, Master!", delete_after=15)
                    await message.delete(delay=15)
                    return
                if str(message.clean_content).startswith("bel get cogs"):
                    await message.channel.send("Corrent cogs list:\n" + str(cogs), delete_after=15)
                    await message.delete(delay=15)
                    return
                if str(message.clean_content).startswith("bel add cog "):
                    await message.add_reaction('🕑')
                    cog = "cogs." + message.clean_content[len("bel add cog "):]
                    cogs.append(cog)
                    await self.load_extension(cog)
                    for extension in cogs:
                        await self.reload_extension(extension)
                    await message.channel.send("Reloaded successfully, Master!", delete_after=15)
                    await message.delete(delay=15)
                    return
                if str(message.clean_content).startswith("bel remove cog "):
                    await message.add_reaction('🕑')
                    cog = "cogs." + message.clean_content[len("bel remove cog "):]
                    cogs.remove(cog)
                    await self.unload_extension(cog)
                    for extension in cogs:
                        await self.reload_extension(extension)
                    await message.channel.send("Reloaded successfully, Master!", delete_after=15)
                    await message.delete(delay=15)
                    return
                if message.channel.id == 416694163179044874 and str(message.clean_content).startswith("bel "):
                    await message.delete()
                    await message.channel.send("🚫 That's Rioghán's channel! 🚫 <@!560867880632320020> 🚫", delete_after=20)
            # process users' messages
            guild = ""
            author = ""
            channel = ""
            if message.guild:
                guild = Fore.GREEN + str(message.guild.name) + "|"
                channel = Fore.YELLOW + str(message.channel) + "|"
                author = Fore.CYAN + str(message.author)
            else:
                channel = Fore.YELLOW + "DM from "
                author = Fore.CYAN + str(message.author)
            print(logtime() + guild + channel + author + ":" + Fore.RESET + message.clean_content)
            if not self.silent_mode:
                if (message.clean_content.strip(" \n") == "@Belfast-chan#8997" and self.user in message.mentions) or (message.content + " ") in prefixes:
                    await message.channel.typing()
                    if await self.is_owner(message.author):
                        await message.channel.send("Yes, Master?", delete_after=15)
                        await message.delete(delay=15)
                    else:
                        await message.channel.send("How can i help you, Commander?\nFor the available commands list, please write `Bel help`.", delete_after=25)
                        await message.delete(delay=25)
                await self.process_commands(message)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if not user.bot:
            emojis = []
            '''todo refactor this shit to wait for reactions to exact message depending on command'''
            '''emojis - list of emojis added by Belfast-chan'''
            for _reaction in reaction.message.reactions:
                if _reaction.me:
                    emojis.append(_reaction.emoji)
            '''if user reacts to message with embed, and that ambed is asked by that user and reacts with proper emoji'''
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

    # guild events
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.process_guilds()
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
            print(Fore.RED + str(error))

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.process_guilds()
        print(logtime() + Fore.YELLOW + "Guild lost: " + Fore.CYAN + guild.name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.process_guilds()
        print(logtime() + Fore.CYAN + "New member " + Fore.GREEN + str(
            member) + Fore.CYAN + " has joined guild: " + Fore.GREEN + member.guild.name)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.process_guilds()
        print(logtime() + Fore.YELLOW + "Member " + Fore.CYAN + str(
            member) + Fore.YELLOW + " has left guild: " + Fore.CYAN + member.guild.name)

    # connect events
    @commands.Cog.listener()
    async def on_connect(self):
        print(logtime() + Fore.GREEN + "Connected successfully!")
        if not self.silent_mode:
            await self.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name="Loading..."))

    @commands.Cog.listener()
    async def on_resume(self):
        print(logtime() + Fore.GREEN + "Connection restored successfully!")
        if not self.silent_mode:
            await self.change_presence(status=discord.Status.online, activity=discord.Game("Azur Lane"))

    @commands.Cog.listener()
    async def on_ready(self):
        self.process_guilds()
        for extension in cogs:
            if extension not in self.extensions:
                await self.load_extension(extension)
            else:
                await self.reload_extension(extension)
        if not self.silent_mode:
            await self.change_presence(status=discord.Status.online, activity=discord.Game("Azur Lane"))
        print(Fore.GREEN + logtime() + "Ready to serve my Master!")

    @commands.Cog.listener()
    async def on_command_error(self, ctx: discord.ext.commands.context, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            return
        elif isinstance(error, discord.ext.commands.errors.NotOwner):
            await ctx.send("I am sorry, Commander! :no_entry:\nBut only my Master can give me this order.", delete_after=15)
            await ctx.message.delete(delay=5)
        elif isinstance(error, discord.ext.commands.errors.NSFWChannelRequired):
            await ctx.send("I am sorry, Commander! :no_entry:\nBut I can not do this outside NSFW channels.", delete_after=15)
            await ctx.message.delete(delay=5)
        elif isinstance(error, discord.ext.commands.errors.CommandOnCooldown):
            await ctx.send(f"I am sorry, Commander! :no_entry:\nBut this command still unavailable.\nYou can use it after {round(error.retry_after, 2)}s", delete_after=15)
            await ctx.message.delete(delay=5)
        else:
            error_log = "========================\n" \
                        "Error type: " + str(type(error)) + \
                        "\n========================\n" + \
                        str(error) + \
                        "\n========================\n" + \
                        str("".join(traceback.format_exception(type(error),
                                                               value=error,
                                                               tb=error.__traceback__))).split(
                            "The above exception was the direct cause of the following")[0] + \
                        "\n========================\n"
            for arg in error.args:
                error_log += "-arg- = " + arg + "\n"
            text = "Encountered an error, gathering data...\n"

            guild = ""
            author = ""
            channel = ""
            if ctx.message.guild:
                guild = str(ctx.message.guild.name)
                channel = str(ctx.message.channel)
                author = str(ctx.message.author)
            else:
                channel = "DM from "
                author = str(ctx.message.author)

            text += "Discord guild: `" + guild + "`\nChannel: `" + channel + "`\nUser: `" + author + "`\n"
            text += "Error-causing message text: `" + ctx.message.clean_content + "`\n"
            text += "Logging...\n"
            filename = "/error_logs/error_log_" + str(time.time()) + ".txt"
            with codecs.open(os.path.abspath(dir_path + filename), encoding='utf-8', mode='w') as output_file:
                output_file.write(text + "\n\n" + str(error_log) + "\n")
                output_file.close()
            text += "Error log created: " + filename
            msg = await ctx.send(embed=discord.Embed(title=":bangbang:ERROR:bangbang:",
                                                     description=text + "\n\n" + str(error)), delete_after=30)
            owner = await self.fetch_user(self.owner_id)
            await owner.send(embed=discord.Embed(title=":bangbang:ERROR:bangbang:",
                                                 description=text + "\n\n" + str(error)))
            await ctx.message.delete(delay=30)


if __name__ == '__main__':
    create_if_not_exists("/config")
    create_if_not_exists("/config/config.ini")
    create_if_not_exists("/config/last maintenance.txt")
    create_if_not_exists("/ALDB")
    create_if_not_exists("/ALDB/ships")
    create_if_not_exists("/servers")
    create_if_not_exists("/suggests")
    create_if_not_exists("/users")
    create_if_not_exists("/battle_logs")
    create_if_not_exists("/logs")
    create_if_not_exists("/error_logs")

    bot = BelfastBot()
    bot.run(config['Main']['token'], reconnect=True, log_level=logging.ERROR)
