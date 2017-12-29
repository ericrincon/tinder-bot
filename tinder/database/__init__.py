from sqlalchemy import *
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

from tinder.config import Config

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(URL())


base = declarative_base()