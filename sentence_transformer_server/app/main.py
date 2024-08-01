from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sentence_transformers import SentenceTransformer

encoder = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

def embed(query: str):
    query_vector = encoder.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    return query_vector[0].tolist()  # Convert to list

from pydantic import BaseModel
app = FastAPI()

class Query(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/embed/")
def embed_query(query: Query):
    embedding = embed(query.query)
    return embedding