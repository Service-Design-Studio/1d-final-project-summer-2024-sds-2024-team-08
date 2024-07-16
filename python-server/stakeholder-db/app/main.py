from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session
from typing import List
from . import crud, models, schemas
from .database import SessionLocal, engine
from typing import Literal
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
import getpass
import os
import requests
from . import lc

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
<<<<<<< Updated upstream:python-server/stakeholder-db/app/main.py
        request.state.db = SessionLocal()
=======
        request.state.db = Session(stakeholder_engine) #session intialises a connection to stakeholder_engine which is a address for the database connection
>>>>>>> Stashed changes:python-server/app/main.py
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/stakeholders/", response_model=List[schemas.Stakeholder])
def read_stakeholders(stakeholder_id: int = None, name: str = None, summary: bool = True, headline: bool = True, photo: bool = True, db: Session = Depends(get_db)):
    
    stakeholders = crud.get_stakeholders(db, stakeholder_id, name, summary, headline, photo)
    if stakeholders == 'No results found.':
        raise HTTPException(status_code=404, detail="No stakeholders found")
    return stakeholders

@app.get("/relationships/", response_model=List[schemas.Relationship])
def read_relationships(subject: int = None, predicate: str = None, object: int = None, db: Session = Depends(get_db)):
    relationships = crud.get_relationships(db, subject, predicate, object)
    return relationships

@app.get("/relationships-with-names/")
def read_relationships_with_names(subject: int = None, predicate: str = None, object: int = None, db: Session = Depends(get_db)):
    relationships_with_names = crud.get_relationships_with_names(db, subject, predicate, object)
    if relationships_with_names == 'No results found.':
        raise HTTPException(status_code=404, detail="No relationships found")
    return relationships_with_names
            
@app.post("/langchain/")
def langchain_endpoint(user_input: schemas.UserInput):
    try:
        user_message = user_input.message
        output = lc.query_model(user_message) 
        return {'responses': output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))