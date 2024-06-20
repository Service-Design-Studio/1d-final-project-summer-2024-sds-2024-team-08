"""
API frontend using FastAPI
Run using:
    fastapi dev api.py
"""

from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import database_query_function as db

app = FastAPI()

class ChatResponse(BaseModel):
    uid: int
    chat_ids: list[int]

class Message(BaseModel):
    id: int
    role: str
    content: str

class MessageResponse(BaseModel):
    chat_id: int
    messages: list[Message]

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/chats", response_model=ChatResponse)
def get_chats(uid: int):
    return {
        "uid": uid,
        "chat_ids": db.get_chats_from_user(uid)
        }

@app.get("/messages", response_model=MessageResponse)
def get_messages(chat_id: int):
    return {
        "chat_id": chat_id,
        "messages": db.get_messages_from_chat(chat_id)
        }