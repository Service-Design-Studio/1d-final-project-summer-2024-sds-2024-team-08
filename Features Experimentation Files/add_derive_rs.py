from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from langgraph.checkpoint import MemorySaver

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import(
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder
)
import GraphRScustom
from GraphRScustom import LLMGraphTransformer
from pyvis.network import Network

import os
import requests
import urllib


from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from sqlalchemy.orm import Session
from sqlalchemy import select
import re
import models
from database import stakeholder_engine, user_engine, media_engine
from qdrant_media import search_in_qdrant, vectorize_query


#Implementation with Qdrant filter is in qdrant_media.py
def derive_rs_from_media(db:Session, stakeholder_id: int= None, query: str=None):
  # from langchain_google_genai import ChatGoogleGenerativeAI
  llm = ChatVertexAI(model="gemini-1.5-flash") 

  # llm = ChatGoogleGenerativeAI(temperature=0, model="gemini-pro")
  llm = ChatVertexAI(model="gemini-1.5-flash") 
  llm_transformer = LLMGraphTransformer(llm=llm)
  
  #get media ids from stakeholder ids
  # Get all media ids from stakeholder ids
  results = get_media_id_from_stakeholder(db, stakeholder_id=stakeholder_id)
  #list of media ids
  media_ids = [result.media_id for result in results]
  # query_vector = vectorize_query(query)
  # top_media = search_in_qdrant(query_vector)
  
  # List of media ids that stakeholder is mentioned in 
  media_ids = [result.media_id for result in results]

  # Pass list of media_ids through to metadata filter function

  # Match list of media_ids and rank top 5 based on user query

  # Join all articles 
  for id in media_ids:
    #get content
    results = get_content_from_media_id(db, media_id = id) #returns list of json dicts
    text = [result.content for result in results] #list of article content
  
  documents = [Document(page_content=' '.join(text))]
  # print(documents) ## for all content in medias 

  # Derive relationships from filtered media ids
  graph_documents = llm_transformer.convert_to_graph_documents(documents)
  
  nodes = graph_documents[0].nodes
  rs = graph_documents[0].relationships
  # print(rs)

  # Initiating dict, dictionary of ids, list of relationships and id 
  nodes_id = {}
  media_rs = []
  node_id_map = {}

def derive_rs_from_media(db:Session, stakeholder_id: int= None, query: str=None):
    node_id_map[node.id] = node_counter
    nodes_id[node_counter] = node.id

  # Relationships with ids
  # Format relationships with ids
    for relation in rs:
        source_id = node_id_map.get(relation.source.id)
        target_id = node_id_map.get(relation.target.id)

        if source_id is None:
            print(f"KeyError: '{relation.source.id}' not found in node_id_map")
        if target_id is None:
            print(f"KeyError: '{relation.target.id}' not found in node_id_map")

        if source_id is not None and target_id is not None:
            media_rs.append([source_id, relation.type, target_id])
        else:
            # Handle the case where either source_id or target_id is None
            # Either source_id or target_id is None
            continue

  # Output: {nodes: {id:name}, edges:[id,str,id]}
    return {'nodes': nodes_id, 'edges': media_rs}
  # return media_ids

if __name__ == "__main__":
  stakeholder_id = 28235