"""Service for managing application settings."""

from __future__ import annotations

from src.database import database_utils as dbu
from src.models.schemas import SettingSchema


def get_setting(key: str, guild_id: int | None = None) -> str | None:
    """Get a setting value by key and optional guild_id."""
    gid = 0 if guild_id is None else guild_id
    result = dbu.get_by_id(SettingSchema, (gid, key))
    return result.value if result else None


def set_setting(key: str, value: str, guild_id: int | None = None) -> None:
    """Set a setting value by key and optional guild_id."""
    gid = 0 if guild_id is None else guild_id
    current = dbu.get_by_id(SettingSchema, (gid, key))
    if current:
        dbu.update_by_id(SettingSchema, (gid, key), value=value)
    else:
        setting = SettingSchema(guild_id=gid, key=key, value=value)
        dbu.add(setting)
