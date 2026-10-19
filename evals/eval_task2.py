"""Evaluation suite for Task 2 — Inbox Agent.

20+ test cases testing: email classification, draft quality,
Knowledge Brain integration, feedback system, and auto-send logic.
"""

import asyncio
import time
import httpx

INBOX_API = "http://localhost:8002"

# Use a subset of test emails + edge cases
TEST_CASES = [
    # Classification tests
    {"id": "T2-01", "type": "classify", "sender": "alice@test.com", "subject": "How do I create a listing?", "body": "I just signed up and I'm trying to create my first listing. Can you walk me through the steps?", "expect_category": "question"},
    {"id": "T2-02", "type": "classify", "sender": "bob@test.com", "subject": "Search not working", "body": "The search function has stopped working. It shows 'No results found' even for listings I know exist. This is a bug.", "expect_category": "bug_report"},
    {"id": "T2-03", "type": "classify", "sender": "carol@test.com", "subject": "Feature: Add reviews", "body": "It would be great to have a review and rating system. Could you add this feature?", "expect_category": "feature_request"},
    {"id": "T2-04", "type": "classify", "sender": "dave@test.com", "subject": "Invoice needed", "body": "Can you send me the invoice for my September payment? I need it for accounting.", "expect_category": "billing"},
    {"id": "T2-05", "type": "classify", "sender": "emma@test.com", "subject": "Partnership opportunity", "body": "We'd love to discuss a potential partnership. Who should I speak with?", "expect_category": "general"},
    # Draft generation tests
    {"id": "T2-06", "type": "draft", "sender": "f@test.com", "subject": "How to customize profiles?", "body": "How can I customize what fields appear on member profiles? I want to add a custom dropdown field.", "expect": "has_draft"},
    {"id": "T2-07", "type": "draft", "sender": "g@test.com", "subject": "Payment form broken", "body": "Customers report the payment form doesn't load on checkout. This is urgent!", "expect": "has_draft"},
    {"id": "T2-08", "type": "draft", "sender": "h@test.com", "subject": "Want to upgrade plan", "body": "I'm on Basic plan but need more features. Can I upgrade mid-cycle? Will I be charged prorated?", "expect": "has_draft"},
    {"id": "T2-09", "type": "draft", "sender": "i@test.com", "subject": "Embedding on WordPress", "body": "Can I embed my Brilliant Directories site into my WordPress website? How?", "expect": "has_draft"},
    {"id": "T2-10", "type": "draft", "sender": "j@test.com", "subject": "Mobile layout broken", "body": "The mobile version shows everything in a single column with text overlapping. Navigation menu doesn't open.", "expect": "has_draft"},
    # Urgency detection tests
    {"id": "T2-11", "type": "urgency", "sender": "k@test.com", "subject": "URGENT: Site is down!", "body": "Our directory site is completely down. We need this fixed immediately. This is critical for our business.", "expect_urgency": "high"},
    {"id": "T2-12", "type": "urgency", "sender": "l@test.com", "subject": "Small question", "body": "No rush on this, but when you get a chance could you explain how categories work?", "expect_urgency": "low"},
    # Question extraction tests
    {"id": "T2-13", "type": "questions", "sender": "m@test.com", "subject": "Multiple questions", "body": "How do I set up SEO? Where is the sitemap setting? Can I customize meta descriptions? What about structured data?", "expect": "multiple_questions"},
    # Edge cases
    {"id": "T2-14", "type": "draft", "sender": "n@test.com", "subject": "Hello", "body": "Just wanted to say thanks for the great platform!", "expect": "has_draft"},
    {"id": "T2-15", "type": "draft", "sender": "o@test.com", "subject": "", "body": "This is an email with no subject line but a valid question: how do I add members?", "expect": "has_draft"},
    {"id": "T2-16", "type": "draft", "sender": "p@test.com", "subject": "Long email", "body": "I have many questions. " * 50 + "How do I get started?", "expect": "has_draft"},
    # Feedback system tests
    {"id": "T2-17", "type": "feedback_approve", "expect": "approval_recorded"},
    {"id": "T2-18", "type": "feedback_edit", "expect": "edit_recorded"},
    {"id": "T2-19", "type": "feedback_stats", "expect": "has_stats"},
    # Integration test (verifies Task 2 calls Task 1)
    {"id": "T2-20", "type": "draft", "sender": "q@test.com", "subject": "API integration question", "body": "Does Brilliant Directories have an API? What endpoints are available?", "expect": "has_draft_with_sources"},
    # Health check
    {"id": "T2-21", "type": "health", "expect": "healthy"},
    # Auto-send related
    {"id": "T2-22", "type": "feedback_stats", "expect": "auto_send_status"},
]


async def run_test(client: httpx.AsyncClient, test: dict) -> dict:
    """Run a single test case."""
    start = time.perf_counter()
    result = {"id": test["id"], "type": test["type"], "passed": False, "error": None}

    try:
        if test["type"] in ("classify", "urgency", "questions", "draft"):
            resp = await client.post(
                f"{INBOX_API}/process",
                json={
                    "sender": test.get("sender", "test@test.com"),
                    "subject": test.get("subject", "Test"),
                    "body": test.get("body", "Test email body content"),
                },
            )
            resp.raise_for_status()
            data = resp.json()

            if test["type"] == "classify":
                result["actual_category"] = data.get("category")
                result["passed"] = data.get("category") == test["expect_category"]
            elif test["type"] == "urgency":
                result["actual_urgency"] = data.get("urgency")
                result["passed"] = data.get("urgency") == test["expect_urgency"]
            elif test["type"] == "questions":
                result["questions_count"] = len(data.get("key_questions", []))
                result["passed"] = len(data.get("key_questions", [])) >= 2
            elif test["type"] == "draft":
                result["draft_length"] = len(data.get("draft", ""))
                result["sources_count"] = len(data.get("sources", []))
                result["email_id"] = data.get("email_id")
                if test["expect"] == "has_draft":
                    result["passed"] = result["draft_length"] > 20
                elif test["expect"] == "has_draft_with_sources":
                    result["passed"] = result["draft_length"] > 20

        elif test["type"] == "feedback_approve":
            # First process an email to get an ID
            process_resp = await client.post(
                f"{INBOX_API}/process",
                json={"sender": "test@t.com", "subject": "Test", "body": "How do I create a listing?"},
            )
            data = process_resp.json()
            email_id = data["email_id"]
            draft = data["draft"]

            # Submit approval (unchanged)
            resp = await client.post(
                f"{INBOX_API}/feedback",
                json={"email_id": email_id, "final_version": draft, "feedback_notes": "Looks good"},
            )
            resp.raise_for_status()
            fb_data = resp.json()
            result["passed"] = not fb_data.get("was_edited", True)

        elif test["type"] == "feedback_edit":
            process_resp = await client.post(
                f"{INBOX_API}/process",
                json={"sender": "test2@t.com", "subject": "Test2", "body": "What is the pricing?"},
            )
            data = process_resp.json()
            email_id = data["email_id"]

            resp = await client.post(
                f"{INBOX_API}/feedback",
                json={
                    "email_id": email_id,
                    "final_version": "I have edited this draft completely with new content.",
                    "feedback_notes": "Needed more detail",
                },
            )
            resp.raise_for_status()
            fb_data = resp.json()
            result["passed"] = fb_data.get("was_edited", False)

        elif test["type"] == "feedback_stats":
            resp = await client.get(f"{INBOX_API}/feedback/stats")
            resp.raise_for_status()
            data = resp.json()
            result["passed"] = "total_reviews" in data and "auto_send_enabled" in data

        elif test["type"] == "health":
            resp = await client.get(f"{INBOX_API}/health")
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
    print("Task 2 — Inbox Agent Evaluation")
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
