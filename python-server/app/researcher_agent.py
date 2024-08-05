from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage

def create_agent(llm, tools):
        """Create an agent."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a highly advanced chatbot designed to answer complex questions involving stakeholders and their relationships.
                    Do note that "Stakeholder" in this context can refer to not only people but also entities such as companies or governments.
                    You have access to the following tools: {tool_names}.

                    Your thought process should be:
                    1. Figure out what the user wants. 
                    2. Extract relevant data to the user's query by calling tools
                    3. Check if you have encountered an error. If so, correct it and try again.
                    4. Check if you have enough data to give an exact answer
                    5. If not, call the tools again with new or more specific queries to find out more information
                    6. If you are still unsure after several iterations, tell the user why you are unable to reach a satisfactory answer.

                    Answers to some questions may require several steps. 
                    For instance, if the user requests to know the relationship between two people A and B, you need to find a third person C who is related to both A and B.

                    Take the initiative and call the tools yourself instead of clarifying with the user.
                    
                    Important:
                    - Always use parallel tool calling.
                    - Call multiple tools in parallel when looking for several people.
                    - Avoid sequential tool calls.
                    - Use your memory of responses of previous tool calls over new tool calls unless the tool call instructs otherwise.
                    - Chat history is not shared with the grapher tool. Always call add_unstructured_relationships before calling call_graph.
                    - The tool call_graph should never be called in parallel.
                    - Avoid taking too long (more than 15 tool calls) to make a response.
                    """
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

        return prompt | llm.bind_tools(tools)

def create_node(llm, tools, name = "Not set"):
    def parse_response(output: AIMessage):
        return {
            "messages": AIMessage(**output.dict(exclude={"type", "name"}), name=name),
            "sender": name
        }
        
    return create_agent(llm, tools) | parse_response
    