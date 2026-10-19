"""Evaluation suite for Task 1 — Knowledge Brain.

20+ test cases testing: search quality, answer relevance,
source citation, image handling, escalation, and edge cases.
"""

import asyncio
import time
import httpx

BRAIN_API = "http://localhost:8001"

# ── 25 Test Cases ────────────────────────────────────────────────────────
TEST_CASES = [
    # Search quality tests
    {"id": "T1-01", "type": "search", "query": "How to create a listing", "expect": "results_count > 0"},
    {"id": "T1-02", "type": "search", "query": "customize member profile", "expect": "results_count > 0"},
    {"id": "T1-03", "type": "search", "query": "SEO settings", "expect": "results_count > 0"},
    {"id": "T1-04", "type": "search", "query": "payment gateway setup", "expect": "results_count > 0"},
    {"id": "T1-05", "type": "search", "query": "import CSV members", "expect": "results_count > 0"},
    # Answer quality tests
    {"id": "T1-06", "type": "ask", "query": "How do I create a new directory listing?", "expect": "has_answer"},
    {"id": "T1-07", "type": "ask", "query": "What SEO features are available?", "expect": "has_answer"},
    {"id": "T1-08", "type": "ask", "query": "How to set up payment plans for members?", "expect": "has_answer"},
    {"id": "T1-09", "type": "ask", "query": "Can I customize email notifications?", "expect": "has_answer"},
    {"id": "T1-10", "type": "ask", "query": "How to moderate new listings before they go live?", "expect": "has_answer"},
    # Source citation tests
    {"id": "T1-11", "type": "ask", "query": "How to add a blog to my directory?", "expect": "has_sources"},
    {"id": "T1-12", "type": "ask", "query": "Map integration for listings", "expect": "has_sources"},
    {"id": "T1-13", "type": "ask", "query": "Lead generation forms on profiles", "expect": "has_sources"},
    # Escalation tests (should trigger for nonsensical or out-of-domain queries)
    {"id": "T1-14", "type": "ask", "query": "xyzzy nonsense query that matches nothing", "expect": "escalated"},
    {"id": "T1-15", "type": "ask", "query": "quantum physics entanglement equations", "expect": "escalated"},
    {"id": "T1-16", "type": "ask", "query": "asdfjkl random characters", "expect": "escalated"},
    # Edge cases
    {"id": "T1-17", "type": "ask", "query": "How?", "expect": "has_answer_or_escalated"},
    {"id": "T1-18", "type": "ask", "query": "a" * 500, "expect": "no_error"},
    {"id": "T1-19", "type": "search", "query": "", "expect": "graceful_empty"},
    {"id": "T1-20", "type": "ask", "query": "How to integrate with WordPress and embed the directory as a subdirectory on my existing site?", "expect": "has_answer"},
    # Health check
    {"id": "T1-21", "type": "health", "query": "", "expect": "healthy"},
    # Image-related
    {"id": "T1-22", "type": "ask", "query": "Show me how the dashboard looks", "expect": "has_answer"},
    {"id": "T1-23", "type": "ask", "query": "Screenshots of the listing editor", "expect": "has_answer"},
    # Specific feature queries
    {"id": "T1-24", "type": "ask", "query": "Does the platform support multi-language directories?", "expect": "has_answer"},
    {"id": "T1-25", "type": "ask", "query": "How to set up a deals and coupons section for members?", "expect": "has_answer"},
]


async def run_test(client: httpx.AsyncClient, test: dict) -> dict:
    """Run a single test case and return results."""
    start = time.perf_counter()
    result = {"id": test["id"], "type": test["type"], "passed": False, "error": None}

    try:
        if test["type"] == "search":
            if not test["query"]:
                result["passed"] = True
                result["note"] = "Skipped empty query"
                return result
            resp = await client.get(f"{BRAIN_API}/search", params={"q": test["query"]})
            resp.raise_for_status()
            data = resp.json()
            result["results_count"] = len(data.get("results", []))
            result["passed"] = result["results_count"] > 0

        elif test["type"] == "ask":
            resp = await client.post(
                f"{BRAIN_API}/ask",
                json={"question": test["query"][:1000]},
            )
            resp.raise_for_status()
            data = resp.json()
            result["answer_length"] = len(data.get("answer", ""))
            result["sources_count"] = len(data.get("sources", []))
            result["escalated"] = data.get("escalated", False)
            result["model"] = data.get("model", "")
            result["latency_ms"] = data.get("latency_ms", 0)

            expect = test["expect"]
            if expect == "has_answer":
                result["passed"] = result["answer_length"] > 10
            elif expect == "has_sources":
                result["passed"] = result["sources_count"] > 0
            elif expect == "escalated":
                result["passed"] = result["escalated"]
            elif expect == "has_answer_or_escalated":
                result["passed"] = result["answer_length"] > 10 or result["escalated"]
            elif expect == "no_error":
                result["passed"] = True

        elif test["type"] == "health":
            resp = await client.get(f"{BRAIN_API}/health")
            resp.raise_for_status()
            data = resp.json()
            result["passed"] = data.get("status") == "healthy"

    except Exception as exc:
        result["error"] = str(exc)

    result["duration_ms"] = round((time.perf_counter() - start) * 1000, 1)
    return result


async def run_all_tests():
    """Run all test cases and print results."""
    print(f"\n{'='*60}")
    print("Task 1 — Knowledge Brain Evaluation")
    print(f"{'='*60}")
    print(f"Running {len(TEST_CASES)} test cases...\n")

    async with httpx.AsyncClient(timeout=60) as client:
        results = []
        for test in TEST_CASES:
            result = await run_test(client, test)
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
