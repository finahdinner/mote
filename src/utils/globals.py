from dotenv import load_dotenv
import os
from pathlib import Path

""" Env variables """
load_dotenv()
DEBUG_MODE = os.environ.get("DEBUG_MODE", "False")
BOT_TOKEN = os.environ["DISCORD_MOTE_BOT_TOKEN"]
BOT_TEST_TOKEN = os.environ["BOT_TEST_TOKEN"]
_CHROMEDRIVER_PATH = os.environ["_CHROMEDRIVER_PATH"]

""" Absolute file paths """
ENV_PY_PATH = Path(__file__)
SRC_DIR_PATH = ENV_PY_PATH.parent.parent
PROJECT_ROOT_PATH = SRC_DIR_PATH.parent
COGS_PATH = os.path.join(SRC_DIR_PATH, "cogs")
IMAGES_PATH = os.path.join(SRC_DIR_PATH, "images")

""" Bot """
BOT_PREFIX = "mote/"
DISCORD_INVITE_LINK = os.environ["DISCORD_INVITE_LINK"]

""" 7TV-Specific """
_7TV_URL_REGEX = r"^(https://|http://)7tv.app/emotes/([\w]+)$"
LARGE_IMAGE_XPATH = r'//*[@id="app"]/main/main/main/section/div[4]'
EMOTE_URL_REGEX = r"^(https://|http://)cdn.7tv.app/emote/([\w]+)/(\d)x\.webp$"