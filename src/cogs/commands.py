from discord.ext import commands
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
    async def grab(self, ctx):
        contxt = DiscordCtx(ctx)
        if not contxt.has_emoji_perms:
            return await contxt.reply_to_user("You do not have sufficient permissions to use this command.")

    @commands.command()
    async def upload(self, ctx):
        contxt = DiscordCtx(ctx)
        if not contxt.has_emoji_perms:
            return await contxt.reply_to_user("You do not have sufficient permissions to use this command.")

    @commands.command()
    async def convert(self, ctx):
        """ Alias for mote/upload """
        await self.upload(ctx)

    @commands.command()
    async def help(self, ctx):
        commands_msg = textwrap.dedent(f"""\
            `{BOT_PREFIX}grab <7tv_url>` --> Grab an emote from 7TV and upload to the server.
            `{BOT_PREFIX}upload` --> When provided with an uploaded image, will upload it to the server.
            `{BOT_PREFIX}convert` --> Same as {BOT_PREFIX}/convert.
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