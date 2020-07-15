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
from discord.utils import find

from cogs.BelfastUtils import logtime

init(autoreset=True)

dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
print("path: " + dir_path)

description = "How can i help you, Commander?"
config = configparser.ConfigParser()
config.read(dir_path + "/config/config.ini")
prefixes = ['Bel ', 'Belfast ', 'Belfast-chan ', 'Bel-chan ', 'Belchan ', 'bel ', 'belfast ', 'belfast-chan ', 'bel-chan ', 'belchan ']

cogs = ['cogs.AzurLane', 'cogs.FinishedCommands', 'cogs.BelfastUtils', 'cogs.Testing', 'cogs.BelfastGame', 'cogs.MudaHelper']


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
        self.HangOut = self.get_guild(230774538579869708)
        self.MudaMaid15_id = 547713368396529664
        self.MudaIgnoreNextMessage = {}
        self.MudaMessagesToIgnore = []
        for extension in cogs:
            self.load_extension(extension)

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

    def get_user_from_guild(self, guild: discord.Guild, some_user: str) -> discord.User:
        user = find(lambda m: m.name == some_user, guild.members)
        if user is None:
            user = find(lambda m: m.display_name == some_user, guild.members)
        if user is None:
            user = find(lambda m: str(m) == some_user, guild.members)
        if user is None and some_user.strip("@<>!").isdigit():
            user = find(lambda m: m.id == int(some_user.strip("@<>!")), guild.members)
        return user

    @commands.Cog.listener()
    async def on_message_edit(self, message_before, message_after):
        if message_after.author.bot and message_after.author.id!=self.MudaMaid15_id:
            return
        elif message_after.author.id==self.MudaMaid15_id:
            if message_after.channel.id in self.MudaIgnoreNextMessage.keys() and self.MudaIgnoreNextMessage[message_after.channel.id]:
                self.MudaIgnoreNextMessage[message_after.channel.id] = False
                self.MudaMessagesToIgnore.append(message_after.id)
            elif message_after.id not in self.MudaMessagesToIgnore:
                #print(logtime()+ Fore.YELLOW +"processing MudaMesssage in"+ str(message_after.channel))
                #if user checks adl
                titl = self.get_mudatitle_from_ima(str(message_after.embeds[0].author.name))
                if message_after.embeds and str(message_after.embeds[0].author.name).__contains__("'s antidisablelist"):
                    user = self.get_user_from_guild(message_after.guild, str(message_after.embeds[0].author.name).split("'s antidisablelist")[0])
                    #print(logtime() + Fore.YELLOW + "sending to MudaHelper TitleforUser... ")
                    for title in message_after.embeds[0].description.split("\n"):
                        if title and not str(title).__contains__("antidisabled characters"):
                            self.get_cog('MudaHelper').add_ad_title_for_user(user.id, title.strip("*"))
                            await message_after.add_reaction('<:AzurLane:569511684650041364>')
                #if user scrolls title pages
                elif titl:
                    #print(logtime() + Fore.YELLOW + "sending to MudaHelper Characters... " + Fore.CYAN + titl)
                    #await message_after.channel.send(message_after.embeds[0].description)
                    self.get_cog('MudaHelper').add_characters_into_title(titl.strip(" "), str(message_after.embeds[0].author.name)[1+len(titl):], message_after.embeds[0].description)
                    await message_after.add_reaction('<:AzurLane:569511684650041364>')

    print('The probability of 7 heads is: ' + str(sum([1 for i in np.random.binomial(1, 0.3, size=10) if i == 1]) / 10))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot and message.author.id!=self.MudaMaid15_id:
            return
        #elif message.author.id==self.MudaMaid15_id:
        #     if message.embeds and str(message.embeds[0].author.name).__contains__("'s antidisablelist"):
        #         user = self.get_user_from_guild(message.guild, str(message.embeds[0].author.name).split("'s antidisablelist")[0])
        #         for title in message.embeds[0].description.replace("\d+ antidisabled characters\n\n","").split("\n"):
        #             if title:
        #                 await self.get_cog('MudaHelper').add_ad_title_for_user(user.id, title.strip("*"))
        else:
            guild = ""
            author = ""
            if message.guild:
                guild = Fore.GREEN + str(message.guild.name) + "|"
                author = "|" + Fore.CYAN + str(message.author)
            command = str(message.clean_content)
            if command.startswith("$$ima") and len(command)>5 and command[5] != 'w':
                self.MudaIgnoreNextMessage[message.channel.id] = True
            print(logtime() + guild + Fore.YELLOW + str(message.channel) + author + ":" + Fore.RESET + message.clean_content)
            if (message.clean_content.strip(" \n") == "@Belfast-chan#8997" and self.user in message.mentions) or (message.content + " ") in prefixes:
                await message.channel.trigger_typing()
                await asyncio.sleep(2)
                if await self.is_owner(message.author):
                    msg = await message.channel.send("Yes, Master?")
                    await msg.delete(delay=15)
                    await message.delete(delay=15)
                else:
                    msg = await message.channel.send("How can i help you, Commander?\nFor 'help' command, please write `Bel info`.")
                    await msg.delete(delay=25)
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
            print(Fore.RED + error)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.process_guilds()
        print(logtime() + Fore.YELLOW + "Guild lost: " + Fore.CYAN + guild.name)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        self.process_guilds()
        print(logtime() + Fore.CYAN + "New member " + Fore.GREEN + str(
            member) + Fore.CYAN + " has joined guild: " + Fore.GREEN + member.guild.name)
        if member.guild == self.TigersMeadow:
            await member.add_roles(self.TigersMeadow.get_role(569987757238386718))

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        self.process_guilds()
        print(logtime() + Fore.YELLOW + "Member " + Fore.CYAN + str(
            member) + Fore.YELLOW + " has left guild: " + Fore.CYAN + member.guild.name)

    # connect events
    @commands.Cog.listener()
    async def on_connect(self):
        print(logtime() + Fore.GREEN + "Connected successfully!")
        await self.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(name="loading..."))

    @commands.Cog.listener()
    async def on_resume(self):
        print(logtime() + Fore.GREEN + "Connected restored successfully!")
        await self.change_presence(status=discord.Status.online, activity=discord.Game("Azur Lane"))

    @commands.Cog.listener()
    async def on_ready(self):
        self.process_guilds()
        self.get_cog('MudaHelper').load()
        await self.change_presence(status=discord.Status.online, activity=discord.Game("Azur Lane"))
        print(Fore.GREEN + logtime() + "Ready to serve my Master!")
        while self.is_ready():
            from cogs.FinishedCommands import mt_reminder
            await mt_reminder()
            self.get_cog('MudaHelper').save()
            await asyncio.sleep(180)

    @commands.Cog.listener()
    async def on_command_error(self, ctx: discord.ext.commands.context, error):
        if isinstance(error, discord.ext.commands.errors.CommandNotFound):
            await ctx.send("I am sorry, " + self.user_title(ctx.author.id) + "! :no_entry:\nBut this in unknown command.", delete_after=15)
        elif isinstance(error, discord.ext.commands.errors.NotOwner):
            await ctx.send("I am sorry, Commander! :no_entry:\nBut only my Master can give me this order.", delete_after=15)
        else:
            error_log = str(type(error)) + "\n========================\n" + str(error) \
                        + "\n========================\n" + \
                        str("".join(traceback.format_exception(etype=type(error),
                                                               value=error,
                                                               tb=error.__traceback__))).split("The above exception was the direct cause of the following")[0] + "\n"
            for arg in error.args:
                error_log += "-arg- = " + arg + "\n"
            text = "Encountered an error, gathering data...\n"
            text += "Discord guild: `" + ctx.message.guild.name + "`\nChannel: `" + ctx.message.channel.name + "`\nUser: `" + ctx.message.author.display_name + "`\n"
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

    def get_mudatitle_from_ima(self, title_with_charnum:str)->str:
        import re
        ending = re.search(re.compile(" [0-9]+/[0-9]+$"), title_with_charnum)
        if ending:
            #print(title_with_charnum[:ending.start()])
            return title_with_charnum[:ending.start()]
        else:
            return ""

if __name__ == '__main__':
    create_if_not_exists("/config")
    create_if_not_exists("/config/config.ini")
    create_if_not_exists("/config/last maintenance.txt")
    create_if_not_exists("/ALDB")
    create_if_not_exists("/MudaDB")
    create_if_not_exists("/ALDB/ships")
    create_if_not_exists("/servers")
    create_if_not_exists("/suggests")
    create_if_not_exists("/users")
    create_if_not_exists("/battle_logs")
    create_if_not_exists("/logs")
    create_if_not_exists("/error_logs")

    BelfastBot().run(config['Main']['token'], bot=True, reconnect=True)