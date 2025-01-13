from typing import cast

from sqlalchemy.orm import Session

from src.database import database_utils
from src.models.schemas import Gameprogress, Gamegenre


def create_game(game: Gameprogress, db: Session) -> Gameprogress:
    database_utils.add(game, db)
    return game


def get_all_games(db: Session) -> list[Gameprogress]:
    return cast(list[Gameprogress], database_utils.get_all(Gameprogress, db))


def create_type(game_type: Gamegenre, db: Session) -> Gamegenre:
    database_utils.add(game_type, db)
    return game_type


def get_all_types(db: Session) -> list[Gamegenre]:
    return cast(list[Gamegenre], database_utils.get_all(Gamegenre, db))
