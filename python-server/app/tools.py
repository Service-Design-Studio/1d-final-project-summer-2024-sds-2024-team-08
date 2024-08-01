from sqlalchemy.orm import Session
from sqlalchemy import select
from models import Stakeholder, Alias
from database import stakeholder_engine
from functools import wraps, partial, reduce
from langchain_core.tools import tool
from langchain_core.runnables import RunnablePassthrough, RunnableParallel, RunnableLambda
from langchain_core.runnables.config import get_executor_for_config
from qdrant_media import derive_rs_from_media
from langchain_google_vertexai import ChatVertexAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import ToolMessage
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

@tool 
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
    
    with Session(stakeholder_engine) as db:
        subject_rs = crud.get_relationships(db, subject=subject_id)
        object_rs = crud.get_relationships(db, object=subject_id)
        relationships = subject_rs + object_rs
        stakeholder_ids = {result.subject for result in relationships} | {result.object for result in relationships}
        stakeholder_names = crud.get_stakeholder_names(db, list(stakeholder_ids))

    relationships_with_names = []
    for result in relationships:
        subject_name = stakeholder_names.get(result.subject, "Unknown")
        object_name = stakeholder_names.get(result.object, "Unknown")
        predicate = result.predicate
        extracted_info = crud.extract_after_last_slash(predicate)
        # Remove non-alphanumeric characters
        extracted_info = re.sub(r'[^a-zA-Z0-9\' ]', '', extracted_info)
        relationships_with_names.append((subject_name, extracted_info, object_name))

    return relationships_with_names

@tool
def get_relationships(subject_id: int = None) -> dict:
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
    
    Returns:
        dict: A dictionary with "edges" and "nodes". Where "edges" is a list of tuples with the format (subject, predicate, object) and "nodes" is a dictionary with the format {stakeholder_id: stakeholder_name}.
    '''
    subject_id = int(float(subject_id))
    relationships_graph = {
        "edges": [],
        "nodes": {}
    }
    
    with Session(stakeholder_engine) as session:
        relationships = crud.get_relationships(session, subject=subject_id)
        if not relationships:
            relationships = crud.get_relationships(session, object=subject_id)
        else:
            object_rs = crud.get_relationships(session, object=subject_id)
            if object_rs:
                relationships += object_rs
    
    if not relationships:
        return relationships_graph
    
    # Collect unique stakeholder IDs
    unique_ids = set()
    
    for result in relationships:
        predicate = re.sub(r'[^a-zA-Z0-9\' ]', '', crud.extract_after_last_slash(result.predicate))
        relationships_graph["edges"].append((result.subject, predicate, result.object))
        unique_ids.update([result.subject, result.object])
    
    # Retrieve all stakeholder names in a single query
    with Session(stakeholder_engine) as session:
        stakeholder_names = crud.get_stakeholder_names(session, list(unique_ids))
    
    relationships_graph["nodes"] = stakeholder_names
    relationships_graph['type'] = 'rs_db'
    
    return relationships_graph


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

def get_relationships_from_media_build(model):
    @tool
    def get_relationships_from_media(stakeholder_id: int, query: str) -> dict:
        """
        Call this tool to extract relationships from existing media.
        Given a specified stakeholder_id, this tool will extract media sources involving the stakeholder.
        These media sources will be ordered by their similarity to a given query, and only relationships from the closest matches will be returned.
        This information can be used to augment information from get_relationships_with_names if it has insufficient information.
        
        Args:
            stakeholder_id (int): The id of the stakeholder you wish to search for.
            query (str): A word, short phrase or sentence that filters the type of media that this tool will search for.
        
        Returns:
            A dictionary representation of a graph. Edges are defined in (subject, predicate, object) order.
        """
        return derive_rs_from_media(model, stakeholder_id, query)
    
    return get_relationships_from_media

def get_tools(model):
    return [read_stakeholders, get_name_matches, get_relationships_with_names]

def get_all_tools(model):
    return get_tools(model) + [call_graph, get_relationships, get_relationships_from_media_build(model)]

def get_tool_node(model):
    return ToolNode(get_tools(model))


def build_mutable_tool_nodes(model):
    def _run_one(call):
        tool = tools.get(call['name'])
        res = tool.invoke(call['args'])
        
        return {
            "messages": [ToolMessage(repr(res), tool_call_id=call['id'])],
            res['type'] : res }
    
    def mutable_tool_node(state, config=None):
        last_msg = state['messages'][-1]
        
        #Ideally, use the map-reduce pattern in langgraph instead of this
        with get_executor_for_config(config=config) as executor:
            outputs = executor.map(_run_one, [c for c in last_msg.tool_calls if c['name'] in tools])
            output = reduce(lambda a, b: {'messages': a['messages'] + b['messages'],
                                 'rs_db': {
                                     'edges': a['rs_db']['edges'] + b['rs_db']['edges'],
                                     'nodes': dict(a['rs_db']['nodes'], **(b['rs_db']['nodes']))
                                 },
                                 'media': a['media'] or b['media']
                                 }, outputs)
            return output

    tools = {
        "get_relationships": get_relationships,
        "get_relationships_from_media": get_relationships_from_media_build(model)
    }

    return mutable_tool_node