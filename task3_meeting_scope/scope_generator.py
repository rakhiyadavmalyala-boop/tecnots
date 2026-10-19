"""Scope generator — extracts requirements, estimates hours, checks feasibility."""

import logging
from dataclasses import dataclass, field
from typing import Optional

import httpx

from config import settings
from llm import ask as llm_ask
from task3_meeting_scope.transcript_parser import ParsedTranscript

logger = logging.getLogger(__name__)


@dataclass
class Requirement:
    """A single requirement extracted from the meeting."""

    id: str
    title: str
    description: str
    priority: str  # must_have | should_have | nice_to_have
    source_quote: str  # exact quote from transcript
    estimated_hours: float
    feasibility: str  # feasible | needs_research | not_feasible
    feasibility_notes: str = ""


@dataclass
class ScopeOfWork:
    """Complete scope of work from a meeting."""

    meeting_title: str
    requirements: list[Requirement]
    total_hours: float
    assumptions: list[str]
    out_of_scope: list[str]
    risks: list[str]

    def to_dict(self) -> dict:
        return {
            "meeting_title": self.meeting_title,
            "requirements": [
                {
                    "id": r.id,
                    "title": r.title,
                    "description": r.description,
                    "priority": r.priority,
                    "source_quote": r.source_quote,
                    "estimated_hours": r.estimated_hours,
                    "feasibility": r.feasibility,
                    "feasibility_notes": r.feasibility_notes,
                }
                for r in self.requirements
            ],
            "total_hours": self.total_hours,
            "assumptions": self.assumptions,
            "out_of_scope": self.out_of_scope,
            "risks": self.risks,
        }


class ScopeGenerator:
    """Generates scope of work from parsed transcripts using LLM + Knowledge Brain."""

    def __init__(self, brain_api_url: Optional[str] = None):
        self.brain_api = (brain_api_url or settings.knowledge_brain_api).rstrip("/")

    async def check_feasibility(self, requirement: str) -> dict:
        """Check product feasibility by querying Knowledge Brain API.

        This is the required Task 3 → Task 1 integration.
        """
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    f"{self.brain_api}/ask",
                    json={
                        "question": f"Is this feature available or possible: {requirement}",
                        "top_k": 3,
                    },
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                logger.error("Knowledge Brain API call failed: %s", exc)
                return {"answer": "", "sources": []}

    async def generate_scope(
        self,
        transcript: ParsedTranscript,
        model: Optional[str] = None,
    ) -> ScopeOfWork:
        """Generate a complete scope of work from a meeting transcript.

        Steps:
        1. Extract requirements from transcript using LLM
        2. Check each requirement's feasibility against Knowledge Brain
        3. Estimate hours for each requirement
        4. Compile into a scope of work
        """
        # Step 1: Extract requirements using LLM
        system_prompt = (
            "You are a senior tech consultant extracting requirements from a client meeting. "
            "For each requirement found, provide:\n"
            "- A short title\n"
            "- A detailed description\n"
            "- The exact quote from the transcript\n"
            "- Priority: must_have, should_have, or nice_to_have\n"
            "- Estimated hours (be realistic)\n\n"
            "Also list assumptions, out-of-scope items, and risks.\n"
            "Format your response as structured text with clear sections."
        )

        prompt = f"""Meeting Transcript:
{transcript.full_text}

Extract ALL requirements discussed. For each requirement provide:
REQ_ID: R1, R2, etc.
TITLE: short title
DESCRIPTION: detailed description
QUOTE: exact words from transcript
PRIORITY: must_have | should_have | nice_to_have
HOURS: estimated hours

After all requirements, list:
ASSUMPTIONS: (one per line)
OUT_OF_SCOPE: (one per line)
RISKS: (one per line)"""

        llm_response = llm_ask(
            prompt=prompt,
            system=system_prompt,
            model=model,
            max_tokens=2048,
        )

        # Step 2: Parse LLM output into requirements
        requirements = self._parse_requirements(llm_response["answer"])

        # Step 3: Check feasibility for each requirement via Knowledge Brain
        for req in requirements:
            feasibility_result = await self.check_feasibility(req.title)
            answer = feasibility_result.get("answer", "")

            if answer and "[STUB]" not in answer:
                req.feasibility_notes = answer[:300]
                if any(word in answer.lower() for word in
                       ["yes", "available", "supported", "built-in", "possible"]):
                    req.feasibility = "feasible"
                elif any(word in answer.lower() for word in
                         ["not available", "not supported", "cannot", "no"]):
                    req.feasibility = "not_feasible"
                else:
                    req.feasibility = "needs_research"

        # Step 4: Parse assumptions, out-of-scope, risks
        assumptions = self._extract_section(llm_response["answer"], "ASSUMPTIONS")
        out_of_scope = self._extract_section(llm_response["answer"], "OUT_OF_SCOPE")
        risks = self._extract_section(llm_response["answer"], "RISKS")

        total_hours = sum(r.estimated_hours for r in requirements)

        return ScopeOfWork(
            meeting_title=transcript.title,
            requirements=requirements,
            total_hours=total_hours,
            assumptions=assumptions,
            out_of_scope=out_of_scope,
            risks=risks,
        )

    def _parse_requirements(self, text: str) -> list[Requirement]:
        """Parse LLM output into Requirement objects."""
        requirements = []
        import re

        # Split by REQ_ID pattern
        blocks = re.split(r"(?=REQ_ID:\s*R\d+)", text)

        for block in blocks:
            if not block.strip():
                continue

            req_id = self._extract_field(block, "REQ_ID") or f"R{len(requirements) + 1}"
            title = self._extract_field(block, "TITLE")
            if not title:
                continue

            description = self._extract_field(block, "DESCRIPTION") or title
            quote = self._extract_field(block, "QUOTE") or ""
            priority = self._extract_field(block, "PRIORITY") or "should_have"
            hours_str = self._extract_field(block, "HOURS") or "4"

            try:
                hours = float(re.search(r"[\d.]+", hours_str).group())
            except (AttributeError, ValueError):
                hours = 4.0

            # Normalize priority
            priority = priority.lower().strip()
            if priority not in ("must_have", "should_have", "nice_to_have"):
                priority = "should_have"

            requirements.append(Requirement(
                id=req_id.strip(),
                title=title,
                description=description,
                priority=priority,
                source_quote=quote,
                estimated_hours=hours,
                feasibility="needs_research",
            ))

        return requirements

    def _extract_field(self, text: str, field_name: str) -> str:
        """Extract a field value from structured LLM output."""
        import re
        pattern = rf"{field_name}:\s*(.+?)(?:\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""

    def _extract_section(self, text: str, section_name: str) -> list[str]:
        """Extract a list section from LLM output."""
        import re
        pattern = rf"{section_name}:\s*\n(.+?)(?:\n[A-Z_]+:|$)"
        match = re.search(pattern, text, re.DOTALL)
        if not match:
            return []

        items = []
        for line in match.group(1).strip().split("\n"):
            line = line.strip().lstrip("-•* ")
            if line:
                items.append(line)
        return items
