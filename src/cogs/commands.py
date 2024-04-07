from discord.ext import commands
import asyncio
import re
from src.logs import ExecutionOutcome
from src.globals import BOT_INVITE_LINK, BOT_PREFIX
from src.helpers import (
    DiscordCtx,
    is_valid_7tv_url,
    get_7tv_api_url,
    retrieve_7tv_image_info,
    download_7tv_image,
    download_discord_img,
    convert_discord_img,
    resize_img
)


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help="Grab an emote from 7TV and upload to the server.", usage=f"{BOT_PREFIX}grab <7tv_url> [emote_name]")
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
        
        await contxt.send_msg("Working on it...", add_loading_icon=True)

        api_url = get_7tv_api_url(page_url)
        emote, err = retrieve_7tv_image_info(api_url, emote_name)
        if not emote:
            return await(contxt.edit_msg(err, ExecutionOutcome.ERROR))
        
        await contxt.edit_msg(f"Downloading `{emote.name}`...", add_loading_icon=True)

        if not emote.dl_urls: # failsafe
            return await(contxt.edit_msg("No valid download URLs found.", ExecutionOutcome.ERROR))

        # try to download from urls/upload to the server until one works
        num_attempts = len(emote.dl_urls)
        for attempt_num, url in enumerate(emote.dl_urls, 1):
            img_path, err = download_7tv_image(url, emote.format)
            if not img_path:
                # assume that the rest of the urls won't be downloadable either
                return await(contxt.edit_msg(err, ExecutionOutcome.ERROR))
            err_text, err_code = await contxt.upload_emoji_to_server(emote.name, img_path)
            if not err_text: # successful upload
                break
            elif err_code == 50138: # if image too large to upload
                if attempt_num < num_attempts:
                    await contxt.edit_msg(f"Trying to upload a new size... ({attempt_num}/{num_attempts-1})", add_loading_icon=True)
                else: # if the final attempt fails, try to manually resize
                    await contxt.edit_msg("Trying to manually resize...", add_loading_icon=True)
                    img_path, resize_err = resize_img(img_path)
                    if resize_err:
                        return await(contxt.edit_msg(resize_err, ExecutionOutcome.ERROR))
                    err_text, err_code = await contxt.upload_emoji_to_server(emote.name, img_path)
                    if err_code:
                        return await(contxt.edit_msg(err_text, ExecutionOutcome.ERROR))
            else: # any other error
                return await(contxt.edit_msg(err_text, ExecutionOutcome.ERROR))

        return await contxt.edit_msg(f"Success! `{emote.name}` uploaded!", ExecutionOutcome.SUCCESS)


    @commands.command(help="Retrieve an image from a link/attachment, and upload to the server.", usage=f"{BOT_PREFIX}upload <link/attachment> <emote_name>")
    async def upload(self, ctx, *args) -> None:        
        # if uploading an attachment: args = [emote_name]
        # if providing an image link: args = [image_url, emote_name]

        contxt = DiscordCtx(ctx)
        if not contxt.has_emoji_perms:
            return await contxt.reply_to_user("You do not have sufficient permissions to use this command.", ExecutionOutcome.WARNING)
        if not args:
            return await contxt.reply_to_user(f"Usage: `{BOT_PREFIX}upload <link/attachment> <emote_name>`", ExecutionOutcome.WARNING)

        if contxt.attachments:
            img_url = contxt.attachments[0].url
            emote_name = args[0]
        else:
            await asyncio.sleep(0.2) # hacky way to wait for the embed to load
            if ctx.message.embeds:
                if len(args) < 2: # args = [emote_name, image_link]
                    return await contxt.reply_to_user(f"Usage: `{BOT_PREFIX}upload <link/attachment> <emote_name>`", ExecutionOutcome.WARNING)
                emote_name = args[1]
                for embed in ctx.message.embeds:
                    if embed.type == "image":
                        img_url = embed.url
                        break
                else:
                    return await contxt.reply_to_user("An image could not be found from the URL provided.", ExecutionOutcome.WARNING)
            else:
                return await contxt.reply_to_user("You must attach an image or provide a link to an image.", ExecutionOutcome.WARNING)
                
        if not emote_name.replace("_","").isalnum() or len(emote_name) < 2 or len(emote_name) > 32: # only alphanums or underscores allowed in names
            return await contxt.reply_to_user("Emote name must be between 2 and 32 alphanumeric characters long.", ExecutionOutcome.WARNING)

        await contxt.send_msg("Working on it...", add_loading_icon=True)

        img_path, img_size, error = download_discord_img(img_url)
        if error:
            return await contxt.edit_msg(error, ExecutionOutcome.ERROR)
        resized_img_path, error = convert_discord_img(img_path, img_size)
        if error:
            return await contxt.edit_msg(error, ExecutionOutcome.ERROR)
        err_text, _ = await contxt.upload_emoji_to_server(emote_name, resized_img_path)
        if err_text:
            return await contxt.edit_msg(err_text, ExecutionOutcome.ERROR)
        return await contxt.edit_msg(f"Success! `{emote_name}` uploaded!", ExecutionOutcome.SUCCESS)

    @commands.command(
        help="'Steal' an emote from a discord message, by *replying* to it with the name of the emote.",
        usage=f"{BOT_PREFIX}steal <selected_emote> [*new_name]"
    )
    async def steal(self, ctx, selected_emote: str = "", given_emote_name: str = "") -> None:
        contxt = DiscordCtx(ctx)
        if not contxt.has_emoji_perms:
            return await contxt.reply_to_user("You do not have sufficient permissions to use this command.", ExecutionOutcome.WARNING)
        if not selected_emote:
            return await contxt.reply_to_user(f"Usage: `{BOT_PREFIX}steal <selected_emote> [*new_name]`", ExecutionOutcome.WARNING)
        
        # to remove extra chars in case they copy and pasted an emote directly
        selected_emote_pattern = re.compile(rf"<*(a)*:(\w+):(\d+)>*", re.IGNORECASE)
        selected_emote_results = re.search(selected_emote_pattern, selected_emote)
        if selected_emote_results:
            selected_emote = selected_emote_results.group(2)

        replied_message = await contxt.get_replied_message()
        if not replied_message:
            return await contxt.reply_to_user("You must reply to a message to yoink an emote from it.", ExecutionOutcome.WARNING)
        
        if given_emote_name:
            if not given_emote_name.startswith("*"):
                return await contxt.reply_to_user(f"Try doing `{BOT_PREFIX}steal {selected_emote} *{given_emote_name}`", ExecutionOutcome.WARNING)
            new_emote_name = given_emote_name.replace("*", "") # replace colons too, in case the user copy pasted them
            if not new_emote_name.replace("_","").isalnum() or len(new_emote_name) < 2 or len(new_emote_name) > 32: # only alphanums or underscores allowed in names
                return await contxt.reply_to_user("New emote name must be between 2 and 32 alphanumeric characters long.", ExecutionOutcome.WARNING)
        
        await contxt.send_msg("Working on it...", add_loading_icon=True)

        img_url, og_emote_name = await contxt.get_emote_info_from_message(replied_message, selected_emote)
        if not img_url:
            return await contxt.edit_msg(f"No emote called {selected_emote} could be found in that message.", ExecutionOutcome.WARNING)
        
        emote_name = og_emote_name if not given_emote_name else new_emote_name
        img_path, img_size, error = download_discord_img(img_url)
        if error:
            return await contxt.edit_msg(error, ExecutionOutcome.ERROR)
        resized_img_path, error = convert_discord_img(img_path, img_size)
        if error:
            return await contxt.edit_msg(error, ExecutionOutcome.ERROR)
        err_text, _ = await contxt.upload_emoji_to_server(emote_name, resized_img_path)
        if err_text:
            return await contxt.edit_msg(err_text, ExecutionOutcome.ERROR)
        return await contxt.edit_msg(f"Success! `{emote_name}` uploaded!", ExecutionOutcome.SUCCESS)

    @commands.command(help="Get the invite link for the bot.", usage=f"{BOT_PREFIX}invite")
    async def invite(self, ctx) -> None:
        """ mote/grab  """
        await ctx.reply(f"Bot invite link:\n{BOT_INVITE_LINK}")


async def setup(bot):
    await bot.add_cog(Commands(bot))