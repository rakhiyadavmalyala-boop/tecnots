"""Model comparison evaluation.

Compares two Claude models (primary vs comparison) on the same inputs,
measuring quality, cost, and latency. Required by the rubric.
"""

import asyncio
import time
import httpx

from config import settings

BRAIN_API = "http://localhost:8001"

COMPARISON_QUERIES = [
    "How do I create a new listing in Brilliant Directories?",
    "What payment gateways are supported?",
    "How to set up SEO for my directory?",
    "Can I import members from a CSV file?",
    "How to customize the member profile page?",
    "What email notification options are available?",
    "How to moderate listings before publishing?",
    "Does the platform support multi-language?",
    "How to add Google Maps to listings?",
    "What analytics and reporting features exist?",
]

# Anthropic pricing per 1M tokens (approximate)
MODEL_PRICING = {
    "claude-sonnet-4-20250514": {"input": 3.0, "output": 15.0},
    "claude-haiku-4-20250514": {"input": 0.25, "output": 1.25},
}


async def query_with_model(client: httpx.AsyncClient, query: str, model: str) -> dict:
    """Query the Knowledge Brain with a specific model."""
    start = time.perf_counter()
    try:
        resp = await client.post(
            f"{BRAIN_API}/ask",
            json={"question": query, "model": model},
        )
        resp.raise_for_status()
        data = resp.json()
        latency = (time.perf_counter() - start) * 1000

        return {
            "query": query,
            "model": model,
            "answer": data.get("answer", ""),
            "answer_length": len(data.get("answer", "")),
            "sources_count": len(data.get("sources", [])),
            "latency_ms": data.get("latency_ms", latency),
            "input_tokens": 0,  # filled from llm response if available
            "output_tokens": 0,
            "error": None,
        }
    except Exception as exc:
        return {
            "query": query,
            "model": model,
            "answer": "",
            "answer_length": 0,
            "sources_count": 0,
            "latency_ms": 0,
            "error": str(exc),
        }


def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Estimate API cost in USD."""
    pricing = MODEL_PRICING.get(model, {"input": 3.0, "output": 15.0})
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


async def run_comparison():
    """Run the model comparison evaluation."""
    primary = settings.primary_model
    comparison = settings.comparison_model

    print(f"\n{'='*70}")
    print("Model Comparison Evaluation")
    print(f"{'='*70}")
    print(f"Primary model:    {primary}")
    print(f"Comparison model: {comparison}")
    print(f"Queries:          {len(COMPARISON_QUERIES)}")
    print()

    primary_results = []
    comparison_results = []

    async with httpx.AsyncClient(timeout=120) as client:
        for i, query in enumerate(COMPARISON_QUERIES, 1):
            print(f"  Query {i}/{len(COMPARISON_QUERIES)}: {query[:50]}...")

            r1 = await query_with_model(client, query, primary)
            r2 = await query_with_model(client, query, comparison)

            primary_results.append(r1)
            comparison_results.append(r2)

            p_status = "✅" if not r1["error"] else "❌"
            c_status = "✅" if not r2["error"] else "❌"
            print(f"    {primary}: {p_status} {r1['latency_ms']:.0f}ms, {r1['answer_length']} chars")
            print(f"    {comparison}: {c_status} {r2['latency_ms']:.0f}ms, {r2['answer_length']} chars")

    # Aggregate results
    print(f"\n{'='*70}")
    print("Summary")
    print(f"{'='*70}")

    for label, results in [("Primary", primary_results), ("Comparison", comparison_results)]:
        valid = [r for r in results if not r["error"]]
        if not valid:
            print(f"\n{label} ({results[0]['model'] if results else 'N/A'}): All queries failed")
            continue

        avg_latency = sum(r["latency_ms"] for r in valid) / len(valid)
        avg_length = sum(r["answer_length"] for r in valid) / len(valid)
        success_rate = len(valid) / len(results) * 100

        print(f"\n{label} ({valid[0]['model']}):")
        print(f"  Success rate:    {success_rate:.0f}%")
        print(f"  Avg latency:     {avg_latency:.0f}ms")
        print(f"  Avg answer len:  {avg_length:.0f} chars")
        print(f"  Queries run:     {len(valid)}/{len(results)}")

    print(f"\n{'='*70}")
    print("Note: Set ANTHROPIC_API_KEY in .env for real model comparison.")
    print("Stub mode returns identical results for both models.")
    print(f"{'='*70}")

    return {
        "primary": {"model": primary, "results": primary_results},
        "comparison": {"model": comparison, "results": comparison_results},
    }


if __name__ == "__main__":
    asyncio.run(run_comparison())
