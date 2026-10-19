"""Task 1 — Knowledge Brain API.

FastAPI service that:
- Crawls and indexes a help center
- Answers questions with source citations
- Returns relevant images
- Escalates unanswered questions to human experts
- Updates daily via background scheduler
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from config import settings
from llm import ask as llm_ask
from task1_knowledge_brain.crawler import Crawler
from task1_knowledge_brain.extractor import Extractor
from task1_knowledge_brain.search import KnowledgeSearch, SearchResult
from task1_knowledge_brain.escalation import EscalationManager
from task1_knowledge_brain.scheduler import start_daily_update, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ── Shared state ─────────────────────────────────────────────────────────
search_engine = KnowledgeSearch()
escalation_mgr = EscalationManager()
extractor = Extractor()


def crawl_and_index():
    """Full crawl → extract → index pipeline."""
    crawler = Crawler()
    pages = crawler.crawl()

    articles = []
    for page in pages:
        if page.status_code == 200:
            article = extractor.extract(page.url, page.html)
            if article.content.strip():
                articles.append(article)

    count = search_engine.index(articles)
    logger.info("Crawl complete: indexed %d articles", count)
    return count


# ── App lifecycle ────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load existing data on startup, start scheduler."""
    loaded = search_engine.load_articles()
    if loaded == 0:
        logger.info("No cached articles — run POST /crawl to populate")

    start_daily_update(crawl_and_index)
    yield
    stop_scheduler()


app = FastAPI(
    title="Knowledge Brain",
    description="Task 1 — AI-powered help center Q&A",
    version="1.0.0",
    lifespan=lifespan,
)


# ── Request / Response models ────────────────────────────────────────────
class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=3, description="The user's question")
    top_k: int = Field(5, ge=1, le=20, description="Number of sources to retrieve")
    model: str | None = Field(None, description="Override the LLM model")


class SourceRef(BaseModel):
    url: str
    title: str
    snippet: str
    score: float
    images: list[dict] = []


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceRef]
    escalated: bool = False
    escalation_id: str | None = None
    model: str = ""
    latency_ms: float = 0.0


class EscalationAnswer(BaseModel):
    answer: str


class CrawlResponse(BaseModel):
    articles_indexed: int


# ── Endpoints ────────────────────────────────────────────────────────────
@app.post("/ask", response_model=AnswerResponse)
async def ask_question(req: QuestionRequest):
    """Answer a question using the knowledge base + LLM."""
    results: list[SearchResult] = search_engine.search(req.question, top_k=req.top_k)

    best_score = results[0].score if results else 0.0

    # Check if we should escalate
    if escalation_mgr.should_escalate(best_score, len(results)):
        esc = escalation_mgr.escalate(
            question=req.question,
            reason="Low confidence or no results",
            results_count=len(results),
            best_score=best_score,
        )
        return AnswerResponse(
            answer=(
                "I don't have enough information to answer this confidently. "
                "Your question has been sent to a human expert for review."
            ),
            sources=[
                SourceRef(
                    url=r.url, title=r.title, snippet=r.snippet,
                    score=r.score, images=r.images,
                )
                for r in results
            ],
            escalated=True,
            escalation_id=esc.question_id,
        )

    # Build context from search results
    context_parts = []
    for i, result in enumerate(results, 1):
        context_parts.append(
            f"[Source {i}] {result.title}\nURL: {result.url}\n{result.snippet}"
        )
    context = "\n\n".join(context_parts)

    # Ask LLM to synthesize an answer
    system_prompt = (
        "You are a helpful support agent for the Brilliant Directories platform. "
        "Answer the user's question using ONLY the provided sources. "
        "Cite sources using [Source N] format. "
        "If the sources don't contain enough information, say so clearly. "
        "Include relevant image references when applicable."
    )

    prompt = f"""Sources:
{context}

Question: {req.question}

Answer the question using the sources above. Cite each source you use."""

    llm_response = llm_ask(
        prompt=prompt,
        system=system_prompt,
        model=req.model,
    )

    return AnswerResponse(
        answer=llm_response["answer"],
        sources=[
            SourceRef(
                url=r.url, title=r.title, snippet=r.snippet,
                score=r.score, images=r.images,
            )
            for r in results
        ],
        model=llm_response["model"],
        latency_ms=llm_response["latency_ms"],
    )


@app.post("/crawl", response_model=CrawlResponse)
async def trigger_crawl():
    """Manually trigger a full re-crawl and re-index."""
    count = crawl_and_index()
    return CrawlResponse(articles_indexed=count)


@app.get("/search")
async def search_articles(q: str, top_k: int = 5):
    """Raw search without LLM — returns matching articles."""
    results = search_engine.search(q, top_k=top_k)
    return {
        "query": q,
        "results": [
            {
                "article_id": r.article_id,
                "url": r.url,
                "title": r.title,
                "snippet": r.snippet,
                "score": r.score,
                "images": r.images,
            }
            for r in results
        ],
    }


@app.get("/articles/{article_id}")
async def get_article(article_id: str):
    """Get full article content by ID."""
    article = search_engine.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return {
        "article_id": article.article_id,
        "url": article.url,
        "title": article.title,
        "content": article.content,
        "headings": article.headings,
        "images": [
            {"url": img.url, "alt": img.alt_text, "context": img.context}
            for img in article.images
        ],
    }


@app.get("/escalations")
async def list_escalations():
    """List all pending escalated questions."""
    pending = escalation_mgr.get_pending()
    return {
        "count": len(pending),
        "questions": [
            {
                "question_id": q.question_id,
                "question": q.question,
                "reason": q.reason,
                "created_at": q.created_at,
            }
            for q in pending
        ],
    }


@app.post("/escalations/{question_id}/answer")
async def answer_escalation(question_id: str, body: EscalationAnswer):
    """Submit an expert's answer to an escalated question."""
    result = escalation_mgr.answer_question(question_id, body.answer)
    if not result:
        raise HTTPException(status_code=404, detail="Escalation not found")
    return {"status": "answered", "question_id": question_id}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "articles_count": len(search_engine.articles),
        "pending_escalations": len(escalation_mgr.get_pending()),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=settings.knowledge_brain_port)
