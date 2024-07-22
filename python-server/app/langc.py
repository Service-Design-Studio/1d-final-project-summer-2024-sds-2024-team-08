from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
import rapidfuzz
from sqlalchemy.orm import Session
from sqlalchemy import select
from PostgreSQLMemorySaver import PostgreSQLMemorySaver
import re
from dotenv import load_dotenv
from models import Alias, Message, Stakeholder, Network_Graph
from database import user_engine, stakeholder_engine, media_engine
import crud
from pyvis.network import Network
import json
from functools import wraps

load_dotenv()

def use_config(**config_):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, config=config_, **kwargs)
        return wrapper
    return decorator

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

@tool
def read_stakeholders(stakeholder_id: int = None, name: str = None, summary: bool = True, headline: bool = True, photo: bool = True) -> bytes:
    """Use this tool to read stakeholders from the database. You can filter by stakeholder_id or name. From the prompt, identify the stakeholder by their name or stakeholder_id. You can also specify whether to include the summary, headline, and photo.
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
    with Session(stakeholder_engine) as session:
        stakeholders = crud.get_stakeholders(session, stakeholder_id, name, summary, headline, photo)
        
    return stakeholders

@tool
def get_name_matches(name: str) -> list:
    """Use this tool to get the best matches for a given name. This tool will return a list of up to 5 stakeholder_ids who have names that are the best matches with the given name. 
    If the output only contains one stakeholder_id, then that is the best match. Depending on the context, if the the user wants to know more about the stakeholder, use the tool read_stakeholders tool to get the information about the identified stakeholder.
    If the user wants to draw a network graph, use the tool get_relationships_with_names to get the relationships of the identified stakeholder.
    If the output contains more than one stakeholder_id, then you should ask the user to clarify which stakeholder they are referring to. Following the format :
        "Which names are you referring to?: 
        1. [name 1]
        2. [name 2]
        ..."
    If the output contains no names, then there are no matches for the given name.
    
    Args:
        name (str): The name of the stakeholder you want to find matches for.
        
    Returns:
        list: A list of up to 5 stakeholder_id who have names that are the best matches with the given name.
    """
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
def get_relationships_with_names(subject_id:int = None) -> bytes:
    '''
    Use this tool to get the every relationship the stakeholders have with one another. This tool will return in JSON format, a list where each element is a list. The format is as such: '[[subject, predicate, object], [subject, predicate, object], ...]'. Where the subject is related to object by the predicate and the subject can have multiple relationships with objects.
    After you have the relationships, you can use the tool generate_network to generate a network graph. The network graph will be generated and stored in the database. Once the graph has been stored, you will need to return the network_graph_id. This id will be used to retrieve the graph from the database.
    If the output is an empty list then it means that the subject has no relationships with the object.

    Args:
        subject_id (int): The name of the stakeholder you want to find matches for.
        
    Returns:
        list: A list of subjects, predicates and objects
    '''
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

def get_photo(name):
    with Session(stakeholder_engine) as session:
        response = session.scalars(select(Stakeholder).where(Stakeholder.name == name).limit(1)).one_or_none()
        if response is not None:
            ref_pic = response.photo
            if ref_pic:
                pic_url = ref_pic.split("||")[0].strip()  # Split by "||" and take the first URL
                return pic_url
            else:
                print(f"No photo field for get_photo({name}): {response}")
                return None
        else:
            print(f"stakeholder {name} does not exist")
            return None

def query_model(query:str, user_id:int, chat_id:int) -> str:
    """
    Call this function from outside the module
    """

    with Session(user_engine) as s:
        message = Message()
        message.chat_id = chat_id
        message.content = query
        message.sender_id = user_id
        message.role = 'user'

        s.add(message)
        s.commit()

    model = ChatVertexAI(model="gemini-1.5-flash", max_retries=2)
    
    @tool
    def generate_network(relationships: list[list[str]]) -> dict:
        """You need to consider the predicates in each of the relationships and identify the appropriate ones only based on the user input. If the user did not mention any specific context, then you can consider all the relationships. 
        You can use the tool map_data to generate the network graph. The network graph will be generated and stored in the database. Once the graph has been stored, you will need to return the network_graph_id. This id will be used to retrieve the graph from the database.
        
        Args:
            relationships (list): A list where each element is a list. The format is as such: '[[subject, predicate, object], [subject, predicate, object], ...]'. Where the subject is related to object by the predicate and the subject can have multiple relationships with objects.

        Returns:
            results (str): A JSON object containing the network_graph_id.
        """
        subj_color="#77E4C8"
        obj_color="#3DC2EC"
        edge_color="#96C9F4"
        subj_shape="image"
        obj_shape="image"
        alg="barnes"
        buttons=False
        g = Network(height="1024px", width="100%",font_color="black")
        if buttons == True:
            g.width = "75%"
            g.show_buttons(filter_=["edges", "physics"])
            
        for rs in relationships:
            subj = rs[0]
            pred = rs[1]
            obj = rs[2]
            s_pic = get_photo(subj)
            o_pic = get_photo(obj)
            g.add_node(subj, color=subj_color, shape=subj_shape, image=s_pic)
            g.add_node(obj, color=obj_color, shape=obj_shape, image=o_pic)
            g.add_edge(subj,obj,label=pred, color=edge_color, smooth=False)
        
        g.barnes_hut()
        g.toggle_physics(False)
        g.set_edge_smooth("dynamic")
        network_graph = g.generate_html()
        with Session(user_engine) as session:
            graph = Network_Graph()
            graph.content = network_graph
            graph.chat_id = chat_id
            
            session.add(graph)
            session.commit()
            generated_id = graph.id
        
        return {"network_graph_id": generated_id}

    tools = [read_stakeholders, 
             get_name_matches, 
             get_relationships_with_names,
             generate_network,
             ]
    
    graph = create_react_agent(model, tools=tools, checkpointer=PostgreSQLMemorySaver(engine=user_engine))
    inputs = {"messages": [
        ("user", query)
        ]}
    
    config = {
        'configurable': {'thread_id': chat_id}
    }
    
    response = graph.invoke(inputs, config=config, stream_mode="updates") #Stream mode set to updates instead of values for less verbosity
    response_str = response[-1]['agent']['messages'][-1].content

    with Session(user_engine) as s:
        message = Message()
        message.chat_id = chat_id
        message.content = response_str
        message.sender_id = 1
        message.role = 'assistant'

        s.add(message)
        s.commit()

    return response_str

if __name__ == '__main__':
    print(query_model("Help me visualize how Ben Carson is related to other stakeholders", 3, 5))