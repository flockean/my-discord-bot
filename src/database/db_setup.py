import logging
import os
import shutil

from sqlalchemy import create_engine

from sqlalchemy.orm import Session
from src.models.schemas import Base

db_path: str = '/src/volume/discordFiles.db'
engine = create_engine(f'sqlite://{db_path}', connect_args={"check_same_thread": False})


def init_db() -> None:
    if not os.path.exists(f'.{db_path}'):
        logging.info("Creating database")
        Base.metadata.create_all(bind=engine)
