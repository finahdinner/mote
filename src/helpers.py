from discord.ext import commands
import discord
import re
import requests
import os
import re
from PIL import Image, ImageSequence
from io import BytesIO
from src.globals import (
    IMAGES_PATH,
    MAX_EMOTE_SIZE_BYTES,
    BASE_API_URL
)


""" Logging """

from src.logs import MyLogger, ExecutionOutcome
from src.globals import LOG_FILE_PATH
my_logger = MyLogger(file_name="bot", log_file_path=LOG_FILE_PATH)


""" Discord context and messages """

class Emote:
    def __init__(self, name: str, _7v_id: str, dl_url: str, format: str, animated: bool):
        self.name = name
        self._7v_id = _7v_id
        self.dl_url = dl_url
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

    async def send_msg(self, message, exec_outcome=ExecutionOutcome.DEFAULT, add_loading_icon: bool = False) -> None:
        msg = emojify_str(message, exec_outcome, add_loading_icon)
        self.curr_message = await self.ctx.send(msg)
        my_logger.log_message(self.ctx, message, exec_outcome)

    async def edit_msg(self, message: str, exec_outcome=ExecutionOutcome.DEFAULT, add_loading_icon: bool = False) -> None:
        if not self.curr_message:
            return
        msg = emojify_str(message, exec_outcome, add_loading_icon)
        await self.curr_message.edit(content=msg)
        my_logger.log_message(self.ctx, message, exec_outcome)

    async def reply_to_user(self, message, exec_outcome=ExecutionOutcome.DEFAULT, ping: bool = False, add_loading_icon: bool = False) -> None:
        msg = emojify_str(message, exec_outcome, add_loading_icon)
        await self.ctx.reply(msg, mention_author=ping)
        my_logger.log_message(self.ctx, message, exec_outcome)

    async def upload_emoji_to_server(self, emote_name: str, image_path: str) -> tuple[str, int]:
        """
        returns (error_text, error_code)
        err_code of 0 is no error. err_code of -1 is an unspecified error.
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
            return err_message, err_code
        return "", 0          
    

def emojify_str(msg, exec_outcome: ExecutionOutcome, add_loading_icon: bool = False):
    """
    Given a specified exec_outcome, pre-pend an appropriate emoji (check mark or cross)
    """
    if add_loading_icon:
        return f":hourglass_flowing_sand: {msg}"

    match exec_outcome.name:
        case "ERROR":
            emoji_str = ":x:"
        case "WARNING":
            emoji_str = ":warning:"
        case "SUCCESS":
            emoji_str = ":white_check_mark:"
        case _:
            emoji_str = ""
    return f"{emoji_str} {msg}"
    

def get_discord_err_info(err_message: str) -> tuple[str, int]:
    """ Returns: (err_message, error_code) """
    res = re.search(r"\(error code:\s(\d+)\):", err_message)
    if not res:
        return err_message, 0
    return err_message, int(res.group(1))


""" Image retrieval and processing """

def is_valid_7tv_url(url: str) -> bool:
    results = re.search(r"^(https://|http://)7tv.app/emotes/([\w]+)$", url)
    return bool(results)


def get_7tv_api_url(command_url: str) -> str:
    emote_id = command_url.split("/")[-1]
    return BASE_API_URL + emote_id


def retrieve_7tv_image_info(api_url: str, suggested_emote_name=None) -> tuple[Emote|None, str]:
    response = requests.get(api_url)
    if response.status_code != 200:
        return None, "Could not load URL."
    data = response.json()

    _7v_id = data["id"]
    emote_name = suggested_emote_name if suggested_emote_name else data["name"]
    is_animated = data["animated"]
    emote_format = "gif" if data["animated"] else "png"

    emote_versions = data["host"]["files"]
    valid_emote_version = None
    for version in emote_versions:
        if version.get("format") == "WEBP" and "1x" in version.get("name"):
            valid_emote_version = version
            break
    
    if not valid_emote_version:
        return None, "Could not find a suitable image version to download."

    image_size_and_format = valid_emote_version["name"].replace("webp", emote_format)
    dl_url = f"{data['host']['url']}/{image_size_and_format}"
    if not dl_url.startswith("https:"):
        dl_url = "https:" + dl_url

    emote = Emote(
        name=emote_name,
        _7v_id=_7v_id,
        dl_url=dl_url,
        animated=is_animated,
        format=emote_format
    )
    return emote, ""


def download_7tv_image(img_url: str, format: str) -> tuple[str, str]:
    response = requests.get(img_url)
    if response.status_code != 200:
        return "", "Unable to download image."
    img_path = os.path.join(IMAGES_PATH, f"download.{format.lower()}") # eg download.gif
    with open(img_path, "wb") as img:
        img.write(response.content)
    return img_path, ""


def download_discord_img(img_url: str) -> tuple[str, int, str]:
    """ returns: (image_path, image_size, error) """
    
    # including a user-agent in case some websites require it
    response = requests.get(img_url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36'
    })
    if response.status_code != 200:
        return "", 0, f"Unable to download image (status code {response.status_code})."
    img = Image.open(BytesIO(response.content))
    if not img.format:
        return "", 0, "Error while processing the image format."
    downloaded_path = os.path.join(IMAGES_PATH, f"download.{img.format.lower()}")
    img.save(downloaded_path, save_all=True)
    try:
        img_file_size = os.path.getsize(downloaded_path)
    except OSError:
        return "", 0, "Error while analysing the image size."
    return downloaded_path, img_file_size, ""


def is_animated(filepath: str) -> bool:
    media = Image.open(filepath)
    idx = 0
    for _ in ImageSequence.Iterator(media):
        idx += 1
    return idx > 1 # true if more than one frame


def resize_img(img_path: str) -> tuple[str, str]:
    optimal_dimensions = get_optimal_frame_size(img_path)
    if is_animated(img_path): # ie an animated gif
        img = Image.open(img_path)
        resized_frames = []
        for idx in range(img.n_frames):
            img.seek(idx)
            resized_frame = img.resize(optimal_dimensions)
            resized_frames.append(resized_frame)
        try:
            resized_frames[0].save(img_path, save_all=True, append_images=resized_frames[1:], loop=0, optimize=True)
        except Exception as e:
            return "", f"Unable to resize image: {e}"
    else: # not animated
        try:
            img = Image.open(img_path)
            img.thumbnail(optimal_dimensions, Image.Resampling.LANCZOS)
            img.save(img_path, optimize=True)
        except Exception as e:
            return "", f"Unable to resize image: {e}"
    return img_path, ""
   

def get_optimal_frame_size(img_path: str) -> tuple[int, int]:
    img = Image.open(img_path)
    width, height = img.size
    # set the smaller dimension to 32, and scale the larger dimension from there
    if width > height:
        new_height = 32
        new_width = 32 * (width / height)
    else: # height >= width
        new_width = 32
        new_height = 32 * (height / width)
    return int(new_width), int(new_height)


def convert_discord_img(img_path: str, img_size: int) -> tuple[str, str]:
    if img_size > MAX_EMOTE_SIZE_BYTES:
        img_path, error = resize_img(img_path)
        if error:
            return "", error
    return img_path, ""