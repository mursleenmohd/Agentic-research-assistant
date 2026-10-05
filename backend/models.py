from pydantic import BaseModel

class ResearchRequest(BaseModel):
    message: str
    thread_id: str

class ResumeRequest(BaseModel):
    thread_id: str
    approved: bool

class ChatResponse(BaseModel):
    status: str
    response: str = ""
    plan: list[str] = []