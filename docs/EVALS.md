# Evaluation Methodology

## Overview

Each task has 20+ automated test cases. We compare two Claude models on the same inputs and measure quality, cost, and latency.

## Test Case Summary

| Task | Test Cases | Categories |
|------|-----------|------------|
| Task 1 — Knowledge Brain | 25 | Search (5), Answers (5), Citations (3), Escalation (3), Edge Cases (4), Images (2), Features (2), Health (1) |
| Task 2 — Inbox Agent | 22 | Classification (5), Drafting (6), Urgency (2), Questions (1), Feedback (3), Edge Cases (3), Integration (1), Health (1) |
| Task 3 — Meeting to Scope | 22 | Parsing (3), Requirements (3), Proposals (2), Feasibility (1), Change Detection (3), Approval (2), Edge Cases (3), Speakers (1), Listing (1), Scope Items (1), Health (1), Multiple Reqs (1) |
| **Total** | **69** | |

## Evaluation Metrics

### Quality Metrics

- **Answer relevance:** Does the answer address the question?
- **Source accuracy:** Are cited sources relevant?
- **Classification accuracy:** Does email category match expected?
- **Requirement completeness:** Are all discussed requirements captured?
- **Change detection accuracy:** Are scope changes correctly identified?

### Performance Metrics

- **Latency (ms):** End-to-end response time per request
- **Token usage:** Input and output tokens per LLM call
- **Cost per query:** Estimated USD cost based on model pricing

### Reliability Metrics

- **Success rate:** Percentage of test cases that pass
- **Error handling:** Graceful degradation on invalid inputs
- **Escalation accuracy:** Correct identification of unanswerable questions

## Model Comparison

| Metric | Claude Sonnet (Primary) | Claude Haiku (Comparison) |
|--------|------------------------|--------------------------|
| Quality | Higher — longer, more detailed answers | Lower — shorter, sometimes misses nuance |
| Latency | ~2-4 seconds | ~0.5-1 second |
| Cost per query | ~$0.01-0.03 | ~$0.001-0.003 |
| Best for | Customer-facing responses, proposals | Internal classification, quick lookups |

*Note: Exact numbers depend on API key configuration. Run `python -m evals.model_comparison` for real measurements.*

## Known Failures (Required by Brief)

The following are known failure modes documented honestly:

1. **TF-IDF search misses semantic matches:** "How to make my site look good" may not match articles about "theme customization" because TF-IDF is keyword-based.

2. **Email classification ambiguity:** An email like "I can't pay because the payment form is broken" could be classified as either `billing` or `bug_report`. The keyword classifier picks the one with more matches.

3. **Vague meeting transcripts produce generic requirements:** If a client says "I want everything," the LLM extracts vague requirements. Garbage in, garbage out.

4. **Change detection is title-based:** If a requirement title changes between meetings but the content is the same, it will be marked as "added" + "removed" rather than "modified."

5. **Stub mode limits testing:** Without a real API key, LLM-dependent tests show that the pipeline works but can't validate answer quality.

## Running Evaluations

```bash
# Start all services first
python start.py

# In a separate terminal, run all evals
python run_evals.py

# Or run individually
python -m evals.eval_task1
python -m evals.eval_task2
python -m evals.eval_task3
python -m evals.model_comparison
```

## How to Read Results

```
✅ PASS  T1-01  (45ms)     — Test passed, took 45ms
❌ FAIL  T1-14  (120ms)    — Test failed
         Error: ...        — Error details shown
```

Final summary shows pass/fail ratio per task.
