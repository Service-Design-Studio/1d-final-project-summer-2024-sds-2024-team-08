from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import MessagesState
from langgraph.graph import END, StateGraph, START
from langchain_core.messages import (
    ToolMessage,
    AIMessage
)
from langgraph.checkpoint import BaseCheckpointSaver
from dotenv import load_dotenv

import grapher_agent, researcher_agent
from tools import get_tool_node, get_all_tools, build_mutable_tool_nodes
    
load_dotenv()

def update_graph_structured(old: dict, new:dict) -> dict:
    nodes = old.get('nodes', {}).copy()
    nodes.update(new.get('nodes', {}))

    return {
        'edges': (old.get('edges', [])) + (new.get('edges', [])),
        'nodes': nodes
    }
    
class AgentState(MessagesState, TypedDict):
    rs_db: Annotated[dict, update_graph_structured] = dict()
    media: dict
    sender: str
    saved_graph_id: Optional[int]

def tool_graph_adaptor(state):
    last_message : AIMessage = state['messages'][-1]
    
    return { "messages": ToolMessage("Redirecting to graph...", tool_call_id=last_message.tool_calls[0]["id"]) }

def create_workflow(model, checkpointer: Optional[BaseCheckpointSaver] = None):
    tool_node = get_tool_node(model)
    mutable_tool_node = build_mutable_tool_nodes(model)

    researcher_name = "Researcher"
    grapher_name = "Grapher"

    researcher_node = researcher_agent.create_node(model, get_all_tools(model), researcher_name)
    grapher_node = grapher_agent.create_node(model, grapher_name)

    def router(state):
        lastMessage = state['messages'][-1]
        if calls := lastMessage.tool_calls:
            for call in calls:
                match call['name']:
                    case 'call_graph':
                        yield 'call_graph'
                    case 'get_relationships' | 'get_relationships_from_media': #Probably shouldn't hardcode
                        yield 'mut_tool_node'
                    case _:
                        yield 'call_tool'
        else:
            return 'end'
    
    workflow = StateGraph(AgentState)
    workflow.add_node(researcher_name, researcher_node)
    workflow.add_node(grapher_name, grapher_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("tool_graph_adaptor", tool_graph_adaptor)
    workflow.add_node("mut_tool_node", mutable_tool_node)
    
    workflow.add_conditional_edges(
        researcher_name,
        router,
        { "call_tool": "tool_node", 
         "call_graph": "tool_graph_adaptor",
         "mut_tool_node": "mut_tool_node",
         "end": END }
    )

    workflow.add_edge("tool_graph_adaptor", grapher_name)
    workflow.add_edge("tool_node", researcher_name)
    workflow.add_edge("mut_tool_node", researcher_name)

    workflow.add_edge(START, researcher_name)
    workflow.add_edge(grapher_name, END)

    return workflow.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    from langchain_google_vertexai import ChatVertexAI
    from langgraph.checkpoint.memory import MemorySaver

    model = ChatVertexAI(model="gemini-1.5-flash", max_retries=3)

    checkpointer = MemorySaver()
    app = create_workflow(model, checkpointer=checkpointer)
    
    #print(app.get_graph().draw_mermaid())
    print("Compiled graph")
    
    input = {"messages": [("user", "Draw me a graph showing the relationship between Joe Biden and Donald Trump.")]}
    config = {"configurable": {"thread_id": 20}}
    
    app.stream_channels = "messages" #"rs_db"
    for chunk in app.stream(input, config, stream_mode="updates"):
        for node, values in chunk.items():
            if isinstance(values, list):
                for v in values:
                    v.pretty_print()
            else:
                values.pretty_print()