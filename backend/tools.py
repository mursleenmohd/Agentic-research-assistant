from datetime import datetime
from langchain_core.tools import tool

@tool
def get_current_time() -> str:
    """
    Get the current date and time.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def research_topic(topic: str) -> str:
    """
    Research a specific topic and return information.

    This is currently a local demonstration research tool.
    Later this will be replaced/enhanced with MCP-based
    external research tools.
    """
    knowledge = {
        "artificial intelligence": (
            "Artificial Intelligence is a field of computer science "
            "that focuses on creating systems capable of performing "
            "tasks that normally require human intelligence."
        ),

        "machine learning": (
            "Machine Learning is a subset of Artificial Intelligence "
            "where systems learn patterns from data and use those "
            "patterns to make predictions or decisions."
        ),

        "large language models": (
            "Large Language Models are neural network models trained "
            "on large collections of text. They can understand and "
            "generate natural language."
        ),

        "llm": (
            "Large Language Models are neural network models trained "
            "on large collections of text. They can understand and "
            "generate natural language."
        ),

        "ai agents": (
            "AI agents are systems that can understand goals, reason "
            "about tasks, use tools, maintain state, and execute "
            "multiple steps to achieve a goal."
        ),

        "langgraph": (
            "LangGraph is a framework for building stateful, "
            "multi-step agent workflows using graphs consisting "
            "of nodes, edges, and shared state."
        ),

        "mcp": (
            "Model Context Protocol is a protocol that standardizes "
            "how AI applications connect to external tools and "
            "data sources."
        ),
    }

    topic_lower = topic.lower()
    for key, information in knowledge.items():
        if key in topic_lower:
            return information

    return (
        f"No local research information was found for: {topic}. "
        "An external research source will be required."
    )