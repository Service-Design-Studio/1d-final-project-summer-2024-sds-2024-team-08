from typing import Annotated, Literal, TypedDict, Sequence, Optional
from langgraph.graph.message import MessagesState
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import (
    BaseMessage,
    ToolMessage,
    AIMessage
)
from langchain_core.runnables import RunnablePassthrough, RunnableConfig
from langgraph.checkpoint import BaseCheckpointSaver
from dotenv import load_dotenv
import operator
from langgraph.graph.message import add_messages

import grapher_agent, researcher_agent
from tools import get_tools, get_all_tools
    
load_dotenv()

# Helper function to create a node for a given agent
# def agent_node(state, agent, name):
#     result = agent.invoke(state, config=config)
    
#     if isinstance(result, ToolMessage):
#         pass
#     else:
#         result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
#     return {
#         "messages": [result],
#         "sender": name,
#     }
class AgentState(MessagesState, TypedDict):
    rs_db: list
    media: list
    sender: str

def agent_node(agent = None, name = "Not set"):
    def parse_response(output: AIMessage):
        return {
            "messages": AIMessage(output.dict(exclude={"type", "name"}), name=name),
            "sender": name
        }
        
    return agent | parse_response

def exit_node(state):
    return { "messages": [ToolMessage("Redirecting to exit..."),
                          AIMessage(state['messages'][-1]['content'])] }

def tool_graph_adaptor(state):
    args = state['messages'][-1].additional_kwargs
    rs_db = args["rs_db"]
    media = args["media"]
    
    return { "messages": ToolMessage("Redirecting to graph..."),
             "rs_db" : rs_db,
             "media" : media }

def create_workflow(model, checkpointer: Optional[BaseCheckpointSaver] = None):


    tool_node = ToolNode(get_tools())

    researcher_name = "Researcher"
    grapher_name = "Grapher"

    researcher_node = agent_node(researcher_agent.create_agent(model, get_all_tools()), researcher_name)
    grapher_node = agent_node(grapher_agent.create_agent(model), grapher_name)

    def router(state):
        lastMessage = state['messages'][-1]
        if calls := lastMessage.get('tool_calls'):
            if 'call_graph' in calls:
                return 'call_graph'
            elif 'send_final_message' in calls:
                return "send_final_message"
    
    workflow = StateGraph(AgentState)
    workflow.add_node(researcher_name, researcher_node)
    workflow.add_node(grapher_name, grapher_node)
    workflow.add_node("call_tool", tool_node)
    workflow.add_node("send_final_message", exit_node)
    workflow.add_node("tool_graph_adaptor", tool_graph_adaptor)
    
    workflow.add_conditional_edges(
        researcher_name,
        router,
        { "call_tool": "call_tool", 
         "call_graph": "tool_graph_adaptor", 
         "send_final_message": "send_final_message" }
    )
    
    workflow.add_edge("tool_graph_adaptor", grapher_name)
    workflow.add_edge("call_tool", "Researcher")
    workflow.add_edge(START, "Researcher")
    workflow.add_edge("send_final_message", END)
    workflow.add_edge("Graph_Master", END)

    return workflow.compile(checkpointer=checkpointer)