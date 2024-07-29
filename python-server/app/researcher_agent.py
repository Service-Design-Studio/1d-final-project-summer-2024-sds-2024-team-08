from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage

def create_agent(llm, tools):
        """Create an agent."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    You are a helpful AI assistant, collaborating with other assistants.
                    Use the provided tools to progress towards answering the question.

                    You have access to the following tools: {tool_names}."""
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))

        return prompt | llm.bind_tools(tools)

def create_node(llm, tools, name = "Not set"):
    def parse_response(output: AIMessage):
        return {
            "messages": AIMessage(output.dict(exclude={"type", "name"}), name=name),
            "sender": name
        }
        
    return create_agent(llm, tools) | parse_response