import discord
import math
import asyncio
from discord.ext import commands
from db import setup_db


class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_top_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!top`"
        help_description = "> Показывает рейтинг пользователей"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Режимы", value=f"> Показать топ 5 в чате и в войсе - `all`\n> Показать топ 10 в чате - `text`\n\
                > Показать топ 10 в войсе - `voice`", inline=False)
        help_embed.add_field(
            name="Шаблон", value=f"> `!top Режим Страница(по желанию)`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!top text 2`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_top_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        mode_error = "Аргумент **top** должен обозначать один из трёх режимов:\n\
            `all` - показать топ 5 в чате и в войсе\n\
            `text` - показать топ 10 в чате\n\
            `voice` - показать топ 10 в войсе"
        mode_error_embed = discord.Embed(
            title=title_error, description=mode_error, color=discord.Color.red())
        mode_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return mode_error_embed

    def get_top_embed(ctx: commands.Context, text_rating, voice_rating):
        embed = discord.Embed(title=f":pushpin: | Рейтинг пользователей",
                              color=discord.Color.blue())
        text_rating = sorted(
            text_rating, key=lambda x: x["text_points"], reverse=True)[:5]
        text = ""
        for i in range(len(text_rating)):
            text += f"#{i + 1} | {ctx.bot.get_user(text_rating[i]['id']).mention}**XP:** `{text_rating[i]['text_points']}`\n"
        if len(text_rating) > 0:
            embed.add_field(name="ТОП 5 В ЧАТЕ :speech_balloon:",
                            value=text, inline=True)
        voice_rating = sorted(
            voice_rating, key=lambda x: x["voice_points"], reverse=True)[:5]
        text = ""
        for i in range(len(voice_rating)):
            text += f"#{i + 1} | {ctx.bot.get_user(voice_rating[i]['id']).mention}**XP:** `{voice_rating[i]['voice_points']}`\n"
        if len(voice_rating) > 0:
            embed.add_field(name="ТОП 5 В ВОЙСЕ :microphone2:",
                            value=text, inline=True)
        embed.set_footer(icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return embed

    def get_text_top_embed(ctx: commands.Context, text_rating, pagenum):
        text_rating = sorted(
            text_rating, key=lambda x: x["text_points"], reverse=True)
        pages = math.ceil(len(text_rating) / 10)
        text = ""
        for i in range(min(10, len(text_rating) - (pagenum - 1) * 10)):
            text += f"#{i + (pagenum - 1) * 10 + 1} | {ctx.bot.get_user(text_rating[i + (pagenum - 1) * 10]['id']).mention} \
                    **XP:** `{text_rating[i + (pagenum - 1) * 10]['text_points']}`\n"
        embed = discord.Embed(title=f":pushpin: | Рейтинг пользователей",
                              color=discord.Color.blue())
        if pagenum <= pages:
            embed.add_field(
                name=f":speech_balloon: ТОП В ЧАТЕ [{pagenum}/{pages}]", value=text, inline=False)
        embed.set_footer(icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return embed

    def get_voice_top_embed(ctx: commands.Context, voice_rating, pagenum):
        voice_rating = sorted(
            voice_rating, key=lambda x: x["voice_points"], reverse=True)
        pages = math.ceil(len(voice_rating) / 10)
        text = ""
        for i in range(min(10, len(voice_rating) - (pagenum - 1) * 10)):
            text += f"#{i + (pagenum - 1) * 10 + 1} | {ctx.bot.get_user(voice_rating[i + (pagenum - 1) * 10]['id']).mention} \
                    **XP:** `{voice_rating[i + (pagenum - 1) * 10]['voice_points']}`\n"
        embed = discord.Embed(title=f":pushpin: | Рейтинг пользователей",
                              color=discord.Color.blue())
        if pagenum <= pages:
            embed.add_field(
                name=f":microphone2: ТОП В ВОЙСЕ [{pagenum}/{pages}]", value=text, inline=False)
        embed.set_footer(icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return embed

    @commands.command()
    async def top(self, ctx: commands.Context, arg: str = None, pagenum: int = 1):
        if arg is None:
            await ctx.send(embed=Leaderboard.get_top_help_embed(ctx))
        else:
            db = setup_db([x.id for x in ctx.guild.members])
            text_rating = db.get_text_rating()
            voice_rating = db.get_voice_rating()
            if arg == "all":
                await ctx.send(embed=Leaderboard.get_top_embed(ctx, text_rating, voice_rating))
            elif arg == "text":
                await ctx.send(embed=Leaderboard.get_text_top_embed(ctx, text_rating, pagenum))
            elif arg == "voice":
                await ctx.send(embed=Leaderboard.get_voice_top_embed(ctx, voice_rating, pagenum))
            else:
                bot_answer = await ctx.send(embed=Leaderboard.get_top_error_embed(ctx))
                await asyncio.sleep(5)
                await bot_answer.delete()


def setup_leaderboard(bot):
    bot.add_cog(Leaderboard(bot))
