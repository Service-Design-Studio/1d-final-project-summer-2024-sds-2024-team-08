from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_google_vertexai import ChatVertexAI

from typing import Annotated, Sequence
from operator import add


class Test:
    messages: Annotated[list, add]

a = Test()
a.messages = ['a']
a.messages = ['b']

print(a.messages)