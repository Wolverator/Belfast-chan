import asyncio
import codecs
import datetime
import os
import time
from datetime import datetime as d

import discord
from colorama import Fore
from dateutil.parser import parser
from discord.ext import commands

from cogs.BelfastUtils import logtime

DateParser = parser()
dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")
time_start = time.time()
maintenance_remind_where_whom = {}
maintenance_finish = None


def already_in_maintenance(_id: int):
    result = False
    for users in maintenance_remind_where_whom.values():
        if users.count(str("<@" + str(_id) + ">")) >= 1:
            result = True
    return result


async def mt_reminder():
    global maintenance_remind_where_whom
    global maintenance_finish
    if maintenance_finish is not None:
        if (maintenance_finish.timestamp() - datetime.datetime.now().timestamp()) <= 0:
            for channel in maintenance_remind_where_whom.keys():
                await channel.send("Maintenance of AzurLane EN server should be finished now." + maintenance_remind_where_whom.get(channel))
            maintenance_remind_where_whom = {}


class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, aliases=['hey', 'hello', 'hello?', 'answer'], hidden=True)
    async def test(self, ctx):
        await ctx.channel.trigger_typing()
        await asyncio.sleep(0.1)
        if await ctx.bot.is_owner(ctx.author):
            test_text = "Yes, Master? <:AzurLane:569511684650041364>" + "\n" + str(time.time()).partition('.')[0]
            msg = await ctx.send(test_text)
            await asyncio.sleep(15)
            await msg.delete()
        else:
            msg = await ctx.send("How can i help you?\nFor more details, please write ``Bel info``.")
            await asyncio.sleep(15)
            await msg.delete()

    @commands.command(pass_context=True, brief="Get invite to my server")
    async def server(self, ctx):
        await ctx.channel.trigger_typing()
        await asyncio.sleep(0.1)
        await ctx.send("Join my Master's guild if you want or if you need some help:\nhttps://discord.gg/86YrJNq")

    @commands.command(pass_context=True, brief="Check online time")
    async def online(self, ctx):
        await ctx.channel.trigger_typing()
        await asyncio.sleep(0.1)
        msg = await ctx.send(
            "I'm online for " + str(datetime.timedelta(seconds=time.time() - time_start)).partition('.')[0] + " already, doing good.\nThanks for asking and may The Force be with you!")
        await asyncio.sleep(15)
        await msg.delete()

    @commands.command(pass_context=True, brief="Leave your suggestion")
    async def suggest(self, ctx, *, text: str):
        path_to_file = os.path.abspath("suggests/suggest by " + str(ctx.author) + " " + str(time.time()).replace('.', '_') + ".txt")
        with codecs.open(path_to_file, encoding='utf-8', mode='w') as output_file:
            output_file.write(text)
            output_file.close()
        msg = await ctx.send("Done! :white_check_mark:")
        print(str(datetime.datetime.utcnow().time()).partition('.')[0] + " " + Fore.CYAN + str(
            ctx.author) + Fore.RESET + " made a suggestion!")
        await asyncio.sleep(15)
        await msg.delete()

    @commands.command(pass_context=True, brief="Invite me to your server")
    async def invite(self, ctx):
        await ctx.channel.trigger_typing()
        await asyncio.sleep(0.1)
        await ctx.send(
            "Let me join your guild too!\nhttps://discordapp.com/api/oauth2/authorize?client_id=568914197048459273"
            "&permissions=117824&scope=bot")

    @commands.command(name='ping', brief='Pong!')
    async def ping(self, ctx):
        start = d.timestamp(d.now())
        msg = await ctx.send(content='Pinging')
        await msg.edit(content=f'Thanks for asking!\nSeems like my ping is {str((d.timestamp(d.now()) - start) * 1000).partition(".")[0]}ms.')
        await asyncio.sleep(15)
        await msg.delete()
        return

    @commands.command(pass_context=True, aliases=['amtf'], brief="Check when servers will be back online")
    @commands.is_owner()
    async def add_mt_reminder_for(self, ctx, user_id: int):
        global maintenance_remind_where_whom
        global maintenance_finish
        if ctx.message.mentions:
            user_id = ctx.message.mentions.pop(0).id
        time_left = datetime.timedelta(
            seconds=(maintenance_finish.timestamp() - datetime.datetime.now().timestamp()))
        if time_left.total_seconds() >= 0:
            text = ":clock1: Servers should be online in " + str(time_left).partition('.')[0] + "."
            if already_in_maintenance(user_id):
                text += "\n" + str(self.bot.get_user(user_id).display_name) + " already in my 'to-remind-list' for the maintenance ending, Master!."
            else:
                if ctx.channel in maintenance_remind_where_whom.keys():
                    maintenance_remind_where_whom[ctx.channel] = maintenance_remind_where_whom.get(ctx.channel) + str(
                        ", <@" + str(user_id) + ">")
                else:
                    maintenance_remind_where_whom[ctx.channel] = str("\n<@" + str(user_id) + ">")
                text += "\n" + str(self.bot.get_user(user_id).display_name) + " was added to my 'to-remind-list', Master!.\nThus I'll mention them in this channel when servers will come online."
                await ctx.message.add_reaction('✅')
        else:
            text = "Servers should be online, Commander.\nMay The Luck be with You!\n\nPrevious maintenance was finished: " + str(maintenance_finish)
        msg = await ctx.send(text)
        await asyncio.sleep(25)
        await msg.delete()

    @commands.command(pass_context=True, aliases=['mt'], brief="Check when servers will be back online")
    async def maintenance(self, ctx):  # TODO: move users to remind mt end about also into file and load that list at start-up
        global maintenance_remind_where_whom
        global maintenance_finish
        if os.path.getsize(dir_path + "/config/last maintenance.txt") > 0:
            maintenance_finish = DateParser.parse(timestr=codecs.open(dir_path + "/config/last maintenance.txt", encoding='utf-8').read())
        if maintenance_finish:
            time_left = datetime.timedelta(
                seconds=(maintenance_finish.timestamp() - datetime.datetime.now().timestamp()))
            if time_left.total_seconds() >= 0:
                text = ":clock1: Servers should be online in " + str(time_left).partition('.')[0] + "."
                if already_in_maintenance(ctx.author.id):
                    text += "\nYou're already in my 'to-remind-list' for the maintenance ending, " + ctx.author.display_name + "."
                else:
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

    @commands.command(pass_context=True, brief="[owner-only]Set time for maintenance end", hidden=True)
    @commands.is_owner()
    async def set_maintenance(self, ctx, *, maintenance_time: str):
        global maintenance_finish
        await ctx.channel.trigger_typing()
        if await self.bot.is_owner(ctx.author):
            maintenance_finish = DateParser.parse(timestr=maintenance_time)
            with codecs.open(os.path.abspath("config/last maintenance.txt"), encoding='utf-8', mode='w') as output_file:
                output_file.write(str(maintenance_finish))
                output_file.close()
            await ctx.send("Yes, Master! :white_check_mark:\nMaintenance finish time updated!")
        else:
            await ctx.send(":no_entry_sign: Sorry, but only my Master is allowed to give me this order!")

    @commands.command(pass_context=True, brief="[owner-only]Send news to each 'belfast-chan-news' channel", hidden=True)
    @commands.is_owner()
    async def news(self, ctx):
        await ctx.channel.trigger_typing()
        chs = 0
        for guild in ctx.bot.guilds:
            for textChannel in guild.text_channels:
                if textChannel.name == 'belfast-chan-news':
                    chs += 1
                    await textChannel.send(ctx.message.content.replace(ctx.prefix + 'news ', ''))
        await ctx.send(
            "Yes, Master! :white_check_mark:\nReposted this to " + str(chs) + " 'belfast-chan-news' channels.")

    @commands.command(pass_context=True, aliases=['logout'], brief="[owner-only]Log out and exit program", hidden=True)
    @commands.is_owner()
    async def exit(self, ctx):
        await ctx.channel.trigger_typing()
        await asyncio.sleep(0.5)
        await ctx.send("Yes, Master! Logging out...")
        await ctx.bot.change_presence(status=discord.Status.offline, activity=None)
        print(logtime() + Fore.YELLOW + "Logged out!")
        # noinspection PyProtectedMember
        os._exit(0)


def setup(bot):
    bot.add_cog(General(bot))
