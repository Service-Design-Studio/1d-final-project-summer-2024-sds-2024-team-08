from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Stakeholder(Base):
    __tablename__ = 'stakeholders'

    stakeholder_id = Column(Integer, primary_key=True, index=True)
    name = Column(Text)
    headline = Column(Text)
    summary = Column(Text)
    photo = Column(Text)
    source = Column(Text)
    source_id = Column(Text)
    series = Column(Integer)

    subjects = relationship(
        "Relationship",
        foreign_keys="[Relationship.subject]",
        back_populates="subject_stakeholder",
        primaryjoin="Stakeholder.stakeholder_id == Relationship.subject"
    )
    objects = relationship(
        "Relationship",
        foreign_keys="[Relationship.object]",
        back_populates="object_stakeholder",
        primaryjoin="Stakeholder.stakeholder_id == Relationship.object"
    )

class Relationship(Base):
    __tablename__ = 'relationships'

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(Integer, ForeignKey('stakeholders.stakeholder_id'))
    predicate = Column(Text)
    object = Column(Integer, ForeignKey('stakeholders.stakeholder_id'))

    subject_stakeholder = relationship(
        "Stakeholder",
        foreign_keys=[subject],
        back_populates="subjects"
    )
    object_stakeholder = relationship(
        "Stakeholder",
        foreign_keys=[object],
        back_populates="objects"
    )


# items = relationship("Item", back_populates="owner")


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)

#     items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")