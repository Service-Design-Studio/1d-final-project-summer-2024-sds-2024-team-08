# from . import crud, schemas, langc, database, models
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
import requests
import urllib
import rapidfuzz
from sqlalchemy.orm import Session
from sqlalchemy import select
import re
from dotenv import load_dotenv

load_dotenv()
# from sqlalchemy import create_engine, Column, Integer, String, ARRAY
# from sqlalchemy.orm import Session
from .database import user_engine, stakeholder_engine, media_engine
# from .models import Stakeholders_mentioned

#     id = Column(Integer, primary_key=True, index=True)
#     media_id = Column(Integer)
#     stakeholder_ids = Column(Integer)

# columns = [
#       Stakeholders_mentioned.
#         models.Stakeholder.stakeholder_id,
#         models.Stakeholder.name,
#         models.Stakeholder.source,
#         models.Stakeholder.source_id,
#         models.Stakeholder.series,
#         models.Stakeholder.summary,
#         models.Stakeholder.headline,
#         models.Stakeholder.photo
#     ]
    
#     query = db.query(*columns)
with Session(media_engine) as s:
        run = Stakeholders_mentioned(s)


# with Session(media_engine) as s:
        # message = Stakeholders_mentioned()
        # message.chat_id = chat_id
        # message.content = query
        # message.sender_id = user_id
        # message.role = 'user'

        # s.add(message)
        # s.commit()

# class Relationship(Base):
#     __tablename__ = 'relationships'

#     id = Column(Integer, primary_key=True, index=True)
#     subject = Column(Integer, ForeignKey('stakeholders.stakeholder_id'))
#     predicate = Column(Text)
#     object = Column(Integer, ForeignKey('stakeholders.stakeholder_id'))
# country_ids