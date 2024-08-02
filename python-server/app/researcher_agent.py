from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage

def create_agent(llm, tools):
        """Create an agent."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a highly advanced chatbot designed to answer complex questions involving people and their relationships.
                    You have access to the following tools: {tool_names}.

                    Your thought process should be:
                    1. Figure out what the user wants
                    2. Extract relevant data to the user's query by calling tools
                    3. Check if you have enough data to give an exact answer
                    4. If not, call the tools again with new or more specific queries to find out more information
                    5. If you are still unsure after several iterations, tell the user why you are unable to reach a satisfactory answer.

                    Answers to some questions may require several steps. 
                    For instance, if the user requests to know the relationship between two people A and B, you need to find a third person C who is related to both A and B.
                    
                    Important:
                    - Always use parallel tool calling!
                    - Call multiple tools when looking for several people.
                    - Avoid sequential tool calls.
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
    