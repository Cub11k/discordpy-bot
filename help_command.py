import discord
import asyncio
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_moder_help_embed(ctx: commands.Context):
        moderation = "> `!mute`\n> `!unmute`\n> `!ban`\n> `!unban`\n> `!warn`\n> `!unwarn`\n> `!set_points`"
        embed = discord.Embed(title=":books: | Команды для модераторов",
                              description=moderation, color=discord.Color.from_rgb(106, 118, 238))
        embed.set_footer(icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return embed

    def get_help_embed(ctx: commands.Context):
        information = "> `!sinners`\n> `!top`\n> `!find`"
        embed = discord.Embed(title=":books: | Список команд",
                              description=information, color=discord.Color.from_rgb(106, 118, 238))
        embed.set_footer(icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return embed

    @commands.command()
    async def help(self, ctx: commands.Context, moder: str = None):
        if moder is None:
            bot_answer = await ctx.send(embed=Help.get_help_embed(ctx))
        else:
            bot_answer = await ctx.send(embed=Help.get_moder_help_embed(ctx))
        await ctx.message.delete()
        await asyncio.sleep(60)
        await bot_answer.delete()


def setup_help_command(bot):
    bot.add_cog(Help(bot))
