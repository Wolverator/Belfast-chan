import asyncio
import json
import math
import os
import random
import urllib.parse

import discord
import mpu
import requests
from discord.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")

stopFlag = False
missingAnimeIDs = []
shikimoriAnimes = {}
SHIKIMORI_ANIMES_FILEPATH = dir_path + "shikimori_animes.pickle"


class Anime:
    id = 0
    title = ""
    status = ""
    myScore = 0
    totalScore = 0
    genres = []

    def __str__(self):
        mscore = ""
        if self.myScore > 0:
            mscore = "**" + str(self.myScore) + "**/"
        tscore = ""
        if self.totalScore > 0:
            tscore = "**" + str(self.totalScore) + "** "
        _title = self.title
        if len(_title) > 35:
            _title = _title[:33] + "..."
        return str(mscore + tscore + _title)

    def __init__(self, _id: int, title: str, status: str, myScore: int, totalScore: float, genres: list):
        self.id = _id
        self.title = title
        self.status = status
        self.myScore = myScore
        self.totalScore = totalScore
        self.genres = genres


class Shikimori(commands.Cog):
    def __init__(self, bot):
        global shikimoriAnimes

        self.bot = bot
        # load main database at bot start
        if os.path.exists(SHIKIMORI_ANIMES_FILEPATH):
            shikimoriAnimes = mpu.io.read(SHIKIMORI_ANIMES_FILEPATH)

    @commands.command(pass_context=True)
    async def rain(self, ctx):
        embed = discord.Embed(title="RAINTIME", description="It's raining!", color=random.randint(0x000000, 0xFFFFFF))
        ed = await ctx.reply(embed=embed, mention_author=False)
        for i in range(10):
            await asyncio.sleep(1)
            embed = discord.Embed(title="RAINTIME", description="It's raining!", color=random.randint(0x000000, 0xFFFFFF))
            await ed.edit(embed=embed)
        await ed.edit(embed=embed, delete_after=1)

    @commands.command(pass_context=True)
    async def shikiFavGenres(self, ctx, *, nickname="Андрей Шерхан"):
        global shikimoriAnimes, missingAnimeIDs, stopFlag
        shikimoriTesetAnimes = {}
        id_as_str = ""
        # getting user ID from their nickname
        try:
            id_as_str = (json.loads(requests.request("GET", "https://shikimori.one/api/users/" + urllib.parse.quote_plus(nickname), data="", headers={"User-Agent": "Waifutsianism"}).text))['id']
        except KeyError:
            await ctx.send("No user with that nickname. Check spelling?")
            return
        await asyncio.sleep(1)  # to prevernt spamming queries
        # getting 'completed' anime list for user ID
        response = json.loads(requests.request("GET", "https://shikimori.one/api/v2/user_rates", data="", headers={"User-Agent": "Waifutsianism"},
                                               params={"user_id": id_as_str, "target_type": "Anime", "status": "completed"}).text)
        await asyncio.sleep(1)  # to prevernt spamming queries
        # checking for missing anime in list of known anime
        for anime in response:
            animeID = int(anime.get('target_id'))
            if animeID not in shikimoriAnimes.keys():
                missingAnimeIDs.append(anime['target_id'])
            if animeID not in shikimoriTesetAnimes.keys():
                shikimoriTesetAnimes[animeID] = Anime(anime.get('target_id'), self.getAnimeTitle(animeID),
                                                      anime.get('status'), anime.get('score'), self.getAnimeTotalScore(animeID), self.getAnimeGenres(animeID))
        # getting missing anime
        if len(missingAnimeIDs) > 0:
            msg = await ctx.send("Starting updating process...")
            missingAnimeIDs.sort()
            amount = len(missingAnimeIDs)
            stopFlag = False
            for i in range(amount):
                if stopFlag:
                    break
                animeID = missingAnimeIDs.pop(0)
                response = self.getAnime(animeID)
                genres1 = []
                for genr in response.get('genres'):
                    genres1.append(genr.get('name'))

                R = random.Random()
                delay = R.randint(1, 3)
                await msg.edit(content=str("Finished requesting {0}/{1} anime...".format(i + 1, amount) +
                                           "\n**ID:** " + str(int(animeID)) +
                                           "\n**Name:** " + str(response.get('name')) +
                                           "\n**Score:** " + str(response.get('score')) +
                                           "\n**Genres:** " + str(genres1) +
                                           "\n\n{0} left, next in {1} seconds...".format(int(amount - (i + 1)), delay)))
                await asyncio.sleep(delay)
            await msg.delete()

        scores = {}
        scores_number = {}
        # calculating genres scores
        for anime in shikimoriTesetAnimes.values():
            for genre in anime.genres:
                if genre in scores.keys():
                    scores[genre] += anime.myScore
                    scores_number[genre] += 1
                else:
                    scores[genre] = anime.myScore
                    scores_number[genre] = 1

        teset = sorted(scores.items(), key=lambda item: item[1], reverse=True)
        result = str("**Top rated genres (additive)** of user **{0}**:".format(nickname))
        for i in range(10):
            if len(teset) > i:
                result += "\n**{0})** ".format(i + 1) + str(teset[i][0]) + " = **" + str(teset[i][1]) + "** from **{0}** item(s)".format(scores_number.get(teset[i][0]))
        await ctx.send(result)

        mean_values = {}
        for genre in scores.keys():
            mean_values[genre] = scores.get(genre) / scores_number.get(genre)
        teset2 = sorted(mean_values.items(), key=lambda item: item[1], reverse=True)
        result2 = str("**Top rated genres (mean)** of user **{0}**:".format(nickname))
        for i in range(10):
            if len(teset2) > i:
                result2 += "\n**{0})** ".format(i + 1) + str(teset2[i][0]) + " = **" + str(round(teset2[i][1], 2)) + "** from **{0}** item(s)".format(scores_number.get(teset2[i][0]))
        await ctx.send(result2)

    @commands.command(pass_context=True)
    async def shikiStop(self, ctx):
        global stopFlag
        stopFlag = True
        await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    def getAnime(self, animeID: int):
        global shikimoriAnimes
        response = json.loads(requests.request("GET", "https://shikimori.one/api/animes/" + str(animeID), data="", headers={"User-Agent": "Waifutsianism"}).text)
        genres1 = []
        for genr in response.get('genres'):
            genres1.append(genr.get('name'))

        shikimoriAnimes[animeID] = Anime(animeID, str(response.get('name')), "", 0, float(response.get('score')), genres1)
        mpu.io.write(SHIKIMORI_ANIMES_FILEPATH, shikimoriAnimes)
        return response

    def getAnimeTitle(self, animeID: int) -> str:
        global shikimoriAnimes
        if animeID in shikimoriAnimes.keys():
            return shikimoriAnimes.get(animeID).title
        else:
            return ''

    def getAnimeTotalScore(self, animeID: int) -> float:
        global shikimoriAnimes
        if animeID in shikimoriAnimes.keys():
            return shikimoriAnimes.get(animeID).totalScore
        else:
            return 0

    def getAnimeGenres(self, animeID: int) -> list:
        global shikimoriAnimes
        if animeID in shikimoriAnimes.keys():
            return shikimoriAnimes.get(animeID).genres
        else:
            return []

    async def simple_paged_embed(self, original_msg: discord.Message, title: str, list_to_page: list, page_str: str, color: discord.Colour, need_sort: bool):
        items_per_page = 30
        item_number = 0
        if need_sort:
            # list.sort() can only sort alphanumerically (only strings and numbers, won't work with list of custom objects)
            list_to_page.sort()
        try:
            item_number = (int(page_str) - 1) * items_per_page
        except Exception:
            await original_msg.channel.send("Wrong argument - must be a page number, " + self.bot.user_title(original_msg.author.id) + "!", delete_after=15)
            await original_msg.delete(delay=15)
            return

        result = ""
        page_max = item_number + items_per_page
        while item_number < page_max and item_number < len(list_to_page):
            result += str(item_number + 1) + ") " + str(list_to_page[item_number]) + '\n'
            item_number += 1
        emb = discord.Embed(title=title, description=result, color=color)
        emb.set_footer(text="Page {0}/{1}".format(page_str, math.ceil(len(list_to_page) / items_per_page)))
        return emb


def setup(bot):
    bot.add_cog(Shikimori(bot))
