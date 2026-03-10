from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from typing import Optional
from app.orchestrator.orchestrator import Orchestrator
from app.core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

# Singleton Orchestrator
_orchestrator = None

def get_orchestrator():
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = Orchestrator()
    return _orchestrator

class ChatRequest(BaseModel):
    user_message: str = Field(..., min_length=1, max_length=settings.MAX_MESSAGE_LENGTH)
    student_id: Optional[str] = Field(default="", max_length=20)
    session_id: Optional[str] = Field(default="default_session", max_length=100)
    phone: Optional[str] = Field(default="", max_length=20)

class ChatResponse(BaseModel):
    reply: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
@limiter.limit("60/minute")
async def chat_endpoint(request: Request, body: ChatRequest, orchestrator: Orchestrator = Depends(get_orchestrator)):
    try:
        reply = await orchestrator.process_message(
            user_message=body.user_message,
            student_id=body.student_id,
            session_id=body.session_id,
            phone=body.phone
        )
        return ChatResponse(reply=reply, session_id=body.session_id)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"API Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.delete("/session/{session_id}")
async def reset_session(session_id: str, orchestrator: Orchestrator = Depends(get_orchestrator)):
    orchestrator.session_memory.clear_session(session_id)
    return {"message": "Session cleared"}

@router.get("/metrics")
async def get_metrics(orchestrator: Orchestrator = Depends(get_orchestrator)):
    metrics = orchestrator.metrics.copy()
    reqs = metrics["total_requests"]
    if reqs > 0:
        metrics["avg_latency_seconds"] = round(metrics["total_latency_seconds"] / reqs, 4)
        metrics["cache_hit_rate"] = f"{(metrics['cache_hits'] / reqs) * 100:.1f}%"
    return metrics
