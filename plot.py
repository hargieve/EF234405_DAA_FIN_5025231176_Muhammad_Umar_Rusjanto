"""
plot.py — Reads data/results.csv and produces two figures:
  1. Runtime vs n (mean + all trials) for Dijkstra and BFS — linear scale
  2. Runtime vs n on log-log axes — for estimating empirical growth exponent

Usage
-----
    python plot.py

Output
------
    data/runtime_plot.png    — linear-scale runtime comparison
    data/loglog_plot.png     — log-log scale for exponent estimation
"""

from __future__ import annotations
import csv
from pathlib import Path
import statistics

# We use matplotlib — cite in README and report
try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("Agg")   # headless rendering (no display required)
except ImportError:
    raise SystemExit("matplotlib not found. Run: pip install matplotlib")


INPUT_CSV = Path("data/results.csv")
OUT_LINEAR = Path("data/runtime_plot.png")
OUT_LOGLOG = Path("data/loglog_plot.png")


def load_results(path: Path) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def group_by_n(rows: list[dict]) -> dict[int, dict[str, list[float]]]:
    """Group timing data by n. Returns {n: {"dijkstra": [...], "bfs": [...]}}"""
    groups: dict[int, dict[str, list[float]]] = {}
    for row in rows:
        n = int(row["n"])
        if n not in groups:
            groups[n] = {"dijkstra": [], "bfs": []}
        groups[n]["dijkstra"].append(float(row["dijkstra_ms"]))
        groups[n]["bfs"].append(float(row["bfs_ms"]))
    return groups


def estimate_exponent(ns: list[int], means: list[float]) -> float:
    """Estimate power-law exponent via log-log linear regression."""
    import math
    log_n = [math.log(n) for n in ns]
    log_t = [math.log(t) for t in means]
    n_pts = len(log_n)
    mean_x = sum(log_n) / n_pts
    mean_y = sum(log_t) / n_pts
    num = sum((log_n[i] - mean_x) * (log_t[i] - mean_y) for i in range(n_pts))
    den = sum((log_n[i] - mean_x) ** 2 for i in range(n_pts))
    return num / den if den != 0 else float("nan")


def plot_linear(groups: dict, ns: list[int]) -> None:
    dijk_means = [statistics.mean(groups[n]["dijkstra"]) for n in ns]
    bfs_means  = [statistics.mean(groups[n]["bfs"])      for n in ns]

    fig, ax = plt.subplots(figsize=(8, 5))

    # Plot individual trial points (light, small)
    for n in ns:
        ax.scatter([n] * len(groups[n]["dijkstra"]), groups[n]["dijkstra"],
                   color="#378ADD", alpha=0.3, s=20)
        ax.scatter([n] * len(groups[n]["bfs"]), groups[n]["bfs"],
                   color="#1D9E75", alpha=0.3, s=20)

    # Plot means
    ax.plot(ns, dijk_means, "o-", color="#185FA5", linewidth=2,
            markersize=6, label="Dijkstra (min-cost)")
    ax.plot(ns, bfs_means,  "s-", color="#0F6E56", linewidth=2,
            markersize=6, label="BFS (min-hops)")

    ax.set_xlabel("Number of airports (n)", fontsize=12)
    ax.set_ylabel("Runtime (ms)", fontsize=12)
    ax.set_title("Runtime vs Graph Size — Dijkstra vs BFS", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(OUT_LINEAR, dpi=150)
    print(f"Saved {OUT_LINEAR}")
    plt.close(fig)


def plot_loglog(groups: dict, ns: list[int]) -> None:
    dijk_means = [statistics.mean(groups[n]["dijkstra"]) for n in ns]
    bfs_means  = [statistics.mean(groups[n]["bfs"])      for n in ns]

    exp_d = estimate_exponent(ns, dijk_means)
    exp_b = estimate_exponent(ns, bfs_means)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.loglog(ns, dijk_means, "o-", color="#185FA5", linewidth=2,
              markersize=6, label=f"Dijkstra (slope ≈ {exp_d:.2f})")
    ax.loglog(ns, bfs_means,  "s-", color="#0F6E56", linewidth=2,
              markersize=6, label=f"BFS (slope ≈ {exp_b:.2f})")

    ax.set_xlabel("Number of airports (n)  [log scale]", fontsize=12)
    ax.set_ylabel("Runtime (ms)  [log scale]", fontsize=12)
    ax.set_title("Log-log Runtime Plot — Empirical Exponent Estimation", fontsize=13)
    ax.legend(fontsize=11)
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    fig.tight_layout()
    fig.savefig(OUT_LOGLOG, dpi=150)
    print(f"Saved {OUT_LOGLOG}")
    plt.close(fig)

    print(f"\nEmpirical growth exponents:")
    print(f"  Dijkstra: {exp_d:.3f}  (theoretical: ~1.0 for n log n on sparse graphs)")
    print(f"  BFS:      {exp_b:.3f}  (theoretical: ~1.0 for O(V+E) on sparse graphs)")


def main() -> None:
    rows = load_results(INPUT_CSV)
    groups = group_by_n(rows)
    ns = sorted(groups.keys())
    plot_linear(groups, ns)
    plot_loglog(groups, ns)


if __name__ == "__main__":
    main()
