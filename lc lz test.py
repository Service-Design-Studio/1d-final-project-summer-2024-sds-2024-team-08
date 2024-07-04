from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
import os
import requests
import urllib

# os.environ["GOOGLE_API_KEY"] = "AIzaSyBPA6ZeKF1XlFJXS5YBPBkK3xXC942vFyw"  #bannons
os.environ["GOOGLE_API_KEY"] = "AIzaSyCtKcsZVbfUtX-QMM8qkO_L9kaH-yq7hbU"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = './google-creds.json'
os.environ["GOOGLE_CLOUD_PROJECT_ID"] = "gemini-test-426508"


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

def query_model(query:str) -> str:
    """
    Call this function from outside the module
    """
    # ChatVertexAI.init(project_id="gemini-test-426508")
    

    model = ChatVertexAI(model="gemini-1.5-flash")
    
    tools = [read_stakeholders]
    graph = create_react_agent(model, tools=tools)
    
    inputs = {"messages": [
        ("user", query)
        ]}
    
    response = graph.invoke(inputs, stream_mode="updates") #Stream mode set to updates instead of values for less verbosity

    return response[-1]['agent']['messages'][-1].content #some nonsense to get to the actual text you want. Can implement StrOutputParser in the future to make it neater

if __name__ == '__main__':
    print(query_model("Who is Ben Carson?"))