
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
import requests
import urllib
import rapidfuzz
from sqlalchemy.orm import Session
from sqlalchemy import select
from .PostgreSQLMemorySaver import PostgreSQLMemorySaver
import re
from dotenv import load_dotenv
from .models import Alias, Message
from .database import user_engine, stakeholder_engine

from sqlalchemy import select
from sqlalchemy.orm import Session
from .database import user_engine, stakeholder_engine, media_engine

print("eh")
# statement = select(stakeholders.id) 

# make orm statement

# with Session(engine) as s:
#     s.scalars("orminstruction") #to retrieve value

#     resp = s.scalars(statement).one()
# with Session(user_engine) as s:
#         message = Message()
#         message.chat_id = chat_id
#         message.content = response_str
#         message.sender_id = 1
#         message.role = 'assistant'

#         s.add(message)
#         s.commit()

# with Session(self.engine) as s:
#             query = insert(Checkpoint_ORM).values(
#                 chat_id=chat_id,
#                 cp_data=self.serde.dumps(checkpoint),
#                 metadata_data=self.serde.dumps(metadata),
#             )
#             query = query.on_conflict_do_update(
#                 index_elements=[Checkpoint_ORM.chat_id],
#                 set_=query.excluded
#             ).returning(Checkpoint_ORM.timestamp)
            
#             ts = s.scalar(query)
            
#             s.commit()