import uuid

import datetime

from swiper.database import base
from tinder.database.models import Image, TinderUser

from sqlalchemy.dialects.postgresql import TEXT, INTEGER, VARCHAR
from sqlalchemy import Column, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY



label_association_table = Table('label_association', base.metadata,
    Column('labeling_session', TEXT, ForeignKey('labeling_session.id')),
    Column('labeled_images', TEXT, ForeignKey('labels.id'))
)


class LabelingSession(base):
    """
    SQLAlcehmy table for sessions

    A session is a collection of labeled data
    """
    __tablename__ = "labeling_session"

    id = Column(TEXT, primary_key=True)
    name = Column(TEXT)
    children = relationship("Label", secondary=label_association_table,
                            back_populates="labeling_session")
    created_datetime = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, name):
        self.id = str(uuid.uuid4())
        self.name = name


class LabeledImage(base):
    __tablename__ = "labeled_image"

    id = Column(TEXT, primary_key=True)
    label = Column(INTEGER)
    # child = relationship("Image", uselist=False, back_populates="LabeledImage")

    def __init__(self, label):
        """

        :param label: An integer representing some classification.
        For example, 0 or 1 would represent left swipe or right swipe.
        """

        self.id = str(uuid.uuid4())
        self.label = label




class Label(base):
    __tablename__ = "label"

    id = Column(TEXT, primary_key=True)
    label_names = Column(ARRAY(TEXT))
    sessions = relationship("labeling_session", secondary=label_association_table,
                             back_populates="label")

    def __init__(self, label_names, sessions):
        self.id = str(uuid.uuid4())
        self.label_names = label_names

        if not isinstance(sessions, list):
            sessions = [sessions]

        self.sessions = sessions