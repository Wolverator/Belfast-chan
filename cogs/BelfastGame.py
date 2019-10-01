import asyncio
import codecs
import configparser
import os
import random
import discord
import pandas
from cogs.AzurLane import no_retro_type, retro_type, submarine_type
from cogs.BelfastUtils import logtime
from colorama import Fore
from discord.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "users/")
build_cost = 100


class BattleGirl(object):
    name = ""
    pic = ""
    rarity = ""
    nationality = ""
    classification = ""
    level = 0
    exp = 0
    health = 0
    firepower = 0
    antiair = 0
    torpedo = 0
    aviation = 0
    reload = 0
    accuracy = 0
    evasion = 0

    def __init__(self, girl_config):
        self.name = girl_config.get('main', 'name')
        self.pic = girl_config.get('main', 'pic')
        self.rarity = girl_config.get('main', 'rarity')
        self.nationality = girl_config.get('main', 'nationality')
        self.classification = girl_config.get('main', 'classification')
        self.level = int(girl_config.get('stats', 'level'))
        self.exp = int(girl_config.get('stats', 'exp'))
        self.health = int(girl_config.get('stats', 'health'))
        self.firepower = int(girl_config.get('stats', 'firepower'))
        self.antiair = int(girl_config.get('stats', 'anti-air'))
        self.torpedo = int(girl_config.get('stats', 'torpedo'))
        self.aviation = int(girl_config.get('stats', 'aviation'))
        self.reload = int(girl_config.get('stats', 'reload'))
        self.accuracy = int(girl_config.get('stats', 'accuracy'))
        self.evasion = int(girl_config.get('stats', 'evasion'))

    def fire_shells(self, enemy):
        dmg = int((self.accuracy / enemy.evasion) * self.firepower)
        dmg = randomize_dmg(dmg)
        if enemy.classification == "Submarine":
            dmg = int(dmg / 5)
        if self.torpedo == 0 and self.aviation == 0:
            dmg = int(dmg * 1.2)
        if self.classification == "Battlecruiser" or self.classification == "Battleship":
            dmg = int(dmg * 2)
        enemy.health = enemy.health - dmg
        return str(self.name + " fired shells at " + enemy.name + " with " + str(dmg) + " damage dealt!\n")

    def launch_torps(self, enemy):
        dmg = int((self.accuracy / enemy.evasion) * self.torpedo)
        dmg = randomize_dmg(dmg)
        if enemy.classification == "Submarine":
            dmg = int(dmg / 5)
        if enemy.classification == "Destroyer":
            dmg = int(dmg / 2)
        enemy.health = enemy.health - dmg
        return str(self.name + " launched torps at " + enemy.name + " with " + str(dmg) + " damage dealt!\n")

    def aviation_attack(self, enemy):
        dmg = int((self.aviation * 6 / (1 + enemy.antiair)) * self.aviation)
        dmg = randomize_dmg(dmg)
        if enemy.classification == "Submarine":
            dmg = int(dmg / 10)
        enemy.health = enemy.health - dmg
        return str(self.name + " attacked " + enemy.name + " using planes with " + str(dmg) + " damage dealt!\n")


class BelfastGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, brief="Duel another player at same server")
    async def duel(self, ctx, *, user_to_duel="placeholderLVL9999999"):
        if user_to_duel != "placeholderLVL9999999":
            user = self.bot.get_cog("BelfastUtils").get_user(ctx.guild, user_to_duel)
            if user is not None:
                if get_profile(ctx.author.id):
                    if get_harem_size(ctx.author.id) and get_harem_size(ctx.author.id) > 0:
                        if get_profile(user.id):
                            if get_harem_size(user.id) and get_harem_size(user.id) > 0:
                                await ctx.send("Battle replacer")
                            else:
                                await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut this Commander have no girls to battle with yet!")
                        else:
                            await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut this Commander doesn't play this game yet (have no profile)!")
                    else:
                        await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut you have no girls to battle with yet! Build some with ``Bel build``")
                else:
                    await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut you have no profile yet. Create one with ``Bel new``")
            else:
                await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nCommander with predicate **" + user_to_duel + "** not found on this server.")
        else:
            await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut it seems like you forgot to choose a player you wanna duel.")

    @commands.command(pass_context=True, brief="Battle 2 girls in test mode")
    async def battle(self, ctx, girl1_id="placeholderLVL9999999", girl2_id="placeholderLVL9999999"):
        if get_profile(ctx.author.id):
            if get_harem_size(ctx.author.id) and get_harem_size(ctx.author.id) > 0:
                if girl1_id != "placeholderLVL9999999":
                    if girl2_id != "placeholderLVL9999999":
                        if girl1_id.isdigit() and girl2_id.isdigit():
                            girl1 = get_harem_girl_by_id(ctx.author.id, int(girl1_id))
                            if girl1 is not None:
                                girl2 = get_harem_girl_by_id(ctx.author.id, int(girl2_id))
                                if girl2 is not None:
                                    if girl1_id != girl2_id:
                                        await ctx.send("```" + self.battle2girls(girl1, girl2) + "```")
                                    else:
                                        await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut this game does not supports self-harm and suicides!")
                                else:
                                    await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut seems like second girl's ID is wrong :thinking:")
                            else:
                                await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut seems like first girl's ID is wrong :thinking:")
                        else:
                            await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut you should choose girls via their IDs, using only numbers")
                    else:
                        await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut you forgot to select second girl")
                else:
                    await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut you forgot to select first girl")
            else:
                await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut you have no girls to battle with yet! Build some with ``Bel build``")
        else:
            await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut you have no profile yet. Create one with ``Bel new``")

    def battle2girls(self, girl1: BattleGirl, girl2: BattleGirl):
        battle_log = ""
        time = 1
        while girl1.health > 0 and girl2.health > 0:
            if girl1.health > 0 and girl1.firepower > 0 and (time % (100 - girl1.reload) == 0):
                battle_log += str(time) + "s: " + girl1.fire_shells(girl2)
            if girl2.health > 0 and girl2.firepower > 0 and (time % (100 - girl2.reload) == 0):
                battle_log += str(time) + "s: " + girl2.fire_shells(girl1)
            if girl1.health > 0 and girl1.torpedo > 0 and (time % (200 - (girl1.reload * 2)) == 0):
                battle_log += str(time) + "s: " + girl1.launch_torps(girl2)
            if girl2.health > 0 and girl2.torpedo > 0 and (time % (200 - (girl2.reload * 2)) == 0):
                battle_log += str(time) + "s: " + girl2.launch_torps(girl1)
            if girl1.health > 0 and girl1.aviation > 0 and (time % (200 - (girl1.reload * 2)) == 0):
                battle_log += str(time) + "s: " + girl1.aviation_attack(girl2)
            if girl2.health > 0 and girl2.aviation > 0 and (time % (200 - (girl2.reload * 2)) == 0):
                battle_log += str(time) + "s: " + girl2.aviation_attack(girl1)
            time += 1
        battle_log += girl1.name + " finished battle with " + str(girl1.health) + " HP while " + girl2.name + " finished battle with " + str(girl2.health) + " HP!"
        return battle_log

    @commands.command(pass_context=True, brief="Build random ship for money")
    async def build(self, ctx, times=1):
        profile = get_profile(ctx.author.id)
        if profile:
            money = int(profile['Profile']['Money'])
            if money >= build_cost * times:
                while times > 0:
                    EMB = None
                    while not EMB:
                        EMB = self._build(ctx.author, profile)
                    await ctx.send(embed=EMB)
                    profile['Profile']['Money'] = str(int(profile['Profile']['Money']) - build_cost)
                    save_profile(ctx.author.id, profile)
                    times -= 1
                    await asyncio.sleep(1)
            else:
                await ctx.send(":no_entry: Sorry, " + self.bot._user(ctx.author.id) + "!\nBut you don't have enough money to do that")
        else:
            await ctx.send(":no_entry: Sorry, " + self.bot._user(ctx.author.id) + "!\nBut you have no profile yet. Create one with ``Bel new``")

    def _build(self, _user: discord.user, profile: configparser.ConfigParser):
        _url = "https://azurlane.koumakan.jp/List_of_Ships"  # _by_Stats"
        path_to_html_file = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "ALDB/List_of_Ships.html")
        self.bot.get_cog("AzurLane").update_html_file(path_to_html_file, _url)
        ships = pandas.read_html(path_to_html_file)
        R = random.Random()
        allowed_nations = ['Eagle Union', 'Royal Navy', 'Sakura Empire', 'Ironblood', 'Eastern Radiance', 'North Union']
        category = random.choices(['Normal', 'Rare', 'Elite', 'Super Rare'], [15, 7, 3, 1])
        if category[0] is 'Normal':
            color = discord.Color.lighter_grey()
        elif category[0] is 'Rare':
            color = discord.Color.blue()
        elif category[0] is 'Elite':
            color = discord.Color.purple()
        else:
            color = discord.Color.gold()
        possible_ship_rolls = []
        for row in range(len(ships[0]['Name'])):
            if ships[0]["Rarity"][row] == category[0] and ships[0]["Affiliation"][row] in allowed_nations:
                possible_ship_rolls.append(ships[0]["Name"][row])

        rolled_girl_name = possible_ship_rolls[R.randint(0, len(possible_ship_rolls) - 1)]
        ship_name = self.bot.get_cog("AzurLane").fix_name(rolled_girl_name)
        path_to_ship_file = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "ALDB/ships/" + ship_name + ".html")
        self.bot.get_cog("AzurLane").update_html_file(path_to_ship_file, 'https://azurlane.koumakan.jp/' + ship_name.replace("'", '%27').replace('(', '%28').replace(')', '%29').replace("%C3%B6", 'ö'))

        ship_info = pandas.read_html(path_to_ship_file)
        dicts_info = {}
        Retrofit = False
        Submarine = False
        for i in range(len(ship_info)):
            dicts_info[i] = ship_info.copy().pop(i)
            if 'Index' in dicts_info[i].keys():
                Retrofit = True
        if dicts_info[1][1][2] == "Submarine":
            Submarine = True
        base = no_retro_type['base']
        if Retrofit:
            base = retro_type['base']
        if Submarine:
            base = submarine_type['base']
        web_raw = codecs.open(path_to_ship_file, encoding='utf-8').read()
        pic_url = 'https://azurlane.koumakan.jp/' + (web_raw.partition('<img alt="' + ship_name.replace('_', ' ')
                                                                       + 'Icon.png" src="')[2].partition('"')[0]).replace("'", '\%27').replace('(', '\%28').replace(')', '\%29').replace("\%C3\%B6",
                                                                                                                                                                                         'ö')
        # noinspection PyUnusedLocal
        waifu_number = 1 + sum(1 for f in os.listdir(dir_path + str(_user.id)))
        try:
            girl = configparser.ConfigParser()
            girl.add_section('main')
            girl.set('main', 'name', rolled_girl_name)
            girl.set('main', 'pic', pic_url)
            girl.set('main', "Rarity", category[0])
            girl.set('main', str(dicts_info[1][0][1]), str(dicts_info[1][1][1]))
            girl.set('main', str(dicts_info[1][0][2]), str(dicts_info[1][1][2]))
            girl.set('main', "Mission_started", "0")

            girl.add_section('stats')
            girl.set('stats', 'level', '1')
            girl.set('stats', "Exp", "0")
            girl.set('stats', "Health", str(dicts_info[base][1][0]).partition('.')[0])
            girl.set('stats', "Firepower", str(dicts_info[base][1][1]).partition('.')[0])
            girl.set('stats', "Anti-air", str(dicts_info[base][1][2]).partition('.')[0])
            girl.set('stats', "Torpedo", str(dicts_info[base][3][1]).partition('.')[0])
            girl.set('stats', "Aviation", str(dicts_info[base][3][2]).partition('.')[0])
            girl.set('stats', "Reload", str(dicts_info[base][5][0]).partition('.')[0])
            girl.set('stats', "Accuracy", str(dicts_info[base][7][2]).partition('.')[0])
            girl.set('stats', "Evasion", str(dicts_info[base][5][1]).partition('.')[0])
        except Exception:
            return False
        else:
            if not os.path.exists(dir_path + str(_user.id)):
                os.mkdir(dir_path + str(_user.id))
            profile['Harem'][str(waifu_number)] = str(rolled_girl_name)
            with codecs.open(dir_path + (str(_user.id) + '/' + str(waifu_number) + ".ini"), 'w', 'utf-8') as waifu:
                girl.write(waifu)
                waifu.flush()
                waifu.close()
                print(logtime() + Fore.CYAN + "Girl built and saved: " + rolled_girl_name)
            return discord.Embed(title=str(waifu_number) + ") " + rolled_girl_name, description=str(dicts_info[1][1][2]) + "\n" + str(dicts_info[1][1][1]) + "\n" + category[0], color=color) \
                .set_thumbnail(url=pic_url) \
                .set_footer(icon_url=_user.avatar_url, text=_user.display_name)

    @commands.command(pass_context=True, aliases=['p'], brief="Show Commander's profile")
    async def profile(self, ctx):
        await ctx.channel.trigger_typing()
        if not get_profile(ctx.author.id):
            await ctx.send(":no_entry: Sorry, Commander!\nBut you have no profile yet. Create one with ``Bel new``")
        else:
            await ctx.send(embed=self.show_profile(ctx))

    def show_profile(self, ctx):
        resultEmbed = discord.Embed()
        profile = get_profile(ctx.author.id)

        resultEmbed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        resultEmbed.title = profile['Profile']['Nickname']
        text = "**Level:** " + profile['Profile']['Level']
        text += "\n**Exp:** " + profile['Profile']['Exp']
        text += "\n**Money:** " + profile['Profile']['Money']
        text += "\n**PvP wins:** " + profile['Profile']['PvP_wins']
        # noinspection PyUnusedLocal
        text += "\n**Harem size:** " + str(get_harem_size(ctx.author.id))

        resultEmbed.description = text
        profile.clear()
        return resultEmbed

    @commands.command(pass_context=True, aliases=['new', 'start', 'reset'], brief="Create new Commander")
    async def create(self, ctx):
        await ctx.channel.trigger_typing()
        user_path = dir_path + str(ctx.author.id) + ".ini"
        if not os.path.exists(user_path):
            await self.create_profile(ctx)
            await ctx.send("Successfully created new profile, Commander! :white_check_mark:\nUse ``Bel profile`` to check it.")
        else:
            answer = await ctx.send(":bangbang: Commander, your profile already exists!\nDo you want to reset it?")
            await answer.add_reaction('✅')
            await answer.add_reaction('❌')

            def check(_reaction, _user):
                return _reaction.message.id == answer.id and _user == ctx.author and (str(_reaction.emoji) == '✅' or str(_reaction.emoji) == '❌')

            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=15.0, check=check)
            except asyncio.TimeoutError:
                await answer.clear_reactions()
                await answer.edit(content="Cancelled due to timeout.")
                await asyncio.sleep(15)
                await answer.delete()
                try:
                    await ctx.message.delete()
                except Exception:
                    ""
            else:
                if reaction.emoji == '✅':
                    await self.create_profile(ctx)
                    await answer.clear_reactions()
                    await answer.edit(content="Profile reset successful!")
                    try:
                        await ctx.message.delete()
                    except Exception:
                        ""
                else:
                    await answer.clear_reactions()
                    await answer.edit(content="Profile reset cancelled.")
                    await asyncio.sleep(15)
                    await answer.delete()
                    try:
                        await ctx.message.delete()
                    except Exception:
                        ""

    async def create_profile(self, ctx: discord.ext.commands.Context):
        ask = await ctx.send("Please, write your nickname:")

        def check(msg):
            return msg.author == ctx.author and msg.channel == ctx.channel and msg.clean_content

        try:
            nickname_msg = await self.bot.wait_for('message', timeout=45.0, check=check)
        except asyncio.TimeoutError:
            await ask.clear_reactions()
            await ask.edit(content="Cancelled due to timeout.")
            await asyncio.sleep(15)
            await ask.delete()
        else:
            user_path = dir_path + str(ctx.author.id) + ".ini"
            if os.path.exists(user_path.replace(".ini", "")):
                clear_folder(user_path.replace(".ini", "/"))
                os.rmdir(os.path.abspath(user_path.replace(".ini", "")))
            if not os.path.exists(dir_path + str(ctx.author.id)):
                os.mkdir(dir_path + str(ctx.author.id))
            user_conf = configparser.ConfigParser()
            user_conf.add_section('Profile')
            user_conf.set('Profile', 'Nickname', nickname_msg.clean_content)
            user_conf.set('Profile', 'Level', '1')
            user_conf.set('Profile', 'Exp', '0')
            user_conf.set('Profile', 'Money', '1000')
            user_conf.set('Profile', 'PvP_wins', '0')
            user_conf.add_section('Harem')
            save_profile(ctx.author.id, user_conf)
            await ask.delete()
            await nickname_msg.add_reaction('✅')

    @commands.is_owner()
    @commands.command(pass_context=True, brief="[bot owner only]Delete all profiles, harems, inventories, etc", hidden=True)
    async def globalreset(self, ctx):
        await ctx.channel.trigger_typing()
        count = clear_folder(dir_path)

        await ctx.send(":white_check_mark: Removed " + str(count) + " file(s) and all empty folders")

    @commands.command(pass_context=True, aliases=['h'], brief="Show Commander's profile")
    async def harem(self, ctx):
        if not get_profile(ctx.author.id):
            await ctx.send(":no_entry: Sorry, Commander!\nBut you have no profile yet. Create one with ``Bel new``")
            return
        if not get_harem_size(ctx.author.id):
            await ctx.send("I am sorry, " + self.bot._user(ctx.author.id) + "!\nBut you have no girls yet! Build some with ``Bel build``")
            return
        await ctx.send(embed=self.show_harem(ctx))

    def show_harem(self, ctx):
        resultEmbed = discord.Embed()
        resultEmbed.description=""
        resultEmbed.set_author(name=str(ctx.author), icon_url=ctx.author.avatar_url)
        profile = get_profile(ctx.author.id)
        resultEmbed.title = str(profile['Profile']['Nickname'])+"'s harem:"
        for girl_id in profile.options('Harem'):
            resultEmbed.description+=girl_id+") "+ profile.get('Harem', girl_id) + "\n"
        return resultEmbed


def clear_folder(string: str):
    count = 0
    for name1 in os.listdir(string):
        name = string + name1
        print(name)
        if os.path.isdir(name):
            count += clear_folder(name + '/')
            os.rmdir(os.path.abspath(name))
        if os.path.isfile(name):
            os.remove(os.path.abspath(name))
            count += 1
    return count


def get_harem_size(user_id: int):
    if os.path.exists(dir_path + str(user_id)):
        return sum(1 for f in os.listdir(dir_path + str(user_id)))


def get_profile(user_id: int):
    if os.path.exists(dir_path + str(user_id) + ".ini"):
        profile = configparser.ConfigParser()
        profile.read(dir_path + str(user_id) + ".ini")
        return profile
    else:
        return None


def save_profile(user_id: int, profile:configparser.ConfigParser):
    with codecs.open(dir_path + str(user_id) + ".ini", mode="w+", encoding="utf-8") as user_file:
        profile.write(user_file)
        user_file.flush()
        user_file.close()


def get_harem_girl_by_id(user_id: int, girl_id: int):
    if os.path.exists(dir_path + str(user_id) + "/" + str(girl_id) + ".ini"):
        girl = configparser.ConfigParser()
        girl.read(dir_path + str(user_id) + "/" + str(girl_id) + ".ini", 'utf-8')
        return BattleGirl(girl)
    else:
        return None


def randomize_dmg(dmg_to_randomize: int):
    R = random.Random()
    difference = dmg_to_randomize * 0.1
    return R.randint(int(dmg_to_randomize - difference), int(dmg_to_randomize + difference))


def setup(bot):
    bot.add_cog(BelfastGame(bot))
