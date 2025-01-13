import datetime
import enum
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped, mapped_column


def get_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


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
