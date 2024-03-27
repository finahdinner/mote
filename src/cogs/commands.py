from discord.ext import commands
import discord
import textwrap
from src.utils.globals import DISCORD_INVITE_LINK, BOT_PREFIX
from src.utils.helpers import DiscordCtx
from src.utils.download_img import get_image_url, download_webp, download_img_correct_format, is_animated


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        await ctx.reply(f"Bot invite link:\n{DISCORD_INVITE_LINK}")

    @commands.command()
    async def grab(self, ctx, page_url, emote_name=None):
        contxt = DiscordCtx(ctx)
        if not contxt.has_emoji_perms:
            return await contxt.reply_to_user("You do not have sufficient permissions to use this command.")
        if not page_url or not emote_name:
            return await contxt.reply_to_user(f"Usage: `{BOT_PREFIX}grab <7tv_url> <emote_name>`")
        
        await contxt.send_msg("Extracting emoji info, bear with me...")

        # retrieve webp url
        webp_url, err_message = get_image_url(page_url)
        if err_message:
            return await contxt.reply_to_user(err_message)
    
        # download webp image
        webp_img_path, err_message = download_webp(webp_url)
        if err_message:
            return await contxt.edit_msg(err_message)
        new_file_extension = "gif" if is_animated(webp_img_path) else "png"
        url = webp_url.replace(".webp", f".{new_file_extension}")

        # try to download the correct .png or .gif in each of the sizes (4x, 3x, 2x, 1x)
        # and try to upload each to Discord
        for size in range(4, 0, -1):
            final_img_path, err_message = download_img_correct_format(
                url=url,
                file_extension=new_file_extension,
                size=size
            )
            if err_message:
                return await contxt.reply_to_user(err_message)
            upload_error = await contxt.upload_emoji_to_server(emote_name, final_img_path)
            if not upload_error:
                return await contxt.edit_msg("Success! Emoji uploaded to Discord.")
            elif isinstance(upload_error, tuple): # image too large
                if size == 1:
                    return await contxt.edit_msg("All emoji sizes were too large to upload to Discord.")
                else: 
                    await contxt.edit_msg(f"Image too large, trying a smaller version. ({5-size})")
            else: # any upload_error other than the emoji being too big
                return await contxt.edit_msg(upload_error)
            
        return await contxt.edit_msg("Unable to upload emoji to Discord.")

    @commands.command()
    async def upload(self, ctx, image_file: discord.Attachment, emote_name):
        contxt = DiscordCtx(ctx)
        if not contxt.has_emoji_perms:
            return await contxt.reply_to_user("You do not have sufficient permissions to use this command.")
        if not image_file:
            return await contxt.reply_to_user(f"You must attach an image to upload (embedded image links won't work).")
        if not emote_name:
            return await contxt.reply_to_user(f"Usage: `{BOT_PREFIX}upload <emote_name>`")
        
        await contxt.send_msg("Extracting emoji info, bear with me...")

    @commands.command()
    async def convert(self, ctx, image_file: discord.Attachment, emote_name):
        """ Alias for mote/upload """
        await self.upload(ctx, image_file, emote_name)

    @commands.command()
    async def help(self, ctx):
        commands_msg = textwrap.dedent(f"""\
            `{BOT_PREFIX}grab <7tv_url> <emote_name>` --> Grab an emote from 7TV and upload to the server.
            `{BOT_PREFIX}upload <emote_name>` --> When provided with an uploaded image, will upload it to the server.
            `{BOT_PREFIX}convert <emote_name>` --> Same as {BOT_PREFIX}/convert.
            `{BOT_PREFIX}help` --> *commandception intensifies*
        """)
        await ctx.reply(commands_msg, mention_author=False)

    @commands.command()
    async def test(self, ctx):
        import time
        contxt = DiscordCtx(ctx)
        await contxt.send_msg("Test message")
        time.sleep(1)
        await contxt.edit_msg("Test edit")


async def setup(bot):
    await bot.add_cog(Commands(bot))