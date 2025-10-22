from __future__ import annotations

import os

from sqlalchemy import create_engine
from sqlalchemy import text

from src.models.schemas import Base
from src.service.logger_service import logger
from src.service.util_service import get_project_root


# Use a project-relative path for the SQLite DB so it's portable and writable.
db_dir = get_project_root() / "volume"
os.makedirs(db_dir, exist_ok=True)
db_file = db_dir / "discordFiles.db"
engine = create_engine(f"sqlite:///{db_file}", echo=True)


def init_db() -> None:
    logger.info("Creating database")
    Base.metadata.create_all(bind=engine)
    # Simple migration: if the birthdays table exists but lacks the
    # last_announced_year column, add it. This keeps backward compatibility
    # for existing SQLite DB files.
    try:
        with engine.begin() as conn:
            res = conn.execute(text("PRAGMA table_info('birthdays')")).fetchall()
            cols = [r[1] for r in res]
            if "last_announced_year" not in cols:
                logger.info(
                    "Adding missing column last_announced_year to birthdays table"
                )
                conn.execute(
                    text("ALTER TABLE birthdays ADD COLUMN last_announced_year INTEGER")
                )
    except Exception as e:
        logger.error(f"Error running DB migration for last_announced_year: {e}")
