from discord.ext import commands
import textwrap
from src.logs import ExecutionOutcome
from src.globals import BOT_INVITE_LINK, BOT_PREFIX
from src.helpers import (
    DiscordCtx,
    is_valid_7tv_url,
    get_api_url,
    retrieve_image_info,
    download_7tv_image,
    download_discord_img,
    convert_discord_img,
    resize_img
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
        
        await contxt.send_msg("Working on it...", add_loading_icon=True)

        api_url = get_api_url(page_url)
        emote, err = retrieve_image_info(api_url, emote_name)
        if not emote:
            return await(contxt.edit_msg(err, ExecutionOutcome.ERROR))
        
        await contxt.edit_msg(f"Downloading `{emote.name}`...", add_loading_icon=True)
        
        img_path, err = download_7tv_image(emote.dl_url, emote.format)
        if err:
            return await(contxt.edit_msg(err, ExecutionOutcome.ERROR))
        err_text, err_code = await contxt.upload_emoji_to_server(emote.name, img_path)
        if err_code == 50138: # if image too large to upload
            await contxt.edit_msg("Trying to resize image...", add_loading_icon=True)
            img_path, resize_err = resize_img(img_path)
            if resize_err:
                return await(contxt.edit_msg(resize_err, ExecutionOutcome.ERROR))
            err_text2, err_code2 = await contxt.upload_emoji_to_server(emote.name, img_path)
            if err_text2:
                return await(contxt.edit_msg(err_text2, ExecutionOutcome.ERROR))
        elif err_text: # any other error
            return await(contxt.edit_msg(err_text, ExecutionOutcome.ERROR))
        return await contxt.edit_msg(f"Success! `{emote.name}` uploaded!", ExecutionOutcome.SUCCESS)

    @commands.command()
    async def upload(self, ctx, emote_name: str = "") -> None:
        contxt = DiscordCtx(ctx)
        if not contxt.attachments:
            return await contxt.reply_to_user(f"You must attach an image to upload (embedded image links won't work).", ExecutionOutcome.WARNING)
        if not emote_name:
            return await contxt.reply_to_user(f"You must provide an emote name.", ExecutionOutcome.WARNING)
        if not emote_name.replace("_","").isalnum() or len(emote_name) < 2 or len(emote_name) > 32: # only alphanums or underscores allowed in names
            return await contxt.reply_to_user("Emote name must be between 2 and 32 alphanumeric characters long.", ExecutionOutcome.WARNING)

        await contxt.send_msg("Working on it...", add_loading_icon=True)

        img_url = contxt.attachments[0].url
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

    @commands.command()
    async def convert(self, ctx, emote_name: str = "") -> None:
        """ Alias for mote/upload """
        await self.upload(ctx, emote_name)

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