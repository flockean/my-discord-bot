from __future__ import annotations

import sys
from types import ModuleType

import src.database.database_utils as dbu
import src.service.birthday_service as bs

import pytest


# Provide a minimal dummy 'discord' package to allow importing birthday_service during tests
if "discord" not in sys.modules:
    pkg = ModuleType("discord")
    ext = ModuleType("discord.ext")
    # create submodules commands and tasks with simple placeholders
    commands = ModuleType("discord.ext.commands")
    tasks = ModuleType("discord.ext.tasks")
    setattr(ext, "commands", commands)
    setattr(ext, "tasks", tasks)
    sys.modules["discord"] = pkg
    sys.modules["discord.ext"] = ext
    sys.modules["discord.ext.commands"] = commands
    sys.modules["discord.ext.tasks"] = tasks


class DummyUser:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.sent = []

    async def send(self, msg):
        # minimal async behaviour for tests
        self.sent.append(msg)


class DummyChannel:
    def __init__(self):
        self.sent = []

    async def send(self, msg):
        self.sent.append(msg)


class DummyMember:
    def __init__(self, id):
        self.id = id


class DummyGuild:
    def __init__(self, id, members=None):
        self.id = id
        self._members = {m.id: m for m in (members or [])}

    def get_member(self, user_id):
        return self._members.get(user_id)


class DummyClient:
    def __init__(self, users=None, guilds=None):
        self._users = {u.id: u for u in (users or [])}
        self.guilds = guilds or []
        self._channels = {}

    def get_user(self, user_id):
        return self._users.get(user_id)

    def get_channel(self, channel_id):
        return self._channels.get(channel_id)

    async def fetch_channel(self, channel_id):
        return self._channels.get(channel_id)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "birthdays,expect_dm,expect_channel",
    [
        ([], False, False),
        ([{"user_id": 1, "id": 42}], True, True),
    ],
)
async def test_run_birthday_checks(monkeypatch, birthdays, expect_dm, expect_channel):
    user = DummyUser(1, "TestUser")
    member = DummyMember(1)
    guild = DummyGuild(10, members=[member])
    channel = DummyChannel()

    client = DummyClient(users=[user], guilds=[guild])
    client._channels[999] = channel

    # run_birthday_checks now queries per-guild via get_birthdays_on(month, day)
    monkeypatch.setattr(dbu, "get_birthdays_on", lambda m, d: birthdays)

    def fake_get_setting(key, guild_id=None):
        if key == "birthday_channel_id":
            return "999" if guild_id == 10 else None
        return None

    monkeypatch.setattr(dbu, "get_setting", fake_get_setting)

    await bs.run_birthday_checks(client)

    if expect_dm:
        assert len(user.sent) >= 1
    else:
        assert len(user.sent) == 0

    if expect_channel:
        assert len(channel.sent) >= 1
    else:
        assert len(channel.sent) == 0
