# import uuid
#
# import datetime
#
# from database.db import Base
#
# from sqlalchemy.dialects.postgresql import TEXT, INTEGER
# from sqlalchemy import Column, ForeignKey, DateTime, Table
# from sqlalchemy.orm import relationship
# from sqlalchemy.dialects.postgresql import ARRAY
#
# label_association_table = Table(
#     "label_association", Base.metadata,
#     Column("labeling_session_id", TEXT, ForeignKey("labeling_session.id")),
#     Column("label_id", TEXT, ForeignKey("label.id"))
# )
#
# labeled_images_table = Table(
#     "labeled_image_association", Base.metadata,
#     Column("labeling_session_id", TEXT, ForeignKey("labeling_session.id")),
#     Column("labeled_image_id", TEXT, ForeignKey("labeled_image.id"))
# )
#
#
# class LabelingSession(Base):
#     """
#     SQLAlcehmy table for sessions
#
#     A session is a collection of labeled data
#     """
#     __tablename__ = "labeling_session"
#
#     id = Column(TEXT, primary_key=True)
#     name = Column(TEXT)
#     labels = relationship("Label", secondary=label_association_table,
#                           back_populates="labeling_session")
#     labeled_data = relationship("LabeledImage", secondary=labeled_images_table,
#                                 back_populates="labeling_session")
#     created_datetime = Column(DateTime, default=datetime.datetime.utcnow)
#
#     def __init__(self, name):
#         self.id = str(uuid.uuid4())
#         self.name = name
#
#
# class LabeledImage(Base):
#     __tablename__ = "labeled_image"
#
#     id = Column(TEXT, primary_key=True)
#     label = Column(INTEGER)
#     image_id = Column(TEXT, ForeignKey("image.id"))
#     labeled_image = Column(TEXT, ForeignKey(""))
#     image = relationship("Image")
#     labeling_session = relationship("LabelingSession", secondary=labeled_images_table, back_populates="labeled_image")
#
#     def __init__(self, label, image):
#         """
#
#         :param label: An integer representing some classification.
#         For example, 0 or 1 would represent left swipe or right swipe.
#         """
#
#         self.id = str(uuid.uuid4())
#         self.label = label
#         self.image = image
#         self.labeled_image = []
#
#
# class Label(Base):
#     __tablename__ = "label"
#
#     id = Column(TEXT, primary_key=True)
#     label_names = Column(ARRAY(TEXT))
#     labeling_session = relationship("LabelingSession", secondary=label_association_table, back_populates="label")
#
#     def __init__(self, label_names, labeling_session):
#         self.id = str(uuid.uuid4())
#         self.label_names = label_names
#
#         if not isinstance(labeling_session, list):
#             labeling_session = [labeling_session]
#
#         self.labeling_session = labeling_session
