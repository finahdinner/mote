from discord.ext import commands
import discord
import re

""" Logging """
from src.logs import MyLogger, ExecutionOutcome
from src.globals import LOG_FILE_PATH
my_logger = MyLogger(file_name="bot", log_file_path=LOG_FILE_PATH)


class Emote:
    def __init__(self, name: str, _7v_id: str, valid_dl_urls: list[str], format: str, animated: bool):
        self.name = name
        self._7v_id = _7v_id
        self.valid_dl_urls = valid_dl_urls
        self.format = format
        self.animated = animated

    def __str__(self):
        return f"Emote(name={self.name}, 7v_id={self._7v_id})"
    

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
        msg = emojify_str(message, exec_outcome)
        await self.curr_message.edit(content=msg)
        my_logger.log_message(self.ctx, message, exec_outcome) # log message

    async def reply_to_user(self, message, exec_outcome=ExecutionOutcome.DEFAULT, ping=False) -> None:
        msg = emojify_str(message, exec_outcome)
        await self.ctx.reply(msg, mention_author=ping)
        my_logger.log_message(self.ctx, message, exec_outcome) # log message

    async def upload_emoji_to_server(self, emote_name: str, image_path: str) -> tuple[str, int]:
        """
        returns (error_text, error_code)
        err_code of 0 is no error. err_code of -1 is unspecified error.
        """
        if not self.has_emoji_perms:
            return "You do not have sufficient permissions to use this command.", -1
        if not self.ctx.guild:
            return "Guild somehow not found??? Internal server error!!", -1
        try:
            with open(image_path, "rb") as img:
                image = img.read()
            await self.ctx.guild.create_custom_emoji(name=emote_name, image=image)
        except discord.errors.HTTPException as e:
            err_message, err_code = get_discord_err_info(e.args[0])
            my_logger.log_message(self.ctx, err_message, ExecutionOutcome.ERROR) # log message
            match err_code:
                case 30008:
                    err_message = "Maximum number of emojis reached."
                case 50138:
                    err_message = "Image too large and could not be uploaded to the server."
                case 50045:
                    err_message = "Format error during upload."
                case 50045:
                    err_message = "Emote name must be between 2 and 32 characters long.\nPlease provide a shorter name to override the 7TV name if not done so already."
                case _:
                    pass
            return err_message, err_code
        return "", 0          
    

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
    

def get_discord_err_info(err_message: str) -> tuple[str, int]:
    """ Returns: (err_message, error_code) """
    res = re.search(r"\(error code:\s(\d+)\):", err_message)
    if not res:
        return err_message, 0
    return err_message, int(res.group(1))