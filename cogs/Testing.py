import os

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

# import threading

dir_path = os.path.dirname(os.path.realpath(__file__)).replace("cogs", "")


class Testing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # self.MT_remind = asyncio.create_task(mt_reminder())

    def user(self, id: int):
        if id == self.bot.owner_id:
            return "Master"
        else:
            return "Commander"

    # testing

    @commands.command(pass_context=True, hidden=True)
    @has_permissions(manage_roles=True)
    @commands.guild_only()
    async def iam(self, ctx, *, role: str):
        CommanderRole = self.bot.get_guild(566171342953512963).get_role(569993566311415809)
        new_role = discord.utils.get(ctx.guild.roles, name=role)
        if ctx.guild == self.bot.TigersMeadow and new_role.id == 569993566311415809:
            await ctx.author.add_roles(new_role)
            await ctx.send("Done! :white_check_mark:")
            return
        if ctx.guild == self.bot.TigersMeadow and new_role.id == 570131573463318528 and CommanderRole in ctx.author.roles:
            await ctx.author.remove_roles(CommanderRole)
            await ctx.author.add_roles(new_role)
            await ctx.send("Done! :white_check_mark:")
            return
        try:
            if ctx.author.top_role > new_role:
                await ctx.author.add_roles(new_role)
                await ctx.send("Done! :white_check_mark:")
        except Exception:
            await ctx.send("Error! :no_entry:\nSomething went wrong or someone don't have permissions for that role.")


def setup(bot):
    bot.add_cog(Testing(bot))