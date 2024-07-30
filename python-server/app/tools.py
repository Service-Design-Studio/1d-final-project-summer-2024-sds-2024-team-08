from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Stakeholder, Alias
from database import stakeholder_engine
from functools import wraps
from langchain_core.tools import tool
import rapidfuzz
import crud
import re
import time

def timing_decorator(func):
    """Decorator that logs the execution time of the function it decorates."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} executed in {end_time - start_time:.6f} seconds")
        return result
    return wrapper


@tool
# @timing_decorator
def read_stakeholders(stakeholder_id: int = None, name: str = None, summary: bool = True, headline: bool = True, photo: bool = True) -> bytes:
    """Use this tool to read stakeholders from the database. You can filter by stakeholder_id or name. From the prompt, identify the stakeholder by their name or stakeholder_id. 
    If you are using stakeholder_id, ensure that it is an integer before you input it into the read_stakeholders tool. You can also specify whether to include the summary, headline, and photo.
    This tool is used to get summaries and information about stakeholders from the database.

    The result returned will be in JSON format.

    Args:
        stakeholder_id (int, optional): Defaults to None.
        name (str, optional): Defaults to None.
        summary (bool, optional): Defaults to True.
        headline (bool, optional): Defaults to True.
        photo (bool, optional): Defaults to True.
        
    Returns:
        str: _description_
    """
    if stakeholder_id is not None:
        stakeholder_id = int(float(stakeholder_id))
    with Session(stakeholder_engine) as session:
        stakeholders = crud.get_stakeholders(session, stakeholder_id, name, summary, headline, photo)

    return stakeholders

@tool
# @timing_decorator
def get_name_matches(name: str) -> list:
    """Use this tool to get the best matches for a given name. This tool will return a list of up to 5 stakeholder_ids who have names that are the best matches with the given name. 
    If the output only contains one stakeholder_id, then that is the best match. Depending on the context, if the the user wants to know more about the stakeholder, use the tool read_stakeholders tool to get the information about the identified stakeholder.
    If the user wants to draw a network graph, use the tool get_relationships to get the relationships of the identified stakeholder.
    If the output contains more than one stakeholder_id, then you should ask the user to clarify which stakeholder they are referring to. Following the format :
        "Which names are you referring to?: 
        1. [name 1]
        2. [name 2]
        ..."
    If the output contains no names, then there are no matches for the given name.
    
    Args:
        name (str): The name of the stakeholder you want to find matches for.
        
    Returns:
        list: A list of up to 5 stakeholder_id who have names that are the best matches with the given name. These stakeolder_id will be integers.
    """
    def normalize_name(name):
        """
        Normalize names by converting to lowercase, removing special characters except spaces
        """
        name = re.sub(r'[^a-z0-9\s]', '', name.lower())
        return name

    with Session(stakeholder_engine) as session:
        aliases = session.scalars(select(Alias)).all()
        aliases_dict = {alias.id: normalize_name(alias.other_names) for alias in aliases}  # Dictionary of id : normalized name
        aliases_sid_dict = {alias.id: [alias.stakeholder_id, normalize_name(alias.other_names)] for alias in aliases}  # Dictionary of id : [stakeholder_id, normalized name]


    normalized_input_name = normalize_name(name)
    
    if normalized_input_name  in aliases_dict.values():
        stakeholder_id = [value[0] for value in aliases_sid_dict.values() if value[1] == normalized_input_name]
        return stakeholder_id
    
    else:
        best_matches = rapidfuzz.process.extract(normalized_input_name, aliases_dict, score_cutoff=75)  # This wil return a list of tuples with the best matches, their scores and the key. (name, score, id)
        
        if len(best_matches) == 1:
            return [best_matches[0][2]]
        
        unique_stakeholders = set()
        result = []
        for match in best_matches:
            
            if aliases_sid_dict[match[2]][0] not in unique_stakeholders:
                unique_stakeholders.add(aliases_sid_dict[match[2]][0])
                result.append(match[0])
        return result

# IN THEORY, the get_names_matches tool will be used to return the stakeholder_id so that it can be run with get_relationships_with_names
@tool 
# @timing_decorator
def get_relationships_with_names(subject_id:int = None) -> bytes:
    '''
    Use this tool to output to the user every relationship the stakeholders have with one another in natural language. This tool should be called when the user wants the relationships of stakeholders in natural language. 
    This tool will return in JSON format, a list where each element is a list. The format is as such: '[[subject, predicate, object], [subject, predicate, object], ...]'. Where the subject is related to object by the predicate and the subject can have multiple relationships with objects.
    If the output is an empty list then it means that the subject has no relationships with the object.

    Args:
        subject_id (int): The name of the stakeholder you want to find matches for.
        
    Returns:
        list: A list of subjects, predicates and objects
    '''
    subject_id = int(float(subject_id))
    with Session(stakeholder_engine) as session:
        subject_rs = crud.get_relationships_with_names(session, subject=subject_id)
        object_rs = crud.get_relationships_with_names(session, object=subject_id)
    if subject_rs == 'No results found.' and object_rs == 'No results found.':
        return []
    
    elif subject_rs == 'No results found.':
        return object_rs
    
    elif object_rs == 'No results found.':
        return subject_rs
    
    return subject_rs + object_rs

@tool
# @timing_decorator
def get_relationships(subject_id:int = None) -> bytes:
    '''
    Use this tool to get the every relationship the stakeholders have with one another. This tool will be used only if the user wants a network graph. This tool will return in JSON format, a list where each element is a list. The format is as such: '[[subject, predicate, object], [subject, predicate, object], ...]'. Where the subject is related to object by the predicate and the subject can have multiple relationships with objects.
    After you have the relationships, you can use the tool generate_network to generate a network graph. The network graph will be generated and stored in the database. Once the graph has been stored, you will need to return the network_graph_id. This id will be used to retrieve the graph from the database.
    If the output is an empty list then it means that the subject has no relationships with the object.

    Args:
        subject_id (int): The name of the stakeholder you want to find matches for.
        
    Returns:
        relationships_with_predicates (list[list[int, str, int]]): A list of subjects, predicates and objects. 
            The subject is the stakeholder_id of the subject and it is an integer. 
            The predicate is the relationship between the subject and the object. The predicate is a string. 
            The object is the stakeholder_id of the object and it is an integer.
    '''
    # print("Getting relationships")
    subject_id = int(float(subject_id))
    with Session(stakeholder_engine) as session:
        subject_rs = crud.get_relationships(session, subject=subject_id)
        object_rs = crud.get_relationships(session, object=subject_id)
    
    if subject_rs == None and object_rs == None:
        return []
    
    elif subject_rs == None:
        relationships = object_rs
    
    elif object_rs == None:
        relationships = subject_rs
    
    else:    
        relationships = subject_rs + object_rs
    
    relationships_with_predicates = []
    for result in relationships:
        predicate = result.predicate
        extracted_info = crud.extract_after_last_slash(predicate)
        extracted_info = re.sub(r'[^a-zA-Z0-9\' ]', '', extracted_info)
        relationships_with_predicates.append((result.subject, extracted_info, result.object))

    return relationships_with_predicates

def get_photo(stakeholder_id: int) -> str:
    stakeholder_id = int(stakeholder_id)
    with Session(stakeholder_engine) as session:
        response = session.scalars(select(Stakeholder).where(Stakeholder.stakeholder_id == stakeholder_id).limit(1)).one_or_none()
        if response is not None:
            ref_pic = response.photo
            if ref_pic:
                pic_url = ref_pic.split("||")[0].strip()  # Split by "||" and take the first URL
                return pic_url
            else:
                print(f"No photo field for get_photo({stakeholder_id}): {response}")
                return None
        else:
            print(f"stakeholder {stakeholder_id} does not exist")
            return None
        
@tool
def call_graph() -> None:
    """
    Call this tool to activate the graphing agent only once you have obtained enough information.

    Args:
        No args
        
    Returns:
        relationships_with_predicates (list[list[int, str, int]]): A list of subjects, predicates and objects. 
            The subject is the stakeholder_id of the subject and it is an integer. 
            The predicate is the relationship between the subject and the object. The predicate is a string. 
            The object is the stakeholder_id of the object and it is an integer.
    """
    # Note: Need to manually point this in the router
    return "calling the graphing agent..."

@tool
def send_final_message(message: str) -> None:
    """
    Call this tool to send your final message to the user.

    Args:
        message (str): The message you wish to send to the user.
        
    Returns:
        Will not return anything to you
    """
    # Note: Need to manually point this in the router
    return message

def get_tools():
    return [read_stakeholders, get_name_matches, get_relationships, get_relationships_with_names]

def get_all_tools():
    return get_tools() + [call_graph]