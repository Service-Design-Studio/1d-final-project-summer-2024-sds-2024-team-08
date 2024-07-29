from typing import Annotated, Literal, TypedDict, Sequence, Optional
from langgraph.graph.message import add_messages
from langgraph.graph import END, StateGraph, START
from langchain_core.messages import (
    BaseMessage,
    ToolMessage,
    AIMessage
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.checkpoint import BaseCheckpointSaver
from dotenv import load_dotenv
import operator
from langgraph.graph.message import add_messages

    
load_dotenv()

def create_agent(llm, tools, system_message: str):
        """Create an agent."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "You are a helpful AI assistant, collaborating with other assistants."
                    " Use the provided tools to progress towards answering the question."
                    " If you are unable to fully answer, that's OK, another assistant with different tools "
                    " will help where you left off. Execute what you can to make progress."
                    " If you or any of the other assistants have the final answer or deliverable,"
                    " You have access to the following tools: {tool_names}.\n{system_message}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        return prompt | llm.bind_tools(tools)

# Helper function to create a node for a given agent
def agent_node(state, config, agent, name):
    print(f"invoking agent {name}")
    # print(f"the state is {state}")
    # print("===============")
    result = agent.invoke(state, config=config)
    print(f"the result is {result}")
    print("----------------")
    # We convert the agent output into a format that is suitable to append to the global state
    if isinstance(result, ToolMessage):
        pass
    else:
        result = AIMessage(**result.dict(exclude={"type", "name"}), name=name)
    return {
        "messages": [result],
        # Since we have a strict workflow, we can
        # track the sender so we know who to pass to next.
        "sender": name,
    }

def create_workflow(model, researcher_node, graph_master_node, tool_node, checkpointer: Optional[BaseCheckpointSaver] = None):
    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], add_messages]
        sender: str


    def router(state) -> Literal["call_tool", "end", "continue"]:
        # This is the router
        messages = state["messages"]
        last_message = messages[-1]
        sender = state["sender"]
        if last_message.tool_calls:
            print(f"============== The agent {sender} is invoking a tool ==============")
            # The previous agent is invoking a tool
            return "call_tool"
        if "FINAL ANSWER" in last_message.content:
            # Any agent decided the work is done
            print(f"=== The agent {sender} determines that the answer is FINAL ==============")
            return "end"
        if "GRAPH_MASTER" in last_message.content:
            # The previous agent is the researcher
            print(f"============== The agent {sender} determines that the response needs Graph_Master ==============")
            return "continue"
        return "continue"
    
    workflow = StateGraph(AgentState)
    workflow.add_node("Researcher", researcher_node)
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
        lambda x: print(f"=============== Travelling from call_tool to {x['sender']} ===============") or x["sender"],
        {
            "Researcher": "Researcher",
            "Graph_Master": "Graph_Master"
        }
    )
    
    workflow.add_edge(START, "Researcher")
    return workflow.compile(checkpointer=checkpointer)

