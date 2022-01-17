import math
import discord
from discord.ext import commands
import re
import asyncio
import pymorphy2
from datetime import datetime
from discord.ext.commands.core import has_permissions
from discord.ext.commands.errors import CheckFailure
from db import setup_db


def get_permissions_embed(ctx: commands.Context):
    title_error = ":x: | Вам не хватает прав"
    permissions_error = "Вам нужны следующие права:\n> Администратор"

    permissions_error_embed = discord.Embed(
        title=title_error, description=permissions_error, color=discord.Color.red())
    permissions_error_embed.set_footer(
        icon_url=ctx.author.avatar_url, text=str(ctx.author))
    return permissions_error_embed


def get_error_embed(ctx: commands.Context):
    embed = discord.Embed(title=":x: | Что-то пошло не так",
                          description="> Похоже, что возникла ошибка!", color=discord.Color.red())
    embed.set_footer(icon_url=ctx.author.avatar_url, text=str(ctx.author))
    return embed

# ------------------------------------------------------------------------------------------------------------------


def parse_time(time: str):
    days = 0
    hours = 0
    minutes = 0
    seconds = 0
    if bool(re.match("(\d+)d$", time)):
        days = int(time.split('d')[0])
    elif bool(re.match("(\d+)h$", time)):
        hours = int(time.split('h')[0])
    elif bool(re.match("(\d+)m$", time)):
        minutes = int(time.split('m')[0])
    elif bool(re.match("(\d+)s$", time)):
        seconds = int(time.split('s')[0])

    elif bool(re.match("(\d+)d(\d+)h$", time)):
        time = time.split('d')
        days = int(time[0])
        hours = int(time[1].split('h')[0])
    elif bool(re.match("(\d+)d(\d+)m$", time)):
        time = time.split('d')
        days = int(time[0])
        minutes = int(time[1].split('m')[0])
    elif bool(re.match("(\d+)d(\d+)s$", time)):
        time = time.split('d')
        days = int(time[0])
        seconds = int(time[1].split('s')[0])
    elif bool(re.match("(\d+)h(\d+)m$", time)):
        time = time.split('h')
        hours = int(time[0])
        minutes = int(time[1].split('m')[0])
    elif bool(re.match("(\d+)h(\d+)s$", time)):
        time = time.split('h')
        hours = int(time[0])
        seconds = int(time[1].split('s')[0])
    elif bool(re.match("(\d+)m(\d+)s$", time)):
        time = time.split('m')
        minutes = int(time[0])
        seconds = int(time[1].split('s')[0])

    elif bool(re.match("(\d+)d(\d+)h(\d+)m$", time)):
        time = time.split('d')
        days = int(time[0])
        time = time[1].split('h')
        hours = int(time[0])
        minutes = int(time[1].split('m')[0])
    elif bool(re.match("(\d+)d(\d+)h(\d+)s$", time)):
        time = time.split('d')
        days = int(time[0])
        time = time[1].split('h')
        hours = int(time[0])
        seconds = int(time[1].split('s')[0])
    elif bool(re.match("(\d+)h(\d+)m(\d+)s$", time)):
        time = time.split('h')
        hours = int(time[0])
        time = time[1].split('m')
        minutes = int(time[0])
        seconds = int(time[1].split('s')[0])

    elif bool(re.match("(\d+)d(\d+)h(\d+)m(\d+)s$", time)):
        time = time.split('d')
        days = int(time[0])
        time = time[1].split('h')
        hours = int(time[0])
        time = time[1].split('m')
        minutes = int(time[0])
        seconds = int(time[1].split('s')[0])

    return 24*60*60*days + 60*60*hours + 60*minutes + seconds


def get_word(word: str, num: int):
    morph = pymorphy2.MorphAnalyzer()
    word = morph.parse(word)[0]
    return word.make_agree_with_number(num).word


def parse_time_for_embed(timer: int):
    parsed = ""
    days = int(timer / (24*60*60))
    timer %= (24*60*60)
    hours = int(timer / (60*60))
    timer %= (60*60)
    minutes = int(timer / 60)
    timer %= 60
    seconds = int(timer)
    flag = 0
    if days > 0:
        parsed += f"{days} " + str(get_word("день", days))
        flag = 1
    if hours > 0:
        if flag == 1:
            parsed += ", "
        parsed += f"{hours} " + str(get_word("час", hours))
        flag = 1
    if minutes > 0:
        if flag == 1:
            parsed += ", "
        parsed += f"{minutes} " + str(get_word("минута", minutes))
        flag = 1
    if seconds > 0:
        if flag == 1:
            parsed += ", "
        parsed += f"{seconds} " + str(get_word("секунда", seconds))
    return parsed

# ------------------------------------------------------------------------------------------------------------------


class Mute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_mute_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!mute`"
        help_description = "> Забирает у участника права отправлять сообщения в большинстве каналов"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Шаблон", value=f"> `!mute Участник Длительность(по желанию) Причина(по желанию)`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!mute @Tom 1h Спам`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_mute_time_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        time_error = "Аргумент **mute** должен обозначать период времени(как минимум 1 секунду) в формате `0d0h0m0s`\n\
            `d` - дни, `h` - часы, `m` - минуты, `s` - секунды\n \
            Например, 1h30m значит 1 час и 30 минут."

        time_error_embed = discord.Embed(
            title=title_error, description=time_error, color=discord.Color.red())
        time_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return time_error_embed

    def get_mute_embed(ctx: commands.Context, member: discord.Member, reason: str, timer: int = None):
        if timer is None:
            description = "**Длительность:** Неопределённый срок\n"
            description += f"**Модератор:** {str(ctx.author)}\n"
            description += f"**Причина:** {reason}"
        else:
            description = f"**Длительность:** {parse_time_for_embed(timer)}\n"
            description += f"**Модератор:** {str(ctx.author)}\n"
            description += f"**Причина:** {reason}"
        embed = discord.Embed(
            title=f":lock: | {str(member)} был замьючен", description=description, color=discord.Color.from_rgb(143, 0, 19))
        return embed

    @commands.command()
    @has_permissions(administrator=True)
    async def mute(self, ctx: commands.Context, member: discord.Member = None, time: str = None, *, reason="Без причины"):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not mute_role:
            mute_role = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(mute_role, speak=True, send_messages=False, read_message_history=True, read_messages=True)
        db = setup_db([x.id for x in ctx.guild.members])
        if member is None:
            bot_answer = await ctx.send(embed=Mute.get_mute_help_embed(ctx))
            if ctx.message.content.startswith("!mute"):
                await asyncio.sleep(5)
                await ctx.message.delete()
            await asyncio.sleep(60)
            await bot_answer.delete()
        elif time is None:
            await member.add_roles(mute_role)
            db.mute_user(member.id, datetime.now().strftime(
                "%H:%M, %d.%m.%y"), "Неопределённый срок")
            await ctx.send(embed=Mute.get_mute_embed(ctx, member, reason))
            if ctx.message.content.startswith("!mute"):
                await asyncio.sleep(5)
                await ctx.message.delete()
        else:
            timer = parse_time(time)
            if timer is None or timer <= 0:
                bot_answer = await ctx.send(embed=Mute.get_mute_time_error_embed(ctx))
                if ctx.message.content.startswith("!mute"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
                await asyncio.sleep(5)
                await bot_answer.delete()
            else:
                await member.add_roles(mute_role)
                db.mute_user(member.id, datetime.now().strftime(
                    "%H:%M, %d.%m.%y"), parse_time_for_embed(timer))
                await ctx.send(embed=Mute.get_mute_embed(ctx, member, reason, timer))
                if ctx.message.content.startswith("!mute"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
                await asyncio.sleep(timer)
                await member.remove_roles(mute_role)
                db.unmute_user(member.id)
                await ctx.send(embed=Unmute.get_unmute_embed(ctx, member))

    @mute.error
    async def mute_error(self, ctx: commands.Context, error):
        if isinstance(error, CheckFailure):
            bot_answer = await ctx.send(embed=get_permissions_embed(ctx))
        else:
            bot_answer = await ctx.send(embed=get_error_embed(ctx))
        if ctx.message.content.startswith("!mute"):
            await asyncio.sleep(5)
            await ctx.message.delete()
        await asyncio.sleep(5)
        await bot_answer.delete()

# ------------------------------------------------------------------------------------------------------------------


class Unmute(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_unmute_embed(ctx: commands.Context, member: discord.Member):
        description = f"**Модератор:** {str(ctx.author)}"
        embed = discord.Embed(
            title=f":unlock: | {str(member)} был размьючен", description=description, color=discord.Color.green())
        return embed

    def get_unmute_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!unmute`"
        help_description = "> Возвращает участнику права отправлять сообщения в большинстве каналов"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Шаблон", value=f"> `!unmute Участник`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!unmute @Tom`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_unmute_no_role_embed(ctx: commands.Context, member: discord.Member):
        description = f"**Модератор:** {str(ctx.author)}"
        embed = discord.Embed(
            title=f":unlock: | {str(member)} не был замьючен", description=description, color=discord.Color.green())
        return embed

    @commands.command()
    @has_permissions(administrator=True)
    async def unmute(self, ctx: commands.Context, member: discord.Member = None):
        mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not member:
            bot_answer = await ctx.send(embed=Unmute.get_unmute_help_embed(ctx))
            await asyncio.sleep(60)
            await bot_answer.delete()
            if ctx.message.content.startswith("!unmute"):
                await asyncio.sleep(5)
                await ctx.message.delete()
        else:
            if not mute_role or mute_role not in member.roles:
                bot_answer = await ctx.send(embed=Unmute.get_unmute_no_role_embed(ctx, member))
                await asyncio.sleep(5)
                await bot_answer.delete()
                if ctx.message.content.startswith("!unmute"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
            else:
                db = setup_db([x.id for x in ctx.guild.members])
                await member.remove_roles(mute_role)
                db.unmute_user(member.id)
                await ctx.send(embed=Unmute.get_unmute_embed(ctx, member))
                if ctx.message.content.startswith("!unmute"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()

    @unmute.error
    async def unmute_error(self, ctx: commands.Context, error):
        if isinstance(error, CheckFailure):
            bot_answer = await ctx.send(embed=get_permissions_embed(ctx))
        else:
            bot_answer = await ctx.send(embed=get_error_embed(ctx))
        if ctx.message.content.startswith("!unmute"):
            await asyncio.sleep(5)
            await ctx.message.delete()
        await asyncio.sleep(5)
        await bot_answer.delete()

# ------------------------------------------------------------------------------------------------------------------


class Ban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_ban_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!ban`"
        help_description = "> Банит участника на сервере"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Шаблон", value=f"> `!ban Участник Длительность(по желанию) Причина(по желанию)`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!ban @Tom 1h Спам`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_ban_time_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        time_error = "Аргумент **ban** должен обозначать период времени(как минимум 1 секунду) в формате `0d0h0m0s`\n\
            `d` - дни, `h` - часы, `m` - минуты, `s` - секунды\n \
            Например, 1h30m значит 1 час и 30 минут."

        time_error_embed = discord.Embed(
            title=title_error, description=time_error, color=discord.Color.red())
        time_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return time_error_embed

    def get_ban_self_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        user_error = "Нельзя забанить себя"

        user_error_embed = discord.Embed(
            title=title_error, description=user_error, color=discord.Color.red())
        user_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return user_error_embed

    def get_ban_embed(ctx: commands.Context, member: discord.Member, reason: str, timer: int = None):
        if timer is None:
            description = "**Длительность:** Неопределённый срок\n"
            description += f"**Модератор:** {str(ctx.author)}\n"
            description += f"**Причина:** {reason}"
        else:
            description = f"**Длительность:** {parse_time_for_embed(timer)}\n"
            description += f"**Модератор:** {str(ctx.author)}\n"
            description += f"**Причина:** {reason}"
        embed = discord.Embed(
            title=f":no_entry: | {str(member)} был забанен", description=description, color=discord.Color.from_rgb(143, 0, 19))
        return embed

    @commands.command()
    @has_permissions(administrator=True)
    async def ban(self, ctx: commands.Context, member: discord.Member = None, time: str = None, *, reason="Без причины"):
        if member is None:
            bot_answer = await ctx.send(embed=Ban.get_ban_help_embed(ctx))
            if ctx.message.content.startswith("!ban"):
                await asyncio.sleep(5)
                await ctx.message.delete()
            await asyncio.sleep(60)
            await bot_answer.delete()
        elif ctx.author.id == member.id:
            bot_answer = await ctx.send(embed=Ban.get_ban_self_error_embed(ctx))
            if ctx.message.content.startswith("!ban"):
                await asyncio.sleep(5)
                await ctx.message.delete()
            await asyncio.sleep(5)
            await bot_answer.delete()
        elif time is None:
            await ctx.guild.ban(user=member, delete_message_days=0, reason=reason)
            await ctx.send(embed=Ban.get_ban_embed(ctx, member, reason))
            if ctx.message.content.startswith("!ban"):
                await asyncio.sleep(5)
                await ctx.message.delete()
        else:
            timer = parse_time(time)
            if timer is None or timer <= 0:
                bot_answer = await ctx.send(embed=Ban.get_ban_time_error_embed(ctx))
                if ctx.message.content.startswith("!ban"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
                await asyncio.sleep(5)
                await bot_answer.delete()
            else:
                await ctx.guild.ban(user=member, delete_message_days=0, reason=reason)
                await ctx.send(embed=Ban.get_ban_embed(ctx, member, reason, timer))
                if ctx.message.content.startswith("!ban"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
                await asyncio.sleep(timer)
                await ctx.guild.unban(user=member)
                await ctx.send(embed=Unban.get_unban_embed(ctx, member))

    @ban.error
    async def ban_error(self, ctx: commands.Context, error):
        if isinstance(error, CheckFailure):
            bot_answer = await ctx.send(embed=get_permissions_embed(ctx))
        else:
            bot_answer = await ctx.send(embed=get_error_embed(ctx))
        if ctx.message.content.startswith("!ban"):
            await asyncio.sleep(5)
            await ctx.message.delete()
        await asyncio.sleep(5)
        await bot_answer.delete()

# ------------------------------------------------------------------------------------------------------------------


class Unban(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_unban_embed(ctx: commands.Context, member: discord.Member):
        description = f"**Модератор:** {str(ctx.author)}"
        embed = discord.Embed(
            title=f":shield: | {str(member)} был разбанен", description=description, color=discord.Color.green())
        return embed

    def get_unban_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!unban`"
        help_description = "> Разбанивает участника на сервере"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Шаблон", value=f"> `!unban Участник`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!unban Tom#1234`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_unban_user_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        user_error = "Аргумент **unban** должен обозначать пользователя Discord в формате `Name#1234` или ID пользователя\nНапример, `Tom#3024`"

        user_error_embed = discord.Embed(
            title=title_error, description=user_error, color=discord.Color.red())
        user_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return user_error_embed

    def get_unban_unknown_user_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        user_error = "Указанный пользователь никогда не был на сервере"

        user_error_embed = discord.Embed(
            title=title_error, description=user_error, color=discord.Color.red())
        user_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return user_error_embed

    def get_unban_no_ban_embed(ctx: commands.Context, member: discord.Member):
        description = f"**Модератор:** {str(ctx.author)}"
        embed = discord.Embed(
            title=f":shield: | {str(member)} не был забанен", description=description, color=discord.Color.green())
        return embed

    @commands.command()
    @has_permissions(administrator=True)
    async def unban(self, ctx: commands.Context, *, member: str = None):
        if member is None:
            bot_answer = await ctx.send(embed=Unban.get_unban_help_embed(ctx))
            if ctx.message.content.startswith("!unban"):
                await asyncio.sleep(5)
                await ctx.message.delete()
            await asyncio.sleep(60)
            await bot_answer.delete()
        else:
            banned_users = await ctx.guild.bans()
            if "#" in member:
                member_name = member.split("#")
                if len(member_name) != 2 or len(member_name[1]) != 4:
                    bot_answer = await ctx.send(embed=Unban.get_unban_user_error_embed(ctx))
                    if ctx.message.content.startswith("!unban"):
                        await asyncio.sleep(5)
                        await ctx.message.delete()
                    await asyncio.sleep(5)
                    await bot_answer.delete()
                else:
                    banned = False
                    for ban_entry in banned_users:
                        user = ban_entry.user
                        if (user.name, user.discriminator) == (member_name[0], member_name[1]):
                            banned = True
                            await ctx.guild.unban(user)
                            await ctx.send(embed=Unban.get_unban_embed(ctx, user))
                            if ctx.message.content.startswith("!unban"):
                                await asyncio.sleep(5)
                                await ctx.message.delete()
                    if banned == False:
                        if (member_name[0], member_name[1]) in [(x.name, x.discriminator) for x in ctx.guild.members]:
                            bot_answer = await ctx.send(embed=Unban.get_unban_no_ban_embed(ctx, member))
                        else:
                            bot_answer = await ctx.send(embed=Unban.get_unban_unknown_user_embed(ctx))
                        if ctx.message.content.startswith("!unban"):
                            await asyncio.sleep(5)
                            await ctx.message.delete()
                        await asyncio.sleep(5)
                        await bot_answer.delete()
            else:
                try:
                    user_id = int(member)
                    banned = False
                    for ban_entry in banned_users:
                        user = ban_entry.user
                        if user.id == user_id:
                            banned = True
                            await ctx.guild.unban(user)
                            await ctx.send(embed=Unban.get_unban_embed(ctx, user))
                            if ctx.message.content.startswith("!unban"):
                                await asyncio.sleep(5)
                                await ctx.message.delete()
                    if banned == False:
                        if user_id in [x.id for x in ctx.guild.members]:
                            bot_answer = await ctx.send(embed=Unban.get_unban_no_ban_embed(ctx, member))
                        else:
                            bot_answer = await ctx.send(embed=Unban.get_unban_unknown_user_embed(ctx))
                        if ctx.message.content.startswith("!unban"):
                            await asyncio.sleep(5)
                            await ctx.message.delete()
                        await asyncio.sleep(5)
                        await bot_answer.delete()
                except:
                    bot_answer = await ctx.send(embed=Unban.get_unban_user_error_embed(ctx))
                    if ctx.message.content.startswith("!unban"):
                        await asyncio.sleep(5)
                        await ctx.message.delete()
                    await asyncio.sleep(5)
                    await bot_answer.delete()

    @unban.error
    async def unban_error(self, ctx: commands.Context, error):
        if isinstance(error, CheckFailure):
            bot_answer = await ctx.send(embed=get_permissions_embed(ctx))
        else:
            bot_answer = await ctx.send(embed=get_error_embed(ctx))
        if ctx.message.content.startswith("!unban"):
            await asyncio.sleep(5)
            await ctx.message.delete()
        await asyncio.sleep(5)
        await bot_answer.delete()

# ------------------------------------------------------------------------------------------------------------------


class Warn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_warn_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!warn`"
        help_description = "> Кидает участнику предупреждение"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Наказания", value=f"> Второе предупреждение - `mute`\n> Четвёртое предупреждение - `ban`", inline=False)
        help_embed.add_field(
            name="Шаблон", value=f"> `!warn Участник Причина(по желанию)`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!warn @Tom Спам`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_warn_embed(ctx: commands.Context, member: discord.Member, warns, reason: str):
        description = f"**Текущие предупреждения:** {warns}\n"
        description += f"**Модератор:** {str(ctx.author)}\n"
        description += f"**Причина:** {reason}"
        embed = discord.Embed(
            title=f":warning: | {str(member)} получил предупреждение", description=description, color=discord.Color.from_rgb(143, 0, 19))
        return embed

    @commands.command()
    @has_permissions(administrator=True)
    async def warn(self, ctx: commands.Context, member: discord.Member = None, *, reason: str = "Без причины"):
        if member is None:
            bot_answer = await ctx.send(embed=Warn.get_warn_help_embed(ctx))
            if ctx.message.content.startswith("!warn"):
                await asyncio.sleep(5)
                await ctx.message.delete()
            await asyncio.sleep(60)
            await bot_answer.delete()
        else:
            db = setup_db([x.id for x in ctx.guild.members])
            warns = db.warn_user(member.id)
            await ctx.send(embed=Warn.get_warn_embed(ctx, member, warns, reason))
            if warns == 2:
                ctx.author = self.bot.user
                cmd = self.bot.get_command("mute")
                await ctx.invoke(cmd, member, None, **{"reason": "Второе предупреждение"})
            elif warns == 4:
                ctx.author = self.bot.user
                cmd = self.bot.get_command("ban")
                await ctx.invoke(cmd, member, None, **{"reason": "Четвёртое предупреждение"})
            if ctx.message.content.startswith("!warn"):
                await asyncio.sleep(5)
                await ctx.message.delete()
            db.disconnect()

    @warn.error
    async def warn_error(self, ctx: commands.Context, error):
        if isinstance(error, CheckFailure):
            bot_answer = await ctx.send(embed=get_permissions_embed(ctx))
        else:
            bot_answer = await ctx.send(embed=get_error_embed(ctx))
        if ctx.message.content.startswith("!warn"):
            await asyncio.sleep(5)
            await ctx.message.delete()
        await asyncio.sleep(5)
        await bot_answer.delete()

# ------------------------------------------------------------------------------------------------------------------


class Unwarn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_unwarn_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!unwarn`"
        help_description = "> Снимает с участника предупреждения"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Шаблон", value=f"> `!unwarn Участник Количество(по желанию)`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!unwarn @Tom 2`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_unwarn_num_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        num_error = "Аргумент **unwarn** должен обозначать количество предупреждений в числовом формате\n\
            Например, 2."
        num_error_embed = discord.Embed(
            title=title_error, description=num_error, color=discord.Color.red())
        num_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return num_error_embed

    def get_unwarn_embed(ctx: commands.Context, member: discord.Member, warns):
        if warns > 0:
            title = f":pushpin: | С {str(member)} сняты предупреждения"
            description = f"**Текущие предупреждения:** {warns}\n"
            description += f"**Модератор:** {str(ctx.author)}\n"
        else:
            title = f":pushpin: | С {str(member)} сняты все предупреждения"
            description = f"**Модератор:** {str(ctx.author)}\n"
        embed = discord.Embed(
            title=title, description=description, color=discord.Color.green())
        return embed

    @commands.command()
    @has_permissions(administrator=True)
    async def unwarn(self, ctx: commands.Context, member: discord.Member = None, num: str = "all"):
        if member is None:
            bot_answer = await ctx.send(embed=Unwarn.get_unwarn_help_embed(ctx))
            if ctx.message.content.startswith("!unwarn"):
                await asyncio.sleep(5)
                await ctx.message.delete()
            await asyncio.sleep(60)
            await bot_answer.delete()
        else:
            db = setup_db([x.id for x in ctx.guild.members])
            if not db.unwarn_user(member.id, num):
                bot_answer = await ctx.send(embed=Unwarn.get_unwarn_num_error_embed(ctx))
                if ctx.message.content.startswith("!unwarn"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
                await asyncio.sleep(5)
                await bot_answer.delete()
            else:
                warns = db.get_user_warns(member.id)
                await ctx.send(embed=Unwarn.get_unwarn_embed(ctx, member, warns))
                if ctx.message.content.startswith("!unwarn"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
            db.disconnect()

    @unwarn.error
    async def unwarn_error(self, ctx: commands.Context, error):
        if isinstance(error, CheckFailure):
            bot_answer = await ctx.send(embed=get_permissions_embed(ctx))
        else:
            bot_answer = await ctx.send(embed=get_error_embed(ctx))
        if ctx.message.content.startswith("!unwarn"):
            await asyncio.sleep(5)
            await ctx.message.delete()
        await asyncio.sleep(5)
        await bot_answer.delete()

# ------------------------------------------------------------------------------------------------------------------


class Sinners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_sinners_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!sinners`"
        help_description = "> Показывает список грешников"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Режимы", value=f"> Показать всех грешников - `all`\n> Показать 10 замьюченных пользователей - `mute`\n\
                > Показать 10 предупреждений - `warn`", inline=False)
        help_embed.add_field(
            name="Шаблон", value=f"> `!sinners Режим Страница(по желанию)`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!sinners mute 2`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_sinners_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        num_error = "Аргумент **sinners** должен обозначать один из трёх режимов:\n\
            `all` - показать всех грешников\n\
            `mute` - показать замьюченных пользователей\n\
            `warn` - показать предупреждения"
        num_error_embed = discord.Embed(
            title=title_error, description=num_error, color=discord.Color.red())
        num_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return num_error_embed

    def get_muted_embed(ctx: commands.Context, mutes, pagenum):
        if len(mutes) == 0:
            embed = discord.Embed(
                title=f":pushpin: | На сервере никто не замьючен", color=discord.Color.green())
            embed.set_footer(icon_url=ctx.author.avatar_url,
                             text=str(ctx.author))
            return embed
        else:
            pages = math.ceil(len(mutes) / 10)
            description = ""
            for i in range(min(10, len(mutes) - (pagenum - 1) * 10)):
                description += f"> **{ctx.bot.get_user(mutes[i + (pagenum - 1) * 10]['id']).mention}:** \
                    `{mutes[i + (pagenum - 1) * 10]['date']}` на `{mutes[i + (pagenum - 1) * 10]['timer']}`\n"
            embed = discord.Embed(title=f":pushpin: | Список замьюченных пользователей",
                                  description=description, color=discord.Color.blue())
            return embed

    def get_warned_embed(ctx: commands.Context, warns, pagenum):
        if len(warns) == 0:
            embed = discord.Embed(
                title=f":pushpin: | На сервере ни у кого нет предупреждений", color=discord.Color.green())
            embed.set_footer(icon_url=ctx.author.avatar_url,
                             text=str(ctx.author))
            return embed
        else:
            pages = math.ceil(len(warns) / 10)
            description = ""
            for i in range(min(10, len(warns) - (pagenum - 1) * 10)):
                description += f"> **{ctx.bot.get_user(warns[i + (pagenum - 1) * 10]['id']).mention}:** `{warns[i + (pagenum - 1) * 10]['warns']}`\n"
            embed = discord.Embed(title=f":pushpin: | Список предупреждений [{pagenum}/{pages}]",
                                  description=description, color=discord.Color.blue())
            return embed

    def get_sinners_embed(ctx: commands.Context, mutes, warns):
        embed = discord.Embed(title=f":pushpin: | Список грешников",
                              color=discord.Color.blue())
        if len(mutes) == 0:
            embed.add_field(name="Замьюченные пользователи",
                            value="> Никто не замьючен", inline=False)
        else:
            muted = ""
            for mute in mutes:
                muted += f"> **{ctx.bot.get_user(mute['id']).mention}:** `{mute['date']}` на `{mute['timer']}`\n"
            embed.add_field(name="Замьюченные пользователи",
                            value=muted, inline=True)
        if len(warns) == 0:
            embed.add_field(name="Предупреждения",
                            value="> Ни у кого нет предупреждений", inline=False)
        else:
            warned = ""
            for warn in warns:
                warned += f"> **{ctx.bot.get_user(warn['id']).mention}:** `{warn['warns']}`\n"
            embed.add_field(name="Предупреждения", value=warned, inline=True)
        return embed

    @commands.command()
    async def sinners(self, ctx: commands.Context, arg: str = None, pagenum: int = 1):
        if arg is None:
            bot_answer = await ctx.send(embed=Sinners.get_sinners_help_embed(ctx))
            if ctx.message.content.startswith("!sinners"):
                await asyncio.sleep(5)
                await ctx.message.delete()
            await asyncio.sleep(60)
            await bot_answer.delete()
        else:
            db = setup_db([x.id for x in ctx.guild.members])
            warns = db.get_warns()
            mutes = db.get_mutes()
            if arg.lower() == "all":
                await ctx.send(embed=Sinners.get_sinners_embed(ctx, mutes[:5], warns[:5]))
                if ctx.message.content.startswith("!sinners"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
            elif arg.lower() == "mute":
                await ctx.send(embed=Sinners.get_muted_embed(ctx, mutes, pagenum))
                if ctx.message.content.startswith("!sinners"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
            elif arg.lower() == "warn":
                await ctx.send(embed=Sinners.get_warned_embed(ctx, warns, pagenum))
                if ctx.message.content.startswith("!sinners"):
                    await asyncio.sleep(5)
                    await ctx.message.delete()
            else:
                bot_answer = await ctx.send(embed=Sinners.get_sinners_error_embed(ctx))
                await ctx.message.delete()
                await asyncio.sleep(5)
                await bot_answer.delete()

# ------------------------------------------------------------------------------------------------------------------


class Points(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_points_help_embed(ctx: commands.Context):
        help_title = ":books: | О команде `!set_points`"
        help_description = "> Устанавливает новое значение очков пользователя"

        help_embed = discord.Embed(
            title=help_title, description=help_description, color=discord.Color.from_rgb(106, 118, 238))
        help_embed.add_field(
            name="Режимы", value=f"> Изменить очки в чате - `text`\n> Изменить очки в войсе - `voice`", inline=False)
        help_embed.add_field(
            name="Шаблон", value=f"> `!set_points Режим Участник Очки`", inline=False)
        help_embed.add_field(
            name="Пример", value=f"> `!set_points text @Tom 100`", inline=False)
        help_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return help_embed

    def get_points_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        mode_error = "Аргумент **set_points** должен обозначать один из двух режимов:\n\
            `text` - изменить очки в чате\n\
            `voice` - изменить очки в войсе"
        mode_error_embed = discord.Embed(
            title=title_error, description=mode_error, color=discord.Color.red())
        mode_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return mode_error_embed

    def get_points_member_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        mode_error = "Аргумент **set_points** должен обозначать участника сервера\n\
            Например, `@Tom`"
        mode_error_embed = discord.Embed(
            title=title_error, description=mode_error, color=discord.Color.red())
        mode_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return mode_error_embed

    def get_points_points_error_embed(ctx: commands.Context):
        title_error = ":x: | Неточность"
        mode_error = "Аргумент **set_points** должен обозначать количество очков\n\
            Например, `100`"
        mode_error_embed = discord.Embed(
            title=title_error, description=mode_error, color=discord.Color.red())
        mode_error_embed.set_footer(
            icon_url=ctx.author.avatar_url, text=str(ctx.author))
        return mode_error_embed

    def get_points_embed(ctx: commands.Context, mode: str, member: discord.Member, points: int):
        title = f":rocket: | Обновление очков для {str(member)}"
        description = f"> **Модератор:** `{ctx.author}`\n"
        description += f"> **Режим:** `{mode}`\n"
        description += f"> **Очки:** `{points}`"
        embed = discord.Embed(
            title=title, description=description, color=discord.Color.from_rgb(239, 165, 55))
        return embed

    @commands.command()
    @has_permissions(administrator=True)
    async def set_points(self, ctx: commands.Context, mode: str = None, member: discord.Member = None, points: int = None):
        if mode is None:
            bot_answer = await ctx.send(embed=Points.get_points_help_embed(ctx))
            await asyncio.sleep(60)
            await bot_answer.delete()
        elif member is None:
            bot_answer = await ctx.send(embed=Points.get_points_member_error_embed(ctx))
            await asyncio.sleep(5)
            await bot_answer.delete()
        elif points is None:
            bot_answer = await ctx.send(embed=Points.get_points_points_error_embed(ctx))
            await asyncio.sleep(5)
            await bot_answer.delete()
        elif mode != "text" and mode != "voice":
            bot_answer = await ctx.send(embed=Points.get_points_error_embed(ctx))
            await asyncio.sleep(5)
            await bot_answer.delete()
        else:
            db = setup_db([x.id for x in ctx.guild.members])
            if mode == "text":
                db.set_text_rating(member.id, points)
            else:
                db.set_voice_rating(member.id, points)
            await ctx.send(embed=Points.get_points_embed(ctx, mode, member, points))
        await ctx.message.delete()

# ------------------------------------------------------------------------------------------------------------------


def setup_moderation_commands(bot):
    bot.add_cog(Mute(bot))
    bot.add_cog(Unmute(bot))
    bot.add_cog(Ban(bot))
    bot.add_cog(Unban(bot))
    bot.add_cog(Warn(bot))
    bot.add_cog(Unwarn(bot))
    bot.add_cog(Sinners(bot))
    bot.add_cog(Points(bot))
