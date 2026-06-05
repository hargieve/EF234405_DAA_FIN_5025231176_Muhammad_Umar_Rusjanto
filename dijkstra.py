"""
dijkstra.py — Algorithm A: minimum-cost path using Dijkstra with a binary min-heap.

All core logic is original (no networkx or similar).
heapq is a standard-library data structure (allowed per spec).

Time  complexity: O((V + E) log V)
Space complexity: O(V + E)
"""

from __future__ import annotations
import heapq
import math
from graph import FlightGraph


def min_cost_path(
    graph: FlightGraph,
    src: str,
    dst: str,
) -> tuple[float, list[str]]:
    """
    Find the minimum-fare path from src to dst using Dijkstra's algorithm.

    Returns
    -------
    (total_fare, path)
        total_fare : float — sum of fares along the path (math.inf if unreachable)
        path       : list[str] — ordered list of airport codes including src and dst
                     (empty list if unreachable)

    Algorithm
    ---------
    Maintain a min-heap of (cumulative_cost, airport).
    For each popped node u:
        - if already finalised, skip (lazy deletion of stale heap entries)
        - otherwise mark finalised, record predecessor
        - relax each outgoing edge (u, v, w):
              if dist[u] + w < dist[v]: update dist[v], push to heap

    Correctness: the greedy invariant holds because all weights are non-negative —
    the first time a node is popped it carries the globally minimal cost to it.
    (See §3 of the report for the full proof.)
    """
    # --- Initialisation ---
    dist: dict[str, float] = {a: math.inf for a in graph.airports()}
    dist[src] = 0.0
    prev: dict[str, str | None] = {a: None for a in graph.airports()}
    finalised: set[str] = set()

    # heap entries: (cost, airport_code)
    heap: list[tuple[float, str]] = [(0.0, src)]

    # --- Main loop ---
    while heap:
        cost_u, u = heapq.heappop(heap)

        # Lazy deletion: skip if already finalised (stale heap entry)
        if u in finalised:
            continue
        finalised.add(u)

        # Early exit once destination is finalised
        if u == dst:
            break

        # Relax outgoing edges
        for v, w in graph.neighbours(u):
            new_cost = cost_u + w
            if new_cost < dist[v]:
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(heap, (new_cost, v))

    # --- Reconstruct path ---
    if dist[dst] == math.inf:
        return math.inf, []

    path: list[str] = []
    node: str | None = dst
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()

    return dist[dst], path
