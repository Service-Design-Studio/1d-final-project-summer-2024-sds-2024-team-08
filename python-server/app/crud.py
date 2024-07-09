from sqlalchemy.orm import Session
import re
from . import models

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
    
    query = db.query(*columns)
    
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