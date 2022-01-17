import asyncio
import discord
from discord.ext import commands, tasks
from datetime import datetime
from db import setup_db
from config import AFK_ID, FATE_ID, GAMES_ID, HUB_ID, TEAM_ASK_ID


class Caps_listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            if message.channel.id == TEAM_ASK_ID:
                await asyncio.sleep(3)
                await message.delete()
            return
        if message.channel.id == TEAM_ASK_ID and not message.content.startswith(self.bot.command_prefix):
            await message.delete()
        else:
            if message.content.isupper() and len(message.content) > 7:
                ctx = await self.bot.get_context(message)
                ctx.author = self.bot.user
                cmd = self.bot.get_command("warn")
                await ctx.invoke(cmd, message.author, **{"reason": "Капс"})


class Spam_listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.author_msg_times = {}
        self.time_window_milliseconds = 4000
        self.max_msg_per_window = 5

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return
        author_id = message.author.id
        curr_time = datetime.now().timestamp() * 1000

        if not self.author_msg_times.get(author_id, False):
            self.author_msg_times[author_id] = []
        self.author_msg_times[author_id].append(curr_time)
        expr_time = curr_time - self.time_window_milliseconds

        for msg_time in self.author_msg_times[author_id]:
            if msg_time < expr_time:
                self.author_msg_times[author_id].remove(msg_time)
        if len(self.author_msg_times[author_id]) >= self.max_msg_per_window:
            ctx = await self.bot.get_context(message)
            ctx.author = self.bot.user
            cmd = self.bot.get_command("warn")
            await ctx.invoke(cmd, message.author, **{"reason": "Спам"})


class Join_listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.recent_new_users = []
        self.max_joins_per_window = 10
        self.new_users_update.start()

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if (member.bot):
            return
        if member.id not in self.recent_new_users:
            self.recent_new_users.append(member.id)

    @tasks.loop(seconds=3)
    async def new_users_update(self):
        if len(self.recent_new_users) >= self.max_joins_per_window:
            for user_id in self.recent_new_users:
                await self.bot.get_guild(FATE_ID).ban(user=self.bot.get_user(user_id), delete_message_days=7, reason="Рейд")
            self.recent_new_users = []


class Text_channels_listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_chatters = []
        self.chatters_update.start()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            return
        if message.author.id not in self.last_chatters:
            self.last_chatters.append(message.author.id)

    @tasks.loop(minutes=1)
    async def chatters_update(self):
        members = self.bot.get_guild(FATE_ID).members
        db = setup_db([x.id for x in members])
        for chatter_id in self.last_chatters:
            db.update_text_rating_user(chatter_id)
        self.last_chatters = []
        db.disconnect()


class Voice_channels_listener(commands.Cog):
    def __init__(self, bot, voicers):
        self.bot = bot
        self.last_voicers = voicers
        self.created_channels = []
        self.voicers_update.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if after.channel is not None and after.channel.category.id != AFK_ID:
            if member.id not in self.last_voicers:
                self.last_voicers.append(member.id)
        if after.channel is None or after.channel.id == AFK_ID:
            if member.id in self.last_voicers:
                self.last_voicers.remove(member.id)

        if before.channel is not None and len(before.channel.members) == 0 and before.channel.id in self.created_channels:
            self.created_channels.remove(before.channel.id)
            await before.channel.delete()

        if after.channel is not None and after.channel.name == "Create room":
            if member.nick is not None:
                new_name = member.nick
            else:
                new_name = member.name
            channel = await after.channel.guild.create_voice_channel(name=new_name, category=after.channel.category)
            self.created_channels.append(channel.id)
            await member.move_to(channel)
            await channel.set_permissions(member, manage_channels=True)

    @tasks.loop(minutes=2)
    async def voicers_update(self):
        members = self.bot.get_guild(FATE_ID).members
        db = setup_db([x.id for x in members])
        for voicer_id in self.last_voicers:
            db.update_voice_rating_user(voicer_id)
        db.disconnect()


async def setup_listeners(bot):
    bot.add_cog(Caps_listener(bot))
    bot.add_cog(Spam_listener(bot))
    bot.add_cog(Join_listener(bot))


async def setup_rating_listeners(bot):
    guild = bot.get_guild(FATE_ID)
    voicers = []
    for channel in guild.voice_channels:
        for member in channel.members:
            voicers.append(member.id)
    bot.add_cog(Text_channels_listener(bot))
    bot.add_cog(Voice_channels_listener(bot, voicers))


async def setup_voice(bot):
    guild = bot.get_guild(FATE_ID)
    hub = discord.utils.get(guild.categories, id=HUB_ID)
    game = discord.utils.get(guild.categories, id=GAMES_ID)
    hub_flag = True
    game_flag = True
    for channel in guild.voice_channels:
        if channel.name == "Create room":
            if channel.category == hub:
                hub_flag = False
            elif channel.category == game:
                game_flag = False
    if hub_flag:
        await guild.create_voice_channel(name="Create room", category=hub)
    if game_flag:
        await guild.create_voice_channel(name="Create room", category=game)
