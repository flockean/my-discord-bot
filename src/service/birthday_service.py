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


def _get_birthday_channel_id() -> int | None:
    """Return the birthday channel id.

    Priority:
    1. DB setting with key 'birthday_channel_id'
    2. Environment variable BIRTHDAY_CHANNEL_ID
    """
    val = database_utils.get_setting("birthday_channel_id")
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


@tasks.loop(hours=24)
async def event_on_day(client: commands.Bot | None = None):
    """Daily task which accepts an optional client for backward compatibility.

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
    # Wait until bot is ready
    if _birthday_client is None:
        # nothing to wait for
        return
    try:
        await _birthday_client.wait_until_ready()
    except Exception:
        # Some test dummies may not implement wait_until_ready
        await asyncio.sleep(0)

    tz = _get_target_timezone()
    delay = _seconds_until_next_midnight(tz)
    logging.info(f"Birthday task sleeping {delay:.1f}s until next midnight in {tz}")
    # Sleep until the next midnight in the configured timezone
    await asyncio.sleep(delay)


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


async def run_birthday_checks(client: commands.Bot):
    """Core logic: for each guild, determine local date (based on guild timezone
    setting fallback to global timezone) and send announcements for birthdays on
    that local date. Also DM users where possible and mark announced rows.
    """
    tz_default = _get_target_timezone()

    announced_ids: set[int] = set()

    # For each guild compute its local month/day and query DB for birthdays on that day
    for guild in client.guilds:
        # guild-specific timezone stored under key 'timezone' (optional)
        tz_name = database_utils.get_setting("timezone", guild_id=guild.id)
        if tz_name:
            try:
                guild_tz = ZoneInfo(tz_name)
            except Exception:
                logging.warning(
                    f"Invalid timezone '{tz_name}' for guild {guild.id}, using default"
                )
                guild_tz = tz_default
        else:
            guild_tz = tz_default

        # Compute local date for the guild
        now_local = datetime.now(guild_tz)
        month = now_local.month
        day = now_local.day

        birthdays = database_utils.get_birthdays_on(month, day)
        if not birthdays:
            continue

        # Filter out already announced rows for current year
        current_year = now_local.year
        birthdays_to_process = [
            b
            for b in birthdays
            if (
                b.get("last_announced_year") is None
                or b.get("last_announced_year") != current_year
            )
        ]
        if not birthdays_to_process:
            continue

        # Build message lines for this guild
        lines: list[str] = []
        for b in birthdays_to_process:
            uid = b.get("user_id")
            user = client.get_user(uid)
            display_name = None
            if user:
                display_name = user.name
                try:
                    await user.send(f"Happy Birthday {user.name}! 🎉")
                except Exception as e:
                    logging.warning(f"Failed to DM user {uid}: {e}")

            member = guild.get_member(uid)
            if member:
                if display_name:
                    lines.append(f"🎂 <@{uid}> — Happy Birthday {display_name}!")
                else:
                    lines.append(f"🎂 <@{uid}> — Happy Birthday!")

            # Regardless of membership, record this uid to mark announced if we actually post
            announced_ids.add(b.get("id"))

        if not lines:
            continue

        # Decide channel to post into
        channel_id = database_utils.get_setting(
            "birthday_channel_id", guild_id=guild.id
        )
        if channel_id is None:
            channel_id = database_utils.get_setting("birthday_channel_id", guild_id=0)
        if channel_id is None:
            continue

        try:
            chan = client.get_channel(int(channel_id))
            if chan is None:
                chan = await client.fetch_channel(int(channel_id))
            await chan.send("\n".join(lines))
        except Exception as e:
            logging.warning(
                f"Failed to send birthday message to guild {guild.id} channel {channel_id}: {e}"
            )

    # Persist announced year for each birthday row that we listed
    for bid in announced_ids:
        database_utils.set_birthday_announced(bid, datetime.now(tz_default).year)
