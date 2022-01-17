from discord.ext import commands, tasks
from config import TRASH_ID


class Antisleep(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_message.start()

    @tasks.loop(minutes=5)
    async def send_message(self):
        msg = await self.bot.get_channel(TRASH_ID).send("I'm online", delete_after=0.1)


async def setup_antisleep_task(bot):
    bot.add_cog(Antisleep(bot))
