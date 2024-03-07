import discord
from discord.ext import commands
from enum import Enum


class ExecutionOutcome(Enum):
    ERROR = 2
    WARNING = 1
    DEFAULT = 0
    SUCCESS = -1


class DiscordCtx:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.bot_message = None # this will be updated to whatever the bot eventually sends

    async def send_msg(self, message) -> None:
        self.curr_message = await self.ctx.send(message)

    async def edit_msg(self, message: str, exec_outcome=ExecutionOutcome.DEFAULT) -> None:
        if not self.curr_message:
            return
        reply_msg = DiscordCtx.emojify_str(message, exec_outcome)
        await self.curr_message.edit(content=reply_msg)

    @staticmethod
    def emojify_str(msg, exec_outcome: ExecutionOutcome):
        """
        Given a specified exec_outcome, pre-pend an appropriate emoji (check mark or cross)
        """
        match exec_outcome.name:
            case "SUCCESS":
                emoji_str = ":white_check_mark: "
            case "ERROR" | "WARNING":
                emoji_str = ":x: "
            case _:
                emoji_str = ""
        return emoji_str + msg