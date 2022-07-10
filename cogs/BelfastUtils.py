import datetime
import itertools
import os
import time
from platform import python_version

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")
time_start = time.time()


def logtime(): return str(datetime.datetime.now().time()).partition('.')[0] + " "


class BelfastUtils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    @has_permissions(manage_roles=True)
    @commands.guild_only()
    async def give_role(self, ctx, user_str: str, role_id: int):
        user = self.bot.get_user_from_guild(ctx.guild, user_str)
        if (user):
            role = self.bot.get_guild(ctx.guild.id).get_role(role_id)
            if (role):
                try:
                    await user.add_roles(role)
                    await ctx.send("Done! :white_check_mark:", delete_after=15)
                except Exception:
                    await ctx.send("Error! :no_entry:\nNo success.", delete_after=15)
                finally:
                    await ctx.message.delete(delay=15)
            else:
                await ctx.send("Error! :no_entry:\nNo role.", delete_after=15)
        else:
            await ctx.send("Error! :no_entry:\nNo user.", delete_after=15)

    @commands.command(pass_context=True, hidden=True)
    @has_permissions(manage_roles=True)
    @commands.guild_only()
    async def iam(self, ctx, *, role: str):
        commander_role = self.bot.get_guild(566171342953512963).get_role(569993566311415809)
        new_role = discord.utils.get(ctx.guild.roles, name=role)
        if ctx.guild == self.bot.MyGuild and new_role.id == 569993566311415809:
            await ctx.author.add_roles(new_role)
            await ctx.send("Done! :white_check_mark:", delete_after=15)
            await ctx.message.delete(delay=15)
            return
        if ctx.guild == self.bot.MyGuild and new_role.id == 570131573463318528 and commander_role in ctx.author.roles:
            await ctx.author.remove_roles(commander_role)
            await ctx.author.add_roles(new_role)
            await ctx.send("Done! :white_check_mark:", delete_after=15)
            await ctx.message.delete(delay=15)
            return
        try:
            if ctx.author.top_role > new_role:
                await ctx.author.add_roles(new_role)
                await ctx.send("Done! :white_check_mark:", delete_after=15)
                await ctx.message.delete(delay=15)
        except Exception:
            await ctx.send("Error! :no_entry:\nSomething went wrong or someone don't have permissions for that role.", delete_after=15)

    @commands.command(pass_context=True, aliases=['ava', 'mypp'], brief="Show your or other user's avatar")
    @commands.guild_only()
    async def avatar(self, ctx, *, some_user="placeholderLVL99999"):
        await ctx.channel.trigger_typing()
        if some_user == "placeholderLVL99999":
            some_user = str(ctx.author.id)
        user = self.bot.get_user_from_guild(ctx.guild, some_user)
        if user is not None:
            resultEmbed = discord.Embed()
            resultEmbed.set_author(name=str(user))
            resultEmbed.set_image(url=user.avatar_url)
            await ctx.send(embed=resultEmbed)
            await ctx.message.delete(delay=15)
        else:
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nUser with predicate **" + some_user + "** not found on this server.")
            await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, hidden=True)
    async def stats(self, ctx):
        await ctx.channel.trigger_typing()
        text = "Bot online for: **" + str(datetime.timedelta(seconds=time.time() - time_start)).partition('.')[0] + "**\n"
        users = 0
        bots = 0

        for guild in self.bot.guilds:
            for member in guild.members:
                if member.bot:
                    bots += 1
                else:
                    users += 1
        author = self.bot.get_user_from_guild(ctx.guild, str(self.bot.owner_id))
        scan_result = self.scan_dir(dir_path)
        resultEmbed = discord.Embed()
        resultEmbed.set_thumbnail(url=self.bot.user.avatar_url)
        resultEmbed.set_author(name=str(self.bot.user))
        resultEmbed.set_footer(text="Bot owner and author: " + str(author), icon_url=author.avatar_url)
        resultEmbed.timestamp = datetime.datetime.utcnow()
        resultEmbed.colour = discord.colour.Color.from_rgb(222, 222, 0)
        resultEmbed.title = "A bit of statistics:"

        text += "Guilds: **{0}**\n".format(len(self.bot.guilds))
        text += "Nearby members: **{0}**\n".format(users)
        text += "Nearby bots: **{0}**\n".format(bots)
        text += "Files in folder: **{0}**\n".format(scan_result[0])
        text += "Code lines: **{0}**\n".format(scan_result[1])
        text += "Total files size: **{0}** MB\n".format(round(scan_result[2] / (1024 * 1024), 2))
        text += "Python version: **{0}**\n".format(str(python_version()))
        text += "Discord.py version: **{0}**\n".format(str(discord.__version__))

        resultEmbed.description = text
        await ctx.send(embed=resultEmbed, delete_after=45)
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def bots(self, ctx):
        text = ""
        for member in itertools.chain.from_iterable([a.members for a in self.bot.guilds]):
            if member.bot:
                text += str(member) + "\n"
        await ctx.send("```" + text + "```", delete_after=35)
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def users(self, ctx):
        text = ""
        for member in itertools.chain.from_iterable([a.members for a in self.bot.guilds]):
            if not member.bot:
                text += str(member) + "\n"
        await ctx.send("```" + text + "```", delete_after=35)
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def guilds2(self, ctx):
        text = ""
        for guild in self.bot.guilds:
            text += str(guild) + " `" + str(guild.id) + "`\n"
        await ctx.send("```" + text + "```", delete_after=35)
        await ctx.message.delete(delay=15)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def fonts(self, ctx, *, page_str="1"):
        await ctx.send(embed=await self.bot.get_cog('MudaHelper').simple_paged_embed(ctx.message, "Fonts:", self.scan_fonts(), page_str, discord.Colour.gold(), True))

    def scan_fonts(self):
        path = "C:\Windows\Fonts"
        resilt = []
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                if os.path.join(path, f).endswith(".ttf"):
                    resilt.append(str(f.partition(".ttf")[0]))
        return resilt

    @commands.command(pass_context=True, aliases=['parse'], hidden=True)
    @commands.is_owner()
    async def parsemessage(self, ctx, *, message_id: int):
        # self.bot.loop.create_task(self.teset(ctx))
        await self.parse_message(ctx, message_id)

    async def parse_message(self, ctx, message_id: int):
        msg_to_parse = await ctx.channel.fetch_message(message_id)
        emb = discord.Embed()
        text = ""
        if msg_to_parse:
            if msg_to_parse.author:
                text += "**Message author:** " + str(msg_to_parse.author) + "\n"
                text += "**Message author.id:** " + str(msg_to_parse.author.id) + "\n\n"
            if msg_to_parse.clean_content:
                text += "**Message clean_content:** " + str(msg_to_parse.clean_content) + "\n\n"
            if msg_to_parse.system_content:
                text += "**Message system_content:** " + str(msg_to_parse.system_content) + "\n\n"
            if msg_to_parse.type:
                text += "**Message type:** " + str(msg_to_parse.type) + "\n\n"
            if msg_to_parse.reference:
                text += "**Message reference:** " + str(msg_to_parse.reference) + "\n\n"
            for embed_ in msg_to_parse.embeds:
                text += "**Embed title:** " + str(embed_.title) + "\n"
                text += "**Embed color:** " + str(embed_.color) + "\n"
                text += "**Embed footer:** " + str(embed_.footer) + "\n"
                text += "**Embed author:** " + str(embed_.author) + "\n"
                text += "**Embed description:** " + str(embed_.description) + "\n\n\n"
        emb.description = text
        await ctx.send(embed=emb)

    @commands.command(pass_context=True, hidden=True)
    @commands.is_owner()
    async def leaveguild(self, ctx, *, guild_id_str: str = "placeholder999999lvl"):
        if guild_id_str == "placeholderLVL99999":
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\nBut you forgot to specify guild's id.", delete_after=35)
            await ctx.message.delete(delay=15)
            return
        try:
            guild = self.bot.get_guild(int(guild_id_str))
        except Exception:
            await ctx.send("I am sorry, " + self.bot.user_title(ctx.author.id) + "!\n"
                           + "But I couldn't find guild with given id.\n"
                           + "Please, make sure you wrote correct guild id as number.", delete_after=35)
            await ctx.message.delete(delay=15)
            return
        if guild:
            await guild.leave()
            await ctx.message.add_reaction('✅')
        await ctx.message.delete(delay=15)

    def scan_dir(self, path):
        count = 0
        code_lines = 0
        size = 0
        for f in os.listdir(path):
            if os.path.isfile(os.path.join(path, f)):
                count += 1
                size += os.path.getsize(os.path.join(path, f))
                if os.path.join(path, f).endswith(".py"):
                    # noinspection PyUnusedLocal
                    code_lines += sum(1 for line in open(file=os.path.join(path, f), mode='r', encoding="UTF-8"))
            elif os.path.join(path, f).count(".idea") == 0 and os.path.join(path, f).count("__pycache__") == 0:
                (c, c_l, s) = self.scan_dir(os.path.join(path, f))
                count += c
                code_lines += c_l
                size += s
        return count, code_lines, size


def setup(bot):
    bot.add_cog(BelfastUtils(bot))
