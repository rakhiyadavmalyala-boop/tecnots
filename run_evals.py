"""Run all evaluations across all three tasks.

Usage: python run_evals.py
Requires all three services to be running (python start.py).
"""

import asyncio
import sys


async def main():
    """Run all evaluation suites."""
    print("\n" + "=" * 70)
    print("AI Tech Consultant — Full Evaluation Suite")
    print("=" * 70)
    print("\nMake sure all 3 services are running (python start.py)\n")

    all_results = {}

    # Task 1
    from evals.eval_task1 import run_all_tests as run_t1
    all_results["task1"] = await run_t1()

    # Task 2
    from evals.eval_task2 import run_all_tests as run_t2
    all_results["task2"] = await run_t2()

    # Task 3
    from evals.eval_task3 import run_all_tests as run_t3
    all_results["task3"] = await run_t3()

    # Model comparison
    from evals.model_comparison import run_comparison
    all_results["model_comparison"] = await run_comparison()

    # Final summary
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")

    total_passed = 0
    total_tests = 0
    for task_name in ["task1", "task2", "task3"]:
        results = all_results[task_name]
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        total_passed += passed
        total_tests += total
        pct = passed / total * 100 if total else 0
        status = "✅" if pct >= 60 else "❌"
        print(f"  {status} {task_name}: {passed}/{total} ({pct:.0f}%)")

    overall_pct = total_passed / total_tests * 100 if total_tests else 0
    print(f"\n  Overall: {total_passed}/{total_tests} ({overall_pct:.0f}%)")
    print(f"{'='*70}")


if __name__ == "__main__":
    asyncio.run(main())
