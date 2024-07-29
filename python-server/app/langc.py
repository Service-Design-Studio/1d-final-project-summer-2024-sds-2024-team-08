from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from sqlalchemy.orm import Session
from PostgreSQLMemorySaver import PostgreSQLMemorySaver
from dotenv import load_dotenv
from models import Message
from database import user_engine
from langchain_core.messages import SystemMessage

load_dotenv()

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

    ls = [read_stakeholders, get_name_matches, get_relationships, get_relationships_with_names]
    
    tools = ls + generate_tools(chat_id=chat_id)
    messages_modifier = """
    # Instructions for the system
    ## 1. Overview
    You are a top-tier algorithm designed for extracting information from our databases to provide users with information about stakeholders if they are present in the database. 
    You are able to present the response as text and you are able to generate a network graph based on the relationships of the stakeholders if requested to. 
    You must capture the user's input and provide the appropriate response based on the user's query. 
    The aim is to provide the user with the most relevant information based on the user's query.
    ## 2. Stakeholders
    When a user asks for information about a stakeholder, you must extract the stakeholder's name from the user's query and use it to extract stakeholder information from the database. 
    You can use these tools to help you identify the appropriate stakeholder: read_stakeholders, get_name_matches.
    If you require more information from the user, you can ask the user to clarify which stakeholder they are referring to.
    ## 3. Relationships
    When a user asks for relationships between stakeholders, you must extract the context from the user's query and use it to filter out or filter in relationships based on the context by evaluating the predicate of each relationship.
    You can use these tools to help you identify the appropriate relationships: get_relationships, get_relationships_with_names.
    If you deem that the relationships are not relevant to the context from the user's query, you will remove those relationships as well.
    ## 4. Network Graph
    When a user asks for a network graph, you must generate a network graph based on the relationships of the stakeholders that you have identified.
    You can use these tools to help you generate the network graph: generate_network.
    Once you have generated the network graph, you will store the graph in the database and return 'The network graph has been created!' to the user.
    ## 5. Strict Compliance
    Adhere to the rules strictly and ensure that you are providing the most relevant information to the user based on the user's query. Non-compiance will result in termination.
    """
    graph = create_react_agent(model, tools=tools, messages_modifier=SystemMessage(content=messages_modifier), checkpointer=PostgreSQLMemorySaver(engine=user_engine))
    inputs = {"messages": [
        ("user", query)
        ]}
    
    config = {
        'configurable': {'thread_id': chat_id}
    }
    
    response = graph.invoke(inputs, config=config, stream_mode="updates") #Stream mode set to updates instead of values for less verbosity
    response_str = response[-1]['agent']['messages'][-1].content
            
    #  insert graph shit into Messages 
    with Session(user_engine) as s:
        message = Message()
        message.chat_id = chat_id
        message.content = response_str
        message.sender_id = 1
        message.role = 'assistant'
        if chat_id in g_id:
            message.network_graph_id = g_id[chat_id]
            del g_id[chat_id]        
        s.add(message)
        s.commit()

    return response_str

if __name__ == '__main__':
    print(query_model("Generate a network graph to show the relationships Joe Biden has. Exclude all the relationships that includes stakeholders giving Joe Biden grants.", 3, 10))
    