from __future__ import annotations

from sqlalchemy import Engine
from sqlalchemy import text
from sqlalchemy.engine.create import event
from sqlalchemy.orm import Session

from src.database.db_setup import engine
from src.models.schemas import Base
from src.models.schemas import SettingSchema
from src.models.schemas import UserSchema
from src.service.logger_service import logger


@event.listens_for(Engine, "connect")
def enable_sqlite_fks(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def add(db_model: Base) -> None:
    try:
        logger.info(f"Adding {db_model} to the database.")
        with Session(bind=engine) as db:
            db.add(db_model)
            db.commit()
            logger.info(f"Added {db_model} to the database.")
            db.refresh(db_model)
    except Exception as e:
        logger.error(f"Error adding {db_model} to the database: {e}")


def delete(table: type[Base], id: str) -> None:
    try:
        with Session(bind=engine) as db:
            result: Base | None = db.get(table, id)
            db.delete(result)
            logger.info(f"Deleted {result} from the database.")
            db.commit()
    except Exception as e:
        logger.error(f"Error deleting {table.__tablename__} with id {id}: {e}")


def get_all(table: type[Base]) -> list[Base]:
    try:
        with Session(bind=engine) as db:
            results: list[Base] = db.query(table).all()
            logger.info(f"Retrieved all records from {table.__tablename__}.")
            return results
    except Exception as e:
        logger.error(f"Error retrieving all records from {table.__tablename__}: {e}")
        return []


def get_birthdays_today() -> list[dict]:
    # Keep for compatibility but delegate to month/day based query using local system date
    from datetime import datetime

    now = datetime.now()
    return get_birthdays_on(now.month, now.day)


def get_birthdays_on(month: int, day: int) -> list[dict]:
    """Return birthdays matching the given month and day (regardless of year).

    Returns list of dicts with keys: id, user_id, last_announced_year
    """
    m = f"{month:02d}"
    d = f"{day:02d}"
    with Session(bind=engine) as db:
        results = db.execute(
            text(
                "SELECT id, user_id, last_announced_year FROM birthdays WHERE strftime('%m', birthday) = :m AND strftime('%d', birthday) = :d"
            ),
            {"m": m, "d": d},
        ).fetchall()
        logger.info("Retrieved birthdays for %s-%s.", m, d)
        return [
            {"id": row[0], "user_id": row[1], "last_announced_year": row[2]}
            for row in results
        ]


def get_birthday_for_user(user_id: int) -> str | None:
    """Return the birthday string for a user_id or None if not found."""
    try:
        with Session(bind=engine) as db:
            result = db.execute(
                text(
                    "SELECT birthday FROM birthdays WHERE user_id = :uid ORDER BY id DESC LIMIT 1"
                ),
                {"uid": user_id},
            ).fetchone()
            if result:
                return result[0]
            return None
    except Exception as e:
        logger.error(f"Error fetching birthday for user {user_id}: {e}")
        return None


def set_birthday_announced(birthday_id: int, year: int) -> None:
    """Mark the birthday row as announced for the given year."""
    try:
        with Session(bind=engine) as db:
            stmt = text(
                "UPDATE birthdays SET last_announced_year = :yr WHERE id = :bid"
            )
            db.execute(stmt, {"yr": year, "bid": birthday_id})
            db.commit()
    except Exception as e:
        logger.error(f"Error marking birthday {birthday_id} announced for {year}: {e}")


def ensure_user_exists(user_id: int, name: str | None = None) -> None:
    """Ensure a UserSchema row exists for the given user_id. Create it if missing."""
    try:
        with Session(bind=engine) as db:
            existing = db.get(UserSchema, user_id)
            if existing:
                # Optionally update name if provided
                if name and existing.name != name:
                    existing.name = name
                    db.commit()
                return
            # Create a user row using the Discord snowflake as PK
            user = UserSchema(id=user_id, name=name or "")
            db.add(user)
            db.commit()
    except Exception as e:
        logger.error(f"Error ensuring user exists {user_id}: {e}")


def get_setting(key: str, guild_id: int | None = None) -> str | None:
    try:
        with Session(bind=engine) as db:
            gid = 0 if guild_id is None else guild_id
            result = db.get(SettingSchema, (gid, key))
            if result:
                return result.value
            return None
    except Exception as e:
        logger.error(f"Error getting setting {key}: {e}")
        return None


def set_setting(key: str, value: str, guild_id: int | None = None) -> None:
    try:
        with Session(bind=engine) as db:
            gid = 0 if guild_id is None else guild_id
            instance = db.get(SettingSchema, (gid, key))
            if instance:
                instance.value = value
            else:
                instance = SettingSchema(guild_id=gid, key=key, value=value)
                db.add(instance)
            db.commit()
    except Exception as e:
        logger.error(f"Error setting {key}={value}: {e}")
