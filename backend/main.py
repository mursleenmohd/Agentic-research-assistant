from fastapi import FastAPI
from langgraph.types import Command
from backend.agent import agent
from backend.models import (ResearchRequest,ResumeRequest,)

app = FastAPI(
    title="Agentic Research Assistant",
    description="Phase 3 Agentic AI Research Assistant",
    version="1.0.0",
)

@app.get("/")
def root():
    return {"message": "Agentic Research Assistant API is running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/research/start")
async def start_research(request: ResearchRequest):
    initial_state = {
        "messages": [],
        "research_topic": request.message,
        "research_plan": [],
        "research_results": [],
        "current_step": 0,
        "approval_status": "pending",
        "final_answer": "",
    }
    config = {
        "configurable": {"thread_id": request.thread_id}
    }
    result = await agent.ainvoke(initial_state,config=config,)
    interrupts = result.get("__interrupt__")
    if interrupts:
        interrupt_value = interrupts[0].value
        return {
            "status": "approval_required",
            "thread_id": request.thread_id,
            "message": interrupt_value["message"],
            "research_topic": interrupt_value["research_topic"],
            "research_plan": interrupt_value["research_plan"],
        }
    return {
        "status": "completed",
        "thread_id": request.thread_id,
        "response": result.get("final_answer", ""),
    }
@app.post("/research/resume")
async def resume_research(request: ResumeRequest):
    config = {
        "configurable": {"thread_id": request.thread_id}
    }
    result = await agent.ainvoke(Command(resume=request.approved),config=config,)
    interrupts = result.get("__interrupt__")

    if interrupts:
        interrupt_value = interrupts[0].value
        return {
            "status": "approval_required",
            "thread_id": request.thread_id,
            "message": interrupt_value["message"],
            "research_topic": interrupt_value["research_topic"],
            "research_plan": interrupt_value["research_plan"],
        }
    return {
        "status": "completed",
        "thread_id": request.thread_id,
        "response": result.get("final_answer", ""),
    }