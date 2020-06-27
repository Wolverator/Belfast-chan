import asyncio
import codecs
import datetime
import os
import time

import discord
import pandas
import requests
from colorama import Fore
from discord.ext import commands

from cogs.BelfastUtils import logtime

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")
no_retro_type = {'120': 3, '100': 4, 'base': 5}
submarine_type = {'120': 3, '100': 5, 'base': 7}
retro_type = {'120r': 3, '120': 4, '100r': 5, '100': 6, 'base': 7}
ships = {}
placeholders = ('--', 'nan', '-')


# noinspection PyMethodMayBeStatic
class AzurLane(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['mt'], brief="Check when servers will be back online")
    async def maintenance(self, ctx):  # TODO: move users to remind mt end about also into file and load that list at start-up
        from cogs.FinishedCommands import maintenance_finish
        if os.path.getsize(dir_path + "/config/last maintenance.txt") > 0:
            from cogs.FinishedCommands import DateParser
            maintenance_finish = DateParser.parse(timestr=codecs.open(dir_path + "/config/last maintenance.txt", encoding='utf-8').read())
        if maintenance_finish:
            time_left = datetime.timedelta(
                seconds=(maintenance_finish.timestamp() - datetime.datetime.now().timestamp()))
            if time_left.total_seconds() >= 0:
                text = ":clock1: Servers should be online in " + str(time_left).partition('.')[0] + "."
                if self.bot.get_cog('General').already_in_maintenance(ctx.author.id):
                    text += "\nYou're already in my 'to-remind-list' for the maintenance ending, " + ctx.author.display_name + "."
                else:
                    from cogs.FinishedCommands import maintenance_remind_where_whom
                    if ctx.channel in maintenance_remind_where_whom.keys():
                        maintenance_remind_where_whom[ctx.channel] = maintenance_remind_where_whom.get(ctx.channel) + str(
                            ", <@" + str(ctx.author.id) + ">")
                    else:
                        maintenance_remind_where_whom[ctx.channel] = str("\n<@" + str(ctx.author.id) + ">")
                    text += "\nI've also added you to 'to-remind-list', " + self.bot._user(ctx.author.id) + ".\nThus I'll mention you in this channel when servers will come online."
                    await ctx.message.add_reaction('✅')
            else:
                text = "Servers should be online, Commander.\nMay The Luck be with You!\n" \
                       + "\nPrevious maintenance was finished: " + str(maintenance_finish) + " (UTC +3)"
        else:
            text = "Sorry, Commander, but there's no info about nor previous, neither incoming maintenances!"
            text += str(os.path.getsize(dir_path + "/config/last maintenance.txt"))
        msg = await ctx.send(text)
        await asyncio.sleep(25)
        await msg.delete()

    @commands.command(pass_context=True, aliases=['ship'], brief="Show girl's info from official Wiki")
    async def info(self, ctx, *, girl_name="placeholderLVL99999"):
        await ctx.channel.trigger_typing()
        # noinspection PyArgumentList
        if girl_name.__contains__("placeholderLVL99999"):
            resultEmbed = discord.Embed()
            resultEmbed.title = "Excuse me, but..."
            resultEmbed.description = "You forgot to choose girl's name, " + self.bot._user(ctx.author.id) + "!"
            await ctx.send(embed=resultEmbed)
        else:
            # noinspection PyCallByClass,PyArgumentList
            girl_name = girl_name.capitalize().strip(" \n")
            embed = self.get_ship_info_web(girl_name)
            if not embed.title == "Excuse me, but...":
                embed.set_footer(text=str(ctx.author.id))
            message = await ctx.send(embed=embed)
            if not embed.title == "Excuse me, but...":
                print(str(datetime.datetime.utcnow().time()).partition('.')[0] + " " + Fore.CYAN + str(
                    ctx.author) + Fore.RESET + " asked info about " + Fore.GREEN + str(embed.title))
                await message.add_reaction("1⃣")
                await message.add_reaction("2⃣")
                await message.add_reaction("3⃣")
                if "**RETROFITTABLE**" in message.embeds[0].description:
                    await message.add_reaction("4⃣")
                    await message.add_reaction("5⃣")

    @commands.command(pass_context=True, brief="Show list of Azur Lane ships by category and type")
    async def ships(self, ctx, category='usual', sort_by='rarity'):
        categories = {'standart': 0, 'usual': 0, 'prototype': 1, 'prototypes': 1, 'collab': 2, 'collabs': 2,
                      'retro': 3,
                      'retrofit': 3, 'retrofits': 3}
        sorts = {'nation': 0, 'nations': 0, 'type': 1, 'types': 1, 'rarity': 2}
        await ctx.channel.trigger_typing()
        if category and category in categories and sort_by and sort_by in sorts:
            await self.bot.get_cog('AzurLane').get_ships_list(ctx, categories.get(category), sorts.get(sort_by))
        else:
            msg = await ctx.send("Please, specify category and sort option:\nCategories: " + (
                ", ".join(categories.keys())) + "\nSort options: " + (", ".join(sorts.keys())))
            await asyncio.sleep(15)
            await msg.delete()

    # finished funcs
    def update_html_file(self, path_to_html_file: str, _url: str):
        file_exists = os.path.exists(path_to_html_file)
        if (not file_exists) or (file_exists and ((time.time() - os.path.getmtime(path_to_html_file)) > 1200 * 3600)):
            print(logtime() + "URL update: " + _url)
            web_info = requests.get(_url)
            with codecs.open(path_to_html_file, mode='w', encoding='utf-8') as output_file:
                output_file.write(str(web_info.text))
                output_file.close()
            info = pandas.read_html(path_to_html_file)
            with codecs.open(path_to_html_file.replace(".html", ".txt"), 'w', 'utf-8') as txt_file:
                for item in info:
                    txt_file.write(item.to_string() + '\n')
        return 1

    async def get_ships_list(self, ctx: discord.ext.commands.context, table: int, column: int):
        columns = {0: 'Affiliation', 1: 'Subtype', 2: 'Rarity'}
        tables = {0: 'Standart', 1: 'Prototype', 2: 'Collab', 3: 'Retrofit'}
        colum = columns.get(column)
        resultEmbed = discord.Embed()
        resultEmbed.title = tables.get(table) + " ships:"
        _url = "https://azurlane.koumakan.jp/List_of_Ships"
        path_to_html_file = dir_path + 'ALDB/List_of_Ships.html'
        ship_types = {}
        file_result = self.update_html_file(path_to_html_file, _url)
        if file_result == 0:
            resultEmbed.title = "Error"
            resultEmbed.description = "Module 'Pandas' couldn't read any data on that page =("
            return resultEmbed
        info = pandas.read_html(path_to_html_file)
        for row in range(len(info[table][colum])):
            if info[table][colum][row] not in ship_types.keys():
                ship_types[info[table][colum][row]] = str(info[table]['Name'][row])
            else:
                ship_types[info[table][colum][row]] += ", " + str(info[table]['Name'][row])
        for key in ship_types.keys():
            emb = discord.Embed()
            emb.title = key
            emb.description = str(ship_types.get(key))
            await ctx.send(embed=emb)

    def get_ship_info_web(self, girl_name: str):
        ship_name = self.fix_name(girl_name)
        resultEmbed = discord.Embed()
        print(">>>>>> " + ship_name)
        path_to_file = dir_path + 'ALDB/ships/' + ship_name + '.html'
        Retrofit = False
        Submarine = False
        try:
            shiplink = 'https://azurlane.koumakan.jp/' + ship_name
            self.update_html_file(path_to_file, shiplink)
        except ImportError:
            resultEmbed.title = "Excuse me, but..."
            resultEmbed.description = "Are you sure you wrote girl's name correctly? :thinking:"
            return resultEmbed
        try:
            info = pandas.read_html(path_to_file)
        except ImportError:
            resultEmbed.title = "Excuse me, but..."
            resultEmbed.description = "There's no info about girls on that page =("
            os.remove(path_to_file)
            return resultEmbed
        file_i = codecs.open(dir_path + 'ALDB/ships/' + ship_name + '.txt', encoding='utf-8', mode='w')
        dicts_info = {}
        for i in range(len(info)):
            dicts_info[i] = info.copy().pop(i)
            if 'Index' in dicts_info[i].keys():
                Retrofit = True
            file_i.write(dicts_info[i].to_string() + "\n")
        file_i.close()
        if dicts_info[1][1][2] == "Submarine" or dicts_info[1][1][2] == "Submarine Carrier":
            Submarine = True
        web_raw = codecs.open(path_to_file, encoding='utf-8').read()
        if ship_name.__contains__("Neptune") and dicts_info[1][1][1].__contains__("Royal Navy"):
            ship_name = "HMS Neptune"
        elif ship_name.__contains__("Neptune") and dicts_info[1][1][1].__contains__("Neptunia"):
            ship_name = "HDN Neptune"
        pic_url = (web_raw.partition('<img alt="')[2].partition('"')[2].partition('"')[2].partition('"')[0]) \
            .replace('\%27', "'") \
            .replace('\%28', '(') \
            .replace('\%29', ')') \
            .replace("\%C3\%B6", 'ö')
        print("pic url = " + pic_url)
        resultEmbed.set_thumbnail(url='https://azurlane.koumakan.jp/' + pic_url)
        resultEmbed.set_author(name="Link to wiki", url=shiplink)
        resultEmbed.description = str(dicts_info[0][0][0]) + ": " + str(dicts_info[0][1][0]) + "\n"
        resultEmbed.description += str(dicts_info[0][0][1]) + ": " + str(dicts_info[0][1][1]) + "\n"
        resultEmbed.description += str(dicts_info[1][0][1]) + ": " + str(dicts_info[1][1][1]) + "\n"
        resultEmbed.description += str(dicts_info[1][0][2]) + ": " + str(dicts_info[1][1][2]) + "\n"
        for i in range(len(dicts_info)):
            if "Obtainment" in dicts_info[i].keys() \
                    and not str(dicts_info[i]["Obtainment"][0]).startswith("Available in Medal Exchange for ") \
                    and not str(dicts_info[i]["Obtainment"][0]).startswith("Research"):
                resultEmbed.description += "**LIMITED SHIP:** "
                for j in range(len(dicts_info[i]["Obtainment"])):
                    resultEmbed.description += str(dicts_info[i]["Obtainment"][j]) + "\n"
        resultEmbed.description += "\n**Skills:**\n"
        if Submarine:
            resultEmbed.description += "**" + str(dicts_info[12]['Skills'][0]).split("CN:")[0] + "**: " + str(dicts_info[12]['Skills.1'][0]).strip("Barrage preview (gif)") + "\n"
            if str(dicts_info[12]['Skills'][1]) not in placeholders:
                resultEmbed.description += "**" + str(dicts_info[12]['Skills'][1]).split("CN:")[0] + "**: " + str(dicts_info[12]['Skills.1'][1]).strip("Barrage preview (gif)") + "\n"
            if str(dicts_info[12]['Skills'][2]) not in placeholders:
                resultEmbed.description += "**" + str(dicts_info[12]['Skills'][2]).split("CN:")[0] + "**: " + str(dicts_info[12]['Skills.1'][2]).strip("Barrage preview (gif)") + "\n"
        elif Retrofit:
            resultEmbed.description += "**" + str(dicts_info[11]['Skills'][0]).split("CN:")[0] + "**: " + str(dicts_info[11]['Skills.1'][0]).strip("Barrage preview (gif)") + "\n"
            if str(dicts_info[11]['Skills'][1]) not in placeholders:
                resultEmbed.description += "**" + str(dicts_info[11]['Skills'][1]).split("CN:")[0] + "**: " + str(dicts_info[11]['Skills.1'][1]).strip("Barrage preview (gif)") + "\n"
            if str(dicts_info[11]['Skills'][2]) not in placeholders:
                resultEmbed.description += "**" + str(dicts_info[11]['Skills'][2]).split("CN:")[0] + "**: " + str(dicts_info[11]['Skills.1'][2]).strip("Barrage preview (gif)") + "\n"
        else:
            resultEmbed.description += "**" + str(dicts_info[9]['Skills'][0]).split("CN:")[0] + "**: " + str(dicts_info[9]['Skills.1'][0]).strip("Barrage preview (gif)") + "\n"
            if str(dicts_info[9]['Skills'][1]) not in placeholders:
                resultEmbed.description += "**" + str(dicts_info[9]['Skills'][1]).split("CN:")[0] + "**: " + str(dicts_info[9]['Skills.1'][1]).strip("Barrage preview (gif)") + "\n"
            if str(dicts_info[9]['Skills'][2]) not in placeholders:
                resultEmbed.description += "**" + str(dicts_info[9]['Skills'][2]).split("CN:")[0] + "**: " + str(dicts_info[9]['Skills.1'][2]).strip("Barrage preview (gif)") + "\n"
        resultEmbed.description += "\nTo choose stats press reactions:\n1 - **1** lvl, 2 - **100** lvl, 3 - **120** lvl"
        if Retrofit and not Submarine:
            resultEmbed.description += "\n  **RETROFITTABLE**: 4 - **100** lvl+**retro**, 5 - **120** lvl+**retro**\n"
        base = no_retro_type['base']
        if Retrofit and not Submarine:
            base = retro_type['base']
        if Submarine:
            base = submarine_type['base']
        resultEmbed.add_field(name="Health", value=str(dicts_info[base][1][0]), inline=True)
        resultEmbed.add_field(name="Firepower", value=str(dicts_info[base][1][1]), inline=True)
        resultEmbed.add_field(name="Anti-air", value=str(dicts_info[base][1][2]), inline=True)
        resultEmbed.add_field(name="Anti-sub", value=str(dicts_info[base][1][3]), inline=True)
        resultEmbed.add_field(name="Armor", value=str(dicts_info[base][3][0]), inline=True)
        resultEmbed.add_field(name="Torpedo", value=str(dicts_info[base][3][1]), inline=True)
        resultEmbed.add_field(name="Aviation", value=str(dicts_info[base][3][2]), inline=True)
        resultEmbed.add_field(name="Reload", value=str(dicts_info[base][5][0]), inline=True)
        resultEmbed.add_field(name="Evasion", value=str(dicts_info[base][5][1]), inline=True)
        resultEmbed.add_field(name="Cost", value=str(dicts_info[base][5][2]), inline=True)
        resultEmbed.add_field(name="Luck", value=str(dicts_info[base][7][0]), inline=True)
        resultEmbed.add_field(name="Speed", value=str(dicts_info[base][7][1]), inline=True)
        resultEmbed.add_field(name="Accuracy", value=str(dicts_info[base][7][2]), inline=True)
        resultEmbed.title = ship_name.replace("_", " ")
        return resultEmbed

    def update_embed(self, embed: discord.Embed, stats_type: str):
        Retrofit = False
        Submarine = False
        resultEmbed = embed
        resultEmbed.clear_fields()
        info = pandas.read_html(dir_path + 'ALDB/ships/' + resultEmbed.title.replace(' ', '_') + '.html')
        dicts_info = {}
        for i in range(len(info)):
            dicts_info[i] = info.copy().pop(i)
            if 'Index' in dicts_info[i].keys():
                Retrofit = True
        if dicts_info[1][1][2] == "Submarine":
            Submarine = True
        ids = no_retro_type
        if Retrofit:
            ids = retro_type
        if Submarine:
            ids = submarine_type
        base = ids.get(stats_type)
        resultEmbed.add_field(name="Health", value=str(dicts_info[base][1][0]), inline=True)
        resultEmbed.add_field(name="Firepower", value=str(dicts_info[base][1][1]), inline=True)
        resultEmbed.add_field(name="Anti-air", value=str(dicts_info[base][1][2]), inline=True)
        resultEmbed.add_field(name="Anti-sub", value=str(dicts_info[base][1][3]), inline=True)
        resultEmbed.add_field(name="Armor", value=str(dicts_info[base][3][0]), inline=True)
        resultEmbed.add_field(name="Torpedo", value=str(dicts_info[base][3][1]), inline=True)
        resultEmbed.add_field(name="Aviation", value=str(dicts_info[base][3][2]), inline=True)
        resultEmbed.add_field(name="Reload", value=str(dicts_info[base][5][0]), inline=True)
        resultEmbed.add_field(name="Evasion", value=str(dicts_info[base][5][1]), inline=True)
        resultEmbed.add_field(name="Cost", value=str(dicts_info[base][5][2]), inline=True)
        resultEmbed.add_field(name="Luck", value=str(dicts_info[base][7][0]), inline=True)
        resultEmbed.add_field(name="Speed", value=str(dicts_info[base][7][1]), inline=True)
        resultEmbed.add_field(name="Accuracy", value=str(dicts_info[base][7][2]), inline=True)
        return resultEmbed

    def fix_name(self, girl_name: str):
        ship_name = girl_name.replace(' ', '_') \
            .replace('(battleship)', '_(Battleship)') \
            .replace('_(battleship)', '_(Battleship)') \
            .replace('_battleship', '_(Battleship)') \
            .replace('_bb', '_(Battleship)') \
            .replace("mkii", "MKII") \
            .replace("grosse", "Grosse") \
            .replace("virginia", "Virginia") \
            .replace("bullin", "Bullin") \
            .replace("ausburne", "Ausburne") \
            .replace("diego", "Diego") \
            .replace("lake", "Lake") \
            .replace("city", "City") \
            .replace("nep", "Nep") \
            .replace("carolina", "Carolina") \
            .replace("island", "Island") \
            .replace("dakota", "Dakota") \
            .replace("elizabeth", "Elizabeth") \
            .replace("wales", "Wales") \
            .replace("york", "York") \
            .replace("Janna", "Jeanne") \
            .replace("konigsberg", "Königsberg") \
            .replace("königsberg", "Königsberg") \
            .replace("koln", "Köln") \
            .replace("köln", "Köln") \
            .replace("Koln", "Köln") \
            .replace("Konigsberg", "Königsberg") \
            .replace("d'ark", "d'Arc") \
            .replace("hipper", "Hipper") \
            .replace("eugene", "Eugene") \
            .replace("graf", "Graf") \
            .replace("spee", "Spee") \
            .replace("zepelin", "Zeppelin") \
            .replace("zeppelin", "Zeppelin") \
            .replace("Janne", "Jeanne") \
            .replace("shan", "Shan") \
            .replace("shun", "Shun") \
            .replace("chun", "Chun") \
            .replace("-la", "-La") \
            .replace("yuan", "Yuan") \
            .replace("_sen", "_Sen") \
            .replace("hai", "Hai") \
            .replace("heart", "Heart") \
            .replace("louis", "Louis") \
            .replace("e_bel", "e_Bel") \
            .replace("Bel-chan", "Little_Bel") \
            .replace("Hieichan", "Hiei-chan") \
            .replace("Belchan", "Little_Bel") \
            .replace("triom", "Triom") \
            .replace("bert", "Bert") \
            .replace("mars", "Mars") \
            .replace("bart", "Bart") \
            .replace("teme", "Teme") \
            .replace("r_hill", "r_Hill") \
            .replace("d'arc", "d'Arc") \
            .replace("darc", "d'Arc") \
            .replace("hms", "HMS") \
            .replace("dark", "d'Arc") \
            .replace("Repulce", "Repulse") \
            .replace("kizuna_ai", "Kizuna_AI") \
            .replace("Kizuna_ai", "Kizuna_AI") \
            .replace("gamer", "Gamer") \
            .replace("sandy", "Sandy") \
            .replace("Hdn", "HDN") \
            .replace("_cavour", "_Cavour") \
            .replace("_george", "_George") \
            .replace("_malin", "_Malin") \
            .replace("_cesare", "_Cesare") \
            .replace("_venetto", "_Veneto") \
            .replace("_veneto", "_Veneto") \
            .replace("_opini", "_Opini") \
            .replace("_aqua", "_Aqua") \
            .replace("_sora", "_Sora") \
            .replace("_mio", "_Mio") \
            .replace("_merkur", "_Merkur") \
            .replace("_soyuz", "_Soyuz") \
            .replace("_rossi", "_Rossi") \
            .replace("_galiss", "_Galiss") \
            .replace("_matsuri", "_Matsuri") \
            .replace("_shion", "_Shion") \
            .replace("_ayame", "_Ayame") \
            .replace("_fubuki", "_Fubuki") \
            .replace("_powell", "_Powell") \
            .replace("Opiniatre", "Opiniâtre")
        if ship_name == "Grosse":
            ship_name = "Friedrich_der_Grosse"
        if ship_name == "Graf_Spee":
            ship_name = "Admiral_Graf_Spee"
        if ship_name == "Enterprize":
            ship_name = "Enterprise"
        return ship_name


def setup(bot):
    bot.add_cog(AzurLane(bot))
