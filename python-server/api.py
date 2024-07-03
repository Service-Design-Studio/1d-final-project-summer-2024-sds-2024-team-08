"""
API frontend using FastAPI
Run using:
    fastapi dev api.py
"""

from typing import Union
from fastapi import FastAPI

app = FastAPI()



@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/chat/{chat_id}")
def read_item(chat_id: int):
    return {"chat_id": chat_id}