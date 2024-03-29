from discord.ext import commands
import textwrap
from src.logs import ExecutionOutcome
from src.classes import DiscordCtx
from src.globals import BOT_INVITE_LINK, BOT_PREFIX
from src.helpers import (
    is_valid_7tv_url,
    get_api_url,
    retrieve_image_info,
    download_7tv_image
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
            return await(contxt.reply_to_user(err, ExecutionOutcome.ERROR))
        img_path, err = download_7tv_image(emote.url, emote.format)
        if not img_path:
            return await(contxt.reply_to_user(err, ExecutionOutcome.ERROR))
        upload_error = await contxt.upload_emoji_to_server(emote.name, img_path)
        if upload_error:
            return await contxt.edit_msg(upload_error, ExecutionOutcome.ERROR)
        
        return await contxt.edit_msg("Success! Emoji uploaded to Discord.", ExecutionOutcome.SUCCESS)

    @commands.command()
    async def upload(self, ctx, emote_name: str = "") -> None:
        contxt = DiscordCtx(ctx)

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