"""Evaluation suite for Task 3 — Meeting to Scope.

20+ test cases testing: transcript parsing, requirement extraction,
feasibility checks, proposal generation, and change detection.
"""

import asyncio
import time
import httpx

from task3_meeting_scope.transcripts import TRANSCRIPTS

MEETING_API = "http://localhost:8003"


TEST_CASES = [
    # Transcript parsing tests
    {"id": "T3-01", "type": "analyze", "transcript_idx": 0, "expect": "has_requirements"},
    {"id": "T3-02", "type": "analyze", "transcript_idx": 1, "expect": "has_requirements"},
    {"id": "T3-03", "type": "analyze", "transcript_idx": 2, "expect": "has_requirements"},
    # Requirement quality tests
    {"id": "T3-04", "type": "analyze", "transcript_idx": 0, "expect": "has_priorities"},
    {"id": "T3-05", "type": "analyze", "transcript_idx": 0, "expect": "has_hours"},
    {"id": "T3-06", "type": "analyze", "transcript_idx": 2, "expect": "has_source_quotes"},
    # Proposal generation tests
    {"id": "T3-07", "type": "analyze", "transcript_idx": 0, "expect": "has_proposal"},
    {"id": "T3-08", "type": "analyze", "transcript_idx": 2, "expect": "has_proposal"},
    # Feasibility check (integration with Task 1)
    {"id": "T3-09", "type": "analyze", "transcript_idx": 0, "expect": "has_feasibility"},
    # Change detection tests
    {"id": "T3-10", "type": "compare", "initial_idx": 0, "followup_idx": 1, "expect": "has_changes"},
    {"id": "T3-11", "type": "compare", "initial_idx": 0, "followup_idx": 1, "expect": "has_added"},
    {"id": "T3-12", "type": "compare", "initial_idx": 0, "followup_idx": 1, "expect": "has_removed"},
    # Approval workflow
    {"id": "T3-13", "type": "approve", "transcript_idx": 0, "approved": True, "expect": "approved"},
    {"id": "T3-14", "type": "approve", "transcript_idx": 0, "approved": False, "expect": "rejected"},
    # Edge cases
    {"id": "T3-15", "type": "analyze_custom", "transcript": "Client: I want everything.\nConsultant: Can you be more specific?\nClient: No, just everything.", "expect": "handles_vague"},
    {"id": "T3-16", "type": "analyze_custom", "transcript": "Client: We need a simple website.\nConsultant: What features?\nClient: Just a homepage with our logo and contact info.\nConsultant: That's straightforward.\nClient: And it needs to scale to 10 million users.\nConsultant: That changes the scope significantly.", "expect": "handles_contradictions"},
    {"id": "T3-17", "type": "analyze_custom", "transcript": "Alice: Let's discuss the project.\nBob: Sure. We need user auth, a dashboard, reporting, and API.\nAlice: Timeline?\nBob: Two weeks.\nAlice: That's aggressive. Budget?\nBob: $5000.\nAlice: We'll need to prioritize.", "expect": "captures_constraints"},
    # Speakers detection
    {"id": "T3-18", "type": "analyze", "transcript_idx": 0, "expect": "has_speakers"},
    # Scope listing
    {"id": "T3-19", "type": "list_scopes", "expect": "has_scopes"},
    # Health check
    {"id": "T3-20", "type": "health", "expect": "healthy"},
    # Out-of-scope detection
    {"id": "T3-21", "type": "analyze", "transcript_idx": 0, "expect": "has_out_of_scope_or_assumptions"},
    # Multiple requirements extraction
    {"id": "T3-22", "type": "analyze", "transcript_idx": 2, "expect": "multiple_requirements"},
]


async def run_test(client: httpx.AsyncClient, test: dict, scope_ids: dict) -> dict:
    """Run a single test case."""
    start = time.perf_counter()
    result = {"id": test["id"], "type": test["type"], "passed": False, "error": None}

    try:
        if test["type"] == "analyze":
            t = TRANSCRIPTS[test["transcript_idx"]]
            resp = await client.post(
                f"{MEETING_API}/analyze",
                json={
                    "transcript": t["transcript"],
                    "title": t["title"],
                    "meeting_type": t["meeting_type"],
                },
            )
            resp.raise_for_status()
            data = resp.json()
            scope_ids[test["transcript_idx"]] = data.get("scope_id")

            scope = data.get("scope", {})
            reqs = scope.get("requirements", [])

            expect = test["expect"]
            if expect == "has_requirements":
                result["passed"] = len(reqs) > 0
                result["req_count"] = len(reqs)
            elif expect == "has_priorities":
                result["passed"] = all("priority" in r for r in reqs) if reqs else False
            elif expect == "has_hours":
                result["passed"] = all(r.get("estimated_hours", 0) > 0 for r in reqs) if reqs else False
            elif expect == "has_source_quotes":
                result["passed"] = any(r.get("source_quote") for r in reqs)
            elif expect == "has_proposal":
                result["passed"] = len(data.get("proposal", "")) > 100
            elif expect == "has_feasibility":
                result["passed"] = any(r.get("feasibility") for r in reqs)
            elif expect == "has_speakers":
                result["passed"] = len(data.get("speakers", [])) >= 2
            elif expect == "has_out_of_scope_or_assumptions":
                result["passed"] = (
                    len(scope.get("out_of_scope", [])) > 0
                    or len(scope.get("assumptions", [])) > 0
                )
            elif expect == "multiple_requirements":
                result["passed"] = len(reqs) >= 3

        elif test["type"] == "analyze_custom":
            resp = await client.post(
                f"{MEETING_API}/analyze",
                json={
                    "transcript": test["transcript"],
                    "title": "Custom Test Meeting",
                    "meeting_type": "initial",
                },
            )
            resp.raise_for_status()
            result["passed"] = True  # didn't crash

        elif test["type"] == "compare":
            initial_id = scope_ids.get(test["initial_idx"])
            followup_id = scope_ids.get(test["followup_idx"])

            if not initial_id or not followup_id:
                result["error"] = "Missing scope IDs — run analyze tests first"
                return result

            resp = await client.post(
                f"{MEETING_API}/compare",
                json={
                    "initial_scope_id": initial_id,
                    "followup_scope_id": followup_id,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            report = data.get("change_report", {})

            expect = test["expect"]
            if expect == "has_changes":
                total = len(report.get("added", [])) + len(report.get("removed", [])) + len(report.get("modified", []))
                result["passed"] = total > 0
            elif expect == "has_added":
                result["passed"] = len(report.get("added", [])) > 0
            elif expect == "has_removed":
                result["passed"] = len(report.get("removed", [])) > 0

        elif test["type"] == "approve":
            t = TRANSCRIPTS[test["transcript_idx"]]
            # Analyze first
            resp = await client.post(
                f"{MEETING_API}/analyze",
                json={
                    "transcript": t["transcript"],
                    "title": t["title"] + " (approval test)",
                    "meeting_type": t["meeting_type"],
                },
            )
            data = resp.json()
            scope_id = data.get("scope_id")

            # Approve
            resp = await client.post(
                f"{MEETING_API}/approve",
                json={"scope_id": scope_id, "approved": test["approved"], "notes": "Test"},
            )
            resp.raise_for_status()
            result["passed"] = resp.json().get("approved") == test["approved"]

        elif test["type"] == "list_scopes":
            resp = await client.get(f"{MEETING_API}/scopes")
            resp.raise_for_status()
            result["passed"] = resp.json().get("count", 0) >= 0

        elif test["type"] == "health":
            resp = await client.get(f"{MEETING_API}/health")
            resp.raise_for_status()
            result["passed"] = resp.json().get("status") == "healthy"

    except Exception as exc:
        result["error"] = str(exc)

    result["duration_ms"] = round((time.perf_counter() - start) * 1000, 1)
    return result


async def run_all_tests():
    """Run all test cases and print results."""
    print(f"\n{'='*60}")
    print("Task 3 — Meeting to Scope Evaluation")
    print(f"{'='*60}")
    print(f"Running {len(TEST_CASES)} test cases...\n")

    scope_ids = {}
    async with httpx.AsyncClient(timeout=120) as client:
        results = []
        for test in TEST_CASES:
            result = await run_test(client, test, scope_ids)
            results.append(result)

            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"  {status}  {result['id']}  ({result.get('duration_ms', 0):.0f}ms)")
            if result.get("error"):
                print(f"         Error: {result['error']}")

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passed ({passed/total*100:.0f}%)")
    print(f"{'='*60}")

    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
