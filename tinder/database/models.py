import uuid

from swiper.
from tinder.database import base

from sqlalchemy.dialects.postgresql import TEXT, INTEGER
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship


class TinderUser(base):
    __tablename__ = 'tinder_user'

    id = Column(TEXT, primary_key=True)

    name = Column(TEXT)
    age = Column(INTEGER)
    bio = Column(TEXT)
    images = relationship('Image')
    birth_date = Column(TEXT, nullable=True)
    instagram_username = Column(TEXT, nullable=True)
    instagram_photos = Column(TEXT, nullable=True)
    schools = Column(TEXT, nullable=True)
    jobs = Column(TEXT, nullable=True)

    def __init__(self, name='', age=None, bio='', images=None, birth_date='',
                 instagram_username='', instagram_photos=None,
                 schools=None, jobs=None):
        """

        :param name:
        :param age:
        :param bio:
        :param images:
        :param birth_date:
        :param instagram_username:
        :param instagram_photos:
        :param schools:
        :param jobs:
        """
        if images is None:
            images = []

        self.id = str(uuid.uuid4())
        self.name = name
        self.age = age
        self.images = images
        self.bio = bio
        self.birth_date = birth_date
        self.instagram_username = instagram_username
        self.instagram_photos = instagram_photos
        self.schools = schools
        self.jobs = jobs


class Image(base):
    """
    Table for storing images of users
    """
    __tablename__ = 'image'

    id = Column(TEXT, primary_key=True)
    url = Column(TEXT)
    file_path = Column(TEXT)
    user_id = Column(TEXT, ForeignKey('tinder_user.id'))
    image_number = Column(INTEGER)

    def __init__(self, url, file_path, image_number):
        self.id = str(uuid.uuid4())
        self.url = url
        self.file_path = file_path
        self.image_number = image_number