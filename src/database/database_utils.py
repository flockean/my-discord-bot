from __future__ import annotations

from typing import Any
from typing import TypeVar

from sqlalchemy import Engine
from sqlalchemy import extract
from sqlalchemy import select
from sqlalchemy.engine.create import event
from sqlalchemy.orm import Session

from src.database.db_setup import engine
from src.models.schemas import Base
from src.service.logger_service import logger


T = TypeVar("T", bound=Base)


@event.listens_for(Engine, "connect")
def enable_sqlite_fks(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def add(db_model: Base) -> None:
    """Add a new model instance to the database."""
    try:
        logger.info(f"Adding {db_model} to the database.")
        with Session(bind=engine) as db:
            db.add(db_model)
            db.commit()
            logger.info(f"Added {db_model} to the database.")
            db.refresh(db_model)
    except Exception as e:
        logger.error(f"Error adding {db_model} to the database: {e}")


def delete(table: type[Base], id: Any) -> None:
    """Delete a record by its primary key."""
    try:
        with Session(bind=engine) as db:
            result: Base | None = db.get(table, id)
            if result:
                db.delete(result)
                logger.info(f"Deleted {result} from the database.")
                db.commit()
            else:
                logger.warning(f"No record found in {table.__tablename__} with id {id}")
    except Exception as e:
        logger.error(f"Error deleting {table.__tablename__} with id {id}: {e}")


def get_by_id(table: type[T], id: Any) -> T | None:
    """Get a single record by its primary key."""
    try:
        with Session(bind=engine) as db:
            result = db.get(table, id)
            return result
    except Exception as e:
        logger.error(f"Error getting {table.__tablename__} with id {id}: {e}")
        return None


def get_all(table: type[T]) -> list[T]:
    """Get all records from a table."""
    try:
        with Session(bind=engine) as db:
            results = db.query(table).all()
            logger.info(f"Retrieved all records from {table.__tablename__}.")
            return results
    except Exception as e:
        logger.error(f"Error retrieving all records from {table.__tablename__}: {e}")
        return []


def get_by_filter(table: type[T], **filters) -> list[T]:
    """Get records matching the given filters."""
    try:
        with Session(bind=engine) as db:
            query = select(table)
            for key, value in filters.items():
                query = query.filter(getattr(table, key) == value)
            results = db.execute(query).scalars().all()
            return results
    except Exception as e:
        logger.error(
            f"Error querying {table.__tablename__} with filters {filters}: {e}"
        )
        return []


def update_by_id(table: type[T], id: Any, **values) -> bool:
    """Update a record by its primary key with the given values."""
    try:
        with Session(bind=engine) as db:
            result = db.get(table, id)
            if result:
                for key, value in values.items():
                    setattr(result, key, value)
                db.commit()
                logger.info(f"Updated {table.__tablename__} record {id}")
                return True
            logger.warning(f"No record found in {table.__tablename__} with id {id}")
            return False
    except Exception as e:
        logger.error(f"Error updating {table.__tablename__} record {id}: {e}")
        return False


def query_by_date_parts(
    table: type[T], date_field: str, month: int, day: int
) -> list[T]:
    """Query records by matching month and day parts of a date field."""
    try:
        with Session(bind=engine) as db:
            query = select(table).filter(
                extract("month", getattr(table, date_field)) == month,
                extract("day", getattr(table, date_field)) == day,
            )
            results = db.execute(query).scalars().all()
            return results
    except Exception as e:
        logger.error(f"Error querying {table.__tablename__} by date parts: {e}")
        return []
