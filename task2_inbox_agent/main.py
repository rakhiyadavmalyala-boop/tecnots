"""Task 2 — Inbox Agent API.

FastAPI service that:
- Receives customer emails
- Classifies them by category and urgency
- Queries Task 1 (Knowledge Brain) for relevant answers
- Drafts email replies
- Supports human review, editing, and feedback
- Learns from human edits (20-consecutive-approval auto-send)
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import settings
from task2_inbox_agent.email_processor import EmailClassifier, ParsedEmail
from task2_inbox_agent.draft_generator import DraftGenerator
from task2_inbox_agent.feedback import FeedbackManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Shared state ─────────────────────────────────────────────────────────
classifier = EmailClassifier()
draft_gen = DraftGenerator()
feedback_mgr = FeedbackManager()

# In-memory store for processed emails and drafts
processed_emails: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    logger.info("Inbox Agent starting — Knowledge Brain API: %s", settings.knowledge_brain_api)
    yield


app = FastAPI(
    title="Inbox Agent",
    description="Task 2 — AI-powered email draft assistant",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Request / Response models ────────────────────────────────────────────
class EmailRequest(BaseModel):
    sender: str = Field(..., description="Sender email address")
    subject: str = Field(..., description="Email subject line")
    body: str = Field(..., min_length=5, description="Email body text")
    model: str | None = Field(None, description="Override LLM model")


class DraftResponse(BaseModel):
    email_id: str
    category: str
    urgency: str
    key_questions: list[str]
    draft: str
    sources: list[dict]
    escalated: bool
    auto_send_eligible: bool
    model: str
    latency_ms: float


class FeedbackRequest(BaseModel):
    email_id: str = Field(..., description="ID of the email being reviewed")
    final_version: str = Field(..., description="The approved/edited version")
    feedback_notes: str = Field("", description="Optional notes about the edit")


class FeedbackResponse(BaseModel):
    email_id: str
    was_edited: bool
    edit_distance_ratio: float
    consecutive_approvals: int
    auto_send_enabled: bool


# ── Endpoints ────────────────────────────────────────────────────────────
@app.post("/process", response_model=DraftResponse)
async def process_email(req: EmailRequest):
    """Process an incoming email: classify → query Brain → draft reply."""
    # Step 1: Parse and classify
    email = ParsedEmail.from_raw(
        sender=req.sender,
        subject=req.subject,
        body=req.body,
    )
    email = classifier.classify(email)

    # Step 2: Get improvement context from past feedback
    improvement_ctx = feedback_mgr.get_improvement_context()

    # Step 3: Generate draft (calls Task 1 API internally)
    result = await draft_gen.generate_draft(
        sender=email.sender,
        subject=email.subject,
        body=email.body,
        category=email.category.value,
        key_questions=email.key_questions,
        model=req.model,
    )

    # Store for later feedback
    processed_emails[email.email_id] = {
        "email": email,
        "draft": result["draft"],
        "sources": result.get("sources", []),
    }

    return DraftResponse(
        email_id=email.email_id,
        category=email.category.value,
        urgency=email.urgency,
        key_questions=email.key_questions,
        draft=result["draft"],
        sources=result.get("sources", []),
        escalated=result.get("escalated", False),
        auto_send_eligible=feedback_mgr.auto_send_enabled,
        model=result.get("model", ""),
        latency_ms=result.get("latency_ms", 0.0),
    )


@app.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(req: FeedbackRequest):
    """Submit human feedback on a draft reply."""
    stored = processed_emails.get(req.email_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Email not found")

    record = feedback_mgr.record_feedback(
        email_id=req.email_id,
        original_draft=stored["draft"],
        final_version=req.final_version,
        feedback_notes=req.feedback_notes,
    )

    return FeedbackResponse(
        email_id=req.email_id,
        was_edited=record.was_edited,
        edit_distance_ratio=record.edit_distance_ratio,
        consecutive_approvals=feedback_mgr.consecutive_approvals,
        auto_send_enabled=feedback_mgr.auto_send_enabled,
    )


@app.get("/feedback/stats")
async def feedback_stats():
    """Get feedback statistics and auto-send status."""
    return feedback_mgr.get_stats()


@app.get("/feedback/history")
async def feedback_history(limit: int = 20):
    """Get recent feedback records."""
    records = feedback_mgr.history[-limit:]
    return {
        "count": len(records),
        "records": [
            {
                "email_id": r.email_id,
                "was_edited": r.was_edited,
                "edit_distance_ratio": r.edit_distance_ratio,
                "feedback_notes": r.feedback_notes,
                "created_at": r.created_at,
            }
            for r in records
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    stats = feedback_mgr.get_stats()
    return {
        "status": "healthy",
        "knowledge_brain_api": settings.knowledge_brain_api,
        "processed_emails": len(processed_emails),
        "feedback_stats": stats,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.inbox_agent_port)
