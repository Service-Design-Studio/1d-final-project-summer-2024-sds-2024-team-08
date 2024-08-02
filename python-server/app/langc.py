from langgraph.prebuilt import create_react_agent
from langchain_google_vertexai import ChatVertexAI
from sqlalchemy.orm import Session
from PostgreSQLMemorySaver import PostgreSQLMemorySaver
from dotenv import load_dotenv
from models import Message
from database import user_engine
from langchain_core.messages import AIMessage
from custom_workflow import create_workflow

load_dotenv()
checkpointer = PostgreSQLMemorySaver(user_engine)
model = ChatVertexAI(model="gemini-1.5-flash", max_retries=3, temperature=0)

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
    
    graph = create_workflow(model, checkpointer=checkpointer)

    inputs = {"messages": [
        ("user", query)
        ]}
    
    config = {
        'configurable': {'thread_id': chat_id}
    }

    stream = graph.stream(inputs, config=config, stream_mode="updates")

    def unwrap_stream():
        for chunk in stream:
            for values in list(chunk.values()):
                if isinstance(values, list):
                    for v in values:
                        yield v
                else:
                    yield values
    
    graph_id = None
    for update in unwrap_stream():
        msg = update.get('messages')
        update_graph_id = update.get('saved_graph_id')
        
        if msg:
            if isinstance(msg, list):
                for m in msg:
                    m.pretty_print()
            else:
                msg.pretty_print()
        
        if isinstance(msg, AIMessage):
            response_str = msg.content
        
        if update_graph_id:
            graph_id = update_graph_id
            
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
    print(query_model("Hello!", 3, 10))
    