import math
import os

import discord
from colorama import Fore
from discord.ext import commands

from cogs.BelfastUtils import logtime

# помощник в фарме гарема дискордового бота Mudae

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "MudaDB/")

users_antidisable_lists = {}
MUDAE_ADLS_FILEPATH = dir_path + "mudae_adls.pickle"

bundles = {}
MUDAE_BUNDLES_FILEPATH = dir_path + "mudae_bundles.pickle"

titles = {}
MUDAE_TITLES_FILEPATH = dir_path + "mudae_titles.pickle"

unclaimed_characters_spawns = {}
MUDAE_SPAWNS_FILEPATH = dir_path + "mudae_spawns.pickle"

wishlist = []
MUDAE_WISHLIST_FILEPATH = dir_path + "mudae_wishlist.pickle"

whitelist = []
MUDAE_WHITELIST_FILEPATH = dir_path + "mudae_whitelist.pickle"

divorcelist = []
MUDAE_DIVORCELIST_FILEPATH = dir_path + "mudae_divorcelist.pickle"

harem = []
MUDAE_HAREM_FILEPATH = dir_path + "mudae_harem.pickle"

CLAIMED_MARK = "  💞"


class MudaTitle(object):
    name = ""
    total = 0
    claimed = 0
    unclaimed = 0
    total_list = []
    claimed_list = []
    unclaimed_list = []

    def __str__(self):
        return str(self.name + " (" + str(self.unclaimed) + " left)\n\n" + "\n".join(self.total_list))

    def __init__(self, name: str, total_list: list):
        self.name = name
        self.total = 0
        self.claimed = 0
        self.unclaimed = 0
        self.total_list = []
        self.claimed_list = []
        self.unclaimed_list = []
        self.add_chars(total_list)

    def add_chars(self, total_list: list):
        for char in total_list:
            cha = char
            if str(cha).endswith(" ka"):
                cha = cha.split(" ka")[0][:cha.rfind(' ')]
            if str(cha).__contains__(" **"):
                cha = cha.split(" **")[0]
            if str(cha).__contains__(" · <:"):
                cha = cha.split(" · <:")[0]
            if str(cha).__contains__(" =>"):
                cha = cha.split(" =>")[0]
            if not str(cha).startswith("\u200B") \
                    and not str(cha).startswith("(No result)") \
                    and cha not in self.total_list:
                self.total_list.append(cha)
        for char in self.total_list:
            if str(char).endswith(CLAIMED_MARK):
                self.add_claimed_char(str(char).partition(CLAIMED_MARK)[0])
            else:
                self.add_unclaimed_char(str(char))
        self.total = len(self.total_list)
        self.claimed = len(self.claimed_list)
        self.unclaimed = len(self.unclaimed_list)
        return self

    def add_claimed_char(self, claimed_char_name_: str):
        global unclaimed_characters_spawns, wishlist

        claimed_char_name_clear = claimed_char_name_.strip(" ")
        claimed_char_name = claimed_char_name_clear + CLAIMED_MARK

        if claimed_char_name_clear in unclaimed_characters_spawns.keys():
            unclaimed_characters_spawns.pop(claimed_char_name_clear)
        if claimed_char_name_clear in wishlist:
            wishlist.pop(wishlist.index(claimed_char_name_clear))
            print(logtime() + "Removed " + Fore.GREEN + claimed_char_name_clear + Fore.RESET + " from wishlist " + Fore.RED + "DUE TO CLAIM!")

        if claimed_char_name not in self.claimed_list:
            if claimed_char_name_clear in self.total_list:
                self.total_list.pop(self.total_list.index(claimed_char_name_clear))
            if claimed_char_name_clear in self.unclaimed_list:
                self.unclaimed_list.pop(self.unclaimed_list.index(claimed_char_name_clear))
            if claimed_char_name not in self.total_list:
                self.total_list.append(claimed_char_name)
            self.claimed_list.append(claimed_char_name)
            self.total = len(self.total_list)
            self.claimed = len(self.claimed_list)
            self.unclaimed = len(self.unclaimed_list)
            print(logtime() + "Added claimed " + Fore.LIGHTRED_EX + claimed_char_name_clear + Fore.RESET + " into " + Fore.GREEN + self.name)

    def add_unclaimed_char(self, unclaimed_char_: str):
        unclaimed_char_name = unclaimed_char_.strip(" ")
        if unclaimed_char_name not in self.unclaimed_list:
            claimed_char_name = unclaimed_char_name + CLAIMED_MARK
            if claimed_char_name in self.total_list:
                self.total_list.pop(self.total_list.index(claimed_char_name))
            if claimed_char_name in self.claimed_list:
                self.claimed_list.pop(self.claimed_list.index(claimed_char_name))
            if unclaimed_char_name not in self.total_list:
                self.total_list.append(unclaimed_char_name)
            self.unclaimed_list.append(unclaimed_char_name)
            self.total = len(self.total_list)
            self.claimed = len(self.claimed_list)
            self.unclaimed = len(self.unclaimed_list)
            print(logtime() + "Added unclaimed " + Fore.LIGHTYELLOW_EX + unclaimed_char_name + Fore.RESET + " into " + Fore.GREEN + self.name)


class MudaHelper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def load_lists(self):
        import mpu
        global users_antidisable_lists, titles, unclaimed_characters_spawns, wishlist, whitelist, harem, divorcelist

        if os.path.exists(MUDAE_ADLS_FILEPATH):
            users_antidisable_lists = mpu.io.read(MUDAE_ADLS_FILEPATH)
        if os.path.exists(MUDAE_TITLES_FILEPATH):
            titles = mpu.io.read(MUDAE_TITLES_FILEPATH)
        if os.path.exists(MUDAE_SPAWNS_FILEPATH):
            unclaimed_characters_spawns = mpu.io.read(MUDAE_SPAWNS_FILEPATH)
        if os.path.exists(MUDAE_WISHLIST_FILEPATH):
            wishlist = mpu.io.read(MUDAE_WISHLIST_FILEPATH)
        if os.path.exists(MUDAE_WHITELIST_FILEPATH):
            whitelist = mpu.io.read(MUDAE_WHITELIST_FILEPATH)
        if os.path.exists(MUDAE_DIVORCELIST_FILEPATH):
            divorcelist = mpu.io.read(MUDAE_DIVORCELIST_FILEPATH)
        if os.path.exists(MUDAE_HAREM_FILEPATH):
            harem = mpu.io.read(MUDAE_HAREM_FILEPATH)

    async def save_lists(self):
        import mpu
        global users_antidisable_lists, titles, unclaimed_characters_spawns, wishlist, whitelist, harem, divorcelist

        mpu.io.write(MUDAE_ADLS_FILEPATH, users_antidisable_lists)
        mpu.io.write(MUDAE_TITLES_FILEPATH, titles)
        mpu.io.write(MUDAE_SPAWNS_FILEPATH, unclaimed_characters_spawns)
        mpu.io.write(MUDAE_WISHLIST_FILEPATH, wishlist)
        mpu.io.write(MUDAE_WHITELIST_FILEPATH, whitelist)
        mpu.io.write(MUDAE_DIVORCELIST_FILEPATH, divorcelist)
        mpu.io.write(MUDAE_HAREM_FILEPATH, harem)

    def add_ad_title_for_user(self, user_id: str, title: str):
        global users_antidisable_lists
        if user_id not in users_antidisable_lists.keys() or not users_antidisable_lists[user_id]:
            users_antidisable_lists[user_id] = [title]
            print(logtime() + Fore.YELLOW + "Added AD title: " + Fore.CYAN + title)
        else:
            if title not in users_antidisable_lists[user_id]:
                users_antidisable_lists[user_id].append(title)
                print(logtime() + Fore.YELLOW + "Added AD title: " + Fore.CYAN + title)

    def add_characters_into_title(self, title: str, charsdata: str):
        global titles
        n = charsdata.count("\n\n")
        if n:
            charlistraw = charsdata.split("\n\n")[n].split("\n")
        else:
            charlistraw = charsdata.split("\n")
        if title not in titles.keys():
            titles[title] = MudaTitle(title, charlistraw)
            # print(logtime() + Fore.YELLOW + "Added new title " + Fore.CYAN + title)
        else:
            titles.get(title).add_chars(charlistraw)
            # print(logtime() + Fore.YELLOW + "Refreshed existing title " + Fore.CYAN + title)

    @commands.command(pass_context=True, aliases=['mwlac'], hidden=True)
    @commands.is_owner()
    async def mwishlistaddchar(self, ctx, *, wished_character: str):
        await ctx.message.delete()
        global wishlist
        if wished_character not in wishlist:
            wishlist.append(wished_character)
            print(logtime() + "Added " + Fore.GREEN + wished_character + Fore.RESET + " to wishlist!")
            await ctx.send('✅', delete_after=5)

    @commands.command(pass_context=True, aliases=['mwldc'], hidden=True)
    @commands.is_owner()
    async def mwishlistdeletechar(self, ctx, *, wished_character: str):
        await ctx.message.delete()
        global wishlist
        if wished_character in wishlist:
            wishlist.pop(wishlist.index(wished_character))
            print(logtime() + "Removed " + Fore.GREEN + wished_character + Fore.RESET + " from wishlist!")
            await ctx.send('✅', delete_after=5)

    @commands.command(pass_context=True, aliases=['mwls'], hidden=True)
    @commands.is_owner()
    async def mwishlistshow(self, ctx, *, page_str="1"):
        await ctx.message.delete()
        global wishlist
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "Wishlist:", wishlist, page_str, discord.Colour.gold(), False), delete_after=30)

    @commands.command(pass_context=True, aliases=['ms'], brief="save_lists everything")
    @commands.guild_only()
    @commands.is_owner()
    async def msave(self, ctx):
        await self.save_lists()
        await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, aliases=['ml'], brief="load_lists everything")
    @commands.guild_only()
    @commands.is_owner()
    async def mload(self, ctx):
        await self.load_lists()
        await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, aliases=['mdadl'], brief="Delete stored info about your ADL (nedded if you removed something from your ADL in Mudae)")
    @commands.guild_only()
    async def mdeletemyadlist(self, ctx):
        global users_antidisable_lists
        users_antidisable_lists.pop(str(ctx.message.author.id), None)
        await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, aliases=['mgsc'], brief="Get amount of spawns of some character")
    @commands.guild_only()
    async def mgetspawncount(self, ctx, *, name_str="-1"):
        if name_str != "-1":
            global unclaimed_characters_spawns
            if name_str in unclaimed_characters_spawns.keys():
                await ctx.send("Character **" + name_str + "** have spawned **" + str(unclaimed_characters_spawns.get(name_str)) + "** times\n*(Master's channel only)*")

    @commands.command(pass_context=True, aliases=['mgts'], brief="Get the list of most spawned characters which still unclaimed")
    @commands.guild_only()
    async def mgettopspawns(self, ctx, *, page_str="1"):
        global unclaimed_characters_spawns
        sor = sorted(unclaimed_characters_spawns, key=unclaimed_characters_spawns.get, reverse=True)
        for char in sor:
            ind = sor.index(char)
            char_ = sor.pop(ind)
            char_ = "`" + char_ + "` (" + str(unclaimed_characters_spawns.get(char)) + ")"
            sor.insert(ind, char_)
        # result = []
        # for char in unclaimed_characters_spawns.keys():
        #     result.append("**"+char+"** spawned **"+str(unclaimed_characters_spawns.get(char))+"** times")
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "Most often spawned characters that still unclaimed:", sor, page_str, discord.Colour.dark_teal(), False))

    @commands.command(pass_context=True, aliases=['mgmadl'], brief="Get your antidisable list")
    @commands.guild_only()
    async def mgetmyadlist(self, ctx, *, page_str="1"):
        global users_antidisable_lists
        await ctx.channel.typing()
        result_list = []
        try:
            result_list = users_antidisable_lists[str(ctx.author.id)]
        except Exception:
            pass
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "Your antidisabled titles:", result_list, page_str, discord.Colour.green(), True))

    @commands.command(pass_context=True, aliases=['mgadl'], brief="Get user's antidisable list (your or others)")
    @commands.guild_only()
    async def mgetadlist(self, ctx, page: int = 1, *, user_id_str="-1"):
        global users_antidisable_lists
        await ctx.channel.typing()
        if user_id_str == "-1":
            await ctx.send("Wrong argument - must be an ID number, " + self.bot.user_title(ctx.author.id) + "!", delete_after=15)
            await ctx.message.delete(delay=15)
            return
        result_list = []
        try:
            page_str = str(page)
            result_list = users_antidisable_lists[user_id_str]
            await ctx.send(
                embed=await self.simple_paged_embed(ctx.message, self.bot.get_user_from_guild(ctx.channel.guild, user_id_str).display_name + "'s antidisabled titles:", result_list, page_str,
                                                    discord.Colour.green(), True))
        except Exception:
            pass

    @commands.command(pass_context=True, aliases=['mgmu'], brief="Get list from titles of your antidisable list with unclaimed characters")
    @commands.guild_only()
    async def mgetmyunclaimed(self, ctx, *, page_str="1"):
        global users_antidisable_lists, titles
        await ctx.channel.typing()
        result_list = []
        for user_id in users_antidisable_lists.keys():
            for title in users_antidisable_lists[user_id]:
                if title in titles.keys() and titles.get(title).unclaimed > 0:
                    result_list.append(title)
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "This titles of your ADL are not fully claimed:", result_list, page_str, discord.Colour.dark_red(), True))

    @commands.command(pass_context=True, aliases=['mgmc'], brief="Get list from titles of your antidisable list with fully claimed characters")
    @commands.guild_only()
    async def mgetmyclaimed(self, ctx, *, page_str="1"):
        global users_antidisable_lists, titles
        await ctx.channel.typing()
        result_list = []
        for title in users_antidisable_lists[str(ctx.author.id)]:
            if title in titles.keys() and titles.get(title).unclaimed == 0:
                result_list.append(title)
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "This titles of your ADL are fully claimed:", result_list, page_str, discord.Colour.dark_green(), True))

    @commands.command(pass_context=True, aliases=['mgu'], brief="Get list from all titles list with unclaimed characters")
    @commands.guild_only()
    async def mgetunclaimed(self, ctx, *, page_str="1"):
        global users_antidisable_lists, titles
        await ctx.channel.typing()
        result_list = []
        for title in titles.keys():
            if titles.get(title).unclaimed > 0:
                result_list.append(title)
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "This titles are not fully claimed:", result_list, page_str, discord.Colour.darker_grey(), True))

    @commands.command(pass_context=True, aliases=['mgc'], brief="Get list from all titles with fully claimed characters")
    @commands.guild_only()
    async def mgetclaimed(self, ctx, *, page_str="1"):
        global users_antidisable_lists, titles
        await ctx.channel.typing()
        result_list = []
        for title in titles.keys():
            if titles.get(title).unclaimed == 0:
                result_list.append(title)
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "This titles are fully claimed:", result_list, page_str, discord.Colour.darker_grey(), True))

    @commands.command(pass_context=True, aliases=['mmt'], brief="Show titles from users' adlists with missing info")
    @commands.guild_only()
    async def mmissingtitles(self, ctx, *, page_str="1"):
        global users_antidisable_lists, titles
        await ctx.channel.typing()

        result_list = []
        for user_id in users_antidisable_lists.keys():
            for title in users_antidisable_lists[user_id]:
                if title not in titles.keys() or (title in titles.keys() and titles.get(title).total == 0):
                    result_list.append("$$ima " + title)
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "Titles with missing info:", result_list, page_str, discord.Colour.red(), True))

    @commands.command(pass_context=True, aliases=['mgt'], brief="Get title's total characters list")
    @commands.guild_only()
    async def mgettitle(self, ctx, page: int = 1, *, title="\u200B"):
        global titles
        await ctx.channel.typing()
        mudaTitle = titles.get(title)
        if not mudaTitle:
            await ctx.send("No such title in my database!\nPlease, check the correct spelling - full title from Mudae, written in bold.")
            return
        emb = await self.simple_paged_embed(ctx.message, title, mudaTitle.total_list, str(page), discord.Colour.blue(), True)

        emb.add_field(name="Total characters:", value=str(mudaTitle.total))
        emb.add_field(name="Claimed characters:", value=str(mudaTitle.claimed))
        emb.add_field(name="Unclaimed characters:", value=str(mudaTitle.unclaimed))

        await ctx.send(embed=emb)

    @commands.command(pass_context=True, aliases=['mgau'], brief="Get title's total characters list")
    @commands.guild_only()
    async def mgetallunclaimed(self, ctx, *, page_str="1"):
        global titles
        await ctx.channel.typing()
        result_list = []  # bel mwhlac
        for title in titles.keys():
            for char in titles.get(title).unclaimed_list:
                result_list.append("**" + char + "** from **" + title + "**")
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "All unclaimed characters from all titles", result_list, page_str, discord.Colour.red(), True))

    @commands.command(pass_context=True, aliases=['mgac'], brief="Get title's total characters list")
    @commands.guild_only()
    async def mgetallclaimed(self, ctx, *, page_str="1"):
        global titles
        await ctx.channel.typing()
        result_list = []
        for title in titles.keys():
            for char in titles.get(title).claimed_list:
                result_list.append("**" + char + "** from **" + title + "**")
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "All claimed characters from all titles", result_list, page_str, discord.Colour.dark_green(), True))

    @commands.command(pass_context=True, aliases=['mwhlac'], hidden=True)
    @commands.is_owner()
    async def mwhitelistaddchar(self, ctx, *, character: str):
        global whitelist
        if character not in whitelist:
            whitelist.append(character)
            await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, aliases=['mwhldc'], hidden=True)
    @commands.is_owner()
    async def mwhitelistdeletechar(self, ctx, *, character: str):
        global whitelist
        if character in whitelist:
            whitelist.pop(whitelist.index(character))
            await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, aliases=['mwhls'], hidden=True)
    @commands.is_owner()
    async def mwhitelistshow(self, ctx, *, page_str="1"):
        global whitelist
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "Whitelist:", whitelist, page_str, discord.Colour.gold(), True))

    @commands.command(pass_context=True, aliases=['mdlac'], hidden=True)
    @commands.is_owner()
    async def mdivorcelistaddchar(self, ctx, *, character: str):
        global divorcelist
        if character not in divorcelist:
            divorcelist.append(character)
            await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, aliases=['mdldc'], hidden=True)
    @commands.is_owner()
    async def mdivorcelistdeletechar(self, ctx, *, character: str):
        global divorcelist
        if character in divorcelist:
            divorcelist.pop(divorcelist.index(character))
            await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, aliases=['mdls'], hidden=True)
    @commands.is_owner()
    async def mdivorcelistshow(self, ctx, *, page_str="1"):
        global divorcelist
        await ctx.send(embed=await self.simple_paged_embed(ctx.message, "Divorcelist:", divorcelist, page_str, discord.Colour.dark_grey(), True))

    @commands.command(pass_context=True, aliases=['mwhlclear'], hidden=True)
    @commands.is_owner()
    async def mwishlistclear(self, ctx):
        global whitelist
        whitelist = []
        await ctx.message.add_reaction('✅')

    @commands.command(pass_context=True, aliases=['mhclear'], hidden=True)
    @commands.is_owner()
    async def mharemclear(self, ctx):
        global harem
        harem = []
        await ctx.message.add_reaction('✅')

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def mstats(self, ctx):
        global titles
        result = "**Mudae Info Stats:**\n"
        titles_num = 0
        uncl_chars = 0
        cl_chars = 0
        for title in titles.keys():
            titles_num += 1
            for char in titles.get(title).claimed_list:
                cl_chars += 1
            for char in titles.get(title).unclaimed_list:
                uncl_chars += 1
        result += "Titles: " + str(titles_num) + "\n"
        result += "Claimed: " + str(cl_chars) + "\n"
        result += "Unclaimed: " + str(uncl_chars) + "\n"
        result += "Total chars: " + str(cl_chars + uncl_chars) + "\n"
        await ctx.send(result)

    @commands.command(pass_context=True, aliases=['mgctd'], hidden=True)
    @commands.is_owner()
    async def mgetcharacterstodivorce(self, ctx, *, page_str="1"):
        global divorcelist, harem
        result = "$$divorce "
        for char in divorcelist:
            if len(result) > 1960:
                break
            if char in harem:
                result += char + "$"
        await ctx.send("Characters to divorce:\n```" + result + "```")

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def mcheck(self, ctx, *, msg_id: int):
        await ctx.send(embed=await self.check_chars_for_whitelist(ctx.message))

    async def check_chars_for_whitelist(self, msg: discord.Message) -> discord.Embed:
        global whitelist, divorcelist
        if msg.embeds and str(msg.embeds[0].author.name).__contains__(self.bot.get_user_from_guild(msg.guild, str(self.bot.owner_id)).name + "'s harem"):
            list_to_check = msg.embeds[0].description.split("\n")
            result = []
            for char in list_to_check:
                cha = char
                if str(cha).endswith(" ka"):
                    cha = cha.split(" ka")[0][:cha.rfind(' ')]
                if str(cha).__contains__(" **"):
                    cha = cha.split(" **")[0]
                if str(cha).__contains__(" · <:"):
                    cha = cha.split(" · <:")[0]
                if str(cha).__contains__(" =>"):
                    cha = cha.split(" =>")[0]
                if (not str(cha).startswith("\u200B")) \
                        and (not cha.startswith("(No result)")) \
                        and (not cha.startswith("Harem value:")) \
                        and cha \
                        and cha not in whitelist \
                        and cha not in divorcelist:
                    result.append("`$$im " + cha + "` **/** `bel mwhlac " + cha + "` **/** `bel mdlac " + cha + "`")
            return await self.simple_paged_embed(msg, "These characters aren't sorted yet:", result, "1", discord.Colour.magenta(), True)

    def add_harem_chars(self, char_list: list):
        global harem
        for char in char_list:
            cha = char
            if str(cha).endswith(" ka"):
                cha = cha.split(" ka")[0][:cha.rfind(' ')]
            if str(cha).__contains__(" **"):
                cha = cha.split(" **")[0]
            if str(cha).__contains__(" · <:"):
                cha = cha.split(" · <:")[0]
            if str(cha).__contains__(" =>"):
                cha = cha.split(" =>")[0]
            if (not str(cha).startswith("\u200B")) \
                    and (not cha.startswith("(No result)")) \
                    and (not cha.startswith("Harem value:")) \
                    and cha \
                    and cha not in harem:
                harem.append(cha)
                print(logtime() + "Added " + Fore.GREEN + cha + Fore.RESET + " into " + Fore.MAGENTA + "HAREM!")

    def add_muda_title(self, title: str, char_list: list):
        global titles
        if title not in titles.keys():
            titles[title] = MudaTitle(title, [])

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


async def setup(bot):
    await bot.add_cog(MudaHelper(bot))
