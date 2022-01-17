import discord
from discord.ext import commands, tasks
from config import FATE_ID, ONLINE_ID, STAT_ID, VOICE_ID


class Statistics(commands.Cog):
    def __init__(self, bot, stat, online, voice):
        self.bot = bot
        self.guild = bot.get_guild(FATE_ID)
        self.stat = stat
        self.online = online
        self.voice = voice
        self.update_channel_name.start()

    @tasks.loop(seconds=30)
    async def update_channel_name(self):
        members = len([x for x in self.guild.members if not x.bot])
        online = len(
            [x for x in self.guild.members if x.status != discord.Status.offline and not x.bot])
        voice = 0
        for x in self.guild.voice_channels:
            voice += len(x.members)
        await self.stat.edit(name=f"Участников: {members}")
        await self.online.edit(name=f"Онлайн: {online}")
        await self.voice.edit(name=f"Голосовой онлайн: {voice}")


async def setup_statistics(bot):
    guild = bot.get_guild(FATE_ID)
    stat = discord.utils.get(guild.channels, id=STAT_ID)
    online = discord.utils.get(guild.channels, id=ONLINE_ID)
    voice = discord.utils.get(guild.channels, id=VOICE_ID)
    bot.add_cog(Statistics(bot, stat, online, voice))
