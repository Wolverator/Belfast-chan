import datetime
import os
import re
import string
import urllib.request

import pandas
from discord.ext import commands
from pandas import DataFrame, ExcelWriter

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")
description_pattern = "test description\n" \
                      + "Health: **{0}/{1}**\nMoney: **{2}**GC **{3}**SS **{4}**P\nEncumb.: **{5}/{6}**"


class Testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def pic(self, ctx):
        await ctx.message.add_reaction('🕑')

        bgPic = "1.webp"
        sprite1 = "2.webp"
        sprite2 = "3.webp"
        sprite3 = "4.webp"
        sprite4 = "5.webp"
        sprite5 = "6.webp"
        sprite6 = "7.webp"

        self.processPicsWithNoiseThreshold(bgPic, sprite1, 7, 7)
        self.processPicsWithNoiseThreshold(bgPic, sprite2, 7, 7)
        self.processPicsWithNoiseThreshold(bgPic, sprite3, 7, 7)
        self.processPicsWithNoiseThreshold(bgPic, sprite4, 7, 7)
        self.processPicsWithNoiseThreshold(bgPic, sprite5, 7, 7)
        self.processPicsWithNoiseThreshold(bgPic, sprite6, 7, 7)

        # await ctx.send(file=discord.File('new'+transparentPic))
        await ctx.message.add_reaction('✅')
        await ctx.message.remove_reaction('🕑', self.bot.user)
        await ctx.message.delete(delay=15)

    def processPicsWithNoiseThreshold(self, _bgPic, _spritePic, _noiseThreshold, _blur):
        from PIL import Image, ImageChops, ImageFilter

        bg = Image.open(_bgPic)
        sprite = Image.open(_spritePic)
        diff1 = ImageChops.difference(bg, sprite).convert('RGBA').filter(ImageFilter.GaussianBlur(_blur))
        newimdata = []
        transparent = (0, 0, 0, 0)
        fillColor = (255, 0, 0, 255)
        dat = diff1.getdata()
        for color in dat:
            if color[0] + color[1] + color[2] <= _noiseThreshold:
                newimdata.append(transparent)
            else:
                newimdata.append(fillColor)
        mask = Image.new('RGBA', diff1.size)
        mask.putdata(newimdata)

        ImageChops.composite(sprite, Image.new("RGBA", sprite.size, 0), mask) \
            .save('new' + _spritePic.replace('.webp', '_' + str(_noiseThreshold) + '_' + str(_blur * 10) + '.webp'), exact=True, loseless=True, quality=100, method=6)

        # original quality
        sprite.save('0' + _spritePic.replace('.webp', '_0.png'))
        # combined quality
        ImageChops.composite(sprite, bg, mask) \
            .save('0' + _spritePic.replace('.webp', '_' + str(_noiseThreshold) + '_' + str(_blur * 10) + '.png'), exact=True, loseless=True, quality=100, method=6)

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def lul(self, ctx):
        await ctx.message.add_reaction('🕑')

        from PIL import Image

        im1 = Image.open("9.webp")
        im1.save("teset.webp", exact=True, loseless=True, quality=100, method=6)

        await ctx.message.remove_reaction('🕑', self.bot.user)
        await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def pc(self, ctx):
        await ctx.message.add_reaction('🕑')
        import discord
        from PIL import Image, ImageChops

        im1 = Image.open("9.webp")
        im2 = Image.open("new9_7_70.webp")

        diff1 = ImageChops.difference(im1, im2).convert('RGBA')

        newimdata = []
        transparent = (0, 0, 0, 0)
        fillColor = (255, 0, 0, 255)
        dat = diff1.getdata()
        for color in dat:
            if color[0] + color[1] + color[2] <= 2:
                newimdata.append(transparent)
            else:
                newimdata.append(fillColor)
        newim = Image.new('RGBA', diff1.size)
        newim.putdata(newimdata)

        newim.crop(newim.getbbox())
        newim.save('diff.webp')

        await ctx.send(file=discord.File("diff.webp"))

        # await ctx.send(dat[0])
        await ctx.message.remove_reaction('🕑', self.bot.user)
        await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def ggn(self, ctx):
        await ctx.message.add_reaction('🕑')

        path = "D:\\Misc\\VNs\\Grisaia 1 debug\\result_sherhan\\clean texts for translations"
        ignored_names = ["JB", "SP", "SP2", "SP3", "019", "???", "Пожилой\\fs　\\fnдетектив", "Детектив",
                         "Мужчина", "Молодая\\fs　\\fnженщина", "Юджи", "Полицейский", "$str60", "leave_empty", "scene_title"]

        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            if os.path.isfile(file_path) and file_path.endswith(".xlsx") and not "~" in f:
                new_text_names = []
                xls = pandas.ExcelFile(file_path)
                df = xls.parse(0)
                text_names = list(df[df.columns[1]]).copy()
                while len(text_names) > 0:
                    new_text_names.append(text_names.pop(0))
                    name = text_names.pop(0)
                    if name not in ignored_names:
                        new_text_names.append(self.translateName(name))
                    else:
                        new_text_names.append(name)

                df1 = DataFrame({"Lines numbers": list(df[df.columns[0]]).copy(),
                                 "Character name": new_text_names,
                                 "Line text": list(df[df.columns[2]]).copy()})
                writer = ExcelWriter(file_path)
                df1.to_excel(writer, sheet_name='sheetName', index=False, na_rep='NaN')
                for column in df1:
                    column_length = min(df1[column].astype(str).map(len).max(), 120)
                    col_idx = df1.columns.get_loc(column)
                    writer.sheets['sheetName'].set_column(col_idx, col_idx, column_length)
                writer.save()

        await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def ts(self, ctx):
        await ctx.channel.trigger_typing()
        path = "D:\\Misc\\VNs\\Grisaia 1 debug\\translate here\\clean texts"
        WRITE_TRANSLATION_HERE = "(write translation here)"
        com_total = 0
        com_trans = 0
        ama_total = 0
        ama_trans = 0
        mak_total = 0
        mak_trans = 0
        mic_total = 0
        mic_trans = 0
        sac_total = 0
        sac_trans = 0
        yum_total = 0
        yum_trans = 0

        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            if os.path.isfile(file_path) and file_path.endswith(".xlsx") and not "~" in f:
                xls = pandas.ExcelFile(file_path)
                df = xls.parse(0)
                text_lines = list(df[df.columns[2]]).copy()
                # result += "op.xlsx has " + str(f[:2]) + " lines"
                while len(text_lines) > 0:
                    text_lines.pop(0)
                    translated = 0
                    if not text_lines.pop(0) == WRITE_TRANSLATION_HERE:
                        translated = 1
                    match f[:2]:
                        case "op" | "co":
                            com_total += 1
                            com_trans += translated
                        case "am":
                            ama_total += 1
                            ama_trans += translated
                        case "ma":
                            mak_total += 1
                            mak_trans += translated
                        case "mi":
                            mic_total += 1
                            mic_trans += translated
                        case "sa":
                            sac_total += 1
                            sac_trans += translated
                        case "yu":
                            yum_total += 1
                            yum_trans += translated
                        case _:
                            pass

        result = "**Прогресс перевода Grisaia no Kajitsu:**" \
                 + "\nОбщий: {0}/{1} строк, **{2}%**".format(com_trans, com_total, round((com_trans / com_total) * 100, 2))
        result += "\nАмане: {0}/{1} строк, **{2}%**".format(ama_trans, ama_total, round((ama_trans / ama_total) * 100, 2))
        result += "\nМакина: {0}/{1} строк, **{2}%**".format(mak_trans, mak_total, round((mak_trans / mak_total) * 100, 2))
        result += "\nМичиру: {0}/{1} строк, **{2}%**".format(mic_trans, mic_total, round((mic_trans / mic_total) * 100, 2))
        result += "\nСачи: {0}/{1} строк, **{2}%**".format(sac_trans, sac_total, round((sac_trans / sac_total) * 100, 2))
        result += "\nЮмико: {0}/{1} строк, **{2}%**".format(yum_trans, yum_total, round((yum_trans / yum_total) * 100, 2))
        sum_trans = ama_trans + com_trans + mak_trans + mic_trans + sac_trans + yum_trans
        sum_total = ama_total + com_total + mak_total + mic_total + sac_total + yum_total
        result += "\n\nИтого: {0}/{1} строк, **{2}%**".format(sum_trans, sum_total, round((sum_trans / sum_total) * 100, 2))

        result += "\n{0}".format(str(datetime.datetime.now()).split('.')[0])
        await ctx.send(result)
        await ctx.message.delete(delay=5)

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def tsen(self, ctx):
        await ctx.channel.trigger_typing()
        path = "D:\\Misc\\VNs\\Grisaia 1 debug\\translate here\\clean texts"
        WRITE_TRANSLATION_HERE = "(write translation here)"
        com_total = 0
        com_trans = 0
        ama_total = 0
        ama_trans = 0
        mak_total = 0
        mak_trans = 0
        mic_total = 0
        mic_trans = 0
        sac_total = 0
        sac_trans = 0
        yum_total = 0
        yum_trans = 0

        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            if os.path.isfile(file_path) and file_path.endswith(".xlsx") and not "~" in f:
                xls = pandas.ExcelFile(file_path)
                df = xls.parse(0)
                text_lines = list(df[df.columns[2]]).copy()
                # result += "op.xlsx has " + str(f[:2]) + " lines"
                while len(text_lines) > 0:
                    text_lines.pop(0)
                    translated = 0
                    if not text_lines.pop(0) == WRITE_TRANSLATION_HERE:
                        translated = 1
                    match f[:2]:
                        case "op" | "co":
                            com_total += 1
                            com_trans += translated
                        case "am":
                            ama_total += 1
                            ama_trans += translated
                        case "ma":
                            mak_total += 1
                            mak_trans += translated
                        case "mi":
                            mic_total += 1
                            mic_trans += translated
                        case "sa":
                            sac_total += 1
                            sac_trans += translated
                        case "yu":
                            yum_total += 1
                            yum_trans += translated
                        case _:
                            pass

        result = "**Translation progress Grisaia no Kajitsu:**" \
                 + "\nCommon: {0}/{1} lines, **{2}%**".format(com_trans, com_total, round((com_trans / com_total) * 100, 2))
        result += "\nAmane: {0}/{1} lines, **{2}%**".format(ama_trans, ama_total, round((ama_trans / ama_total) * 100, 2))
        result += "\nMakina: {0}/{1} lines, **{2}%**".format(mak_trans, mak_total, round((mak_trans / mak_total) * 100, 2))
        result += "\nMichiru: {0}/{1} lines, **{2}%**".format(mic_trans, mic_total, round((mic_trans / mic_total) * 100, 2))
        result += "\nSachi: {0}/{1} lines, **{2}%**".format(sac_trans, sac_total, round((sac_trans / sac_total) * 100, 2))
        result += "\nYumiko: {0}/{1} lines, **{2}%**".format(yum_trans, yum_total, round((yum_trans / yum_total) * 100, 2))
        sum_trans = ama_trans + com_trans + mak_trans + mic_trans + sac_trans + yum_trans
        sum_total = ama_total + com_total + mak_total + mic_total + sac_total + yum_total
        result += "\n\nTotal: {0}/{1} lines, **{2}%**".format(sum_trans, sum_total, round((sum_trans / sum_total) * 100, 2))

        result += "\n{0}".format(str(datetime.datetime.now()).split('.')[0])
        await ctx.send(result)
        await ctx.message.delete(delay=5)

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def tsw(self, ctx):
        await ctx.channel.trigger_typing()
        path = "D:\\Misc\\VNs\\Grisaia 1 debug\\translate here\\clean texts"
        WRITE_TRANSLATION_HERE = "(write translation here)"
        com_total = 0
        com_trans = 0
        ama_total = 0
        ama_trans = 0
        mak_total = 0
        mak_trans = 0
        mic_total = 0
        mic_trans = 0
        sac_total = 0
        sac_trans = 0
        yum_total = 0
        yum_trans = 0

        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            if os.path.isfile(file_path) and file_path.endswith(".xlsx") and not "~" in f:
                xls = pandas.ExcelFile(file_path)
                df = xls.parse(0)
                text_lines = list(df[df.columns[2]]).copy()
                # result += "op.xlsx has " + str(f[:2]) + " lines"
                while len(text_lines) > 0:
                    original_line = str(text_lines.pop(0))
                    translated_line = str(text_lines.pop(0))
                    original = len(original_line.translate(str.maketrans('', '', string.punctuation)).split())
                    translated = 0
                    if not translated_line == WRITE_TRANSLATION_HERE:
                        translated = len(translated_line.translate(str.maketrans('', '', string.punctuation)).split())
                    match f[:2]:
                        case "op" | "co":
                            com_total += original
                            com_trans += translated
                        case "am":
                            ama_total += original
                            ama_trans += translated
                        case "ma":
                            mak_total += original
                            mak_trans += translated
                        case "mi":
                            mic_total += original
                            mic_trans += translated
                        case "sa":
                            sac_total += original
                            sac_trans += translated
                        case "yu":
                            yum_total += original
                            yum_trans += translated
                        case _:
                            pass

        result = "**Прогресс перевода Grisaia no Kajitsu:**\n(слов стало в переводе / слов в оригинале)" \
                 + "\nОбщий: {0} / {1} слов, {2}%".format(com_trans, com_total, round((com_trans / com_total) * 100, 2))
        result += "\nАмане: {0} / {1} слов, {2}%".format(ama_trans, ama_total, round((ama_trans / ama_total) * 100, 2))
        result += "\nМакина: {0} / {1} слов, {2}%".format(mak_trans, mak_total, round((mak_trans / mak_total) * 100, 2))
        result += "\nМичиру: {0} / {1} слов, {2}%".format(mic_trans, mic_total, round((mic_trans / mic_total) * 100, 2))
        result += "\nСачи: {0} / {1} слов, {2}%".format(sac_trans, sac_total, round((sac_trans / sac_total) * 100, 2))
        result += "\nЮмико: {0} / {1} слов, {2}%".format(yum_trans, yum_total, round((yum_trans / yum_total) * 100, 2))
        sum_trans = ama_trans + com_trans + mak_trans + mic_trans + sac_trans + yum_trans
        sum_total = ama_total + com_total + mak_total + mic_total + sac_total + yum_total
        result += "\n\nИтого: {0} / {1} слов, {2}%".format(sum_trans, sum_total, round((sum_trans / sum_total) * 100, 2))

        result += "\n{0}".format(str(datetime.datetime.now()).split('.')[0])
        await ctx.send(result)
        await ctx.message.delete(delay=5)

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def sao(self, ctx):
        template = "https://9bc-a3e-2200g0.streamalloha.live/hs/46/1657661945/XHT7pydqrti9LmT6SG_J5A/395/628395/seg-{0}-f2-v1-f5-a1.ts"
        msg = await ctx.send("Starting...")
        for i in range(1, 735):
            if not os.path.exists("part{0}.ts".format(i)):
                try:
                    urllib.request.urlretrieve(template.format(i), "part{0}.ts".format(i))
                    await msg.edit(content="Finished {0}/735 parts...".format(i))
                except Exception as e:
                    await ctx.send("**ERROR**\n" + str(e) + "\n\nTry again")
                    break

        with open("SAO Progressive.ts", 'wb') as f:
            for i in range(1, 735):
                with open("part{0}.ts".format(i), 'rb') as f1:
                    f.write(f1.read())
                    f1.close()
                    await msg.edit(content="Compiled {0}/735 parts...".format(i))
            f.close()
        await msg.delete()
        await ctx.send("Done!")

    @commands.command(pass_context=True)
    @commands.is_owner()
    async def translatecommonphrases(self, ctx):
        lines = {}
        lines_to_translate = {
            'Hrm...': 'Хм-м...',
            'I [see...]': 'Понятно...',
            'Huh...?': 'А?..',
            'Ah...': 'А...',
            'Yeah...': 'Да...',
            '...Huh?': 'А?..',
            '...What?': 'Что?..',
            'Yeah.': 'Да.'
        }
        path = "D:\\Misc\\VNs\\Grisaia 1 debug\\translate here\\clean texts"
        WRITE_TRANSLATION_HERE = "(write translation here)"

        for f in os.listdir(path):
            lines_text = []
            file_path = os.path.join(path, f)
            if os.path.isfile(file_path) and file_path.endswith(".xlsx") and not "~" in f:
                xls = pandas.ExcelFile(file_path)
                df = xls.parse(0)
                text_lines = list(df[df.columns[2]]).copy()
                while len(text_lines) > 0:
                    line = str(text_lines.pop(0))
                    translation = text_lines.pop(0)

                    if translation == WRITE_TRANSLATION_HERE:
                        if line not in lines.keys():
                            lines[line] = 1
                        else:
                            lines[line] = lines[line] + 1

                        try:
                            if (None == re.search('[a-zA-Z]', line)):
                                lines_text.append(line)
                                lines_text.append(line)
                            elif (line in lines_to_translate.keys()):
                                lines_text.append(line)
                                lines_text.append(lines_to_translate[line])
                            else:
                                lines_text.append(line)
                                lines_text.append(translation)
                        except Exception as ex:
                            await ctx.send("Error processing line ```" + line + "```")
                    else:
                        lines_text.append(line)
                        lines_text.append(translation)

                if (len(list(df[df.columns[0]])) != len(list(df[df.columns[1]]))) or (len(list(df[df.columns[0]])) != len(lines_text)):
                    await ctx.send(str(len(list(df[df.columns[0]]))) + " " + str(len(list(df[df.columns[1]]))) + " " + str(len(lines_text)) + " in ```" + file_path + "```")
                df1 = DataFrame({"Lines numbers": list(df[df.columns[0]]).copy(),
                                 "Character name": list(df[df.columns[1]]).copy(),
                                 "Line text": lines_text})
                writer = ExcelWriter(file_path)
                df1.to_excel(writer, sheet_name='sheetName', index=False, na_rep='NaN')
                for column in df1:
                    column_length = min(df1[column].astype(str).map(len).max(), 120)
                    col_idx = df1.columns.get_loc(column)
                    writer.sheets['sheetName'].set_column(col_idx, col_idx, column_length)
                writer.save()

        i = 0
        result_text = ""
        for w in sorted(lines, key=lines.get, reverse=True):
            if i < 20:
                i += 1
                result_text += str(i) + ")`" + str(w) + "` = " + str(lines[w]) + str(None == re.search('[a-zA-Z]', w)) + "\n"
        await ctx.send(result_text)

    def translateName(self, _name: str) -> str:
        new_name = _name \
            .replace("Cardboard\\fs　\\fnCreature", "Картонное существо") \
            .replace("General\\fs　\\fnSpareribs", "Генерал Рёбрышки") \
            .replace("BBQ\\fs　\\fnBelligerent", "Воинственный Барбекю") \
            .replace("Tunafish\\fs　\\fnMan", "Человек-тунец") \
            .replace("Woman\\fs　\\fnNext\\fs　\\fnDoor", "Соседка") \
            .replace("Military\\fs　\\fnCommentator", "Военный комментатор") \
            .replace("Stooped\\fs　\\fnGrandmother", "Сутулая бабушка") \
            .replace("Mom\\fs　\\fnand\\fs　\\fnDad", "Мама+Папа") \
            .replace("Elderly\\fs　\\fnDetective", "Пожилой детектив") \
            .replace("Economic\\fs　\\fnAnalyst", "Аналитик по экономике") \
            .replace("Chief\\fs　\\fnSecretary", "Главный секретарь") \
            .replace("Yumiko+Michiru+Amane", "Юмико+Мичиру+Амане") \
            .replace("Three\\fs　\\fn[People]", "Три человека") \
            .replace("Investigator\\fs　\\fnB", "Следователь Б") \
            .replace("Investigator\\fs　\\fnA", "Следователь А") \
            .replace("Professor\\fs　\\fnDave", "Профессор Дейв") \
            .replace("Sachi+Michiru+Makina", "Сачи+Мичиру+Макина") \
            .replace("Michiru+Sachi+Yumiko", "Мичиру+Сачи+Юмико") \
            .replace("Sachi`s\\fs　\\fnUncle", "Дядя Сачи") \
            .replace("Yumiko+Makina+Amane", "Юмико+Макина+Амане") \
            .replace("Energetic\\fs　\\fnKid", "Энергичный ребёнок") \
            .replace("Innocent\\fs　\\fnGirl", "Невинная девочка") \
            .replace("Friendly\\fs　\\fnLady", "Дружелюбная дама") \
            .replace("Three\\fs　\\fnPeople", "Три человека") \
            .replace("Delivery\\fs　\\fnMan", "Курьер") \
            .replace("Classmate\\fs　\\fnD", "Одноклассник(ца) Г") \
            .replace("Classmate\\fs　\\fnC", "Одноклассник(ца) В") \
            .replace("Classmate\\fs　\\fnB", "Одноклассник(ца) Б") \
            .replace("Classmate\\fs　\\fnA", "Одноклассник(ца) А") \
            .replace("Young\\fs　\\fnWoman", "Молодая женщина") \
            .replace("Kidnapper\\fs　\\fnB", "Похититель Б") \
            .replace("Kidnapper\\fs　\\fnA", "Похититель А") \
            .replace("Four\\fs　\\fnPeople", "Четыре человека") \
            .replace("Naughty\\fs　\\fnKid", "Непослушный пацан") \
            .replace("Blond\\fs　\\fnMan", "Блондинчик") \
            .replace("Servant\\fs　\\fn3", "Прислуга 3") \
            .replace("Servant\\fs　\\fn2", "Прислуга 2") \
            .replace("Servant\\fs　\\fn1", "Прислуга 1") \
            .replace("Other\\fs　\\fnMen", "Другие мужчины") \
            .replace("Old\\fs　\\fnLady", "Дама в возрасте") \
            .replace("Michiru+Makina", "Мичиру+Макина") \
            .replace("Bush\\fs　\\fnDog", "Кустарниковый пёс") \
            .replace("Yumiko+Michiru", "Юмико+Мичиру") \
            .replace("Makina+Michiru", "Макина+Мичиру") \
            .replace("Man\\fs　\\fnA+B", "Мужчины А+Б") \
            .replace("Businesswoman", "Бизнес-леди") \
            .replace("Michiru+Amane", "Мичиру+Амане") \
            .replace("Yumiko+Makina", "Юмико+Макина") \
            .replace("Girl\\fs　\\fnB", "Девушка Б") \
            .replace("Girl\\fs　\\fnA", "Девушка А") \
            .replace("Receptionist", "Администратор") \
            .replace("Amane+Makina", "Амане+Макина") \
            .replace("Yumiko+Amane", "Юмико+Амане") \
            .replace("Makina+Amane", "Макина+Амане") \
            .replace("Makina+Sachi", "Макина+Сачи") \
            .replace("Sachi+Makina", "Макина+Сачи") \
            .replace("Grandmother", "Бабушка") \
            .replace("Man\\fs　\\fnG", "Мужчина Ж") \
            .replace("Man\\fs　\\fnF", "Мужчина Е") \
            .replace("Man\\fs　\\fnE", "Мужчина Д") \
            .replace("Man\\fs　\\fnD", "Мужчина Г") \
            .replace("Man\\fs　\\fnC", "Мужчина В") \
            .replace("Man\\fs　\\fnB", "Мужчина Б") \
            .replace("Man\\fs　\\fnA", "Мужчина А") \
            .replace("Man\\fs　\\fn5", "Мужчина 5") \
            .replace("Man\\fs　\\fn4", "Мужчина 4") \
            .replace("Man\\fs　\\fn3", "Мужчина 3") \
            .replace("Man\\fs　\\fn2", "Мужчина 2") \
            .replace("Man\\fs　\\fn1", "Мужчина 1") \
            .replace("Kid\\fs　\\fnB", "Ребёнок Б") \
            .replace("Kid\\fs　\\fnA", "Ребёнок А") \
            .replace("Yuuji&Sachi", "Юджи+Сачи") \
            .replace("Businessman", "Бизнесмен") \
            .replace("Grandfather", "Дедушка") \
            .replace("Greengrocer", "Продавец овощей") \
            .replace("Son-in-Law", "Зять") \
            .replace("Classmates", "Одноклассники") \
            .replace("Muramatsu", "Мурамацу") \
            .replace("Conductor", "Кондуктор") \
            .replace("Secretary", "Секретарь") \
            .replace("Physician", "Врач") \
            .replace("Detective", "Детектив") \
            .replace("Kittymeow", "Киттимяу") \
            .replace("Voicemail", "Автоответчик?") \
            .replace("Printcher", "Директище") \
            .replace("Narration", "Рассказчик") \
            .replace("Policeman", "Полицейский") \
            .replace("Sakashita", "Сакашита") \
            .replace("Moderator", "Модератор") \
            .replace("Principal", "Директор") \
            .replace("Matsuyama", "Мацуяма") \
            .replace("Employee", "Сотрудник") \
            .replace("Students", "Студенты") \
            .replace("Servants", "Прислуги") \
            .replace("Daughter", "Дочка") \
            .replace("Reporter", "Журналист") \
            .replace("Shopkeep", "Хозяин магазина") \
            .replace("Masataka", "Масатака") \
            .replace("Michiaki", "Мичиаки") \
            .replace("Masahiko", "Масахико") \
            .replace("Everyone", "Все") \
            .replace("Meowmel", "Мяумель") \
            .replace("Tadashi", "Тадаши") \
            .replace("Laborer", "Рабочий") \
            .replace("Females", "Женщины") \
            .replace("Servant", "Слуга") \
            .replace("M-Chiru", "М-чиру") \
            .replace("Matcher", "Макинище") \
            .replace("Satcher", "Сачище") \
            .replace("Mitcher", "Мичирище") \
            .replace("Sakurai", "Сакурай") \
            .replace("Hirooka", "Хируока") \
            .replace("Captain", "Капитан") \
            .replace("Michiru", "Мичиру") \
            .replace("Worker", "Рабочий") \
            .replace("Kanako", "Канако") \
            .replace("Toshie", "Тошиэ") \
            .replace("Misako", "Мисако") \
            .replace("Hitomi", "Хитоми") \
            .replace("Komine", "Комине") \
            .replace("Mother", "Мать") \
            .replace("Doctor", "Доктор") \
            .replace("Father", "Отец") \
            .replace("Rommel", "Роммель") \
            .replace("Driver", "Водитель") \
            .replace("Otsuka", "Оцука") \
            .replace("Kiyoka", "Киёка") \
            .replace("Sawada", "Савада") \
            .replace("Sarina", "Сарина") \
            .replace("Sacchi", "Сачи") \
            .replace("Y-Miko", "Ю-ико") \
            .replace("K-Mine", "К-мине") \
            .replace("C-Zuru", "Ч-зуру") \
            .replace("Chiara", "Киара") \
            .replace("Atcher", "Аманище") \
            .replace("Nanano", "Нанано") \
            .replace("Kitten", "Котёнок") \
            .replace("Komori", "Комори") \
            .replace("Sakuma", "Сакума") \
            .replace("Kaneda", "Канеда") \
            .replace("Kazuki", "Казуки") \
            .replace("Suzune", "Сузуне") \
            .replace("Yumiko", "Юмико") \
            .replace("Makina", "Макина") \
            .replace("Pilot", "Пилот") \
            .replace("Child", "Ребёнок") \
            .replace("Nurse", "Медсестра") \
            .replace("Phone", "Телефон") \
            .replace("Tutor", "Репетитор") \
            .replace("Okuda", "Окуда") \
            .replace("Ihara", "Ихара") \
            .replace("Woman", "Женщина") \
            .replace("Carny", "Карни") \
            .replace("Clerk", "Клерк") \
            .replace("Renge", "Ренж") \
            .replace("Voice", "Голос") \
            .replace("Ibuki", "Ибуки") \
            .replace("Ritsu", "Рицу") \
            .replace("Sachi", "Сачи") \
            .replace("Yuuji", "Юджи") \
            .replace("Amane", "Амане") \
            .replace("Yuma", "Юма") \
            .replace("Aide", "Айде") \
            .replace("Girl", "Девочка") \
            .replace("Atou", "Атоу") \
            .replace("A-Ne", "А-не") \
            .replace("Ochi", "Очи") \
            .replace("Men", "Мужчины") \
            .replace("Dad", "Папа") \
            .replace("Mom", "Мама") \
            .replace("Man", "Мужчина") \
            .replace("Kid", "Пацан") \
            .replace("Cat", "Кот") \
            .replace(" ", "\\fs　\\fn")
        return new_name


def setup(bot):
    bot.add_cog(Testing(bot))
