# Mote, a Discord bot

Mote is a Discord bot designed to help you with **uploading 7TV emotes** to your Discord server.<br>
It works with *7tv.app*, a website/browser extension acting as a database for emotes, which was designed for *twitch.tv*.<br>
The bot also allows you to upload emotes from attached images.

This is a more robust version of my [previous Discord bot of the same name](https://github.com/finahdinner/mote-old).

---

**Bot Usage:**

- `mote/grab <7tv_url> [emote_name]` -- Grab an emote from 7TV and upload to the server.
- `mote/upload <link/attachment> <emote_name>` -- Retrieve an image from a link/attachment, and upload to the server.
- `mote/steal <selected_emote> [*new_name]` -- 'Steal' an emote from a discord message, by replying to the message with the name of the emote.
- `mote/invite` -- Get the invite link for the bot.
- `mote/help [command_name]` -- provides usage information (of a command if specified).<br>

**The Bot requires the following Discord permissions:**
- Send Messages
- Manage Emojis and Stickers

*The user invoking bot commands must have "Manage Emojis and Stickers" permissions as well.*

**Creating your own bot instance**:

- Download a Chromedriver executable, compatible with your current Google Chrome version.
- Navigate to the root directory and create a python virtual environment with `python -m venv venv`
- Activate the environment using:
    - (Linux/MacOS) `source venv/bin/activate`
    - (Windows CMD) `.\venv\Scripts\activate` 
- Use the command `pip install -r requirements.txt`
- Create a **.env** file in the root directory, and inside it provide the following key-value pairs:
```
DEBUG_MODE="False"
DISCORD_MOTE_BOT_TOKEN=<TOKEN>
BOT_TEST_TOKEN=""
BOT_INVITE_LINK=<INVITE_LINK>
_CHROMEDRIVER_PATH=<FILEPATH>
```

Where `<TOKEN>` is the secret token for your bot, `<INVITE_LINK>` is the invite link for your bot, and `<FILEPATH>` is the absolute filepath to your *Chromedriver* executable.

- Inside the root directory, use `python main.py` to run the bot.
