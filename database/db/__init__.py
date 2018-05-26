from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import Config


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(Config.DATABASE_URL)


base = declarative_base()
engine = db_connect()
Session = sessionmaker(bind=engine)


def create_db(drop=False):
    from database.db.models.user import TinderUser, Image
    from database.db.models.labeling import LabelingSession, LabeledImage, \
        Label

    # Find a better way to do this...
    tables = [TinderUser, Image, LabelingSession, LabeledImage, Label]

    # Drop and create tables
    for table in tables:
        if drop:
            table.__table__.drop(engine)
        table.__table__.create(engine)