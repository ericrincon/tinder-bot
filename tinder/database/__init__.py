from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from tinder.config import Config


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(Config.DATABASE_URL)


base = declarative_base()
engine = db_connect()
Session = sessionmaker(bind=engine)


def create_db():
    from tinder.database.models import TinderUser, Image

    tables = [TinderUser, Image]

    # Drop and create tables

    for table in tables:
        table.__table__.drop(engine)
        table.__table__.create(engine)