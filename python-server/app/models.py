from sqlalchemy import (
    Column, 
    Text, 
    Integer, 
    DateTime, 
    ForeignKey, 
    BLOB,
    func)

from sqlalchemy.orm import relationship, DeclarativeBase

class Base(DeclarativeBase):
    pass

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
    
    #aliases = relationship("Aliases", back_populates="stakeholders")

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
    
class Alias(Base):
    __tablename__ = 'aliases'

    id = Column(Integer, primary_key=True, index=True)
    stakeholder_id = Column(Integer, ForeignKey('stakeholders.stakeholder_id'))
    other_names = Column(Text)
    
    #stakeholder = relationship("Stakeholder", back_populates="aliases")
    
class Chat(Base):
    __tablename__ = 'chats'
    chat_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)

class Checkpoint_ORM(Base):
    __tablename__ = 'checkpoints'
    chat_id = Column(Integer, ForeignKey('chats.chat_id'),primary_key=True, unique=True)
    timestamp = Column(DateTime, server_default=func.now(), server_onupdate=func.now())
    cp_data = Column(BLOB)
    metadata_data = Column(BLOB, name='metadata')
    
class Message(Base):
    __tablename__ = 'messages'
    message_id = Column(Integer, autoincrement=True, primary_key=True)
    chat_id = Column(Integer, ForeignKey('chats.chat_id'), index=True)
    sender_id = Column(Integer, index=True)
    role = Column(Text, index=True)
    content = Column(Text)
    timestamp = Column(DateTime)