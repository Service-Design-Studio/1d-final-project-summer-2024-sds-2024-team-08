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
    generated_graph_id: Optional[int]
    had_error: bool

def error_node(state):
    last_message : AIMessage = state['messages'][-1]
    calls = last_message.tool_calls

    result = []

    for call in calls:
        message_s = "ParallelError: Call these tools sequentially this time."
        result.append(ToolMessage(message_s, tool_call_id=call["id"]))

    return({
        "messages": result
    })

def create_workflow(model, checkpointer: Optional[BaseCheckpointSaver] = None):
    tool_node = get_tool_node(model)
    mutable_tool_node = build_mutable_tool_nodes(model)

    researcher_name = "Researcher"
    grapher_name = "Grapher"

    researcher_node = researcher_agent.create_node(model, get_all_tools(model), researcher_name)
    grapher_node = grapher_agent.create_node(model, grapher_name)

    def tool_graph_adaptor(state):
        last_message : AIMessage = state['messages'][-1]
        calls = last_message.tool_calls

        result = []
        if len(calls) > 1:
            had_error = True
            for call in calls:
                if call["name"] == "call_graph":
                    message_s = "ParallelError: Call this tool sequentially only after the other tools have been called. Do not call it in parallel."
                else:
                    message_s = "ParallelError: Call this tool by itself again immediately to fix your mistake. Do not call call_graph until you get the return value from this tool."
                result.append(ToolMessage(message_s, tool_call_id=call["id"]))
        else:
            message_s = "Redirecting to graph..."
            result.append(ToolMessage(message_s, tool_call_id=calls[0]["id"]))
            had_error = False

        return({
            "messages": result,
            "had_error": had_error
        })

        

    def router(state):
        lastMessage = state['messages'][-1]
        dest = []
        if calls := lastMessage.tool_calls:
            # Note: This is a bad implementation. 
            # There should only be 1 node in charge of routing tool calls to ensure that the message state is consistent.
            # I have no idea why this hasn't broken down earlier but do NOT use this method for new projects.
            call_names = set(call['name'] for call in calls)
            
            if ('get_relationships' in call_names or 'get_relationships_from_media' in call_names or 'add_unstructured_relationships' in call_names):
                dest.append("mut_tool_node")
            if ('get_name_matches' in call_names or 'read_stakeholders' in call_names or 'call_graph' in call_names):
                dest.append("tool_node")
            if ('call_graph' in call_names):
                dest.append('tool_graph_adaptor')
        else:
            dest.append('End')
        if len(dest) == 1:
            return dest[0]
        elif 'tool_graph_adaptor' in dest:
            return 'tool_graph_adaptor'
        else:
            return 'error_node'
    
    workflow = StateGraph(AgentState)
    
    workflow.add_node(researcher_name, researcher_node)
    workflow.add_node(grapher_name, grapher_node)
    workflow.add_node("tool_graph_adaptor", tool_graph_adaptor)
    workflow.add_node("tool_node", tool_node)
    workflow.add_node("mut_tool_node", mutable_tool_node)
    
    workflow.add_node("error_node", error_node)
    
    workflow.add_conditional_edges(
        researcher_name,
        router
    )

    workflow.add_conditional_edges(
        "tool_graph_adaptor",
        lambda state: state["had_error"], {
            True: researcher_name,
            False: grapher_name}
    )

    workflow.add_edge("tool_node", researcher_name)
    workflow.add_edge("mut_tool_node", researcher_name)
    workflow.add_edge("error_node", researcher_name)

    workflow.add_edge(START, researcher_name)
    workflow.add_edge(grapher_name, END)

    return workflow.compile(checkpointer=checkpointer)


if __name__ == "__main__":
    from langchain_google_vertexai import ChatVertexAI
    from langgraph.checkpoint.memory import MemorySaver
    from langchain_core.messages import HumanMessage

    model = ChatVertexAI(model="gemini-1.5-flash", max_retries=3, temperature=0.01)

    checkpointer = MemorySaver()
    app = create_workflow(model, checkpointer=checkpointer)

    # print(app.get_graph().draw_mermaid())

    print("Compiled graph")
    
    input_ = {"messages": [("user", "How is Joe Biden connected to the Oil and Gas industry? Draw me a graph.")]}
    
    config = {"configurable": {"thread_id": 20}, "recursion_limit": 50}
    
    app.stream_channels = "messages"

    while (True):
        for chunk in app.stream(input_, config, stream_mode="updates"):
            for node, values in chunk.items():
                if isinstance(values, list):
                    for v in values:
                        v.pretty_print()
                else:
                    values.pretty_print()
                    
        input_ = {"messages": HumanMessage(input())}