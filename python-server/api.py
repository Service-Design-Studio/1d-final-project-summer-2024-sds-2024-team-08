"""
API frontend using FastAPI
Run using:
    fastapi dev api.py
"""

from typing import Union
from fastapi import FastAPI
import database_query_function as db
import json

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/chats")
def get_chats(uid: int):
    return json.dumps({
        "uid": uid,
        "chat_ids": db.get_chats_from_user(uid)
        })

@app.get("/messages")
def get_messages(chat_id: int):
    return json.dumps({
        "chat_id": chat_id,
        "messages": db.get_messages_from_chat(chat_id)
        })