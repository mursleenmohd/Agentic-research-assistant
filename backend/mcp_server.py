from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Research Tools")

@mcp.tool()
def research_topic(topic: str) -> str:
    """
    Research a topic using the research knowledge source.
    """
    knowledge = {
        "artificial intelligence": (
            "Artificial Intelligence is a field of computer science "
            "focused on creating systems capable of performing tasks "
            "that normally require human intelligence."
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
            "Model Context Protocol is an open protocol that "
            "standardizes how AI applications connect to external "
            "tools and data sources."
        ),
    }

    topic_lower = topic.lower()
    for key, information in knowledge.items():
        if key in topic_lower:
            return information

    return (f"No specific information was found for '{topic}'. " "An external research source would be required.")

@mcp.tool()
def get_research_summary(topic: str) -> str:
    """
    Return a short research summary for a topic.
    """
    return (
        f"Research summary requested for: {topic}. "
        "The research system can use this MCP tool as an "
        "additional source during the agent workflow."
    )

if __name__ == "__main__":
    mcp.run()