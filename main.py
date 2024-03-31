import asyncio
from discord import Intents
from discord.ext import commands
from src.globals import (
    DEBUG_MODE,
    BOT_TOKEN,
    BOT_TEST_TOKEN,
    BOT_PREFIX,
    COGS_PATH
)
import sys
import os
import textwrap


class MyHelpCommand(commands.DefaultHelpCommand):
    def __init__(self):
        super().__init__()

    async def send_bot_help(self, mapping) -> None:
        help_msg = "List of commands:\n\n"
        for cog in mapping:
            for command in mapping[cog]:
                help_msg += f"`{command.name}` - {command.help}\n"
        help_msg += "\nUse `mote/help <command_name>` to see how to use a specific command."
        await self.get_destination().send(help_msg)
    
    async def send_command_help(self, command) -> None:
        if command.name == "help":
            help_msg = f"Use `{BOT_PREFIX}help` to show all commands."
        else:
            help_msg = textwrap.dedent(f"""
                {command.help}
                Usage: `{command.usage}`
                (`<>` = *required* parameters, `[]` = *optional* parameters)
            """)
        await self.get_destination().send(help_msg)


class MyBot(commands.Bot):
    def __init__(self, command_prefix, description, intents, help_command):
        super().__init__(
            command_prefix=command_prefix,
            description=description,
            intents=intents,
            help_command=help_command,
            case_insensitive=True
        )

    async def on_ready(self):
        print(f"Logged in as {self.user}.")

    async def load_cogs(self):
        sys.path.insert(0, COGS_PATH)
        for file in os.listdir(COGS_PATH):
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
    token = BOT_TOKEN if DEBUG_MODE == "False" else BOT_TEST_TOKEN
    prefixes = [BOT_PREFIX, BOT_PREFIX.title()] # both lowercase and title case are options
    bot = MyBot(
        command_prefix=commands.when_mentioned_or(*prefixes),
        description="Mote Bot",
        intents=Intents.all(),
        help_command=MyHelpCommand()
    )
    await bot.start(token)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())