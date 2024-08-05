from langchain_google_vertexai import ChatVertexAI
from sqlalchemy.orm import Session
from PSQLCheckpointer import PostgresSaver
from dotenv import load_dotenv
from models import Message
from database import user_engine, pool
from langchain_core.messages import AIMessage, BaseMessage
from custom_workflow import create_workflow

load_dotenv()

checkpointer = PostgresSaver(sync_connection=pool)
checkpointer.create_tables(pool)

model = ChatVertexAI(model="gemini-1.5-flash", max_retries=3, temperature=0)
graph = create_workflow(model, checkpointer=checkpointer)

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
    
    inputs = {"messages": [
        ("user", query)
        ]}
    
    config = {
        'configurable': {'thread_id': chat_id}
    }

    stream = graph.stream(inputs, config=config, stream_mode="updates")

    def unwrap_stream():
        for chunk in stream:
            for updates in chunk.values():
                for channel, update in updates.items():
                    if channel == 'messages':
                        if isinstance(update, list):
                            for msg in update:
                                yield msg
                        else:
                            yield update
                    elif channel == 'saved_graph_id':
                        print(updates)
                        yield updates
    
    graph_id = None

    for update in unwrap_stream():
        if isinstance(update, BaseMessage):
            update.pretty_print()        

            if isinstance(update, AIMessage):
                last_message_by = update.name
                response_str = update.content
        
        if isinstance(update, dict) and (id_ := update.get('saved_graph_id')):
            graph_id = id_ #TODO: Graph state not updating properly. Need to fix
    
    #Hacky workaround first
    if last_message_by == 'Grapher' and response_str.startswith('The network graph has been created!:'):
        graph_id = int(response_str.split(': ')[1].strip())
        response_str = response_str.split(': ')[0].strip()
        
    with Session(user_engine) as s:
        message = Message()
        message.chat_id = chat_id
        message.content = response_str
        message.sender_id = 1
        message.role = 'assistant'
        if graph_id:
            message.network_graph_id = graph_id
        s.add(message)
        s.commit()

    return response_str

if __name__ == '__main__':
    print(query_model("Generate a network graph of the relationship between ExxonMobil and Ivanka Trump.", 3, 10))
    