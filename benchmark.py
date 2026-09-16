#!/usr/bin/env python3
"""
QueryPilot Performance Benchmark Script
Tests response times for cached vs uncached queries
"""

import requests
import time
import json
from typing import Dict, List

BASE_URL = "http://localhost:8000"

class Benchmark:
    def __init__(self):
        self.results: List[Dict] = []

    def query(self, question: str, session_id: str = None) -> Dict:
        """Execute a query and measure response time."""
        payload = {
            "question": question,
            "session_id": session_id
        }

        start = time.time()
        response = requests.post(
            f"{BASE_URL}/query",
            json=payload
        )
        elapsed = time.time() - start

        result = {
            "question": question,
            "elapsed_ms": round(elapsed * 1000, 2),
            "status": response.status_code,
            "cached": False
        }

        if response.status_code == 200:
            data = response.json()
            result["cached"] = data.get("from_cache", False)
            result["row_count"] = data.get("row_count", 0)
        else:
            result["error"] = response.text

        self.results.append(result)
        return result

    def print_report(self):
        """Print a formatted performance report."""
        print("\n" + "="*80)
        print("QUERYPILOT PERFORMANCE BENCHMARK REPORT".center(80))
        print("="*80 + "\n")

        cached_times = [r["elapsed_ms"] for r in self.results if r.get("cached")]
        uncached_times = [r["elapsed_ms"] for r in self.results if not r.get("cached")]

        print(f"{'Question':<40} {'Time (ms)':<12} {'Cached?':<10} {'Rows':<8}")
        print("-" * 80)

        for r in self.results:
            question = r["question"][:37] + "..." if len(r["question"]) > 40 else r["question"]
            cached = "✓ YES" if r.get("cached") else "✗ NO"
            rows = r.get("row_count", "N/A")
            print(f"{question:<40} {r['elapsed_ms']:<12.2f} {cached:<10} {rows:<8}")

        print("\n" + "="*80)
        print("SUMMARY".center(80))
        print("="*80)

        if uncached_times:
            avg_uncached = sum(uncached_times) / len(uncached_times)
            print(f"\nUncached queries (first run):")
            print(f"  Count: {len(uncached_times)}")
            print(f"  Average: {avg_uncached:.2f}ms")
            print(f"  Min: {min(uncached_times):.2f}ms")
            print(f"  Max: {max(uncached_times):.2f}ms")

        if cached_times:
            avg_cached = sum(cached_times) / len(cached_times)
            print(f"\nCached queries (repeat runs):")
            print(f"  Count: {len(cached_times)}")
            print(f"  Average: {avg_cached:.2f}ms")
            print(f"  Min: {min(cached_times):.2f}ms")
            print(f"  Max: {max(cached_times):.2f}ms")

        if cached_times and uncached_times:
            speedup = avg_uncached / avg_cached
            print(f"\n🚀 Speedup Factor: {speedup:.1f}x faster (cached vs uncached)")

        print("\n" + "="*80 + "\n")


def main():
    """Run benchmark tests."""
    print("\n📊 Starting QueryPilot Performance Benchmark...")
    print(f"   Target: {BASE_URL}")

    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=2)
        if response.status_code != 200:
            print("\n❌ ERROR: Server is not responding correctly")
            return
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to server at", BASE_URL)
        print("   Make sure FastAPI server is running: python -m uvicorn app.main:app --reload")
        return

    print("✓ Server is running\n")

    benchmark = Benchmark()

    # Test queries
    test_queries = [
        "How many customers are there?",
        "What is the average order value?",
        "Show me the top 5 products by price",
        "Get all orders above 1000",
        "How many customers are there?",  # Repeat - should be cached
        "What is the average order value?",  # Repeat - should be cached
        "Show me the top 5 products by price",  # Repeat - should be cached
    ]

    print("Running queries...\n")

    for i, question in enumerate(test_queries, 1):
        print(f"[{i}/{len(test_queries)}] {question[:50]}...", end=" ", flush=True)
        try:
            result = benchmark.query(question)
            status = "✓" if result["status"] == 200 else "✗"
            cached = "📦 CACHED" if result.get("cached") else "🌐 API"
            print(f"{status} {result['elapsed_ms']:>6.0f}ms {cached}")
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")

    benchmark.print_report()


if __name__ == "__main__":
    main()
