from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
import requests
import urllib
import rapidfuzz
from sqlalchemy.orm import Session
from sqlalchemy import select
from .PostgreSQLMemorySaver import PostgreSQLMemorySaver
import re
from dotenv import load_dotenv
from .models import Alias, Message
from .database import user_engine, stakeholder_engine

load_dotenv()

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
        stakeholder_id (int, optional): _description_. Defaults to None.
        name (str, optional): _description_. Defaults to None.
        summary (bool, optional): _description_. Defaults to True.
        headline (bool, optional): _description_. Defaults to True.
        photo (bool, optional): _description_. Defaults to True.
        db (Session, optional): _description_. Defaults to Depends(get_db).
        
    Returns:
        _type_: _description_
    """
    #TODO: REFACTOR THIS TO PROPERLY POINT TO THE CORRECT MODULE
    #IT IS CURRENTLY CALLING ITSELF (????)
    
    #Cleaner way of building urls
    url = r'https://python-server-ohgaalojiq-de.a.run.app?'
    
    params = {'summary': summary,
            'headline': headline,
            'photo': photo}
    
    #Only insert stakeholder_id and name into the URL if given
    if stakeholder_id is not None:
        params['stakeholder_id'] = stakeholder_id
    
    if name is not None: #Remove periods from names (in cases such as Dr.)
        name = name.replace('.', '')
        params['name'] = name

    parsed_url = url + urllib.parse.urlencode(params)

    return requests.get(parsed_url).content #Returns the result in JSON format (bytes)

@tool
def get_name_matches(name: str) -> list:
    """Use this tool to get the best matches for a given name. This tool will return a list of up to 5 stakeholder_ids who have names that are the best matches with the given name. 
    If the output only contains one stakeholder_id, then that is the best match use the tool read_stakeholders tool to get the information about the identified stakeholder.
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

    model = ChatVertexAI(model="gemini-1.5-flash")
    
    tools = [read_stakeholders, get_name_matches]
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
    print(query_model("Who is Ben Carson?", 3, 5))