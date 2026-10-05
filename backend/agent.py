from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from backend.config import GROQ_API_KEY, GROQ_MODEL
from backend.prompts import (PLANNER_PROMPT, RESEARCHER_PROMPT, SYNTHESIZER_PROMPT,)
from backend.state import AgentState
from backend.mcp_client import get_mcp_tools


llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=0,
)

def planner_node(state: AgentState):
    topic = state["research_topic"]
    messages = [
        SystemMessage(content=PLANNER_PROMPT),
        HumanMessage(content=(
                f"Create a research plan for this topic:\n"
                f"{topic}"
            )
        ),
    ]
    response = llm.invoke(messages)
    plan_text = response.content
    plan = []
    for line in plan_text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line[0].isdigit():
            cleaned = line.split(".", 1)[-1].strip()
            if cleaned:
                plan.append(cleaned)

    if not plan:
        plan = [topic]
    return {
        "research_plan": plan,
        "current_step": 1,
        "approval_status": "pending",
    }


def human_approval_node(state: AgentState):
    plan = state["research_plan"]
    approval = interrupt(
        {
            "message": (
                "Research plan ready. "
                "Do you want to start research?"
            ),
            "research_topic": state["research_topic"],
            "research_plan": plan,
        }
    )
    if approval:
        return {
            "approval_status": "approved",
            "current_step": 2,
        }
    return {
        "approval_status": "rejected",
        "current_step": 2,
    }

async def research_node(state: AgentState):
    plan = state["research_plan"]
    results = []
    try:
        mcp_tools = await get_mcp_tools()
    except Exception as e:
        return {
            "research_results": [
                (
                    "MCP research system could not be connected. "
                    f"Error: {str(e)}"
                )
            ],
            "current_step": 3,
        }
    research_tool = None
    summary_tool = None
    for tool in mcp_tools:
        if tool.name == "research_topic":
            research_tool = tool
        elif tool.name == "get_research_summary":
            summary_tool = tool

    if research_tool is None:
        return {
            "research_results": [
                "No MCP research tool was available."
            ],
            "current_step": 3,
        }

    for question in plan:
        try:
            result = await research_tool.ainvoke(
                {
                    "topic": question
                }
            )
            results.append((f"Research Question:\n{question}\n\n" f"Research Result:\n{result}"))
        except Exception as e:
            results.append(
                (
                    f"Research Question:\n{question}\n\n"
                    f"Research failed:\n{str(e)}"
                )
            )

    if summary_tool is not None:
        try:
            summary = await summary_tool.ainvoke(
                {
                    "topic": state["research_topic"]
                }
            )
            results.append(
                (
                    "Additional MCP Research Summary:\n"
                    f"{summary}"
                )
            )
        except Exception as e:
            results.append(
                (
                    "MCP summary tool failed:\n"
                    f"{str(e)}"
                )
            )
    return {
        "research_results": results,
        "current_step": 3,
    }


def synthesis_node(state: AgentState):
    topic = state["research_topic"]
    results = "\n\n".join(state["research_results"])
    messages = [
        SystemMessage(content=SYNTHESIZER_PROMPT),
        HumanMessage(
            content=(
                f"Original topic:\n"
                f"{topic}\n\n"
                f"Research results:\n"
                f"{results}"
            ),
        ),
    ]

    response = llm.invoke(messages)
    return {
        "final_answer": response.content,
        "current_step": 4,
    }

def rejected_node(state: AgentState):
    return {
        "final_answer": (
            "Research was stopped because the "
            "research plan was not approved."
        ),
        "current_step": 4,
    }

def approval_router(state: AgentState):
    if state["approval_status"] == "approved":
        return "researcher"
    return "rejected"


graph = StateGraph(AgentState)
graph.add_node("planner",planner_node)
graph.add_node("human_approval", human_approval_node)
graph.add_node("researcher",research_node)
graph.add_node("synthesizer",synthesis_node)
graph.add_node("rejected",rejected_node)

graph.add_edge(START,"planner")
graph.add_edge("planner","human_approval")
graph.add_conditional_edges(
    "human_approval",
    approval_router,
    {
        "researcher": "researcher",
        "rejected": "rejected",
    },
)
graph.add_edge("researcher","synthesizer")
graph.add_edge("synthesizer",END)
graph.add_edge("rejected",END)

checkpointer = InMemorySaver()
agent = graph.compile(checkpointer=checkpointer)