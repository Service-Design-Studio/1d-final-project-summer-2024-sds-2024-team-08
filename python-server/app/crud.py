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
os.environ["GOOGLE_API_KEY"] = "AIzaSyCtKcsZVbfUtX-QMM8qkO_L9kaH-yq7hbU"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './google-creds.json'
os.environ["GOOGLE_CLOUD_PROJECT_ID"] = "gemini-test-426508"
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document

from sqlalchemy.orm import Session
from sqlalchemy import select
import re
import models
from database import stakeholder_engine, user_engine, media_engine
from qdrant_media import search_in_qdrant, vectorize_query


def get_stakeholders(db: Session, stakeholder_id: int = None, name: str = None, summary: bool = True, headline: bool = True, photo: bool = True):
    columns = [
        models.Stakeholder.stakeholder_id,
        models.Stakeholder.name,
        models.Stakeholder.source,
        models.Stakeholder.source_id,
        models.Stakeholder.series,
        models.Stakeholder.summary,
        models.Stakeholder.headline,
        models.Stakeholder.photo
    ]
    
    if summary == False:
        columns.remove(models.Stakeholder.summary)
    if headline == False:
        columns.remove(models.Stakeholder.headline)
    if photo == False:
        columns.remove(models.Stakeholder.photo)
    
    query = db.query(*columns)
    #stakeholder_id is matched to sql table header
    if stakeholder_id is not None:
        query = query.filter(models.Stakeholder.stakeholder_id == stakeholder_id)
    
    if name is not None:
        query = query.filter(models.Stakeholder.name == name)
    
    results = query.all()
    
    if not results:
        return 'No results found.'
    
    # Format the results as a list of dictionaries
    formatted_results = [dict(zip([column.name for column in columns], row)) for row in results]
    return formatted_results

def get_relationships(db: Session, subject: int = None, predicate: str = None, object: int = None):
    query = db.query(models.Relationship)
    
    if subject is not None:
        query = query.filter(models.Relationship.subject == subject)
    
    if predicate is not None:
        query = query.filter(models.Relationship.predicate == predicate)
    
    if object is not None:
        query = query.filter(models.Relationship.object == object)
    
    results = query.all()
    return results

def get_stakeholder_name(db: Session, stakeholder_id: int) -> str:
    result = db.query(models.Stakeholder.name).filter(models.Stakeholder.stakeholder_id == stakeholder_id).first()
    return result[0] if result else None

def extract_after_last_slash(text: str) -> str:
    import re
    match = re.search(r'[^/]+$', text)
    if match:
        return match.group(0)
    return None

def get_relationships_with_names(db: Session, subject: int = None, predicate: str = None, object: int = None):

    relationships = get_relationships(db, subject, predicate, object)
    relationships_with_names = []
    for result in relationships:
        subject_name = get_stakeholder_name(db, result.subject)
        object_name = get_stakeholder_name(db, result.object)
        predicate = result.predicate
        extracted_info = extract_after_last_slash(predicate)
        extracted_info = re.sub(r'[^a-zA-Z0-9\' ]', '', extracted_info)
        relationships_with_names.append((subject_name, extracted_info, object_name))
    
    if not relationships_with_names:
        return 'No results found.'
    return relationships_with_names

def get_graph(db: Session, id):
    return db.scalar(select(models.Network_Graph.content).where(models.Network_Graph.id == id).limit(1))
  
def get_media_id_from_stakeholder(db: Session, id: int= None, media_id : int = None, stakeholder_id: int = None):
    query = db.query(models.StakeholdersMentioned)

    if stakeholder_id is not None:
      query = query.filter(models.StakeholdersMentioned.stakeholder_id == stakeholder_id)

    results = query.all()
    # media_ids = [result.media_id for result in results]
    return results 

def get_content_from_media_id(db: Session, media_id: int=None, content: str = None):   
  query = db.query(models.Media)

  if media_id is not None:
    query = query.filter(models.Media.id == media_id)

  results = query.all()

  return results

def derive_rs_from_media(db:Session, stakeholder_id: int= None, query: str=None):
  # from langchain_google_genai import ChatGoogleGenerativeAI
  llm = ChatVertexAI(model="gemini-1.5-flash") 

  # llm = ChatGoogleGenerativeAI(temperature=0, model="gemini-pro")
  llm_transformer = LLMGraphTransformer(llm=llm)
  
  #get media ids from stakeholder ids
  results = get_media_id_from_stakeholder(db, stakeholder_id=stakeholder_id)
  #list of media ids
  media_ids = [result.media_id for result in results]
  # query_vector = vectorize_query(query)
  # top_media = search_in_qdrant(query_vector)
  
  for id in media_ids:
    #get content
    results = get_content_from_media_id(db, media_id = id) #returns list of json dicts
    text = [result.content for result in results] #list of article content
  
  documents = [Document(page_content=' '.join(text))]
  # print(documents) ## for all content in medias 
  graph_documents = llm_transformer.convert_to_graph_documents(documents)
  
  nodes = graph_documents[0].nodes
  rs = graph_documents[0].relationships
  # print(rs)

  nodes_id = {}
  media_rs = []
  node_id_map = {}
  node_counter = 0

  # Assign ids to nodes and map them to names
  for node in nodes:
    node_counter += 1
    node_id_map[node.id] = node_counter
    nodes_id[node_counter] = node.id

  # Relationships with ids
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
            continue

  # Output: {nodes: {id:name}, edges:[id,str,id]}
  # return {'nodes': nodes_id, 'edges': media_rs}
  return media_ids

if __name__ == "__main__":
  stakeholder_id = 28235
  query = "Generate a network graph to show only the relationships between Joe Biden has with his immediate family members. On the same network graph, help me visualize any relationships that his family members might have with other stakeholders."
  with Session(media_engine) as s:
    ls = derive_rs_from_media(s,stakeholder_id=28235, query=query)
    print(ls)
