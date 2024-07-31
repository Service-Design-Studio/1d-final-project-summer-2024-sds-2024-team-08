from typing import TypedDict, Optional
from langgraph.graph.message import MessagesState
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import (
    ToolMessage,
)
from langgraph.checkpoint import BaseCheckpointSaver
from dotenv import load_dotenv

import grapher_agent, researcher_agent
from tools import get_tools, get_all_tools
    
load_dotenv()

class AgentState(MessagesState, TypedDict):
    rs_db: list
    media: list
    sender: str
    saved_graph_id: Optional[int]

def tool_graph_adaptor(state):
    last_message = state['messages'][-1]

    return { "messages": ToolMessage("Redirecting to graph...", tool_call_id=last_message.id) }

def create_workflow(model, checkpointer: Optional[BaseCheckpointSaver] = None):
    tool_node = ToolNode(get_tools())

    researcher_name = "Researcher"
    grapher_name = "Grapher"

    researcher_node = researcher_agent.create_node(model, get_all_tools(), researcher_name)
    grapher_node = grapher_agent.create_node(model, grapher_name)

    def router(state):
        lastMessage = state['messages'][-1]
        if calls := lastMessage.tool_calls:
            if calls[0]['name'] == 'call_graph':
                return 'call_graph'
            else:
                return 'call_tool'
        else:
            return 'end'
    
    workflow = StateGraph(AgentState)
    workflow.add_node(researcher_name, researcher_node)
    workflow.add_node(grapher_name, grapher_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("tool_graph_adaptor", tool_graph_adaptor)
    
    workflow.add_conditional_edges(
        researcher_name,
        router,
        { "call_tool": "tool_node", 
         "call_graph": "tool_graph_adaptor",
         "end": END }
    )
    workflow.add_edge("tool_graph_adaptor", grapher_name)
    workflow.add_edge("tool_node", researcher_name)
    workflow.add_edge(START, researcher_name)
    workflow.add_edge(grapher_name, END)

    return workflow.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    from langchain_google_vertexai import ChatVertexAI
    from langgraph.checkpoint.memory import MemorySaver

    model = ChatVertexAI(model="gemini-1.5-flash", max_retries=2)

    checkpointer = MemorySaver()
    app = create_workflow(model, checkpointer=checkpointer)
    
    #print(app.get_graph().draw_mermaid())
    
    input = {"messages": [("user", "Generate a network graph for the relationships of Ben Carson. Include people from the media database too.")]}
    config = {"configurable": {"thread_id": 20}}
    
    app.stream_channels = "messages"
    for chunk in app.stream(input, config, stream_mode="updates"):
        for node, values in chunk.items():
            if isinstance(values, list):
                for v in values:
                    v.pretty_print()
            else:
                values.pretty_print()