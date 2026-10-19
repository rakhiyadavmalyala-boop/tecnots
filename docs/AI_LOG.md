# AI Tool Usage Log

## Tool Used

**Antigravity** — Google's AI coding assistant (single tool as required by the brief).

## Usage Summary

| Phase | What Was Done | AI Assistance |
|-------|--------------|---------------|
| Planning | Architecture design, file structure, build order | Discussed approach, decided on microservice architecture |
| Task 1 | Crawler, extractor, search, escalation, API | Generated core modules, refined search logic |
| Task 2 | Email processor, draft generator, feedback, API | Generated classification logic, 50 test emails |
| Task 3 | Transcript parser, scope generator, change detector, API | Generated transcript parsing, proposal builder |
| Evals | 69 test cases across 3 tasks, model comparison | Generated test case structures |
| Docs | README, DESIGN, EVALS, AI_LOG | Generated documentation templates, refined content |

## Key Decisions Made with AI

1. **TF-IDF over vector embeddings** — Chose simplicity and zero external dependencies over semantic accuracy.
2. **Rule-based classification** — Chose explainability over LLM-based classification.
3. **JSON file storage** — Chose one-command startup over database setup.
4. **Stub mode** — Designed the system to work without an API key for development.

## What I Understood vs What AI Generated

- **I understood:** The architecture, the requirement for API integration between tasks, the evaluation rubric, and the design rationale.
- **AI generated:** Boilerplate code (FastAPI endpoints, Pydantic models), test email content, meeting transcript content, and documentation structure.
- **I could change live:** Any endpoint, any classification rule, any search parameter, any test case.

## Prompts and Iterations

All conversation history with Antigravity is submitted as required. The main iterations were:

1. Initial plan → approved
2. Task 1 modules → built sequentially (crawler → extractor → search → escalation → API)
3. Task 2 modules → built with API integration to Task 1
4. Task 3 modules → built with API integration to Task 1
5. Evaluations → 69 test cases + model comparison
6. Documentation → 4 required documents

## Self-Improvement

The system improves through:
- **Feedback loop (Task 2):** Human edits to drafts are stored and used as few-shot examples for future drafts
- **Escalation learning (Task 1):** Expert answers to escalated questions can be indexed for future retrieval
- **Change detection (Task 3):** Follow-up meetings capture evolving requirements
