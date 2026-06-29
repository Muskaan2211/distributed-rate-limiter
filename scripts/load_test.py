from __future__ import annotations

import argparse
import concurrent.futures
import statistics
import time
import httpx


def hit(url: str, api_key: str) -> tuple[int, float]:
    start = time.perf_counter()
    response = httpx.get(url, headers={"X-API-Key": api_key}, timeout=5)
    return response.status_code, (time.perf_counter() - start) * 1000


def main() -> None:
    parser = argparse.ArgumentParser(description="Simple local burst benchmark for the gateway.")
    parser.add_argument("--url", default="http://localhost:8000/api/v1/limited")
    parser.add_argument("--requests", type=int, default=500)
    parser.add_argument("--concurrency", type=int, default=50)
    args = parser.parse_args()

    latencies = []
    statuses: dict[int, int] = {}
    start = time.perf_counter()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futures = [pool.submit(hit, args.url, f"bench-user-{i % 100}") for i in range(args.requests)]
        for future in concurrent.futures.as_completed(futures):
            status, latency = future.result()
            statuses[status] = statuses.get(status, 0) + 1
            latencies.append(latency)
    elapsed = time.perf_counter() - start
    p99 = statistics.quantiles(latencies, n=100)[98] if len(latencies) >= 100 else max(latencies)
    print({"requests": args.requests, "elapsed_seconds": round(elapsed, 3), "rps": round(args.requests / elapsed, 2), "p99_ms": round(p99, 2), "statuses": statuses})


if __name__ == "__main__":
    main()
