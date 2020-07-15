import ast
import codecs
import configparser
import os

import discord
from colorama import Fore
from discord.ext import commands

from cogs.BelfastUtils import logtime

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "MudaDB/")

users_antidisable_lists = {}
titles = {}
user_info_channels = {}


class MudaTitle(object):
    name = ""
    total = 0
    claimed = 0
    unclaimed = 0
    total_list = []
    claimed_list = []
    unclaimed_list = []

    def __str__(self):
        return str(self.name + "(" + str(self.unclaimed) + " left)\n\n" + "\n".join(self.total_list))

    def __init__(self, name: str, total_list: list):
        self.name = name
        self.total_list = []
        self.add_chars(total_list)

    @classmethod
    def load_from_config(cls, config):
        # print(logtime() + Fore.CYAN + str(configparser.ConfigParser(config).sections()))
        return MudaTitle(str(config.get('main', 'title')), ast.literal_eval(config.get('main', 'total_list')))

    def add_chars(self, total_list: list):
        for char in total_list:
            if not str(char).startswith("\u200B") \
                    and not str(char).startswith("(No result)") \
                    and char not in self.total_list:
                cha = char
                if str(char).endswith(" ka"):
                    cha = cha.split(" ka")[0][:cha.rfind(' ')]
                if str(char).__contains__(" **"):
                    cha = cha.split(" **")[0]
                if str(char).__contains__(" · <:"):
                    cha = cha.split(" · <:")[0]
                if str(char).__contains__(" => "):
                    cha = cha.split(" => ")[0]

                self.total_list.append(cha)
                print(logtime() + Fore.YELLOW + "Adding " + Fore.CYAN + cha + Fore.YELLOW + " into " + Fore.CYAN + self.name)
        self.claimed_list = [char for char in self.total_list if str(char).endswith('💞')]
        self.unclaimed_list = [char for char in self.total_list if char not in self.claimed_list]
        self.total = len(self.total_list)
        self.claimed = len(self.claimed_list)
        self.unclaimed = len(self.unclaimed_list)


class MudaHelper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def load(self):
        global users_antidisable_lists, user_info_channels, titles
        user_info_channels = ast.literal_eval(codecs.open(dir_path.replace("MudaDB/", "servers/230774538579869708/user_info_channels.txt"), encoding='utf-8').read())
        users_antidisable_lists = ast.literal_eval(codecs.open(dir_path.replace("MudaDB/", "servers/230774538579869708/users_antidisable_lists.txt"), encoding='utf-8').read())
        print(logtime() + Fore.CYAN + "Loading " + str(len(os.listdir(dir_path))) + " titles...")
        for f in os.listdir(dir_path):
            profile = configparser.ConfigParser()
            # print(logtime() + Fore.CYAN + dir_path+f)
            profile.read(dir_path + f, encoding='utf-8')
            titles[f[:len(f) - 4]] = MudaTitle.load_from_config(profile)
        print(logtime() + Fore.CYAN + "Loaded " + str(len(os.listdir(dir_path))) + " titles!")

    def save(self):
        global users_antidisable_lists, user_info_channels, titles
        with codecs.open(dir_path.replace("MudaDB/", "servers/230774538579869708/users_antidisable_lists.txt"), "w") as f:
            f.write(str(users_antidisable_lists))
            f.flush()
            f.close()
        with codecs.open(dir_path.replace("MudaDB/", "servers/230774538579869708/user_info_channels.txt"), "w") as f:
            f.write(str(user_info_channels))
            f.flush()
            f.close()
        for title in titles.keys():
            t = titles[title]
            user_conf = configparser.ConfigParser()
            user_conf.add_section('main')
            user_conf.set('main', 'title', title)
            user_conf.set('main', 'total', str(t.total))
            user_conf.set('main', 'claimed', str(t.claimed))
            user_conf.set('main', 'unclaimed', str(t.unclaimed))
            user_conf.set('main', 'total_list', str(t.total_list))
            user_conf.set('main', 'claimed_list', str(t.claimed_list))
            user_conf.set('main', 'unclaimed_list', str(t.unclaimed_list))
            with codecs.open(dir_path + title + ".ini", mode="w", encoding="utf-8") as user_file:
                user_conf.write(user_file)
        # print(Fore.GREEN + logtime() + "Saved MudaDB!")

    def add_ad_title_for_user(self, user_id: int, title: str):
        global users_antidisable_lists
        if not user_id in users_antidisable_lists.keys():
            users_antidisable_lists[user_id] = [title]
            print(logtime() + Fore.YELLOW + "Added AD title: " + Fore.CYAN + title)
        else:
            if title not in users_antidisable_lists[user_id]:
                users_antidisable_lists[user_id].append(title)
                print(logtime() + Fore.YELLOW + "Added AD title: " + Fore.CYAN + title)

    def add_characters_into_title(self, title: str, numbers: str, descr: str):
        global titles
        n = descr.count("\n\n")
        if n:
            charlistraw = descr.split("\n\n")[n].split("\n")
        else:
            charlistraw = descr.split("\n")
        # print(logtime() + Fore.GREEN + ' '.join(titles.keys()))
        if not titles.keys().__contains__(title):
            titles[title] = MudaTitle(title, charlistraw)
            # print(logtime() + Fore.YELLOW + "Writing Title Characters... " + Fore.CYAN + "'"+title+ "'")
            #return "Created title `" + title + "` with characters:\n```" + "\n" \
                #.join([c for c in titles[title].total_list]) + "```"
        else:
            #prev_chars = titles[title].total_list.copy()
            titles[title].add_chars(charlistraw)
            #return "Updated title `" + title + "` with characters:\n```" + "\n" \
                #.join([c for c in titles[title].total_list if c not in prev_chars]) + "```"

    @commands.command(pass_context=True, aliases=['msch'], brief="Set this channel to get info about your preferences")
    @commands.guild_only()
    async def msetchannel(self, ctx):
        user_info_channels[ctx.author.id] = ctx.channel.id
        await ctx.message.add_reaction('✅')

    @commands.command(pass_context=True, aliases=['ms'], brief="save everything")
    @commands.guild_only()
    async def msave(self, ctx):
        self.save()
        await ctx.message.add_reaction('✅')

    @commands.command(pass_context=True, aliases=['mgu'], brief="Get list from titles of your antidisable list with unclaimed characters")
    @commands.guild_only()
    async def mgetmyunclaimed(self, ctx):
        global users_antidisable_lists, titles
        await ctx.channel.trigger_typing()
        result = '\n'.join([title for title in titles if title in users_antidisable_lists[ctx.author.id] and titles[title].unclaimed > 0])
        await ctx.send(embed=discord.Embed(title="This titles are still not fully claimed:", description=result))

    @commands.command(pass_context=True, aliases=['mgadl'], brief="Get your antidisable list")
    @commands.guild_only()
    async def mgetmyadlist(self, ctx):
        global users_antidisable_lists
        await ctx.channel.trigger_typing()
        result = '\n'.join(users_antidisable_lists[ctx.author.id])
        await ctx.send(embed=discord.Embed(title="Your antidisable list:", description=result))

    @commands.command(pass_context=True, aliases=['mgt'], brief="Get title total characters list")
    @commands.guild_only()
    async def mgettitle(self, ctx, *, title):
        global titles
        await ctx.channel.trigger_typing()
        result = str(titles[title])
        await ctx.send(embed=discord.Embed(description=result))


def setup(bot):
    bot.add_cog(MudaHelper(bot))
