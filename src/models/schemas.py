<<<<<<< HEAD
from __future__ import annotations

=======
import datetime
import enum
import uuid
>>>>>>> dc8e8ae1474c4c3c520d6a8f97911efb38783c3a
from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


def get_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass

<<<<<<< HEAD

class BirthdaySchema(Base):
    """Model for storing user birthdays."""

    __tablename__ = "birthdays"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    birthday: Mapped[datetime] = mapped_column(nullable=False)
    # Track the year when the bot last announced this birthday to avoid duplicate announcements
    last_announced_year: Mapped[int | None] = mapped_column(nullable=True)

    # reference the actual mapped class name
    user = relationship("UserSchema", back_populates="birthdays")


class UserSchema(Base):
    """Model for storing user information."""

    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    birthdays: Mapped[list[BirthdaySchema]] = relationship(
        "BirthdaySchema", back_populates="user", cascade="all, delete-orphan"
    )


class SettingSchema(Base):
    """Guild-scoped settings table. Primary key is (guild_id, key).

    Use guild_id=0 for global settings.
    """

    __tablename__ = "settings"
    guild_id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(primary_key=True)
    value: Mapped[str] = mapped_column(nullable=False)
=======

class DMMessage(Base):
    __tablename__ = "dmmessage"
    id: Mapped[str] = mapped_column(primary_key=True, default=get_uuid())
    time: Mapped[datetime]
    author: Mapped[str]
    content: Mapped[str]

    def __repr__(self):
        return f'{self.id} - {self.author} - {self.content} \n'


class Gamegenre(Base):
    __tablename__ = "gamegenre"
    id: Mapped[str] = mapped_column(primary_key=True, default=get_uuid())
    name: Mapped[str]

    games: Mapped[list["Gameprogress"]] = relationship(back_populates="game_type")

    def __init__(self, name):
        self.name = name

    def __repr__(self) -> str:
        return f"{self.name}"


class Gameprogress(Base):
    __tablename__ = "gameprogress"
    id: Mapped[str] = mapped_column(primary_key=True, default=get_uuid())
    name: Mapped[str] = mapped_column(unique=True)
    type_id: Mapped[str] = mapped_column(ForeignKey("gamegenre.id"))
    in_progress: Mapped[int]

    game_type: Mapped["Gamegenre"] = relationship(back_populates="games",
                                                  primaryjoin="Gameprogress.type_id==Gamegenre.id")

    def __init__(self, name, type_id, in_progress):
        self.name = name
        self.type_id = type_id
        self.in_progress = in_progress

    def __repr__(self):
        return f'> {self.name} {self.in_progress}'


class ProgressStatus(enum.Enum):
    notStarted = 1
    inProgress = 2
    finished = 3
>>>>>>> dc8e8ae1474c4c3c520d6a8f97911efb38783c3a
