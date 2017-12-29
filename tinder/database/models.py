import uuid

from tinder.database import base
from sqlalchemy.dialects.postgresql import TEXT, INTEGER
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship




class TinderBot(base):
    pass


class TinderUser(base):
    __tablename__ = 'tinder_user'

    id = Column(TEXT)

    name = Column(TEXT)
    age = Column()
    bio = Column(TEXT)
    images = relationship('Image')
    birth_date = Column()
    instagram_username = Column()
    instagram_photos = Column()
    schools = Column()
    jobs = Column()


    def __init__(self, name='', age=None, bio='', images=None, birth_date='',
                 instagram_username='', instagram_photos=None,
                 schools=None, jobs=None):

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

    id = Column(TEXT)
    url = Column(TEXT)
    file_path = Column(TEXT)
    user_id = Column(TEXT, ForeignKey('tinder_user.id'))
    image_number = Column(INTEGER)

    def __init__(self, url, file_path, image_number):
        self.id = str(uuid.uuid4())
        self.url = url
        self.file_path = file_path
        self.image_number = image_number