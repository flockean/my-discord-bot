from __future__ import annotations

import asyncio
from datetime import datetime
from datetime import timedelta
import logging
import os
from zoneinfo import ZoneInfo

from discord.ext import commands
from discord.ext import tasks

from src.database import database_utils
from src.models.schemas import BirthdaySchema
from src.service import settings_service


def _get_birthday_channel_id() -> int | None:
    """Return the birthday channel id.

    Priority:
    1. DB setting with key 'birthday_channel_id'
    2. Environment variable BIRTHDAY_CHANNEL_ID
    """
    val = settings_service.get_setting("birthday_channel_id")
    if not val:
        val = os.getenv("BIRTHDAY_CHANNEL_ID")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        logging.warning("Invalid birthday channel id: not an int")
        return None


async def send_message_to_birthday_channel(client: commands.Bot, message: str) -> bool:
    """Send a message to the configured birthday channel.

    Returns True if the message was sent, False if there was no configured channel or sending failed.
    """
    channel_id = _get_birthday_channel_id()
    if channel_id is None:
        logging.info("No birthday channel configured (BIRTHDAY_CHANNEL_ID missing).")
        return False

    # get_channel can return None if the channel isn't in cache; fetch_channel works via API
    channel = client.get_channel(channel_id)
    if channel is None:
        try:
            channel = await client.fetch_channel(channel_id)
        except Exception as e:
            logging.warning(f"Failed to fetch birthday channel {channel_id}: {e}")
            return False

    try:
        await channel.send(message)
        return True
    except Exception as e:
        logging.warning(f"Failed to send message to birthday channel {channel_id}: {e}")
        return False


def _get_target_timezone() -> ZoneInfo:
    tz_name = os.getenv("BIRTHDAY_TIMEZONE", "UTC")
    try:
        return ZoneInfo(tz_name)
    except Exception:
        logging.warning(f"Invalid timezone {tz_name}, falling back to UTC")
        return ZoneInfo("UTC")


def _seconds_until_next_midnight(tz: ZoneInfo) -> float:
    """Return seconds until the next midnight in the given timezone."""
    now = datetime.now(tz)
    # Next midnight (start of next day) in that timezone
    next_mid = (now + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    delta = next_mid - now
    return delta.total_seconds()


_birthday_client: commands.Bot | None = None


@tasks.loop(minutes=15)  # Check every 15 minutes
async def event_on_day(client: commands.Bot | None = None):
    """Birthday check task that runs every 15 minutes.

    If a client is provided (old code called event_on_day.start(client)), we use
    that client and store it on the module so future runs use the same client.
    Otherwise the module-level `_birthday_client` is used.
    """
    global _birthday_client
    used_client = client or _birthday_client
    if used_client is None:
        logging.warning("Birthday task started without a client set; skipping run")
        return
    # If a client was passed in, remember it for future runs
    if client is not None:
        _birthday_client = client

    await run_birthday_checks(used_client)


@event_on_day.before_loop
async def _before_event_on_day():
    """Wait for the bot to be ready before starting the birthday check loop."""
    if _birthday_client is None:
        return

    try:
        await _birthday_client.wait_until_ready()
        logging.info("Birthday check task starting, will check every 15 minutes")
    except Exception:
        # Some test dummies may not implement wait_until_ready
        await asyncio.sleep(0)


def start_birthday_task(client: commands.Bot) -> None:
    """Set the client used by the task and start the daily loop.

    Call this once with your bot instance (for example in on_ready).
    """
    global _birthday_client
    _birthday_client = client
    if not event_on_day.is_running():
        event_on_day.start()


def stop_birthday_task() -> None:
    """Stop the daily birthday task and clear the client."""
    global _birthday_client
    if event_on_day.is_running():
        event_on_day.cancel()
    _birthday_client = None


def get_guild_timezone(guild_id: int, default_tz: ZoneInfo) -> ZoneInfo:
    """Get timezone for a specific guild, falling back to default if not set or invalid."""
    tz_name = settings_service.get_setting("timezone", guild_id=guild_id)
    if not tz_name:
        return default_tz

    try:
        return ZoneInfo(tz_name)
    except Exception:
        logging.warning(
            f"Invalid timezone '{tz_name}' for guild {guild_id}, using default"
        )
        return default_tz


async def dm_birthday_user(user, uid: int) -> None:
    """Send a DM to a user for their birthday."""
    if not user:
        return
    try:
        await user.send(f"Happy Birthday {user.name}! 🎉")
    except Exception as e:
        logging.warning(f"Failed to DM user {uid}: {e}")


async def send_guild_birthday_message(
    client: commands.Bot, guild_id: int, channel_id: str, message: str
) -> None:
    """Send a birthday announcement to a guild channel."""
    try:
        chan = client.get_channel(int(channel_id)) or await client.fetch_channel(
            int(channel_id)
        )
        await chan.send(message)
    except Exception as e:
        logging.warning(
            f"Failed to send birthday message to guild {guild_id} channel {channel_id}: {e}"
        )


async def send_birthday_messages(
    client: commands.Bot, guild, birthdays_today: list
) -> set[int]:
    """Send birthday messages for a specific guild and return announced birthday IDs."""
    announced_ids = set()
    lines = []

    for birthday in birthdays_today:
        uid = birthday.get("user_id")
        user = client.get_user(uid)
        member = guild.get_member(uid)

        await dm_birthday_user(user, uid)

        if member:
            display_name = user.name if user else None
            message = (
                f"🎂 <@{uid}> — Happy Birthday {display_name}!"
                if display_name
                else f"🎂 <@{uid}> — Happy Birthday!"
            )
            lines.append(message)
            announced_ids.add(birthday.get("id"))

    if not lines:
        return announced_ids

    # Get appropriate channel and send message via settings_service
    channel_id = settings_service.get_setting(
        "birthday_channel_id", guild_id=guild.id
    ) or settings_service.get_setting("birthday_channel_id", guild_id=0)

    if channel_id:
        await send_guild_birthday_message(
            client, guild.id, channel_id, "\n".join(lines)
        )

    return announced_ids


async def run_birthday_checks(client: commands.Bot):
    """Core logic: Check birthdays for each guild and send announcements."""
    tz_default = _get_target_timezone()
    all_announced_ids = set()

    for guild in client.guilds:
        # Get guild-specific timezone
        guild_tz = get_guild_timezone(guild.id, tz_default)

        # Get current date in guild's timezone
        now_local = datetime.now(guild_tz)

        # Get birthdays for today using generic query_by_date_parts
        raw = database_utils.query_by_date_parts(
            BirthdaySchema, "birthday", now_local.month, now_local.day
        )
        # convert to the old dict shape used by the rest of the service
        birthdays = [
            {
                "id": b.id,
                "user_id": b.user_id,
                "last_announced_year": b.last_announced_year,
            }
            for b in raw
        ]
        if not birthdays:
            continue

        # Filter out already announced birthdays
        birthdays_to_process = [
            b for b in birthdays if b.get("last_announced_year") != now_local.year
        ]
        if not birthdays_to_process:
            continue

        # Send messages and collect announced IDs
        announced = await send_birthday_messages(client, guild, birthdays_to_process)
        all_announced_ids.update(announced)

    # Mark all announced birthdays
    current_year = datetime.now(tz_default).year
    for bid in all_announced_ids:
        # mark announced using generic update
        database_utils.update_by_id(
            BirthdaySchema, bid, last_announced_year=current_year
        )
