from discord.ext import commands
import discord
from enum import Enum


class ExecutionOutcome(Enum):
    ERROR = 2
    WARNING = 1
    DEFAULT = 0
    SUCCESS = -1


class DiscordCtx:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.has_emoji_perms = self.ctx.message.author.guild_permissions.manage_emojis
        self.bot_message = None # this will be updated to whatever the bot eventually sends

    async def send_msg(self, message) -> None:
        self.curr_message = await self.ctx.send(message)

    async def edit_msg(self, message: str, exec_outcome=ExecutionOutcome.DEFAULT) -> None:
        if not self.curr_message:
            return
        reply_msg = DiscordCtx.emojify_str(message, exec_outcome)
        await self.curr_message.edit(content=reply_msg)

    async def reply_to_user(self, message, ping=False) -> None:
        await self.ctx.reply(message. mention_author==ping)
        print("hello?")

    async def upload_emoji_to_server(self, emote_name: str, image_path: str) -> str|list:
        print(image_path)
        """ returns (is_uploaded: bool, ) """
        if not self.has_emoji_perms:
            return "You do not have sufficient permissions to use this command."
        if not self.ctx.guild:
            return "Guild somehow not found??? Internal server error!!"
        try:
            with open(image_path, "rb") as img:
                image = img.read()
            await self.ctx.guild.create_custom_emoji(name=emote_name, image=image)
        except discord.errors.HTTPException as e:
            if 'error code: 30008' in e.args[0]: # if max number of emojis reached
                return "Maximum number of emojis reached."
            elif 'error code: 50138' in e.args[0]: # if image too big, return the list
                return e.args[0]
            else:
                return "Unknown HTTP error - unable to upload emoji to Discord."
        return ""

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