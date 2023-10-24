import asyncio
import codecs
import configparser
import copy
import datetime
import math
import os
import random
import time
import traceback
from enum import IntEnum

import dill
import discord
import pandas
from discord.ext import commands

from cogs.AzurLane import no_retro_type, retro_type, submarine_type, no_retro_type_new

PICKLE = '.pickle'

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "users/")
build_cost = 1


class CellType(IntEnum):
    WATER = 1
    EARTH = 2
    WATER_WITH_CURRENT = 3
    ANOMALY = 4


class MapCell(object):
    def __init__(self, _type: CellType, _x: int, _y: int):
        self.type = _type
        self.x = _x
        self.y = _y
        self.player_base = None
        self.treasures = None


class MapWorld(object):
    def __init__(self, _w=500, _h=500):
        self.w = _w
        self.h = _h
        self.cells = []

    def generate_world(self):
        for w in range(self.w):
            line = []
            for h in range(self.h):
                line.append(MapCell(random.choices(
                    (CellType.WATER, CellType.EARTH, CellType.WATER_WITH_CURRENT, CellType.ANOMALY),
                    [30, 11, 1, 1])[0], w, h))
            self.cells.append(line)

    async def get_random_water_cell(self, including_player_bases=False) -> MapCell:
        result = None
        r = random.Random()
        while not result:
            W = r.randint(1, self.w - 1)
            H = r.randint(1, self.h - 1)
            if self.cells[W][H].type == CellType.WATER:
                if including_player_bases:
                    result = self.cells[W][H]
                else:
                    if self.cells[W][H].player_base == None:
                        result = self.cells[W][H]
        return result


class PlayerBase(object):
    def __init__(self):
        self.core_lvl = 1
        self.hq_lvl = 1
        self.radar_lvl = 0
        self.storage_lvl = 1
        self.vault_lvl = 0
        self.barracks_lvl = 1
        self.docks_lvl = 1
        self.market_lvl = 0
        self.wall_lvl = 0
        self.def_aa_lvl = 0
        self.def_water_lvl = 1
        self.def_underwater_lvl = 0


class BattleGirl(object):
    id = 0
    name = ""
    pic = ""
    rarity = ""
    faction = ""
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

    def __str__(self):
        return str(str(self.id) + "=" + self.name + "=" + str(self.health))

    def __init__(self, girl_config):
        self.id = int(girl_config.get('main', 'id'))
        self.name = girl_config.get('main', 'name')
        self.pic = girl_config.get('main', 'pic')
        self.rarity = girl_config.get('main', 'rarity')
        self.faction = girl_config.get('main', 'faction')
        self.classification = girl_config.get('main', 'classification')
        self.level = int(girl_config.get('stats', 'level'))
        self.exp = int(girl_config.get('stats', 'exp'))
        self.health = int(girl_config.get('stats', 'health'))
        self.firepower = int(girl_config.get('stats', 'firepower'))
        self.antiair = int(girl_config.get('stats', 'anti-air'))
        self.antisub = int(girl_config.get('stats', 'anti-sub'))
        self.torpedo = int(girl_config.get('stats', 'torpedo'))
        self.aviation = int(girl_config.get('stats', 'aviation'))
        self.reload = int(girl_config.get('stats', 'reload'))
        self.accuracy = int(girl_config.get('stats', 'accuracy'))
        self.evasion = int(girl_config.get('stats', 'evasion'))

    def set_id(self, girl_id: int):
        self.id = girl_id

    def fire_shells(self, enemy):
        dmg = int((self.accuracy / enemy.evasion) * self.firepower)
        dmg = randomize(dmg)
        if enemy.classification == "Submarine":
            dmg = int(dmg / 5)
        if self.torpedo == 0 and self.aviation == 0:
            dmg = int(dmg * 1.2)
        if self.classification == "Battlecruiser" or self.classification == "Battleship":
            dmg = int(dmg * 2)
        previous_health = enemy.health
        enemy.health = enemy.health - dmg
        return str(self.name + "(ID:" + str(self.id) + ") fired shells at " + enemy.name + "(" + str(previous_health) + "hp) dealing " + str(dmg) + "dmg. New " + enemy.name + "'s health=" + str(
            enemy.health) + "\n"), dmg

    def launch_torps(self, enemy):
        dmg = int((self.accuracy / (enemy.evasion * 1.5)) * self.torpedo)
        dmg = randomize(dmg)
        if enemy.classification == "Submarine":
            dmg = int(dmg / 5)
        if enemy.classification == "Destroyer":
            dmg = int(dmg / 2)
        if self.classification == "Destroyer" or self.classification == "Submarine":
            dmg = int(dmg * 2)
        previous_health = enemy.health
        enemy.health = enemy.health - dmg
        return str(self.name + "(ID:" + str(self.id) + ") send torps at " + enemy.name + "(" + str(previous_health) + "hp) dealing " + str(dmg) + "dmg. New " + enemy.name + "'s health=" + str(
            enemy.health) + "\n"), dmg

    def aviation_attack(self, enemy):
        dmg = int((self.aviation * 6 / (1 + enemy.antiair)) * self.aviation)
        dmg = randomize(dmg)
        if enemy.classification == "Submarine":
            dmg = int(dmg / 10)
        previous_health = enemy.health
        enemy.health = enemy.health - dmg
        return str(
            self.name + "(ID:" + str(self.id) + ") launched aviastrike at " + enemy.name + "(" + str(previous_health) + "hp) dealing " + str(dmg) + "dmg. New " + enemy.name + "'s health=" + str(
                enemy.health) + "\n"), dmg

    def add_exp(self, exp: int):
        self.exp += exp
        return self.check_lvlup()

    def check_lvlup(self):
        result = ""
        info = pandas.read_html(dir_path.replace("users/", 'ALDB/ships/') + self.name.replace(' ', '_') + '.html')

        while self.exp > ((self.level ^ 2) * 200):
            self.exp -= (self.level ^ 2) * 200
            self.level += 1
            result = str(self.name) + " leveled up to " + str(self.level) + " level!"
            self.lvlup_stats(info)
        return result

    def lvlup_stats(self, info):
        Retrofit = False
        Submarine = False
        dicts_info = {}
        for i in range(len(info)):
            dicts_info[i] = info.copy().pop(i)
            if 'Index' in dicts_info[i].keys():
                Retrofit = True
        if len(dicts_info[0]) > 1 and str(dicts_info[0][0][0]).__contains__("Construction Time"):
            if dicts_info[1][1][2] == "Submarine":
                Submarine = True
            ids = no_retro_type
            if Retrofit:
                ids = retro_type
            if Submarine:
                ids = submarine_type
            base = ids.get('120')
            self.health += int(int(dicts_info[base][1][0]) / 20)
            self.firepower += int(int(dicts_info[base][1][1]) / 20)
            self.antiair += int(int(dicts_info[base][1][2]) / 20)
            self.antisub += int(int(dicts_info[base][1][3]) / 20)
            self.torpedo += int(int(dicts_info[base][3][1]) / 20)
            self.aviation += int(int(dicts_info[base][3][2]) / 20)
            self.reload += int(int(dicts_info[base][5][0]) / 20)
            self.evasion += int(int(dicts_info[base][5][1]) / 20)
            self.accuracy += int(int(dicts_info[base][7][2]) / 20)
        else:
            base = no_retro_type_new.get('120')
            self.health += int(int(dicts_info[base][1][0]) / 20)
            self.firepower += int(int(dicts_info[base][1][1]) / 20)
            self.antiair += int(int(dicts_info[base][1][2]) / 20)
            self.antisub += int(int(dicts_info[base][1][4]) / 20)
            self.torpedo += int(int(dicts_info[base][3][1]) / 20)
            self.aviation += int(int(dicts_info[base][3][2]) / 20)
            self.accuracy += int(int(dicts_info[base][3][3]) / 20)
            self.reload += int(int(dicts_info[base][5][0]) / 20)
            self.evasion += int(int(dicts_info[base][5][1]) / 20)


class Player(object):

    def __str__(self):
        return str(self.username + "_" + str(self.pid))

    def __init__(self, username: str, pid: int):
        self.pid = pid
        self.username = username
        self.money = 10
        self.level = 1
        self.pvpw = 0
        self.pvpl = 0
        self.exp = 0
        self.harem = []
        self.base = PlayerBase()

    def add_money(self, amount: int):
        self.money += amount

    def add_exp(self, amount: int):
        self.exp += amount

    def get_harem_length(self):
        return len(self.harem)

    def get_girl(self, girl_id: int):
        return self.harem[girl_id - 1]

    def add_girl(self, girl: BattleGirl):
        girl.id = self.get_harem_length() + 1
        self.harem.append(girl)
        return girl.id

    def add_pvp_win(self):
        self.pvpw += 1

    def add_pvp_loss(self):
        self.pvpl += 1


class BelfastGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.girls_info = {}
        self.players = {}
        self.world = None
        _url = "https://azurlane.koumakan.jp/List_of_Ships"  # _by_Stats"
        path_to_html_file = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "ALDB/List_of_Ships.html")
        self.bot.get_cog("AzurLane").update_html_file(path_to_html_file, _url)
        self.ships = pandas.read_html(path_to_html_file)

        # girls = os.listdir(dir_path.replace("users/", "ALDB/ships/"))
        # for girl in girls:
        #     if girl.endswith('.html'):
        #         try:
        #             self.load_girl(str(girl.replace('.html', '')))
        #         except Exception:
        #             pass

        self.world_file_path = dir_path + "world" + PICKLE
        # if os.path.exists(self.world_file_path):
        # s = datetime.datetime.utcnow()
        # with open(file=self.world_file_path, mode="rb") as f:
        # self.world = dill.load(file=f)
        # f = datetime.datetime.utcnow()
        # print("loaded world " + str(f-s))
        # if not self.world:
        self.world = MapWorld()
        self.world.generate_world()

        # ps = os.listdir(dir_path)
        # for p in ps:
        #     if (not p.startswith("world")) and p.endswith(PICKLE) and int(p.replace(PICKLE, '')) not in self.players.keys():
        #         self.load_player(str(p))

    @commands.is_owner()
    @commands.command(pass_context=True, aliases=['ge'], hidden=True)
    async def give_exp(self, ctx, girl_id: int, exp: int):
        if 0 < int(girl_id) <= await self.get_profile(ctx.author.id).get_harem_length():
            if exp > 0:
                await ctx.channel.typing()
                girl = self.get_harem_girl_by_id(ctx.author.id, int(girl_id))
                result = girl.add_exp(exp)
                # save_harem_girl_by_id(ctx.author.id, girl)
                if result == "":
                    await ctx.message.add_reaction('✅')
                    await ctx.message.delete(delay=15)
                else:
                    await ctx.send(embed=discord.Embed(description=result), delete_after=15)
            else:
                await ctx.message.add_reaction('🚫')
            await ctx.message.delete(delay=15)
        else:
            resultEmbed = discord.Embed()
            resultEmbed.title = "Excuse me, but..."
            resultEmbed.description = "You do not have a girl with the stated ID, " + self.bot.user_title(ctx.author.id) + "!"
            await ctx.send(embed=resultEmbed)
            await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, brief="[WIP time=0]Send your girl for scouting area, get money, girl exp [WIP and some other stuff]")
    async def pve(self, ctx, girl_id="placeholderLVL9999999"):
        profile = await self.get_profile(ctx.author.id)
        if girl_id.isdigit():
            if profile:
                if 0 < int(girl_id) <= await self.get_profile(ctx.author.id).get_harem_length():
                    girl = self.get_harem_girl_by_id(ctx.author.id, int(girl_id))
                    R = random.Random()
                    result = girl.add_exp(R.randint(1550, 5500))
                    # todo
                    # save_harem_girl_by_id(ctx.author.id, girl)
                    # money = int(profile.get('Profile', 'Money'))
                    # profile.set('Profile', 'Money', str(money + R.randint(100,1000)))
                    # save_profile(ctx.author.id, profile)
                    if result != "":
                        await ctx.send(embed=discord.Embed(description=result), delete_after=15)
                    await ctx.message.add_reaction('✅')
                    await ctx.message.delete(delay=5)
                else:
                    resultEmbed = discord.Embed()
                    resultEmbed.title = "Excuse me, but..."
                    resultEmbed.description = "You do not have a girl with the stated ID, " + self.bot.user_title(ctx.author.id) + "!"
                    await ctx.send(embed=resultEmbed, delete_after=15)
            else:
                resultEmbed = discord.Embed()
                resultEmbed.title = "Excuse me, but..."
                resultEmbed.description = "You do not have a game profile yet, " + self.bot.user_title(ctx.author.id) + "!"
                await ctx.send(embed=resultEmbed, delete_after=15)
        else:
            resultEmbed = discord.Embed()
            resultEmbed.title = "Excuse me, but..."
            resultEmbed.description = "You forgot to specify girl's ID, " + self.bot.user_title(ctx.author.id) + "!"
            await ctx.send(embed=resultEmbed, delete_after=15)

    @commands.is_owner()
    @commands.command(pass_context=True, aliases=['gm'], hidden=True)
    async def give_money(self, ctx, user_id: int, money_: int):
        profile = await self.get_profile(user_id)
        if profile:
            profile.add_money(money_)
            await self.save_profile(ctx.author.id)
            await ctx.message.add_reaction('✅')
            await ctx.message.delete(delay=15)
        else:
            await ctx.message.add_reaction('🚫')
            await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, brief="Duel another player at same server")
    # @commands.is_owner()
    async def duel(self, ctx, *, user_to_duel="placeholderLVL9999999"):
        await ctx.channel.typing()
        try:
            if ctx.message.mentions:
                user_to_duel = ctx.message.mentions.pop(0).id
            author_id = ctx.author.id
            if user_to_duel == "placeholderLVL9999999":
                await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut it seems like you forgot to choose a player you wanna duel.", delete_after=15)
            else:
                user = self.bot.get_user_from_guild(ctx.guild, str(user_to_duel))
                if user is None:
                    await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nCommander with predicate **" + user_to_duel + "** not found on this server.", delete_after=15)
                elif user.id is author_id:
                    await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut you can't battle yourself. Please, use ``Bel battle`` command instead.", delete_after=15)
                elif not await self.get_profile(author_id):
                    await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut you have no profile yet. Create one with ``Bel new``", delete_after=15)
                elif not await self.get_profile(author_id).get_harem_length() > 0:
                    await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut you have no girls to battle with yet! Build some with ``Bel build``", delete_after=15)
                elif not await self.get_profile(user.id):
                    await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut this Commander doesn't play this game yet (have no profile)!", delete_after=15)
                elif not await self.get_profile(user.id).get_harem_length() > 0:
                    await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut this Commander have no girls to battle with yet!")
                else:
                    result = await self.duel2players(ctx.guild, author_id, user.id)
                    await ctx.send(embed=result['embed'], delete_after=45)
                    await ctx.message.delete(delay=45)
                    # await ctx.send(file=discord.File(fp=result['filename'], filename="battle_log.log"), embed=result['embed'])
        except Exception:
            raise

    async def duel2players(self, guild: discord.Guild, user1id: int, user2id: int):
        battle_log = ""
        res_log = ""
        bat_start = datetime.datetime.utcnow()
        battle_time = 1
        dmg_dealt_by_user1 = 0
        dmg_dealt_by_user2 = 0
        user1 = self.bot.get_user_from_guild(guild, str(user1id))
        user2 = self.bot.get_user_from_guild(guild, str(user2id))
        fleet1 = {}
        fleet2 = {}
        embed = discord.Embed()
        embedtitle = user1.display_name + " fleet VS " + user2.display_name + " fleet!"
        battle_log += embedtitle + "\n"
        user1team = ""
        user2team = ""

        # don't mind all that shitton of commented logging :sweat_smile:
        for i in range(self.get_profile(user1id).get_harem_length()):
            fleet1[i + 1] = self.get_harem_girl_by_id(user1id, i + 1)
            # user1team += fleet1[i + 1].name + ", "
        # embed.add_field(name=user1.display_name + " girls: ", value=user1team)

        # battle_log += user1.display_name + " girls: " + user1team + "\n"

        for i in range(self.get_profile(user2id).get_harem_length()):
            fleet2[i + 1] = self.get_harem_girl_by_id(user2id, i + 1)
            # user2team += fleet2[i + 1].name + ", "
        # embed.add_field(name=user2.display_name + " girls: ", value=user2team)

        # battle_log += user2.display_name + " girls: " + user2team + "\n"

        R = random.Random()
        fleet1alive = len(fleet1)
        fleet2alive = len(fleet2)
        while fleet1alive > 0 and fleet2alive > 0:
            fleet1alive = 0
            fleet2alive = 0

            # print(str(battle_time) + "s, start")
            for girl in fleet1.values():
                if girl and girl.health > 0:
                    if girl.firepower > 0 and (battle_time % int(get_reload_time(girl.reload)) == 0):
                        gid = await self.get_random_girl_alive_id(fleet2)
                        if gid > 0:
                            # print(str(battle_time) + "s, team " + user1.display_name + ": " + "trying to do 1shl by " + str(girl))
                            dmg = girl.fire_shells(fleet2[gid])
                            dmg_dealt_by_user1 += dmg[1]
                            # battle_log += str(battle_time) + "s, team " + user1.display_name + ": " + str(dmg[0])
                            # print(str(battle_time) + "s, team " + user1.display_name + ": " + str(dmg[0]))
                            # for girl in fleet1.values():
                            #     print(str(girl))
                            # for girl in fleet2.values():
                            #     print(str(girl))

                    if girl.torpedo > 0 and (battle_time % int(get_reload_time(girl.reload) * 2) == 0):
                        gid = await self.get_random_girl_alive_id(fleet2)
                        if gid > 0:
                            # print(str(battle_time) + "s, team " + user1.display_name + ": " + "trying to do 1trp by " + str(girl))
                            dmg = girl.launch_torps(fleet2[gid])
                            dmg_dealt_by_user1 += dmg[1]
                            # battle_log += str(battle_time) + "s, team " + user1.display_name + ": " + str(dmg[0])
                            # print(str(battle_time) + "s, team " + user1.display_name + ": " + str(dmg[0]))
                            # for girl in fleet1.values():
                            #     print(str(girl))
                            # for girl in fleet2.values():
                            #     print(str(girl))
                    if girl.aviation > 0 and (battle_time % int(get_reload_time(girl.reload) * 2) == 0):
                        gid = await self.get_random_girl_alive_id(fleet2)
                        if gid > 0:
                            # print(str(battle_time) + "s, team " + user1.display_name + ": " + "trying to do 1avi by " + str(girl))
                            dmg = girl.aviation_attack(fleet2[gid])
                            dmg_dealt_by_user1 += dmg[1]
                            # battle_log += str(battle_time) + "s, team " + user1.display_name + ": " + str(dmg[0])
                            # print(str(battle_time) + "s, team " + user1.display_name + ": " + str(dmg[0]))
                            # for girl in fleet1.values():
                            #     print(str(girl))
                            # for girl in fleet2.values():
                            #     print(str(girl))

            for girl in fleet2.values():
                if girl and girl.health > 0:
                    if girl.firepower > 0 and (battle_time % int(get_reload_time(girl.reload)) == 0):
                        gid = await self.get_random_girl_alive_id(fleet1)
                        if gid > 0:
                            # print(str(battle_time) + "s, team " + user2.display_name + ": " + "trying to do 2shl by " + str(girl))
                            dmg = girl.fire_shells(fleet1[gid])
                            dmg_dealt_by_user2 += dmg[1]
                            # battle_log += str(battle_time) + "s, team " + user2.display_name + ": " + str(dmg[0])
                            # print(str(battle_time) + "s, team " + user2.display_name + ": " + str(dmg[0]))
                            # for girl in fleet1.values():
                            #     print(str(girl))
                            # for girl in fleet2.values():
                            #     print(str(girl))
                    if girl.torpedo > 0 and (battle_time % int(get_reload_time(girl.reload) * 2) == 0):
                        gid = await self.get_random_girl_alive_id(fleet1)
                        if gid > 0:
                            # print(str(battle_time) + "s, team " + user2.display_name + ": " + "trying to do 2trp by " + str(girl))
                            dmg = girl.launch_torps(fleet1[gid])
                            dmg_dealt_by_user2 += dmg[1]
                            # battle_log += str(battle_time) + "s, team " + user2.display_name + ": " + str(dmg[0])
                            # print(str(battle_time) + "s, team " + user2.display_name + ": " + str(dmg[0]))
                            # for girl in fleet1.values():
                            #     print(str(girl))
                            # for girl in fleet2.values():
                            #     print(str(girl))
                    if girl.aviation > 0 and (battle_time % int(get_reload_time(girl.reload) * 2) == 0):
                        gid = await self.get_random_girl_alive_id(fleet1)
                        if gid > 0:
                            # print(str(battle_time) + "s, team " + user2.display_name + ": " + "trying to do 2avi by " + str(girl))
                            dmg = girl.aviation_attack(fleet1[gid])
                            dmg_dealt_by_user2 += dmg[1]
                            # battle_log += str(battle_time) + "s, team " + user2.display_name + ": " + str(dmg[0])
                            # print(str(battle_time) + "s, team " + user2.display_name + ": " + str(dmg[0]))
                            # for girl in fleet1.values():
                            #     print(str(girl))
                            # for girl in fleet2.values():
                            #     print(str(girl))

            fl1 = {}
            fl2 = {}

            # print(str(len(fleet1.values())) + " fl1 len")
            for i in range(len(fleet1.values())):
                girl = fleet1.get(i + 1)
                if girl and girl.health > 0:
                    fl1[i + 1] = girl
                    fleet1alive += 1

            # print(str(len(fleet2.values())) + " fl2 len")
            for i in range(len(fleet2.values())):
                girl = fleet2.get(i + 1)
                if girl and girl.health > 0:
                    fl2[i + 1] = girl
                    fleet2alive += 1
            fleet1 = None
            fleet2 = None
            fleet1 = fl1.copy()
            fleet2 = fl2.copy()

            # print(str(battle_time) + "s, fin")
            battle_time += 1

        battle_log_name = dir_path.replace("users/", "") + "battle_logs/" + "battle" + str(time.time()).partition('.')[0] + "_" + str(user1id) + "_vs_" + str(user2id) + ".log"
        # with codecs.open(battle_log_name, mode="w+", encoding="utf-8") as battle_log_file:
        #     battle_log_file.write(battle_log)

        # print(str(battle_time))
        bat_fin = datetime.datetime.utcnow()
        res_log += "\n**Results**\n"
        res_log += "time passed = " + str(battle_time) + " units / " + str(bat_fin - bat_start) + "\n"
        res_log += user1.display_name + " dealt " + str(dmg_dealt_by_user1) + " damage!\n"
        res_log += user2.display_name + " dealt " + str(dmg_dealt_by_user2) + " damage!\n"
        if len(fleet1.values()) < 15:
            res_log += user1.display_name + " team:\n"
            for girl in fleet1.values():
                res_log += str(girl.id) + ") " + girl.name + " (" + str(girl.health) + " hp)\n"
        if len(fleet2.values()) < 15:
            res_log += user2.display_name + " team:\n"
            for girl in fleet2.values():
                res_log += str(girl.id) + ") " + girl.name + " (" + str(girl.health) + " hp)\n"

        if fleet1alive > 0:
            color = discord.Colour.green()
            url = user1.avatar_url
            winner_id = user1id
            looser_id = user2id
        else:
            color = discord.Colour.red()
            url = user2.avatar_url
            winner_id = user2id
            looser_id = user1id
        winner = await self.get_profile(winner_id)
        winner.add_pvp_win()
        await self.save_profile(winner_id)
        looser = await self.get_profile(looser_id)
        looser.add_pvp_loss()
        await self.save_profile(looser_id)
        res_log += "**<@" + str(winner_id) + "> won!**"
        return {'filename': battle_log_name,
                'embed': discord.Embed(title=embedtitle, description=res_log, color=color).set_thumbnail(url=url).set_footer(icon_url=user1.avatar_url, text=user1.display_name)}

    async def get_random_girl_alive_id(self, fleet: dict):
        R = random.Random()
        temp_fleet = {}
        for g in fleet.values():
            if g.health > 0:
                temp_fleet[g.id] = int(g.id)
        number = -1
        while number not in temp_fleet.values() and len(temp_fleet) > 0:
            number = R.randint(0, len(fleet))
        return number

    @commands.command(pass_context=True, brief="Battle 2 girls in test mode")
    # @commands.is_owner()
    async def battle(self, ctx, girl1_id="placeholderLVL9999999", girl2_id="placeholderLVL9999999"):
        await ctx.channel.typing()
        if not await self.get_profile(ctx.author.id):
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you have no profile yet. Create one with ``Bel new``")
        elif not await self.get_profile(ctx.author.id).get_harem_length() > 0:
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you have no girls to battle with yet! Build some with ``Bel build``")
        elif girl1_id == "placeholderLVL9999999":
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you forgot to select first girl")
        elif girl2_id == "placeholderLVL9999999":
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you forgot to select second girl")
        elif not girl1_id.isdigit() or not girl2_id.isdigit():
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you should choose girls via their IDs, using only numbers")
        else:
            girl1 = self.get_harem_girl_by_id(ctx.author.id, int(girl1_id))
            if girl1 is None:
                await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut seems like first girl's ID is wrong :thinking:")
            else:
                girl2 = self.get_harem_girl_by_id(ctx.author.id, int(girl2_id))
                if girl2 is None:
                    await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut seems like second girl's ID is wrong :thinking:")
                else:
                    result = await self.battle2girls(girl1, girl2)
                    await ctx.send(file=discord.File(fp=result['filename'], filename="battle_log.log"))

    async def battle2girls(self, girl1: BattleGirl, girl2: BattleGirl):
        battle_log = ""
        battle_time = 1
        while girl1.health > 0 and girl2.health > 0:
            if girl1.health > 0 and girl1.firepower > 0 and (battle_time % (100 - girl1.reload) == 0):
                battle_log += str(battle_time) + "s: " + girl1.fire_shells(girl2)[0]
            if girl2.health > 0 and girl2.firepower > 0 and (battle_time % (100 - girl2.reload) == 0):
                battle_log += str(battle_time) + "s: " + girl2.fire_shells(girl1)[0]
            if girl1.health > 0 and girl1.torpedo > 0 and (battle_time % (200 - (girl1.reload * 2)) == 0):
                battle_log += str(battle_time) + "s: " + girl1.launch_torps(girl2)[0]
            if girl2.health > 0 and girl2.torpedo > 0 and (battle_time % (200 - (girl2.reload * 2)) == 0):
                battle_log += str(battle_time) + "s: " + girl2.launch_torps(girl1)[0]
            if girl1.health > 0 and girl1.aviation > 0 and (battle_time % (200 - (girl1.reload * 2)) == 0):
                battle_log += str(battle_time) + "s: " + girl1.aviation_attack(girl2)[0]
            if girl2.health > 0 and girl2.aviation > 0 and (battle_time % (200 - (girl2.reload * 2)) == 0):
                battle_log += str(battle_time) + "s: " + girl2.aviation_attack(girl1)[0]
            battle_time += 1
        battle_log += girl1.name + " finished battle with " + str(girl1.health) + " HP while " + girl2.name + " finished battle with " + str(girl2.health) + " HP!"

        battle_log_name = dir_path.replace("users/", "") + "logs/" + str(girl1.id) + "_vs_" + str(girl2.id) + "_" + str(time.time()).partition('.')[0] + ".log"
        with codecs.open(battle_log_name, mode="w", encoding="utf-8") as battle_log_file:
            battle_log_file.write(battle_log)

        return {'filename': battle_log_name}

    @commands.command(pass_context=True, brief="List girls saved in memory")
    @commands.is_owner()
    async def listgirls(self, ctx, *, page="1"):
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "Girls:", list(self.girls_info.keys()), page, discord.Colour.gold(), False))

    @commands.command(pass_context=True, brief="Load existing girls into memory")
    @commands.is_owner()
    async def loadgirls(self, ctx):
        await ctx.message.add_reaction('🕑')
        girls = os.listdir(dir_path.replace("users/", "ALDB/ships/"))
        for girl in girls:
            if girl.endswith('.html'):
                try:
                    self.load_girl(girl.replace('.html', ''))
                except Exception:
                    pass
        await ctx.message.add_reaction('✅')

    def load_girl(self, ship_name: str):
        if ship_name not in self.girls_info.keys():
            # print("loading girl " + ship_name + " ...")

            path_to_ship_file = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "ALDB/ships/" + ship_name + ".html")

            web_raw = codecs.open(path_to_ship_file, encoding='utf-8').read()
            pic_url = 'https://azurlane.koumakan.jp/' + (web_raw.partition('<img alt="' + ship_name.replace('_', ' ')
                                                                           + 'Icon.png" src="')[2].partition('"')[0]) \
                .replace("'", '\%27').replace('(', '\%28').replace(')', '\%29').replace("\%C3\%B6", 'ö')
            self.girls_info[ship_name + "pic"] = str(pic_url)
            self.bot.get_cog("AzurLane").update_html_file(path_to_ship_file,
                                                          'https://azurlane.koumakan.jp/' + ship_name.replace("'", '%27').replace('(', '%28').replace(')', '%29').replace("%C3%B6", 'ö'))

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

            # f0 = datetime.datetime.utcnow()
            # print("0 stage time = "+str(f0-s0))
            # s1 = datetime.datetime.utcnow()
            girl = configparser.ConfigParser()
            result_girl = None
            try:
                girl.add_section('main')
                girl.set('main', 'id', "0")
                girl.set('main', 'name', ship_name.replace('_', ' '))
                girl.set('main', 'pic', str(self.girls_info.get(ship_name + "pic")).replace('%28', '(').replace('%29', ')'))
                girl.set('main', "Rarity", str(dicts_info[0][1][1]).strip('★'))
                girl.set('main', str(dicts_info[1][0][1]), str(dicts_info[1][1][1]))
                girl.set('main', str(dicts_info[1][0][2]), str(dicts_info[1][1][2]))
                girl.set('main', "Mission_started", "0")

                girl.add_section('stats')
                girl.set('stats', 'level', '1')
                girl.set('stats', "Exp", "0")
                girl.set('stats', "Health", str(dicts_info[base][1][0]).partition('.')[0])
                girl.set('stats', "Firepower", str(dicts_info[base][1][1]).partition('.')[0])
                girl.set('stats', "Anti-air", str(dicts_info[base][1][2]).partition('.')[0])
                girl.set('stats', "Anti-sub", str(dicts_info[base][1][3]).partition('.')[0])
                girl.set('stats', "Torpedo", str(dicts_info[base][3][1]).partition('.')[0])
                girl.set('stats', "Aviation", str(dicts_info[base][3][2]).partition('.')[0])
                girl.set('stats', "Reload", str(dicts_info[base][5][0]).partition('.')[0])
                girl.set('stats', "Accuracy", str(dicts_info[base][7][2]).partition('.')[0])
                girl.set('stats', "Evasion", str(dicts_info[base][5][1]).partition('.')[0])
                result_girl = BattleGirl(girl)
                # f1 = datetime.datetime.utcnow()
                # print("1 stage time = "+str(f1-s1))
            except Exception as error:
                print(str("".join(traceback.format_exception(etype=type(error),
                                                             value=error,
                                                             tb=error.__traceback__))).split("The above exception was the direct cause of the following")[0] + "\n")
            self.girls_info[ship_name] = result_girl
            # print("loaded girl " + ship_name + "")

    @commands.command(pass_context=True, brief="Build random ship for money")
    # @commands.is_owner()
    async def build(self, ctx, _times=1):
        player = await self.get_profile(ctx.author.id)
        times = _times
        if player:
            money = player.money
            if money >= build_cost * times:
                if times <= 5:
                    while times > 0:
                        EMB = None
                        start = datetime.datetime.utcnow()
                        while not EMB:
                            EMB = await self._build(ctx.author)
                        player.add_money(int(-build_cost))
                        finish = datetime.datetime.utcnow()
                        EMB.set_footer(text=str(finish - start), icon_url=ctx.author.avatar_url)
                        await ctx.send(embed=EMB)
                        times -= 1
                    await self.save_profile(ctx.author.id)
                elif times <= 100:
                    descr = ""
                    await ctx.message.add_reaction('🕑')
                    start = datetime.datetime.utcnow()
                    color_id = 1
                    result_color = discord.Color.lighter_grey()
                    while times > 0:
                        EMB = None
                        while not EMB:
                            EMB = await self._build(ctx.author)
                        descr += EMB.title + await self.color_to_rarity(EMB.color) + "\n"
                        if EMB.color == discord.Color.blue() and color_id < 2:
                            color_id = 2
                            result_color = discord.Color.blue()
                        if EMB.color == discord.Color.purple() and color_id < 3:
                            color_id = 3
                            result_color = discord.Color.purple()
                        if EMB.color == discord.Color.gold() and color_id < 4:
                            color_id = 4
                            result_color = discord.Color.gold()
                        if EMB.color == discord.Color.teal() and color_id < 5:
                            color_id = 5
                            result_color = discord.Color.teal()
                        player.add_money(int(-build_cost))
                        times -= 1

                    finish = datetime.datetime.utcnow()
                    resultEmbed = discord.Embed(title=self.bot.user_title(ctx.author.id) + " " + ctx.author.display_name + " got following girls:",
                                                description=descr, color=result_color)
                    resultEmbed.set_footer(text=str(finish - start), icon_url=ctx.author.avatar_url)
                    await self.save_profile(ctx.author.id)
                    await ctx.send(embed=resultEmbed, delete_after=45)
                    await ctx.message.delete(delay=45)
                else:
                    descr = ""
                    await ctx.message.add_reaction('🕑')
                    start = datetime.datetime.utcnow()
                    color_id = 1
                    result_color = discord.Color.lighter_grey()
                    while times > 0:
                        EMB = None
                        while not EMB:
                            EMB = await self._build(ctx.author)
                        descr += EMB.title + await self.color_to_rarity(EMB.color) + "\n"
                        if EMB.color == discord.Color.blue() and color_id < 2:
                            color_id = 2
                            result_color = discord.Color.blue()
                        if EMB.color == discord.Color.purple() and color_id < 3:
                            color_id = 3
                            result_color = discord.Color.purple()
                        if EMB.color == discord.Color.gold() and color_id < 4:
                            color_id = 4
                            result_color = discord.Color.gold()
                        if EMB.color == discord.Color.teal() and color_id < 5:
                            color_id = 5
                            result_color = discord.Color.teal()
                        player.add_money(int(-build_cost))
                        times -= 1

                    finish = datetime.datetime.utcnow()
                    await self.save_profile(ctx.author.id)
                    await ctx.message.add_reaction('✅')
                    await ctx.send("Finished building " + str(_times) + " girls for <@" + str(ctx.author.id) + ">!\nTook " + str(finish - start))
                    await ctx.message.delete(delay=45)
            else:
                await ctx.send(":no_entry: Sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you don't have enough money to do that")
        else:
            await ctx.send(":no_entry: Sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you have no profile yet. Create one with ``Bel new``")

    async def _build(self, _user: discord.user):
        # s0 = datetime.datetime.utcnow()
        R = random.Random()
        allowed_nations = ['Eagle Union', 'Royal Navy', 'Sakura Empire', 'Ironblood', 'Eastern Radiance', 'North Union', 'Iris Libre', 'Vichya Dominion', 'Sardegna Empire',
                           'Bilibili', 'Neptunia', 'Utawarerumono', 'KizunaAI', 'Kizuna AI', 'Hololive', 'Siren']
        category = random.choices(['Normal', 'Rare', 'Elite', 'Super Rare', 'Ultra Rare'], [25, 15, 7, 3, 1])
        if category[0] == 'Normal':
            color = discord.Color.lighter_grey()
        elif category[0] == 'Rare':
            color = discord.Color.blue()
        elif category[0] == 'Elite':
            color = discord.Color.purple()
        elif category[0] == 'Super Rare':
            color = discord.Color.gold()
        else:
            color = discord.Color.teal()
        possible_ship_rolls = []
        for row in range(len(self.ships[0]['Name'])):
            if self.ships[0]["Rarity"][row] == category[0] and self.ships[0]["Affiliation"][row] in allowed_nations:
                possible_ship_rolls.append(self.ships[0]["Name"][row])

        rolled_girl_name = possible_ship_rolls[R.randint(0, len(possible_ship_rolls) - 1)]
        ship_name = self.bot.get_cog("AzurLane").fix_name(rolled_girl_name)
        if not set("µÉéèâ").isdisjoint(ship_name):
            return False
        if ship_name not in self.girls_info.keys():
            self.load_girl(ship_name)

        player = self.players[_user.id]
        girl_copy = copy.copy(self.girls_info.get(ship_name))
        waifu_number = player.add_girl(girl_copy)

        # f0 = datetime.datetime.utcnow()
        # print("0 = " + str(f0-s0))
        # s1 = datetime.datetime.utcnow()
        emb = discord.Embed(title=str(waifu_number) + ") " + rolled_girl_name, description=str(girl_copy.classification) + "\n" + str(girl_copy.faction) + "\n" + category[0], color=color) \
            .set_thumbnail(url=self.girls_info.get(ship_name + "pic")) \
            .set_footer(icon_url=_user.avatar_url, text=player.username)
        # f1 = datetime.datetime.utcnow()
        # print("1 = " + str(f1-s1))
        return emb

    @commands.command(pass_context=True, aliases=['girl'], brief="Show girl's info from your harem")
    async def mygirl(self, ctx, *, girl_id=1):
        await ctx.channel.typing()
        if 0 < int(girl_id) <= (await self.get_profile(ctx.author.id)).get_harem_length():
            girl = self.players.get(ctx.author.id).get_girl(girl_id)
            if girl.rarity == 'Normal':
                color = discord.Color.lighter_grey()
            elif girl.rarity == 'Rare':
                color = discord.Color.blue()
            elif girl.rarity == 'Elite':
                color = discord.Color.purple()
            elif girl.rarity == 'Super Rare':
                color = discord.Color.gold()
            else:
                color = discord.Color.teal()
            resultEmbed = discord.Embed(color=color)
            resultEmbed.title = girl.name
            resultEmbed.set_thumbnail(url=girl.pic)

            resultEmbed.add_field(name="Id", value=str(girl.id))
            resultEmbed.add_field(name="Rarity", value=girl.rarity)
            resultEmbed.add_field(name="Faction", value=girl.faction)
            resultEmbed.add_field(name="Classification", value=girl.classification)
            resultEmbed.add_field(name="Level", value=str(girl.level))
            resultEmbed.add_field(name="Exp", value=str(girl.exp))
            resultEmbed.add_field(name="Health", value=str(girl.health))
            resultEmbed.add_field(name="Firepower", value=str(girl.firepower))
            resultEmbed.add_field(name="Anti-air", value=str(girl.antiair))
            resultEmbed.add_field(name="Torpedo", value=str(girl.torpedo))
            resultEmbed.add_field(name="Aviation", value=str(girl.aviation))
            resultEmbed.add_field(name="Reload", value=str(girl.reload))
            resultEmbed.add_field(name="Accuracy", value=str(girl.accuracy))
            resultEmbed.add_field(name="Evasion", value=str(girl.evasion))

            await ctx.send(embed=resultEmbed)
        else:
            resultEmbed = discord.Embed()
            resultEmbed.title = "Excuse me, but..."
            resultEmbed.description = "You do not have a girl with the stated ID, " + self.bot.user_title(ctx.author.id) + "!"
            await ctx.send(embed=resultEmbed)
        # else:
        #     resultEmbed = discord.Embed()
        #     resultEmbed.title = "Excuse me, but..."
        #     resultEmbed.description = "You forgot to choose girl's ID, " + self.bot.user_title(ctx.author.id) + "!"
        #     await ctx.send(embed=resultEmbed)

    @commands.command(pass_context=True, aliases=['p'], brief="Show Commander's profile")
    async def profile(self, ctx, *, target_user="placeholderLVL9999999"):
        await ctx.channel.typing()
        if target_user == "placeholderLVL9999999":
            if not await self.get_profile(ctx.author.id):
                await ctx.send(":no_entry: Sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you have no profile yet. Create one with ``Bel new``")
            else:
                await ctx.send(embed=await self.show_profile(ctx.author))
        else:
            user = self.bot.get_user_from_guild(ctx.guild, target_user)
            if not await self.get_profile(user.id):
                await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut this Commander doesn't play this game yet (have no profile)!")
            else:
                await ctx.send(embed=await self.show_profile(user))

    async def show_profile(self, user: discord.User):
        resultEmbed = discord.Embed()
        profile = await self.get_profile(user.id)

        resultEmbed.set_author(name=str(user), icon_url=user.avatar_url)
        resultEmbed.title = profile.username
        text = "\n**Level:** " + str(profile.level)
        text += "\n**Exp:** " + str(profile.exp)
        text += "\n**Money:** " + str(profile.money)
        text += "\n**PvP wins:** " + str(profile.pvpw)
        text += "\n**PvP losses:** " + str(profile.pvpl)
        text += "\n**Harem:** " + str(profile.get_harem_length())

        resultEmbed.description = text
        return resultEmbed

    @commands.command(pass_context=True, aliases=['new', 'start', 'reset'], brief="Create new Commander")
    async def create(self, ctx):
        await ctx.channel.typing()
        if not await self.get_profile(ctx.author.id):
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
            self.players[ctx.author.id] = Player(username=nickname_msg.clean_content, pid=ctx.author.id)
            # (await self.world.get_random_water_cell(False)).player_base = self.players[ctx.author.id].base
            await self.save_profile(ctx.author.id)
            await ask.delete()
            await nickname_msg.add_reaction('✅')

    @commands.is_owner()
    @commands.command(pass_context=True, brief="[bot owner only]Delete all profiles, harems, inventories, etc", hidden=True)
    async def globalreset(self, ctx):
        self.players = None
        self.players = {}
        await ctx.channel.typing()
        count = clear_folder(dir_path)
        self.world = MapWorld()
        self.world.generate_world()
        await ctx.send(":white_check_mark: Removed " + str(count) + " file(s), all empty folders and created new world!")

    async def color_to_rarity(self, color) -> str:
        if color == discord.Colour.teal():
            return "★★★★ Ultra Rare"
        if color == discord.Colour.gold():
            return "★★★ Super Rare"
        elif color == discord.Colour.purple():
            return "★★ Epic"
        elif color == discord.Colour.blue():
            return "★ Rare"
        else:
            return ""

    # @commands.is_owner()
    @commands.command(pass_context=True, brief="Show your owned girls list")
    async def harem(self, ctx, *, page_str="1"):
        await ctx.channel.typing()
        await ctx.send(embed=await self.simple_harem_paged_embed(ctx.message, "Your harem:", self.players.get(ctx.author.id).harem, page_str, discord.Colour.greyple(), False))

    async def simple_paged_embed(self, original_msg: discord.Message, title: str, list_to_page: list, page_str: str, color: discord.Colour, need_sort: bool):
        items_per_page = 40
        item_number = 0
        if need_sort:
            list_to_page.sort()
        try:
            item_number = (int(page_str) - 1) * items_per_page
        except Exception:
            await original_msg.channel.send("Wrong argument - must be a page number, " + self.bot.user_title(original_msg.author.id) + "!", delete_after=15)
            await original_msg.delete(delay=15)
            return
        result = ""
        page_max = item_number + items_per_page
        try:
            while item_number < page_max:
                result += str(item_number + 1) + ") " + (list_to_page[item_number]) + '\n'
                item_number += 1
        except Exception:
            pass
        emb = discord.Embed(title=title, description=result, color=color)
        emb.set_footer(text="Page {0}/{1}".format(page_str, math.ceil(len(list_to_page) / items_per_page)))
        return emb

    async def simple_harem_paged_embed(self, original_msg: discord.Message, title: str, list_to_page: list, page_str: str, color: discord.Colour, need_sort: bool):
        items_per_page = 40
        item_number = 1
        if need_sort:
            list_to_page.sort()
        try:
            item_number = ((int(page_str) - 1) * items_per_page) + 1
        except Exception:
            await original_msg.channel.send("Wrong argument - must be a page number, " + self.bot.user_title(original_msg.author.id) + "!", delete_after=15)
            await original_msg.delete(delay=15)
            return
        result = ""
        page_max = item_number + items_per_page
        try:
            while item_number <= page_max and item_number <= len(list_to_page):
                result += str(item_number) + ") " + str(list_to_page[item_number - 1].name) + '\n'
                item_number += 1
        except Exception:
            pass
        emb = discord.Embed(title=title, description=result, color=color)
        emb.set_footer(text="Page {0}/{1}".format(page_str, math.ceil(len(list_to_page) / items_per_page)))
        return emb

    async def get_profile(self, user_id: int) -> Player:
        if user_id in self.players.keys():
            return self.players.get(user_id)
        if os.path.exists(dir_path + str(user_id) + PICKLE):
            with open(file=dir_path + str(user_id) + PICKLE, mode="rb") as f:
                self.players[user_id] = dill.load(file=f)
            print("loaded player " + self.players.get(user_id).username)
            return self.players.get(user_id)
        return None

    @commands.is_owner()
    @commands.command(pass_context=True, brief="Save everything to hard drive", hidden=True)
    async def saveall(self, ctx):
        await ctx.message.add_reaction('✅')
        await self.save_all()

    async def save_all(self):
        while (True):
            # for uid in self.players.keys():
            # await self.save_profile(uid)
            await self.save_world()
            await asyncio.sleep(500)

    async def save_profile(self, user_id: int):
        s = datetime.datetime.utcnow()
        with open(file=dir_path + str(user_id) + PICKLE, mode="wb") as f:
            dill.dump(obj=self.players.get(user_id), file=f)
        f = datetime.datetime.utcnow()
        print("saved player " + self.players.get(user_id).username + " " + str(f - s))

    async def save_world(self):
        s = datetime.datetime.utcnow()
        with open(file=self.world_file_path, mode="wb") as f:
            dill.dump(obj=self.world, file=f)
        f = datetime.datetime.utcnow()
        print("saved world " + str(f - s))

    def load_player(self, path: str):
        pid = int(path.replace(PICKLE, ''))
        with open(file=dir_path + path, mode="rb") as f:
            self.players[pid] = dill.load(file=f)
        print("loaded player " + self.players.get(pid).username)

    async def get_harem_girl_by_id(self, user_id: int, girl_id: int) -> BattleGirl:
        return self.players[user_id].get_girl(girl_id)


def clear_folder(string: str):
    count = 0
    for name1 in os.listdir(string):
        name = string + name1
        # print(name)
        if os.path.isdir(name):
            count += clear_folder(name + '/')
            os.rmdir(os.path.abspath(name))
        if os.path.isfile(name):
            os.remove(os.path.abspath(name))
            count += 1
    return count


def randomize(to_randomize: int):
    R = random.Random()
    difference = to_randomize * 0.1
    return R.randint(int(to_randomize - difference), int(to_randomize + difference))


def get_reload_time(reload_stat: int):
    return math.log(reload_stat, 1.15)


async def setup(bot):
    await bot.add_cog(BelfastGame(bot))
