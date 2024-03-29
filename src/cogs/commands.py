from discord.ext import commands
import textwrap
from src.logs import ExecutionOutcome
from src.classes import DiscordCtx
from src.globals import BOT_INVITE_LINK, BOT_PREFIX
from src.helpers import (
    is_valid_7tv_url,
    get_api_url,
    retrieve_image_info,
    download_7tv_image,
    download_discord_img,
    convert_discord_img
)


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx) -> None:
        await ctx.reply(f"Bot invite link:\n{BOT_INVITE_LINK}")

    @commands.command()
    async def grab(self, ctx, page_url: str, emote_name: str|None = None) -> None:
        contxt = DiscordCtx(ctx)
        if not contxt.has_emoji_perms:
            return await contxt.reply_to_user("You do not have sufficient permissions to use this command.", ExecutionOutcome.WARNING)
        if not page_url:
            return await contxt.reply_to_user(f"Usage: `{BOT_PREFIX}grab <7tv_url> [emote_name]`")
        if emote_name is not None:
            if not emote_name.replace("_","").isalnum() or len(emote_name) < 2 or len(emote_name) > 32: # only alphanums or underscores allowed in names
                return await contxt.reply_to_user("Emote name must be between 2 and 32 alphanumeric characters long.", ExecutionOutcome.WARNING)
        if not is_valid_7tv_url(page_url):
            return await contxt.reply_to_user("Please provide a valid 7TV URL.", ExecutionOutcome.WARNING)

        await contxt.send_msg(f"Working on it{' (defaulting to 7TV name)' if emote_name is None else ''}...")

        api_url = get_api_url(page_url)
        emote, err = retrieve_image_info(api_url, emote_name)
        if not emote:
            return await(contxt.edit_msg(err, ExecutionOutcome.ERROR))        

        # try to download from urls/upload to the server until one works
        num_attempts = len(emote.valid_dl_urls)
        for attempt_num, url in enumerate(emote.valid_dl_urls, 1):
            img_path, err = download_7tv_image(url, emote.format)
            if not img_path:
                # assume that the rest of the urls won't be downloadable either
                return await(contxt.edit_msg(err, ExecutionOutcome.ERROR))
            err_text, err_code = await contxt.upload_emoji_to_server(emote.name, img_path)
            if err_code == 50138: # if image too large to upload
                if attempt_num == num_attempts: # if the final attempt produces an error
                    return await(contxt.edit_msg(err_text, ExecutionOutcome.ERROR))
                await contxt.edit_msg(f"Trying to upload a new size... ({attempt_num}/{num_attempts-1})")
                continue # try the next size
            elif err_text:
                return await(contxt.edit_msg(err_text, ExecutionOutcome.ERROR))
        
        return await contxt.edit_msg(f"Success! `{emote_name}` uploaded!", ExecutionOutcome.SUCCESS)

    @commands.command()
    async def upload(self, ctx, emote_name: str = "") -> None:
        contxt = DiscordCtx(ctx)
        if not contxt.attachments:
            return await contxt.reply_to_user(f"You must attach an image to upload (embedded image links won't work).", ExecutionOutcome.WARNING)
        if not emote_name:
            return await contxt.reply_to_user(f"You must provide an emote name.", ExecutionOutcome.WARNING)
        if not emote_name.replace("_","").isalnum() or len(emote_name) < 2 or len(emote_name) > 32: # only alphanums or underscores allowed in names
            return await contxt.reply_to_user("Emote name must be between 2 and 32 alphanumeric characters long.", ExecutionOutcome.WARNING)

        await contxt.send_msg("Working on it...")

        img_url = contxt.attachments[0].url
        img_path, img_size, error = download_discord_img(img_url)
        if error:
            return await contxt.edit_msg(error, ExecutionOutcome.ERROR)
        
        resized_img_path, error = convert_discord_img(img_path, img_size)
        if error:
            return await contxt.edit_msg(error, ExecutionOutcome.ERROR)
        upload_error = await contxt.upload_emoji_to_server(emote_name, resized_img_path)
        if not upload_error:
            return await contxt.edit_msg(f"Success! :{emote_name}: uploaded!", ExecutionOutcome.SUCCESS)
        elif isinstance(upload_error, tuple):
            return await contxt.edit_msg("An error occurred and your image was unable to be uploaded.", ExecutionOutcome.ERROR)
        else:
            return await contxt.edit_msg(upload_error, ExecutionOutcome.ERROR)

    @commands.command()
    async def convert(self, ctx, emote_name: str = "") -> None:
        contxt = DiscordCtx(ctx)

    @commands.command()
    async def help(self, ctx) -> None:
        commands_msg = textwrap.dedent(f"""\
            `{BOT_PREFIX}grab <7tv_url> [emote_name]` --> Grab an emote from 7TV and upload to the server.
            `{BOT_PREFIX}upload <emote_name>` --> When provided with an uploaded image, will upload it to the server.
            `{BOT_PREFIX}convert <emote_name>` --> Same as `{BOT_PREFIX}convert`.
            `{BOT_PREFIX}invite` --> Get the invite link for the bot.
            `{BOT_PREFIX}help` --> *commandception intensifies*
        """)
        await ctx.reply(commands_msg, mention_author=False)


async def setup(bot):
    await bot.add_cog(Commands(bot))