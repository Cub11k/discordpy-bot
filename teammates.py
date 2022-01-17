import discord
import asyncio
from discord.ext import commands
from discord.ext.commands.errors import RoleNotFound
from config import TEAM_SEARCH_ID


class Find(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_find_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!find`"
        help_description = "> Отправляет в канал #team-search приглашение в пати"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Шаблон", value=f"> `!find Игра Количество тиммейтов Рейтинг(по желанию)`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!find @CS:GO 2 Gold Nova II`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_find_role_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        mode_error = "Аргумент **find** должен обозначать роль для поиска тиммейтов в игре:\n\
            Например, `@CS:GO` - поиск тиммейтов в CS:GO."
        mode_error_embed = discord.Embed(
            title=title_error, description=mode_error, color=discord.Color.red())
        mode_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return mode_error_embed

    def get_find_mates_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        mode_error = "Аргумент **find** должен обозначать количество тиммейтов для поиска:\n\
            Например, `2` - поиск двух тиммейтов."
        mode_error_embed = discord.Embed(
            title=title_error, description=mode_error, color=discord.Color.red())
        mode_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return mode_error_embed

    def get_find_no_voice_embed(ctx: commands.Context):
        title_error = ":x: | Ошибка"
        mode_error = "Чтобы начать поиск тиммейтов, вы должны находиться в голосовом канале"
        mode_error_embed = discord.Embed(
            title=title_error, description=mode_error, color=discord.Color.red())
        mode_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return mode_error_embed

    def get_find_embed(ctx: commands.Context, role: discord.Role, mates, rating):
        title = f":video_game: | Поиск тиммейтов в {role}"
        description = f"> **Свободные слоты:** `{mates}`\n"
        description += f"> **Рейтинг:** `{rating}`"
        embed = discord.Embed(
            title=title, description=description, color=discord.Color.from_rgb(230, 230, 0))
        embed.set_footer(icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return embed

    @commands.command()
    async def find(self, ctx: commands.Context, role: discord.Role = None, mates: int = None, *, rating: str = "Не указан"):
        if ctx.author.voice is None:
            bot_answer = await ctx.send(embed=Find.get_find_no_voice_embed(ctx))
            if ctx.message.content.startswith("!find"):
                await asyncio.sleep(5)
                await ctx.message.delete()
        else:
            if role is None:
                bot_answer = await ctx.send(embed=Find.get_find_help_embed(ctx))
                if ctx.message.content.startswith("!find"):
                    await ctx.message.delete()
            else:
                if mates is None:
                    bot_answer = await ctx.send(embed=Find.get_find_mates_error_embed(ctx))
                    if ctx.message.content.startswith("!find"):
                        await ctx.message.delete()
                else:
                    await ctx.author.voice.channel.edit(user_limit=len(
                        ctx.author.voice.channel.members) + mates)
                    invite = await ctx.author.voice.channel.create_invite()
                    await ctx.guild.get_channel(TEAM_SEARCH_ID).send(content=f"```NEW INVITE```\n{role.mention}\n{invite}",
                                                                     embed=Find.get_find_embed(ctx, role, mates, rating))
                    if ctx.message.content.startswith("!find"):
                        await ctx.message.delete()

    @find.error
    async def find_error(self, ctx: commands.Context, error):
        if isinstance(error, RoleNotFound):
            bot_answer = await ctx.send(embed=Find.get_find_role_error_embed(ctx))
            if ctx.message.content.startswith("!find"):
                await ctx.message.delete()


def setup_find_teammates(bot):
    bot.add_cog(Find(bot))
