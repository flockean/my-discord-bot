from __future__ import annotations

import os

import discord
from discord import app_commands
from discord.ext import commands
from discord.ext import commands as _commands
from dotenv import load_dotenv

from src.cogs import birthday_cog
from src.cogs import neko_cog
from src.cogs import settings_cog
from src.database import database_utils
from src.database.db_setup import init_db
from src.service.birthday_service import event_on_day
from src.service.birthday_service import run_birthday_checks
from src.service.birthday_service import send_message_to_birthday_channel
from src.service.birthday_service import start_birthday_task
from src.service.logger_service import logger
from src.service.util_service import Category
from src.service.util_service import random_joke


# Generate Discord-Bot client
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
# Accept both 'f!_' (existing) and the more common 'f!' prefix to reduce user confusion.
client = commands.Bot(intents=intents, command_prefix=["f!_", "f!"])
client.remove_command("help")


def start_bot():
    load_dotenv()
    # Start the bot
    init_db()
    client.run(os.getenv("DISCORD_BOT"))


@client.event
async def on_ready():
    logger.info("BotStats: " + str(client.user) + " Id: " + str(client.application_id))
    await settings_cog.setup(client)
    await neko_cog.setup(client)
    await birthday_cog.setup(client)
    # Start the birthday check loop: default once per day (86400s).
    # For testing, set DEBUG_BIRTHDAY_LOOP=1 to run every 10 seconds.
    try:
        if os.getenv("DEBUG_BIRTHDAY_LOOP") == "1":
            event_on_day.change_interval(seconds=10)
        else:
            event_on_day.change_interval(seconds=86400)
        if not event_on_day.is_running():
            # use start_birthday_task to set the client and start the parameterless loop
            start_birthday_task(client)
    except Exception as e:
        logger.error(f"Failed to start birthday event loop: {e}")

    # Quick guild-scoped slash command sync for development (set TEST_GUILD_ID env var)
    try:
        test_gid = os.getenv("TEST_GUILD_ID")
        if test_gid:
            gid = int(test_gid)
            # Sync only to the test guild for fast updates
            await client.tree.sync(guild=discord.Object(id=gid))
            logger.info(f"Synced application commands to test guild {gid}")
        else:
            # Default: perform a global sync (may be slow)
            await client.tree.sync()
            logger.info("Synced application commands globally")
    except Exception as e:
        logger.error(f"Failed to sync application commands: {e}")

    logger.info("Bot is now Ready")


# --- Slash commands (module-level) ---
@client.tree.command(name="ping", description="Quick check that the bot responds")
async def _slash_ping(interaction):
    await interaction.response.send_message("pong")


@client.tree.command(
    name="get_birthday_channel",
    description="Show configured birthday channel for this guild",
)
async def _slash_get_birthday_channel(interaction):
    gid = interaction.guild.id if interaction.guild else 0
    val = database_utils.get_setting("birthday_channel_id", guild_id=gid)
    if val:
        await interaction.response.send_message(
            f"Configured birthday channel: <#{val}>"
        )
    else:
        await interaction.response.send_message(
            "No birthday channel configured for this guild."
        )


@client.tree.command(
    name="set_birthday_channel",
    description="Set the birthday announcement channel (mention or id)",
)
@app_commands.describe(channel_id="Channel ID to use; if omitted uses current channel")
async def _slash_set_birthday_channel(interaction, channel_id: str = None):
    gid = interaction.guild.id if interaction.guild else 0
    if channel_id is None:
        cid = interaction.channel.id if interaction.channel else None
    else:
        import re

        m = re.search(r"(\d{17,20})", channel_id)
        cid = int(m.group(1)) if m else None
    if cid is None:
        await interaction.response.send_message("Could not determine channel id.")
        return
    database_utils.set_setting("birthday_channel_id", str(cid), guild_id=gid)
    await interaction.response.send_message(f"Birthday channel set to <#{cid}>")


@client.tree.command(
    name="run_birthdays", description="Run birthday checks immediately (admin only)"
)
async def _slash_run_birthdays(interaction):
    if interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Running birthday checks...")
        await run_birthday_checks(client)
        await interaction.followup.send("Birthday checks completed.")
    else:
        await interaction.response.send_message(
            "You must be an administrator to run this.", ephemeral=True
        )


@client.command(
    name="run_birthdays",
    help="Run birthday checks immediately (admin only)",
    usage=Category.management,
)
@_commands.has_permissions(administrator=True)
async def run_birthdays(ctx):
    await ctx.send("Running birthday checks...")
    await run_birthday_checks(client)
    await ctx.send("Birthday checks completed.")


@client.command(
    name="RandomJoke",
    help="Gibt dir ein zufälligen schlechten Witz",
    usage=Category.rest,
)
async def joke(ctx):
    await ctx.send(random_joke())


@client.command(name="nsfw", help="Gibt ein random Nsfw Bild", usage=Category.nsfw)
async def nsfw(ctx):
    await ctx.send(
        "Leider gerade nicht aktiv! <:Screenshot20240514161554:1291407970646757386>"
    )


@client.command(
    name="ping", help="Quick check that the bot responds", usage=Category.management
)
async def ping(ctx):
    await ctx.send("pong")


@client.command(
    name="send_birthday_message",
    help="Send a custom message to the configured birthday channel (admin only)",
    usage=Category.management,
)
@_commands.has_permissions(administrator=True)
async def send_birthday_message(ctx, *, message: str):
    """Admin command: send a custom message to the configured birthday channel."""
    sent = await send_message_to_birthday_channel(client, message)
    if sent:
        await ctx.send("Message sent to birthday channel.")
    else:
        await ctx.send("No birthday channel configured or sending failed.")


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(
            "Es scheint ein Argument zu fehlen, probiere nochmal mit: ***f!_[befehl] [message]***"
        )


@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    logger.info(f"{msg.author}: {msg.content}")
    await client.process_commands(msg)


@client.event
async def on_command(ctx):
    logger.info(f"Command invoked: {ctx.command} by {ctx.author} in {ctx.guild}")


@client.event
async def on_command_completion(ctx):
    logger.info(f"Command completed: {ctx.command} by {ctx.author}")
