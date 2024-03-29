from discord.ext import commands
import discord
from enum import Enum

""" Logging """
from src.logs import MyLogger, ExecutionOutcome
from pathlib import Path
from src.utils.globals import LOG_FILE_PATH
my_logger = MyLogger(file_name="bot", log_file_path=LOG_FILE_PATH)


class DiscordCtx:
    def __init__(self, ctx: commands.Context):
        self.ctx = ctx
        self.has_emoji_perms = self.ctx.message.author.guild_permissions.manage_emojis
        self.bot_message = None # this will be updated to whatever the bot eventually sends
        self.attachments = self.ctx.message.attachments

    async def send_msg(self, message, exec_outcome=ExecutionOutcome.DEFAULT) -> None:
        self.curr_message = await self.ctx.send(message)
        my_logger.log_message(self.ctx, message, exec_outcome) # log message

    async def edit_msg(self, message: str, exec_outcome=ExecutionOutcome.DEFAULT) -> None:
        if not self.curr_message:
            return
        msg = DiscordCtx.emojify_str(message, exec_outcome)
        await self.curr_message.edit(content=msg)
        my_logger.log_message(self.ctx, message, exec_outcome) # log message

    async def reply_to_user(self, message, exec_outcome=ExecutionOutcome.DEFAULT, ping=False) -> None:
        msg = DiscordCtx.emojify_str(message, exec_outcome)
        await self.ctx.reply(msg, mention_author=ping)
        my_logger.log_message(self.ctx, message, exec_outcome) # log message

    async def upload_emoji_to_server(self, emote_name: str, image_path: str) -> str|tuple:
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
                return e.args
            elif 'error code: 50045' in e.args[0]: # if image format is wrong
                return "Internal server error - wrong image format is being used (not your fault)."
            elif 'error code: 50035' in e.args[0]: # if provided name is too long
                return "Emote name must be between 2 and 32 characters long."
            else:
                return "Unknown HTTP error - unable to upload emoji to Discord."
        return ""

    @staticmethod
    def emojify_str(msg, exec_outcome: ExecutionOutcome):
        """
        Given a specified exec_outcome, pre-pend an appropriate emoji (check mark or cross)
        """
        match exec_outcome.name:
            case "ERROR":
                emoji_str = ":x: "
            case "WARNING":
                emoji_str = ":warning: "
            case "SUCCESS":
                emoji_str = ":white_check_mark: "
            case _:
                emoji_str = ""
        return emoji_str + msg