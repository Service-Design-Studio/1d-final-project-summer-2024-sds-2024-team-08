from qdrant_client import QdrantClient
from qdrant_client.http.models import PointStruct, Payload
import ast  # To safely evaluate strings that represent lists
import psycopg2 
from sentence_transformers import SentenceTransformer
from database import stakeholder_engine, user_engine, media_engine
from crud import get_media_id_from_stakeholder

# Vectorize user quer
def vectorize_query(query):
    encoder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    query_vector = encoder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    return query_vector[0].tolist()  # Convert to list

query = "Show me the network of Joe Biden"
query_vector = vectorize_query(query)

# Configure the Qdrant client
def search_in_qdrant(query_vector):  
  client = QdrantClient(
    url="https://867dab82-8992-4189-986f-1c75995eb872.us-east4-0.gcp.cloud.qdrant.io:6333", 
    api_key="Lwrqwe1aDB77aXYCDT8i7l-YgX6dcJ90et0Ch3POORLkBTvLbPF-6w",
  )

  search_result = client.search(
    collection_name="media_collection", 
    query_vector=query_vector, 
    with_payload=True, limit=5
  )
  return search_result

top_media = search_in_qdrant(query_vector)

for result in top_media:
  print(result.payload)