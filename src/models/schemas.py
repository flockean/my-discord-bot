from __future__ import annotations

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
