import asyncio
from discord import Intents
from discord.ext import commands
from src.utils.globals import (
    DEBUG,
    BOT_TOKEN,
    BOT_TEST_TOKEN,
    BOT_PREFIX,
    COGS_PATH
)
import sys
import os


class MyBot(commands.Bot):
    def __init__(self, command_prefix, description, intents):
        super().__init__(
            command_prefix=command_prefix,
            description=description,
            intents=intents,
            case_insensitive=True,
            help_command=None
        )

    async def on_ready(self):
        print(f"Logged in as {self.user}.")

    async def load_cogs(self):

        for dir_path in COGS_PATH:
            sys.path.insert(0, dir_path)
            for file in os.listdir(dir_path):
                if file.endswith(".py"):
                    extension_name = file[:-3]
                    try:
                        await self.load_extension(extension_name)
                    except commands.ExtensionError as e:
                        sys.exit(f"Error loading extension: {e}")
                    except Exception as f:
                        sys.exit(str(f))
                    else:
                        print(f"{self.description}: {extension_name} loaded")
            sys.path.pop(0)

    async def setup_hook(self):
        """ Runs when the bot first starts up """
        await self.load_cogs()


async def main():
    token = BOT_TOKEN if DEBUG == "False" else BOT_TEST_TOKEN
    prefixes = [BOT_PREFIX, BOT_PREFIX.title()] # both lowercase and title case are options
    bot = MyBot(
        command_prefix=commands.when_mentioned_or(*prefixes),
        description="Mote Bot",
        intents=Intents.all()
    )
    await bot.start(token)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())