from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    research_topic: str
    research_plan: list[str]
    research_results: list[str]
    current_step: int
    approval_status: str
    final_answer: str