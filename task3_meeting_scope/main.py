"""Task 3 — Meeting to Scope API.

FastAPI service that:
- Parses meeting transcripts
- Extracts requirements with source references
- Checks feasibility via Task 1 (Knowledge Brain) API
- Generates scope, estimates, and proposals
- Compares initial and follow-up meetings for change detection
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import settings
from task3_meeting_scope.transcript_parser import TranscriptParser
from task3_meeting_scope.scope_generator import ScopeGenerator
from task3_meeting_scope.proposal import ProposalBuilder
from task3_meeting_scope.change_detector import ChangeDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Shared state ─────────────────────────────────────────────────────────
parser = TranscriptParser()
scope_gen = ScopeGenerator()
proposal_builder = ProposalBuilder()
change_detector = ChangeDetector()

# Store generated scopes for comparison
scopes_store: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    logger.info("Meeting to Scope starting — Knowledge Brain API: %s", settings.knowledge_brain_api)
    yield


app = FastAPI(
    title="Meeting to Scope",
    description="Task 3 — Meeting transcript to scope of work and proposal",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Request / Response models ────────────────────────────────────────────
class TranscriptRequest(BaseModel):
    transcript: str = Field(..., min_length=50, description="Meeting transcript text")
    title: str = Field("Meeting", description="Meeting title")
    meeting_type: str = Field("initial", description="initial or follow_up")
    model: str | None = Field(None, description="Override LLM model")


class CompareRequest(BaseModel):
    initial_scope_id: str = Field(..., description="ID of the initial scope")
    followup_scope_id: str = Field(..., description="ID of the follow-up scope")


class ApprovalRequest(BaseModel):
    scope_id: str
    approved: bool
    notes: str = ""


# ── Endpoints ────────────────────────────────────────────────────────────
@app.post("/analyze")
async def analyze_transcript(req: TranscriptRequest):
    """Parse a transcript and generate scope of work with proposal."""
    # Step 1: Parse the transcript
    parsed = parser.parse(
        text=req.transcript,
        title=req.title,
        meeting_type=req.meeting_type,
    )

    # Step 2: Generate scope (includes feasibility checks via Task 1 API)
    scope = await scope_gen.generate_scope(parsed, model=req.model)

    # Step 3: Build proposal
    proposal_md = proposal_builder.build(scope)

    # Step 4: Store for later comparison
    import hashlib
    scope_id = hashlib.md5(
        f"{req.title}{req.meeting_type}{len(req.transcript)}".encode()
    ).hexdigest()[:12]

    scopes_store[scope_id] = {
        "scope": scope,
        "proposal": proposal_md,
        "transcript_title": req.title,
        "meeting_type": req.meeting_type,
    }

    return {
        "scope_id": scope_id,
        "meeting_title": scope.meeting_title,
        "meeting_type": req.meeting_type,
        "speakers": [
            {"name": s.name, "role": s.role} for s in parsed.speakers
        ],
        "scope": scope.to_dict(),
        "proposal": proposal_md,
    }


@app.post("/compare")
async def compare_scopes(req: CompareRequest):
    """Compare two scopes to detect changes."""
    initial_data = scopes_store.get(req.initial_scope_id)
    followup_data = scopes_store.get(req.followup_scope_id)

    if not initial_data:
        raise HTTPException(status_code=404, detail="Initial scope not found")
    if not followup_data:
        raise HTTPException(status_code=404, detail="Follow-up scope not found")

    report = change_detector.compare(
        initial=initial_data["scope"],
        followup=followup_data["scope"],
    )

    return {
        "initial_scope_id": req.initial_scope_id,
        "followup_scope_id": req.followup_scope_id,
        "change_report": report.to_dict(),
    }


@app.post("/approve")
async def approve_scope(req: ApprovalRequest):
    """Record human approval or rejection of a scope."""
    if req.scope_id not in scopes_store:
        raise HTTPException(status_code=404, detail="Scope not found")

    scopes_store[req.scope_id]["approved"] = req.approved
    scopes_store[req.scope_id]["approval_notes"] = req.notes

    return {
        "scope_id": req.scope_id,
        "approved": req.approved,
        "notes": req.notes,
    }


@app.get("/scopes")
async def list_scopes():
    """List all generated scopes."""
    return {
        "count": len(scopes_store),
        "scopes": [
            {
                "scope_id": sid,
                "title": data["transcript_title"],
                "meeting_type": data["meeting_type"],
                "approved": data.get("approved"),
            }
            for sid, data in scopes_store.items()
        ],
    }


@app.get("/scopes/{scope_id}")
async def get_scope(scope_id: str):
    """Get a specific scope with its proposal."""
    data = scopes_store.get(scope_id)
    if not data:
        raise HTTPException(status_code=404, detail="Scope not found")

    return {
        "scope_id": scope_id,
        "scope": data["scope"].to_dict(),
        "proposal": data["proposal"],
        "approved": data.get("approved"),
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "knowledge_brain_api": settings.knowledge_brain_api,
        "scopes_count": len(scopes_store),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.meeting_scope_port)
