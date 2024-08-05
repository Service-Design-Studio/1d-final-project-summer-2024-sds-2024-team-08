from langchain_google_vertexai import ChatVertexAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
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

def derive_rs_from_media(model, stakeholder_id, query: str=None):  
  with Session(media_engine) as db:
    media_ids = get_media_ids_for_stakeholder(db, int(float(stakeholder_id)))
  #Apply filter if query is defined
    if query:
      query_vector = vectorize_query(query)
      hits = rank_ids_qdrant(query_vector, media_ids, limit=2)
      media_ids = [hit.id for hit in hits]
    
    articles = get_content_from_media_ids(db, media_ids)

  # llm_transformer = LLMGraphTransformer(llm=model)
  documents = [Document(page_content='\n'.join(articles))]

  # Derive relationships from filtered media ids
  graph_documents = llm_transformer_custom(text=documents, user_query=query)
  
  return graph_documents
  # nodes = graph_documents[0].nodes
  # rs = graph_documents[0].relationships

  # nodes_map = {node.id: i for i, node in enumerate(nodes)}

  # media_rs = []
  # for relation in rs:
  #     source_id = nodes_map.get(relation.source.id)
  #     target_id = nodes_map.get(relation.target.id)

  #     if source_id and target_id:
  #         media_rs.append([source_id, relation.type, target_id])
  #     else:
  #         # Either source_id or target_id does not appear in the nodes
  #         continue
      
  # return {'nodes': {i: name for name, i in nodes_map.items()}, 'edges': media_rs, 'type': 'media'}
  # return filtered_media_ids

if __name__ == "__main__":
  model = ChatVertexAI(model="gemini-1.5-flash", max_retries=2)
  query = "Joe Biden supporters"
  ls = derive_rs_from_media(model, stakeholder_id=28235, query=query)
  print(ls)
