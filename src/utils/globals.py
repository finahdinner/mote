"""
Accesses all required environment variables from the .env file
Also creates absolute paths for all important directories and folders
"""

from dotenv import load_dotenv
import os
from pathlib import Path

""" Env variables """
load_dotenv()
DEBUG = os.environ.get("DEBUG", "False")
BOT_TOKEN = os.environ["DISCORD_MOTE_BOT_TOKEN"]
BOT_TEST_TOKEN = os.environ["BOT_TEST_TOKEN"]

""" Absolute file paths """
ENV_PY_PATH = Path(__file__)
SRC_DIR_PATH = ENV_PY_PATH.parent.parent
PROJECT_ROOT_PATH = SRC_DIR_PATH.parent
COGS_PATH = os.path.join(SRC_DIR_PATH, "cogs")

""" Bot """
BOT_PREFIX = "mote/"
DISCORD_INVITE_LINK = os.environ["DISCORD_INVITE_LINK"]