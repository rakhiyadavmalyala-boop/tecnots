# Design Document

## Overview

This system is an AI Tech Consultant composed of three microservices that communicate via REST APIs. The architecture enforces separation of concerns while allowing integration through well-defined interfaces.

## Key Design Decisions

### 1. Microservice Architecture

**Decision:** Three separate FastAPI services, each with its own port.

**Rationale:** The brief explicitly requires Tasks 2 and 3 to call Task 1 through its API, not share code. Separate services enforce this naturally and make the integration testable.

**Trade-off:** More operational complexity (3 processes) vs. clean API boundaries.

### 2. TF-IDF Search Instead of Vector Embeddings

**Decision:** Use scikit-learn's TF-IDF vectorizer with cosine similarity for article search.

**Rationale:**
- Zero external dependencies (no Pinecone, Weaviate, or external embedding API)
- Fast indexing and retrieval for hundreds of articles
- Deterministic and explainable results
- No additional API cost for embeddings

**Trade-off:** Lower semantic understanding than embeddings. Acceptable for a help center with consistent terminology.

### 3. Rule-Based Email Classification

**Decision:** Keyword-based classification instead of LLM classification.

**Rationale:**
- Deterministic and explainable (important for live review)
- Fast (no API call needed for classification)
- Easy to debug and extend
- LLM is used for the harder task (drafting replies)

**Trade-off:** Less accurate than LLM classification for ambiguous emails. Mitigated by the categories being well-defined for a help center context.

### 4. Stub Mode for LLM

**Decision:** All LLM calls go through a single `llm.py` module that returns stub responses when no API key is configured.

**Rationale:**
- Development and testing without API costs
- Clear separation of LLM logic from business logic
- Easy model swapping (configured in .env)

### 5. JSON File Persistence

**Decision:** Store articles, escalations, and feedback as JSON files on disk.

**Rationale:**
- No database setup required
- One-command startup
- Sufficient for the demo scale
- Easy to inspect and debug

**Trade-off:** Not suitable for production scale. Acceptable for a capstone demo.

### 6. Word-Level Edit Distance for Feedback

**Decision:** Use set-based word overlap ratio instead of character-level Levenshtein distance.

**Rationale:**
- Faster to compute
- More meaningful for comparing email drafts (word-level changes matter more than character-level)
- Simple to explain in live review

## Data Flow

### Task 1: Knowledge Brain

```
Crawl → Extract → Index → Search → LLM → Answer
  ↓                                   ↓
Sitemap/Links  →  TF-IDF Matrix    Escalation Queue
```

### Task 2: Inbox Agent

```
Email → Classify → Extract Questions → Query Brain API → Draft → Human Review
                                                            ↓
                                                    Feedback History
                                                            ↓
                                                    Auto-Send Logic
```

### Task 3: Meeting to Scope

```
Transcript → Parse → Extract Requirements → Check Feasibility (Brain API)
                           ↓
                    Estimate Hours → Build Proposal
                           ↓
                    Follow-up → Change Detection → Approval
```

## API Integration Points

| Caller | Endpoint Called | Purpose |
|--------|----------------|---------|
| Task 2 `draft_generator.py` | Task 1 `POST /ask` | Get knowledge base answers for email questions |
| Task 3 `scope_generator.py` | Task 1 `POST /ask` | Check product feasibility of requirements |

## Error Handling Strategy

1. **API failures:** Return graceful degraded responses (draft without KB answers)
2. **Low confidence:** Escalate to human expert (Task 1 threshold: 0.1 cosine similarity)
3. **Invalid input:** Pydantic validation with clear error messages
4. **Missing API key:** Stub mode with clear indicators

## Security Considerations

- API keys stored in `.env` (not committed)
- No authentication on internal APIs (development scope)
- Input length limits via Pydantic validators
- No direct HTML rendering of crawled content
