"""Draft generator — queries Knowledge Brain API and drafts email replies."""

import logging
from typing import Optional

import httpx

from config import settings
from llm import ask as llm_ask

logger = logging.getLogger(__name__)


class DraftGenerator:
    """Generates email reply drafts using the Knowledge Brain API + LLM."""

    def __init__(self, brain_api_url: Optional[str] = None):
        self.brain_api = (brain_api_url or settings.knowledge_brain_api).rstrip("/")

    async def query_knowledge_brain(self, question: str) -> dict:
        """Call Task 1's /ask endpoint to get an answer with sources.

        This is the key integration point — Task 2 calls Task 1 via HTTP API.
        """
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                response = await client.post(
                    f"{self.brain_api}/ask",
                    json={"question": question, "top_k": 3},
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPError as exc:
                logger.error("Knowledge Brain API call failed: %s", exc)
                return {
                    "answer": "",
                    "sources": [],
                    "escalated": False,
                }

    async def generate_draft(
        self,
        sender: str,
        subject: str,
        body: str,
        category: str,
        key_questions: list[str],
        model: Optional[str] = None,
    ) -> dict:
        """Generate a draft reply for an incoming email.

        Steps:
        1. Query Knowledge Brain for each key question
        2. Combine the answers into context
        3. Ask LLM to draft a professional reply
        """
        # Step 1: Get answers from Knowledge Brain for each question
        kb_answers = []
        all_sources = []
        escalated_any = False

        questions_to_ask = key_questions if key_questions else [body[:500]]

        for question in questions_to_ask:
            result = await self.query_knowledge_brain(question)
            if result.get("answer"):
                kb_answers.append(result["answer"])
            if result.get("sources"):
                all_sources.extend(result["sources"])
            if result.get("escalated"):
                escalated_any = True

        # Step 2: Build context for the draft
        kb_context = "\n\n".join(kb_answers) if kb_answers else "No relevant information found."

        unique_sources = []
        seen_urls = set()
        for src in all_sources:
            url = src.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_sources.append(src)

        source_refs = "\n".join(
            f"- {src.get('title', 'Untitled')}: {src.get('url', '')}"
            for src in unique_sources[:5]
        )

        # Step 3: Draft the reply using LLM
        system_prompt = (
            "You are a professional customer support agent for Brilliant Directories. "
            "Draft a helpful, friendly email reply. "
            "Use the provided knowledge base answers as your source of truth. "
            "Include relevant links from the sources. "
            "If the question was escalated, acknowledge that a specialist will follow up. "
            "Keep the tone professional but warm."
        )

        prompt = f"""Original email from: {sender}
Subject: {subject}
Body: {body}

Category: {category}
Key questions identified: {', '.join(key_questions) if key_questions else 'None specific'}

Knowledge Base answers:
{kb_context}

Relevant sources:
{source_refs}

Escalated to expert: {escalated_any}

Draft a professional reply email addressing all the customer's concerns."""

        llm_response = llm_ask(
            prompt=prompt,
            system=system_prompt,
            model=model,
        )

        return {
            "draft": llm_response["answer"],
            "sources": unique_sources[:5],
            "escalated": escalated_any,
            "model": llm_response["model"],
            "latency_ms": llm_response["latency_ms"],
            "kb_answers": kb_answers,
        }
