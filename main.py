from discord.ext import commands
from discord.flags import Intents
from config import TOKEN
import logging
# from add_roles import setup_roles
from help_command import setup_help_command
from members import setup_statistics
from moderation_utils import setup_moderation_commands
from listeners import setup_listeners, setup_rating_listeners, setup_voice
from leaderboard import setup_leaderboard
from teammates import setup_find_teammates
from always_online import setup_antisleep_task

bot = commands.Bot(command_prefix="!",
                   intents=Intents.all(), help_command=None)


@bot.event
async def on_ready():
    await setup_voice(bot)
    await setup_listeners(bot)
    await setup_rating_listeners(bot)
    await setup_antisleep_task(bot)
    await setup_statistics(bot)
    # await setup_roles(bot)


def main():
    logger = logging.getLogger("discord")
    logger.setLevel(logging.INFO)  # Do not allow DEBUG messages through
    handler = logging.FileHandler(
        filename="bot.log", encoding="utf-8", mode="w")
    handler.setFormatter(logging.Formatter(
        "{asctime}: {levelname}: {name}: {message}", style="{"))
    logger.addHandler(handler)

    setup_moderation_commands(bot)
    setup_help_command(bot)
    setup_leaderboard(bot)
    setup_find_teammates(bot)


if __name__ == '__main__':
    main()
    while True:
        try:
            bot.run(TOKEN, reconnect=True)
        except Exception as e:
            print(e.with_traceback(type(e.__traceback__)))
