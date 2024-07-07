from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
import os
import requests
import urllib
import rapidfuzz
from .database import SessionLocal
from .models import Aliases

os.environ["GOOGLE_API_KEY"] = "INSERT API KEY HERE"

with SessionLocal() as session:
    aliases = session.query(Aliases.id, Aliases.stakeholder_id, Aliases.other_names).all()
    aliases_dict = {alias.id: alias.other_names for alias in aliases}  # Dictionary of id : name. id is the unique id from the aliases table so that i can map back to the actual stakeholder_id again if there is a match
    aliases_sid_dict = {alias.id: [alias.stakeholder_id, alias.other_names] for alias in aliases}  # Dictionary of id : [stakeholder_id, name]. id is the unique id from the aliases table so that i can map back to the actual stakeholder_id again if there is a match


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
    
    #Cleaner way of building urls
    url = r'https://stakeholder-api-hafh6z44mq-de.a.run.app/stakeholders/?'

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
    """Use this tool to get the best matches for a given name. This tool will return a list of up to 5 names who are the best matches with the given name. 
    If the output only contains one name, then that is the best match use the tool read_stakeholders tool to get the information about the identified stakeholder.
    If the output contains more than one name, then you should ask the user to clarify which stakeholder they are referring to. Following the format "Which names are you referring to?: list the name".
    If the output contains no names, then there are no matches for the given name.
    
    Args:
        name (str): The name of the stakeholder you want to find matches for.
        
    Returns:
        list: A list of up to 5 names who are the best matches with the given name.
    """
    
    if name in aliases_dict.values():
        stakeholder_id = [value[0] for value in aliases_sid_dict.values() if value[1] == name]
        return stakeholder_id
    
    else:
        best_matches = rapidfuzz.process.extract(name, aliases_dict, score_cutoff=75)  # This wil return a list of tuples with the best matches, their scores and the key. (name, score, id)
        
        if len(best_matches) == 1:
            return [best_matches[0][2]]
        
        unique_stakeholders = set()
        result = []
        for match in best_matches:
            
            if aliases_sid_dict[match[2]][0] not in unique_stakeholders:
                unique_stakeholders.add(aliases_sid_dict[match[2]][0])
                result.append(match[0])
                
        return result


def query_model(query:str) -> str:
    """
    Call this function from outside the module
    """
    model = ChatVertexAI(model="gemini-1.5-flash")
    
    tools = [read_stakeholders, get_name_matches]
    graph = create_react_agent(model, tools=tools)
    
    inputs = {"messages": [
        ("user", query)
        ]}
    
    response = graph.invoke(inputs, stream_mode="updates") #Stream mode set to updates instead of values for less verbosity

    return response[-1]['agent']['messages'][-1].content #some nonsense to get to the actual text you want. Can implement StrOutputParser in the future to make it neater

if __name__ == '__main__':
    print(query_model("Who is Ben Carson?"))