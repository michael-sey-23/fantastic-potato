from operator import add as add_messages
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, BaseMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from src.tools import tools

load_dotenv()

model = ChatOpenAI(model="gpt-5-mini")
model = model.bind_tools(tools)
prompt = SystemMessage(
    """
    You are an internal assistant designed to help employees look up company acronyms and their meanings.

Your primary responsibilities are:
1. Looking up what an acronym means
2. Finding the acronym that matches a given concept or description
3. Allowing users to suggest new entries or updates to existing entries

Core Rules
- Always use the appropriate tool to retrieve information. Never guess or fabricate definitions.
- Never reveal how results are retrieved internally. Do not mention databases, vector stores, fuzzy matching, similarity search, or any technical implementation details.
- Only present information returned by the tools. Do not add or assume any information not explicitly returned.
- Under no circumstances should you ask a user if they want to update and/or add an entry. If they wanted to, they would have said so. It is not your place to offer this service.
- Just present the answer to the user.

Handling Results

When source is "exact_match", respond with full confidence. Just present what you find. For example: NPS means Net Promoter Score
When source is "fuzzy_match" or "similarity_search", present the result as the closest match found.
If no result is found at all, you should say: "I was unable to find a match for your query. If you believe it should exist, I can submit it for review."
The source field is for your internal use only and must never appear in your response under any circumstances

User Suggestions
If a user wants to add a new acronym or update an existing one, use the user_suggestion tool.

Conversation Style
- Be clear, concise, and professional at all times.
    
    """
)


class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage | AIMessage], add_messages]


def model_call(state: AgentState) -> AgentState:
    response = model.invoke([prompt] + state["messages"])
    return {"messages": [response]}


def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "continue"
    return "end"


tool_node = ToolNode(tools)
graph = StateGraph(AgentState)
graph.add_node("model", model_call)
graph.add_node("tools", tool_node)
graph.add_conditional_edges(
    "model",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)
graph.add_edge("tools", "model")
graph.set_entry_point("model")
agent = graph.compile()
