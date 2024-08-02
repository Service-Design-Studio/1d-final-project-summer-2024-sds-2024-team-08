from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import MessagesState
from langgraph.graph import END, StateGraph, START
from langgraph.constants import Send
from langchain_core.messages import (
    ToolMessage,
    AIMessage
)
from langgraph.checkpoint import BaseCheckpointSaver
from dotenv import load_dotenv

import grapher_agent, researcher_agent
from tools import get_tool_node, get_all_tools, build_mutable_tool_nodes, update_graph_structured, update_graph_unstructured
    
load_dotenv()
    
class AgentState(MessagesState, TypedDict):
    rs_db: Annotated[dict, update_graph_structured] = dict()
    media: Annotated[dict, update_graph_unstructured] = dict()
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
            #Should send each individual call but no time to refactor :/
            sent_tool_node = False
            sent_mut_tool_node = False
            for call in calls:
                match call['name']:
                    case 'call_graph':
                        yield Send('tool_graph_adaptor', state)
                    case 'get_relationships' | 'get_relationships_from_media': #Probably shouldn't hardcode
                        if not sent_mut_tool_node:
                            yield Send('mut_tool_node', state)
                    case _:
                        if not sent_tool_node:
                            yield Send('tool_node', state)
        else:
            yield END
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node(researcher_name, researcher_node)
    workflow.add_node(grapher_name, grapher_node)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("tool_graph_adaptor", tool_graph_adaptor)
    workflow.add_node("mut_tool_node", mutable_tool_node)
    
    workflow.add_conditional_edges(
        researcher_name,
        router
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