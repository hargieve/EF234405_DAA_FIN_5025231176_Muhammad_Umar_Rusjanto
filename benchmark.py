"""
benchmark.py — One-command benchmark harness.

Sweeps n over 5 sizes spanning two orders of magnitude,
times Dijkstra and BFS on the same graph instances,
and writes results to data/results.csv.

Usage
-----
    python benchmark.py

Output
------
    data/results.csv   — timing data (one row per (size, trial))
    Prints summary table to stdout.

Design notes
------------
- Random seed is FIXED (42) for full reproducibility.
- Each (n, trial) generates a fresh graph so timing includes graph construction,
  matching real use — algorithm timing is measured separately and excludes it.
- We run TRIALS repetitions per size and report the mean, to reduce noise.
- time.perf_counter() is used (highest resolution wall-clock timer in Python).
"""

from __future__ import annotations
import csv
import os
import random
import time
from pathlib import Path

from generator import generate_flight_network
from dijkstra import min_cost_path
from bfs import min_hops_path

# ── Configuration ────────────────────────────────────────────────────────────

SIZES = [100, 500, 1_000, 5_000, 10_000]   # n values (airports)
TRIALS = 5                                   # repetitions per size
SEED = 42                                    # fixed RNG seed — DO NOT CHANGE
OUTPUT_CSV = Path("data/results.csv")

# ── Helpers ──────────────────────────────────────────────────────────────────


def pick_endpoints(airports: list[str], rng: random.Random) -> tuple[str, str]:
    """Pick a random (src, dst) pair that are not the same airport."""
    src, dst = rng.sample(airports, k=2)
    return src, dst


def time_algorithm(fn, *args) -> tuple[float, object]:
    """Return (elapsed_seconds, result) for a single call."""
    t0 = time.perf_counter()
    result = fn(*args)
    t1 = time.perf_counter()
    return t1 - t0, result


# ── Main benchmark ────────────────────────────────────────────────────────────


def run_benchmark() -> None:
    os.makedirs("data", exist_ok=True)

    rows: list[dict] = []

    print(f"{'n':>8}  {'trial':>5}  {'dijkstra_ms':>12}  {'bfs_ms':>10}  "
          f"{'dijk_cost':>12}  {'bfs_hops':>9}  {'same_reachable':>14}")
    print("-" * 80)

    for n in SIZES:
        for trial in range(1, TRIALS + 1):
            # Fresh graph per trial; seed is deterministic given (n, trial)
            trial_seed = SEED + n * 1000 + trial
            graph, airports = generate_flight_network(n=n, seed=trial_seed)

            # Same endpoints for both algorithms on this instance
            rng = random.Random(trial_seed)
            src, dst = pick_endpoints(airports, rng)

            # Time Dijkstra
            dijk_time, (dijk_cost, dijk_path) = time_algorithm(
                min_cost_path, graph, src, dst
            )

            # Time BFS
            bfs_time, (bfs_hops, bfs_path) = time_algorithm(
                min_hops_path, graph, src, dst
            )

            # Cross-check: both should agree on reachability
            dijk_reachable = dijk_cost < float("inf")
            bfs_reachable = bfs_hops < float("inf")
            same_reachable = dijk_reachable == bfs_reachable

            row = {
                "n": n,
                "trial": trial,
                "seed": trial_seed,
                "src": src,
                "dst": dst,
                "dijkstra_ms": round(dijk_time * 1000, 4),
                "bfs_ms": round(bfs_time * 1000, 4),
                "dijkstra_cost": round(dijk_cost, 2) if dijk_reachable else "inf",
                "bfs_hops": bfs_hops if bfs_reachable else "inf",
                "same_reachable": same_reachable,
                "num_flights": graph.num_flights,
            }
            rows.append(row)

            print(f"{n:>8}  {trial:>5}  {dijk_time*1000:>12.4f}  "
                  f"{bfs_time*1000:>10.4f}  "
                  f"{str(row['dijkstra_cost']):>12}  "
                  f"{str(row['bfs_hops']):>9}  "
                  f"{str(same_reachable):>14}")

    # Write CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nResults written to {OUTPUT_CSV}")

    # Print mean summary
    print(f"\n{'n':>8}  {'mean_dijkstra_ms':>18}  {'mean_bfs_ms':>13}  {'speedup':>9}")
    print("-" * 55)
    for n in SIZES:
        n_rows = [r for r in rows if r["n"] == n]
        mean_d = sum(r["dijkstra_ms"] for r in n_rows) / len(n_rows)
        mean_b = sum(r["bfs_ms"] for r in n_rows) / len(n_rows)
        speedup = mean_d / mean_b if mean_b > 0 else float("inf")
        print(f"{n:>8}  {mean_d:>18.4f}  {mean_b:>13.4f}  {speedup:>9.2f}x")


if __name__ == "__main__":
    run_benchmark()
