from typing import Type

from sqlalchemy import Engine
from sqlalchemy.engine.create import event
from sqlalchemy.orm import Session

from src.database.db_setup import engine
from src.models.schemas import Base


@event.listens_for(Engine, "connect")
def enable_sqlite_fks(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


def add(db_model: Base, db: Session) -> None:
    db.add(db_model)
    db.commit()
    db.refresh(db_model)


def delete(table: Type[Base], id: str, db: Session) -> None:
    result: Base | None = db.get(table, id)
    db.delete(result)
    db.commit()


def get_all(table: Type[Base], db: Session) -> list[Base]:
    results: list[Base] = db.query(table).all()
    return results
