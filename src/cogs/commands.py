from discord.ext import commands
import discord
from src.utils.globals import DISCORD_INVITE_LINK, BOT_PREFIX
from src.utils.helpers import DiscordCtx
import textwrap


class Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def invite(self, ctx):
        await ctx.reply(f"Bot invite link:\n{DISCORD_INVITE_LINK}")

    @commands.command()
    async def grab(self, ctx, page_url, emote_name):
        contxt = DiscordCtx(ctx)
        if not contxt.has_emoji_perms:
            return await contxt.reply_to_user("You do not have sufficient permissions to use this command.")
        if not page_url or not emote_name:
            return await contxt.reply_to_user(f"Usage: `{BOT_PREFIX}/grab <7tv_url> <emote_name>`")
        
        await contxt.send_msg("Extracting emoji info, bear with me...")

    @commands.command()
    async def upload(self, ctx, image_file: discord.Attachment, emote_name):
        contxt = DiscordCtx(ctx)
        if not contxt.has_emoji_perms:
            return await contxt.reply_to_user("You do not have sufficient permissions to use this command.")
        if not image_file:
            return await contxt.reply_to_user(f"You must attach an image to upload (embedded image links won't work).")
        if not emote_name:
            return await contxt.reply_to_user(f"Usage: `{BOT_PREFIX}/upload <emote_name>`")
        
        await contxt.send_msg("Extracting emoji info, bear with me...")


    @commands.command()
    async def convert(self, ctx):
        """ Alias for mote/upload """
        await self.upload(ctx)

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