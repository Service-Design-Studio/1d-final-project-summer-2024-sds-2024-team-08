from typing import Annotated, Literal, TypedDict, Sequence, Optional
from langgraph.graph.message import add_messages
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import (
    BaseMessage,
    ToolMessage,
    AIMessage
)
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint import BaseCheckpointSaver
from dotenv import load_dotenv
import operator
from langgraph.graph.message import add_messages

    
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

def agent_node(state, agent, name):
    def parse_response(output):
        if not isinstance(output, ToolMessage):
            output = AIMessage(**output.dict(exclude={"type", "name"}), name=name)
        return {
            "messages": output['messages'] [output],
            "sender": name,
        }
    
    return state | RunnablePassthrough.assign(**(agent | parse_response))

def create_workflow(model, tool_node, checkpointer: Optional[BaseCheckpointSaver] = None):
    class AgentState(TypedDict):
        data: list
        messages: Annotated[Sequence[BaseMessage], add_messages]
        sender: str


    def router(state) -> Literal["call_tool", "end", "continue"]:
        # This is the router
        messages = state["messages"]
        last_message = messages[-1]
        sender = state["sender"]

        if last_message.tool_calls:

            return "call_tool"
        return "continue"
    
    workflow = StateGraph(AgentState)
    workflow.add_node("Researcher", )
    workflow.add_node("Graph_Master", graph_master_node)
    workflow.add_node("call_tool", tool_node)
    
    workflow.add_conditional_edges(
        "Researcher",
        router,
        {"continue": "Graph_Master", "call_tool": "call_tool", "end": END}
    )
    
    workflow.add_conditional_edges(
        "Graph_Master",
        router,
        {"continue": END, "call_tool": "call_tool", "end": END}
    )
    
    workflow.add_conditional_edges(
        "call_tool",
        lambda x: x["sender"],
        {
            "Researcher": "Researcher",
            "Graph_Master": "Graph_Master"
        }
    )
    
    workflow.add_edge(START, "Researcher")
    return workflow.compile(checkpointer=checkpointer)

