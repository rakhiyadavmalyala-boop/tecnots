# AI Tech Consultant

An AI-powered tech consultant system with three interconnected components: Knowledge Brain, Inbox Agent, and Meeting to Scope.

## Quick Start

```bash
# 1. Clone and setup
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start all services (one command)
python start.py
```

This starts:
- **Task 1 — Knowledge Brain** on `http://localhost:8001`
- **Task 2 — Inbox Agent** on `http://localhost:8002`
- **Task 3 — Meeting to Scope** on `http://localhost:8003`

## Architecture

```
┌─────────────────┐     HTTP API      ┌─────────────────┐
│  Task 2: Inbox  │ ────────────────► │  Task 1: Brain  │
│  Agent (:8002)  │                   │  (:8001)         │
└─────────────────┘                   └─────────────────┘
                                             ▲
┌─────────────────┐     HTTP API             │
│  Task 3: Meeting│ ────────────────────────┘
│  to Scope(:8003)│
└─────────────────┘
```

**Key rule:** Tasks 2 and 3 call Task 1 through its REST API — no shared code or imports.

## API Endpoints

### Task 1 — Knowledge Brain (`:8001`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ask` | Answer a question with source citations |
| GET | `/search?q=` | Raw search without LLM |
| POST | `/crawl` | Trigger full re-crawl |
| GET | `/articles/{id}` | Get full article |
| GET | `/escalations` | List pending escalations |
| POST | `/escalations/{id}/answer` | Answer an escalation |
| GET | `/health` | Health check |

### Task 2 — Inbox Agent (`:8002`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/process` | Process email → classify + draft reply |
| POST | `/feedback` | Submit human feedback on draft |
| GET | `/feedback/stats` | Feedback statistics |
| GET | `/feedback/history` | Recent feedback records |
| GET | `/health` | Health check |

### Task 3 — Meeting to Scope (`:8003`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/analyze` | Analyze transcript → scope + proposal |
| POST | `/compare` | Compare initial vs follow-up scope |
| POST | `/approve` | Approve/reject a scope |
| GET | `/scopes` | List all scopes |
| GET | `/scopes/{id}` | Get specific scope |
| GET | `/health` | Health check |

## Running Evaluations

```bash
# Run all evaluations (requires all 3 services running)
python run_evals.py

# Individual task evaluations
python -m evals.eval_task1
python -m evals.eval_task2
python -m evals.eval_task3

# Model comparison
python -m evals.model_comparison
```

## Project Structure

```
├── config.py                  # Shared configuration
├── llm.py                     # Claude LLM integration
├── task1_knowledge_brain/     # Knowledge Brain service
│   ├── main.py                # FastAPI app
│   ├── crawler.py             # Sitemap + page crawler
│   ├── extractor.py           # Text + image extraction
│   ├── search.py              # TF-IDF search engine
│   ├── escalation.py          # Human escalation queue
│   └── scheduler.py           # Daily update scheduler
├── task2_inbox_agent/         # Inbox Agent service
│   ├── main.py                # FastAPI app
│   ├── email_processor.py     # Email parsing + classification
│   ├── draft_generator.py     # Reply drafting (calls Task 1 API)
│   ├── feedback.py            # Human feedback + auto-send logic
│   └── test_emails.py         # 50 test emails
├── task3_meeting_scope/       # Meeting to Scope service
│   ├── main.py                # FastAPI app
│   ├── transcript_parser.py   # Meeting transcript parser
│   ├── scope_generator.py     # Requirements + estimates (calls Task 1 API)
│   ├── proposal.py            # Proposal document builder
│   ├── change_detector.py     # Scope change detection
│   └── transcripts.py         # 3 role-played meetings
├── evals/                     # Evaluation suite
│   ├── eval_task1.py          # 25 test cases
│   ├── eval_task2.py          # 22 test cases
│   ├── eval_task3.py          # 22 test cases
│   └── model_comparison.py    # Two-model comparison
├── docs/
│   ├── DESIGN.md              # Architecture decisions
│   ├── EVALS.md               # Evaluation methodology
│   └── AI_LOG.md              # AI tool usage log
├── start.py                   # One-command startup
├── run_evals.py               # Run all evaluations
├── requirements.txt           # Python dependencies
└── .env.example               # Environment template
```

## Configuration

Copy `.env.example` to `.env` and set:
- `ANTHROPIC_API_KEY` — your Claude API key
- `HELP_CENTER_URL` — the help center URL to crawl

The system works in stub mode without an API key (returns placeholder responses).
