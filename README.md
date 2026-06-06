# Flight Journey Planner
### EF234405 Design & Analysis of Algorithms — Final Exam Capstone

A flight network planner that answers two distinct routing queries on the same weighted directed graph:
- **Min-cost** (Algorithm A — Dijkstra with binary min-heap): cheapest fare path
- **Min-hops** (Algorithm B — BFS): fewest flight legs path

---

## Project Structure

```
flight_planner/
├── graph.py          # FlightGraph: adjacency-list weighted directed graph
├── dijkstra.py       # Algorithm A: Dijkstra min-cost (own implementation)
├── bfs.py            # Algorithm B: BFS min-hops (own implementation)
├── generator.py      # Synthetic hub-and-spoke network generator (seeded)
├── benchmark.py      # Benchmark harness → data/results.csv
├── plot.py           # Plots → data/runtime_plot.png, data/loglog_plot.png
├── demo.py           # CLI interactive demo
├── data/             # Generated CSV outputs (created at runtime)
└── README.md
```

---

## Requirements

- Python 3.10 or higher
- matplotlib (for plotting only)

Install dependencies:
```bash
pip install matplotlib
```

No other external packages are required. All algorithmic logic (`graph.py`, `dijkstra.py`, `bfs.py`, `generator.py`) uses only the Python standard library.

---

## Quick Start

### 1. Run the demo (interactive)
```bash
python demo.py --n 1000
```
Then type any two airport codes shown in the prompt.

### 2. Run the demo with specific airports
```bash
python demo.py --n 1000 --src AAB --dst XYZ
```
> **Tip:** Run `python demo.py --n 1000` first to see available airport codes in the generated network.

### 3. Reproduce the full benchmark (one command)
```bash
python benchmark.py
```
This sweeps n ∈ {100, 500, 1000, 5000, 10000}, runs 5 trials each, and writes `data/results.csv`.

### 4. Generate plots from benchmark data
```bash
python plot.py
```
Outputs:
- `data/runtime_plot.png` — linear-scale runtime comparison
- `data/loglog_plot.png` — log-log plot for empirical exponent estimation

---

## Reproducing Results

All random seeds are fixed. The benchmark uses seed = `42 + n*1000 + trial` for each (n, trial) pair. To reproduce exactly:

```bash
python benchmark.py && python plot.py
```

Expected output summary (reference machine: Intel Core i5, Python 3.11):

| n      | Dijkstra (ms) | BFS (ms) |
|--------|--------------|----------|
| 100    | ~0.1         | ~0.05    |
| 500    | ~0.5         | ~0.2     |
| 1,000  | ~1.2         | ~0.5     |
| 5,000  | ~8.0         | ~3.0     |
| 10,000 | ~18.0        | ~7.0     |

---

## Algorithm Notes

All core algorithmic logic is original. The following standard-library modules are used as data structures only (not as algorithm implementations):

- `heapq` — binary min-heap used inside Dijkstra (standard-library, not an algorithm library)
- `collections.deque` — queue used inside BFS
- `random` — seeded RNG for graph generation
- `matplotlib` — plotting only (not used in algorithms)

---

## Attribution & References

- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to Algorithms* (4th ed.). MIT Press. — Dijkstra §24.3, BFS §22.2.
- Python `heapq` documentation: https://docs.python.org/3/library/heapq.html
- Python `collections.deque` documentation: https://docs.python.org/3/library/collections.html#collections.deque
- `matplotlib` library: https://matplotlib.org/ — used for plotting only.

---

## Team Contributions

| Member | Student ID | Contribution |
|--------|-----------|--------------|
| Muhammad Umar Rusjanto | 5025231176 | [Role] |
