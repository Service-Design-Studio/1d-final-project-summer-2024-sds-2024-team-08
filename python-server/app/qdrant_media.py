from langchain_google_vertexai import ChatVertexAI
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_core.documents import Document
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from database import stakeholder_engine, user_engine, media_engine
from crud import get_content_from_media_id, get_media_id_from_stakeholder
from os import getenv
from dotenv import load_dotenv

load_dotenv()

# Vectorize user query
def vectorize_query(query):
    encoder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    query_vector = encoder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    return query_vector[0].tolist()  # Convert to list


def search_in_qdrant(query_vector, media_ids):  
  client = QdrantClient(
        url=getenv['QDRANT_HOST'], 
        api_key=getenv['QDRANT_PASS'],
    )

  search_result = client.search(
    collection_name="media_collection", 
    query_filter=models.Filter(
      must=[
          models.HasIdCondition(has_id=media_ids,)
      ],
    ),
    query_vector=query_vector, 
    with_payload=True,
    limit=5
  )
  return search_result

def derive_rs_from_media(db:Session, model, stakeholder_id: int= None, query: str=None):
  llm_transformer = LLMGraphTransformer(llm=model).chain
  
  # Get all media ids from stakeholder ids
  results = get_media_id_from_stakeholder(db, stakeholder_id=stakeholder_id)
  
  # List of media ids that stakeholder is mentioned in 
  media_ids = [result.media_id for result in results]

  #Vectorize user query
  query_vector = vectorize_query(query)

  # Pass list of media_ids through to metadata filter function
  search_result = search_in_qdrant(query_vector, media_ids)
  filtered_media_ids = [hit.id for hit in search_result]

  # Join all articles 
  for id in media_ids:
    #get content
    results = get_content_from_media_id(db, media_id = id) #returns list of json dicts
    text = [result.content for result in results] #list of article content
  documents = [Document(page_content=' '.join(text))]

  # Derive relationships from filtered media ids
  graph_documents = llm_transformer.convert_to_graph_documents(documents)
  nodes = graph_documents[0].nodes
  rs = graph_documents[0].relationships
  # print(rs)

  # Initiating dict, dictionary of ids, list of relationships and id 
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

        if source_id is not None and target_id is not None:
            media_rs.append([source_id, relation.type, target_id])
        else:
            # Either source_id or target_id is None
            continue

  # Output: {nodes: {id:name}, edges:[id,str,id]}
  return {'nodes': nodes_id, 'edges': media_rs}
  # return filtered_media_ids


if __name__ == "__main__":
  query = "Generate a network graph to show only the relationships between Joe Biden has with his immediate family members. On the same network graph, help me visualize any relationships that his family members might have with other stakeholders."
  with Session(media_engine) as s:
    ls = derive_rs_from_media(s,stakeholder_id=28235, query=query)
    print(ls)
