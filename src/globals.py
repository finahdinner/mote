from dotenv import load_dotenv
import os
from pathlib import Path

""" Env variables """
load_dotenv()
DEBUG_MODE = os.environ.get("DEBUG_MODE", "False")
BOT_TOKEN = os.environ["DISCORD_MOTE_BOT_TOKEN"]
BOT_TEST_TOKEN = os.environ["BOT_TEST_TOKEN"]

""" Absolute file paths """
env_py_path = Path(__file__)
src_dir_path = env_py_path.parent
COGS_PATH = os.path.join(src_dir_path, "cogs")
IMAGES_PATH = os.path.join(src_dir_path, "images")

""" Bot """
BOT_PREFIX = "mote/"
BOT_INVITE_LINK = os.environ["BOT_INVITE_LINK"]

""" Discord """
MAX_EMOTE_SIZE_BYTES = 262144
MAX_EMOTE_SIZE_DIMENSIONS = (256, 256)

""" Logging """
log_dir_path = os.path.join(src_dir_path, "logs")
LOG_FILE_PATH = os.path.join(log_dir_path, "bot.log")

""" 7TV """
BASE_API_URL = "https://7tv.io/v3/emotes/"