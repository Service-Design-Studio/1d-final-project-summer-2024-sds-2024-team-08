from langchain_google_vertexai import ChatVertexAI
# from langchain_experimental.graph_transformers import LLMGraphTransformer
# from langchain_core.documents import Document
from qdrant_client import models
from sqlalchemy.orm import Session
from database import media_engine, qdrant_client
import requests
from crud import get_media_ids_for_stakeholder, get_content_from_media_ids
from rs_finder_llm import llm_transformer_custom

# Vectorize user query
def vectorize_query(query):
    url = 'https://sentence-transformer-server-ohgaalojiq-de.a.run.app/embed/'
    x = requests.post(url, json = {'query': query})

    return x.json()


def rank_ids_qdrant(query_vector, media_ids, limit=5):  
  search_result = qdrant_client.search(
    collection_name="media_collection", 
    query_filter=models.Filter(
      must=[
          models.HasIdCondition(has_id=media_ids,)
      ],
    ),
    query_vector=query_vector, 
    with_payload=True,
    limit=limit
  )
  return search_result

def derive_rs_from_media(model, stakeholder_id: int=None, query: str=""):  
  with Session(media_engine) as db:
    if stakeholder_id is not None:
        media_ids = get_media_ids_for_stakeholder(db, int(float(stakeholder_id)))
      #Apply filter if query is defined
        if query:
          query_vector = vectorize_query(query)
          hits = rank_ids_qdrant(query_vector, media_ids, limit=2)
          # media_ids = [hit.id for hit in hits]
      
    elif stakeholder_id is None:
      query_vector = vectorize_query(query)
      hits = qdrant_client.search(
        collection_name="media_collection", 
        query_vector=query_vector, 
        with_payload=True,
        limit=2
      )
    
    media_ids = [hit.id for hit in hits]
    # Get content from media ids
    articles = get_content_from_media_ids(db, media_ids)
  response = '\n'.join(articles)
  return response

def derive_rs_from_media(model, query: str="", stakeholder_id: int=None):  
  page_content = read_media(stakeholder_id, query)

  # Derive relationships from filtered media ids
  graph_documents = llm_transformer_custom(model, user_query=query, media_text=page_content)
  
  return graph_documents

if __name__ == "__main__":
  model = ChatVertexAI(model="gemini-1.5-flash", max_retries=2)
  query = "Joe Biden supporters"
  stakeholder_id=28235
  ls = derive_rs_from_media(ChatVertexAI(model="gemini-1.5-flash", max_retries=3, temperature=0.01), query="")
  print(ls)
