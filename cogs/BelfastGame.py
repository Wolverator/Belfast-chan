import asyncio
import codecs
import configparser
import os
import random
import time

import discord
import pandas
from colorama import Fore
from discord.ext import commands

from cogs.AzurLane import no_retro_type, retro_type, submarine_type, no_retro_type_new
from cogs.BelfastUtils import logtime

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "users/")
build_cost = 100


class BattleGirl(object):
    id = 0
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

    def __str__(self):
        return str(str(self.id) + "=" + self.name + "=" + str(self.health))

    def __init__(self, girl_config):
        self.id = int(girl_config.get('main', 'id'))
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
        self.antisub = int(girl_config.get('stats', 'anti-sub'))
        self.torpedo = int(girl_config.get('stats', 'torpedo'))
        self.aviation = int(girl_config.get('stats', 'aviation'))
        self.reload = int(girl_config.get('stats', 'reload'))
        self.accuracy = int(girl_config.get('stats', 'accuracy'))
        self.evasion = int(girl_config.get('stats', 'evasion'))

    def add_exp(self, exp: int):
        self.exp += exp
        return self.check_lvlup()

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

    def check_lvlup(self):
        result = ""
        while self.exp > (self.level * 200):
            self.exp -= self.level * 200
            self.level += 1
            result = str(self.name) + " leveled up to " + str(self.level) + " level!"
            self.lvlup_stats()
        return result

    def lvlup_stats(self):
        Retrofit = False
        Submarine = False
        info = pandas.read_html(dir_path.replace("users/", 'ALDB/ships/') + self.name.replace(' ', '_') + '.html')
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
            self.health+= int(int(dicts_info[base][1][0])/20)
            self.firepower+= int(int(dicts_info[base][1][1])/20)
            self.antiair+= int(int(dicts_info[base][1][2])/20)
            self.antisub+= int(int(dicts_info[base][1][3])/20)
            self.torpedo+= int(int(dicts_info[base][3][1])/20)
            self.aviation+= int(int(dicts_info[base][3][2])/20)
            self.reload+= int(int(dicts_info[base][5][0])/20)
            self.evasion+= int(int(dicts_info[base][5][1])/20)
            self.accuracy+= int(int(dicts_info[base][7][2])/20)
        else:
            base = no_retro_type_new.get('120')
            self.health+= int(int(dicts_info[base][1][0])/20)
            self.firepower+= int(int(dicts_info[base][1][1])/20)
            self.antiair+= int(int(dicts_info[base][1][2])/20)
            self.antisub+= int(int(dicts_info[base][1][4])/20)
            self.torpedo+= int(int(dicts_info[base][3][1])/20)
            self.aviation+= int(int(dicts_info[base][3][2])/20)
            self.accuracy+= int(int(dicts_info[base][3][3])/20)
            self.reload+= int(int(dicts_info[base][5][0])/20)
            self.evasion+= int(int(dicts_info[base][5][1])/20)


class BelfastGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.is_owner()
    @commands.command(pass_context=True, aliases=['ge'], hidden=True)
    async def give_exp(self, ctx, girl_id:int, exp:int):
        #if girl_id.isdigit():
        if 0 < int(girl_id) <= get_harem_size(ctx.author.id):
            if exp>0:
                await ctx.channel.trigger_typing()
                girl = get_harem_girl_by_id(ctx.author.id, int(girl_id))
                result = girl.add_exp(exp)
                save_harem_girl_by_id(ctx.author.id, girl)
                if result=="":
                    await ctx.message.add_reaction('✅')
                else:
                    await ctx.send(embed=discord.Embed(description=result))
            else:
                await ctx.message.add_reaction('🚫')
        else:
            resultEmbed = discord.Embed()
            resultEmbed.title = "Excuse me, but..."
            resultEmbed.description = "You do not have a girl with the stated ID, " + self.bot.user_title(ctx.author.id) + "!"
            await ctx.send(embed=resultEmbed)
        #else:
         #   resultEmbed = discord.Embed()
         #   resultEmbed.title = "Excuse me, but..."
        #    resultEmbed.description = "You forgot to choose girl's ID, " + self.bot.user_title(ctx.author.id) + "!"
        #    await ctx.send(embed=resultEmbed)

    @commands.command(pass_context=True, brief="Duel another player at same server")
    async def duel(self, ctx, *, user_to_duel="placeholderLVL9999999"):
        await ctx.channel.trigger_typing()
        try:
            if ctx.message.mentions:
                user_to_duel = ctx.message.mentions.pop(0).id
            author_id = ctx.author.id
            if user_to_duel != "placeholderLVL9999999":
                user = self.bot.get_user_from_guild(ctx.guild, str(user_to_duel))
                if user is not None:
                    if get_profile(author_id):
                        if get_harem_size(author_id) and get_harem_size(author_id) > 0:
                            if get_profile(user.id):
                                if get_harem_size(user.id) and get_harem_size(user.id) > 0:
                                    result = self.duel2players(ctx.guild, author_id, user.id)
                                    await ctx.send(file=discord.File(fp=result['filename'], filename="battle_log.log"), embed=result['embed'])
                                else:
                                    await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut this Commander have no girls to battle with yet!")
                            else:
                                await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut this Commander doesn't play this game yet (have no profile)!")
                        else:
                            await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut you have no girls to battle with yet! Build some with ``Bel build``")
                    else:
                        await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut you have no profile yet. Create one with ``Bel new``")
                else:
                    await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nCommander with predicate **" + user_to_duel + "** not found on this server.")
            else:
                await ctx.send("I am sorry, " + self.bot.user_title(author_id) + "!\nBut it seems like you forgot to choose a player you wanna duel.")
        except Exception:
            raise

    @commands.command(pass_context=True, brief="Battle 2 girls in test mode")
    async def battle(self, ctx, girl1_id="placeholderLVL9999999", girl2_id="placeholderLVL9999999"):
        await ctx.channel.trigger_typing()
        if get_profile(ctx.author.id):
            if get_harem_size(ctx.author.id) and get_harem_size(ctx.author.id) > 0:
                if girl1_id != "placeholderLVL9999999":
                    if girl2_id != "placeholderLVL9999999":
                        if girl1_id.isdigit() and girl2_id.isdigit():
                            girl1 = get_harem_girl_by_id(ctx.author.id, int(girl1_id))
                            if girl1 is not None:
                                girl2 = get_harem_girl_by_id(ctx.author.id, int(girl2_id))
                                if girl2 is not None:
                                    await ctx.send("```" + self.battle2girls(girl1, girl2) + "```")
                                else:
                                    await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut seems like second girl's ID is wrong :thinking:")
                            else:
                                await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut seems like first girl's ID is wrong :thinking:")
                        else:
                            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you should choose girls via their IDs, using only numbers")
                    else:
                        await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you forgot to select second girl")
                else:
                    await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you forgot to select first girl")
            else:
                await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you have no girls to battle with yet! Build some with ``Bel build``")
        else:
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you have no profile yet. Create one with ``Bel new``")

    def duel2players(self, guild: discord.Guild, user1id: int, user2id: int):
        battle_log = ""
        res_log = ""

        battle_time = 0
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

        for i in range(get_harem_size(user1id)):
            fleet1[i + 1] = get_harem_girl_by_id(user1id, i + 1)
            user1team += fleet1[i + 1].name + ", "
        embed.add_field(name=user1.display_name + " girls: ", value=user1team)

        battle_log += user1.display_name + " girls: " + user1team + "\n"

        for i in range(get_harem_size(user2id)):
            fleet2[i + 1] = get_harem_girl_by_id(user2id, i + 1)
            user2team += fleet2[i + 1].name + ", "
        embed.add_field(name=user2.display_name + " girls: ", value=user2team)

        battle_log += user2.display_name + " girls: " + user2team + "\n"

        R = random.Random()
        fleet1alive = len(fleet1)
        fleet2alive = len(fleet2)
        while fleet1alive > 0 and fleet2alive > 0:
            fleet1alive = 0
            fleet2alive = 0

            for girl in fleet1.values():
                if girl and girl.health > 0:
                    if girl.firepower > 0 and (battle_time % int(get_reload_time(girl.reload)) == 0):
                        gid = self.get_random_girl_alive_id(fleet2)
                        if gid > 0:
                            dmg = girl.fire_shells(fleet2[gid])
                            dmg_dealt_by_user1 += dmg[1]
                            battle_log += str(battle_time) + "s, team " + user1.display_name + ": " + str(dmg[0])
                    if girl.torpedo > 0 and (battle_time % int(get_reload_time(girl.reload) * 2) == 0):
                        gid = self.get_random_girl_alive_id(fleet2)
                        if gid > 0:
                            dmg = girl.launch_torps(fleet2[gid])
                            dmg_dealt_by_user1 += dmg[1]
                            battle_log += str(battle_time) + "s, team " + user1.display_name + ": " + str(dmg[0])
                    if girl.aviation > 0 and (battle_time % int(get_reload_time(girl.reload) * 2) == 0):
                        gid = self.get_random_girl_alive_id(fleet2)
                        if gid > 0:
                            dmg = girl.aviation_attack(fleet2[gid])
                            dmg_dealt_by_user1 += dmg[1]
                            battle_log += str(battle_time) + "s, team " + user1.display_name + ": " + str(dmg[0])

            for girl in fleet2.values():
                if girl and girl.health > 0:
                    if girl.firepower > 0 and (battle_time % int(get_reload_time(girl.reload)) == 0):
                        gid = self.get_random_girl_alive_id(fleet1)
                        if gid > 0:
                            dmg = girl.fire_shells(fleet1[gid])
                            dmg_dealt_by_user2 += dmg[1]
                            battle_log += str(battle_time) + "s, team " + user2.display_name + ": " + str(dmg[0])
                    if girl.torpedo > 0 and (battle_time % int(get_reload_time(girl.reload) * 2) == 0):
                        gid = self.get_random_girl_alive_id(fleet1)
                        if gid > 0:
                            dmg = girl.launch_torps(fleet1[gid])
                            dmg_dealt_by_user2 += dmg[1]
                            battle_log += str(battle_time) + "s, team " + user2.display_name + ": " + str(dmg[0])
                    if girl.aviation > 0 and (battle_time % int(get_reload_time(girl.reload) * 2) == 0):
                        gid = self.get_random_girl_alive_id(fleet1)
                        if gid > 0:
                            dmg = girl.aviation_attack(fleet1[gid])
                            dmg_dealt_by_user2 += dmg[1]
                            battle_log += str(battle_time) + "s, team " + user2.display_name + ": " + str(dmg[0])
            for girl in fleet1.values():
                if girl and girl.health > 0:
                    fleet1alive += 1
            for girl in fleet2.values():
                if girl and girl.health > 0:
                    fleet2alive += 1
            battle_time += 1

        battle_log_name = dir_path.replace("users/", "") + "battle_logs/" + str(user1id) + "_vs_" + str(user2id) + "_" + str(time.time()).partition('.')[0] + ".log"
        with codecs.open(battle_log_name, mode="w", encoding="utf-8") as battle_log_file:
            battle_log_file.write(battle_log)

        res_log += "\n**Results**\n"
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
        winner = get_profile(winner_id)
        winner.set('Profile', 'PvP_wins', str(1 + int(winner.get('Profile', 'PvP_wins'))))
        save_profile(winner_id, winner)
        looser = get_profile(looser_id)
        looser.set('Profile', 'PvP_loses', str(1 + int(looser.get('Profile', 'PvP_loses'))))
        save_profile(looser_id, looser)

        return {'filename': battle_log_name, 'embed': discord.Embed(title=embedtitle, description=res_log, color=color) \
            .set_thumbnail(url=url) \
            .set_footer(icon_url=user1.avatar_url, text=user1.display_name)}

    def get_random_girl_alive_id(self, fleet: dict):
        R = random.Random()
        temp_fleet = {}
        for g in fleet.values():
            if g.health > 0:
                temp_fleet[g.id] = int(g.id)
        number = -1
        # print(str(temp_fleet))
        while number not in temp_fleet.values() and len(temp_fleet) > 0:
            number = R.randint(0, len(fleet))
            # print(str(temp_fleet)+"----"+str(number))
        return number

    def battle2girls(self, girl1: BattleGirl, girl2: BattleGirl):
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
        return battle_log

    @commands.command(pass_context=True, brief="Build random ship for money")
    async def build(self, ctx, times=1):
        profile = get_profile(ctx.author.id)
        if profile:
            money = int(profile.get('Profile', 'Money'))
            if money >= build_cost * times:
                if times < 5:
                    while times > 0:
                        await ctx.channel.trigger_typing()
                        EMB = None
                        while not EMB:
                            EMB = self._build(ctx.author)
                        await ctx.send(embed=EMB)
                        profile.set('Profile', 'Money', str(int(profile.get('Profile', 'Money')) - build_cost))
                        save_profile(ctx.author.id, profile)
                        times -= 1
                        await asyncio.sleep(1)
                else:
                    color = discord.Colour.lighter_grey()
                    descr = ""
                    while times > 0:
                        await ctx.channel.trigger_typing()
                        EMB = None
                        while not EMB:
                            EMB = self._build(ctx.author)
                        descr += EMB.title + self.color_to_rarity(EMB.color) + "\n"
                        if EMB.color == discord.Colour.gold() and color != discord.Colour.gold():
                            color = discord.Colour.gold()
                        if EMB.color == discord.Colour.purple() and color != discord.Colour.gold() and color != discord.Colour.purple():
                            color = discord.Colour.purple()
                        if (EMB.color == discord.Colour.blue() and color != discord.Colour.gold() and color != discord.Colour.purple()
                                and color != discord.Colour.blue()):
                            color = discord.Colour.blue()
                        profile.set('Profile', 'Money', str(int(profile.get('Profile', 'Money')) - build_cost))
                        save_profile(ctx.author.id, profile)
                        times -= 1
                    resultEmbed = discord.Embed(title=self.bot.user_title(ctx.author.id) + " " + ctx.author.display_name + " got following girls:",
                                                description=descr, color=color)
                    await ctx.send(embed=resultEmbed)
            else:
                await ctx.send(":no_entry: Sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you don't have enough money to do that")
        else:
            await ctx.send(":no_entry: Sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you have no profile yet. Create one with ``Bel new``")

    def _build(self, _user: discord.user):
        _url = "https://azurlane.koumakan.jp/List_of_Ships"  # _by_Stats"
        path_to_html_file = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "ALDB/List_of_Ships.html")
        self.bot.get_cog("AzurLane").update_html_file(path_to_html_file, _url)
        ships = pandas.read_html(path_to_html_file)
        R = random.Random()
        allowed_nations = ['Eagle Union', 'Royal Navy', 'Sakura Empire', 'Ironblood', 'Eastern Radiance', 'North Union', 'Iris Libre', 'Vichya Dominion', 'Sardegna Empire',
                           'Bilibili', 'Neptunia', 'Utawarerumono', 'KizunaAI', 'Kizuna AI', 'Hololive', 'Siren']
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
        girl = configparser.ConfigParser()
        try:
            girl.add_section('main')
            girl.set('main', 'id', str(waifu_number))
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
            girl.set('stats', "Anti-sub", str(dicts_info[base][1][3]).partition('.')[0])
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
            with codecs.open(dir_path + (str(_user.id) + '/' + str(waifu_number) + ".ini"), 'w', 'utf-8') as waifu:
                girl.write(waifu)
                waifu.flush()
                #print(logtime() + Fore.CYAN + "Girl built and saved: " + rolled_girl_name)
            return discord.Embed(title=str(waifu_number) + ") " + rolled_girl_name, description=str(dicts_info[1][1][2]) + "\n" + str(dicts_info[1][1][1]) + "\n" + category[0], color=color) \
                .set_thumbnail(url=pic_url) \
                .set_footer(icon_url=_user.avatar_url, text=_user.display_name)

    @commands.command(pass_context=True, aliases=['girl'], brief="Show girl's info from your harem")
    async def mygirl(self, ctx, *, girl_id="-"):
        await ctx.channel.trigger_typing()
        if girl_id.isdigit():
            if 0 < int(girl_id) <= get_harem_size(ctx.author.id):
                girl = get_harem_girl_by_id(ctx.author.id, int(girl_id))
                resultEmbed = discord.Embed()
                resultEmbed.title = girl.name
                resultEmbed.set_thumbnail(url=girl.pic)

                resultEmbed.add_field(name="Id", value=str(girl.id))
                resultEmbed.add_field(name="Rarity", value=girl.rarity)
                resultEmbed.add_field(name="Nationality", value=girl.nationality, )
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
        else:
            resultEmbed = discord.Embed()
            resultEmbed.title = "Excuse me, but..."
            resultEmbed.description = "You forgot to choose girl's ID, " + self.bot.user_title(ctx.author.id) + "!"
            await ctx.send(embed=resultEmbed)

    @commands.command(pass_context=True, aliases=['p'], brief="Show Commander's profile")
    async def profile(self, ctx, *, target_user="placeholderLVL9999999"):
        await ctx.channel.trigger_typing()
        if target_user is "placeholderLVL9999999":
            if not get_profile(ctx.author.id):
                await ctx.send(":no_entry: Sorry, Commander!\nBut you have no profile yet. Create one with ``Bel new``")
            else:
                await ctx.send(embed=self.show_profile(ctx.author))
        else:
            user = self.bot.get_user_from_guild(ctx.guild, target_user)
            if not get_profile(user.id):
                await ctx.send(":no_entry: Sorry, Commander!\nBut you have no profile yet. Create one with ``Bel new``")
            else:
                await ctx.send(embed=self.show_profile(user))

    def show_profile(self, user: discord.User):
        resultEmbed = discord.Embed()
        profile = get_profile(user.id)

        resultEmbed.set_author(name=str(user), icon_url=user.avatar_url)
        resultEmbed.title = profile.get('Profile', 'Nickname')
        text = "**Level:** " + profile.get('Profile', 'Level')
        text += "\n**Exp:** " + profile.get('Profile', 'Exp')
        text += "\n**Money:** " + profile.get('Profile', 'Money')
        text += "\n**PvP wins:** " + profile.get('Profile', 'PvP_wins')
        text += "\n**PvP loses:** " + profile.get('Profile', 'PvP_loses')
        # noinspection PyUnusedLocal
        text += "\n**Harem:** " + str(get_harem_size(user.id))

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
                os.mkdir(dir_path + "/" + str(ctx.author.id))
            user_conf = configparser.ConfigParser()
            user_conf.add_section('Profile')
            user_conf.set('Profile', 'Nickname', nickname_msg.clean_content)
            user_conf.set('Profile', 'Level', '1')
            user_conf.set('Profile', 'Exp', '0')
            user_conf.set('Profile', 'Money', '1000')
            user_conf.set('Profile', 'PvP_wins', '0')
            user_conf.set('Profile', 'PvP_loses', '0')
            with codecs.open(user_path, mode="w", encoding="utf-8") as user_file:
                user_conf.write(user_file)
            await ask.delete()
            await nickname_msg.add_reaction('✅')

    @commands.is_owner()
    @commands.command(pass_context=True, brief="[bot owner only]Delete all profiles, harems, inventories, etc", hidden=True)
    async def globalreset(self, ctx):
        await ctx.channel.trigger_typing()
        count = clear_folder(dir_path)

        await ctx.send(":white_check_mark: Removed " + str(count) + " file(s) and all empty folders")

    def color_to_rarity(self, color) -> str:
        if color == discord.Colour.gold():
            return "★★★ Super Rare"
        elif color == discord.Colour.purple():
            return "★★ Epic"
        elif color == discord.Colour.blue():
            return "★ Rare"
        else:
            return ""

def save_harem_girl_by_id(user_id:int, battle_girl: BattleGirl):
    girl = configparser.ConfigParser()
    if os.path.exists(dir_path + str(user_id) + "/" + str(battle_girl.id) + ".ini"):
        girl.read(dir_path + str(user_id) + "/" + str(battle_girl.id) + ".ini", 'utf-8')

        girl.set('stats', 'level', str(battle_girl.level))
        girl.set('stats', "Exp", str(battle_girl.exp))
        girl.set('stats', "Health", str(battle_girl.health))
        girl.set('stats', "Firepower", str(battle_girl.firepower))
        girl.set('stats', "Anti-air", str(battle_girl.antiair))
        girl.set('stats', "Anti-sub", str(battle_girl.antisub))
        girl.set('stats', "Torpedo", str(battle_girl.torpedo))
        girl.set('stats', "Aviation", str(battle_girl.aviation))
        girl.set('stats', "Reload", str(battle_girl.reload))
        girl.set('stats', "Accuracy", str(battle_girl.accuracy))
        girl.set('stats', "Evasion", str(battle_girl.evasion))
        with codecs.open(dir_path + (str(user_id) + '/' + str(battle_girl.id) + ".ini"), 'w', 'utf-8') as waifu:
            girl.write(waifu)
            waifu.flush()
            #print(logtime() + Fore.CYAN + "Girl updated: " + battle_girl.name)


def clear_folder(string: str):
    count = 0
    for name1 in os.listdir(string):
        name = string + name1
        #print(name)
        if os.path.isdir(name) and not name.endswith("568914197048459273") and not name.endswith("624990745132138496"):
            count += clear_folder(name + '/')
            os.rmdir(os.path.abspath(name))
        if os.path.isfile(name) \
                and not name.endswith("568914197048459273/1.ini") and not name.endswith("624990745132138496/1.ini") \
                and not name.endswith("568914197048459273.ini") and not name.endswith("624990745132138496.ini"):
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


def save_profile(user_id: int, profile):
    with codecs.open(dir_path + str(user_id) + ".ini", mode="w", encoding="utf-8") as user_file:
        profile.write(user_file)


def get_harem_girl_by_id(user_id: int, girl_id: int) -> BattleGirl:
    girl = configparser.ConfigParser()
    if os.path.exists(dir_path + str(user_id) + "/" + str(girl_id) + ".ini"):
        girl.read(dir_path + str(user_id) + "/" + str(girl_id) + ".ini", 'utf-8')
    return BattleGirl(girl)


def randomize(to_randomize: int):
    R = random.Random()
    difference = to_randomize * 0.1
    return R.randint(int(to_randomize - difference), int(to_randomize + difference))


def get_reload_time(reload):
    if reload < 400:
        return 10 + (reload / 50)
    elif reload < 500:
        return 8 + (reload / 40)
    elif reload < 600:
        return 4 + (reload / 30)
    elif reload < 700:
        return (reload / 20) - 6
    elif reload < 800:
        return (reload / 10) - 41
    elif reload < 900:
        return (reload / 5) - 120
    else:
        return (reload / 2) - 390


def setup(bot):
    bot.add_cog(BelfastGame(bot))
