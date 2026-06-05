"""
bfs.py — Algorithm B: minimum-hops path using Breadth-First Search.

All core logic is original.
collections.deque is a standard-library structure (allowed per spec).

Time  complexity: O(V + E)
Space complexity: O(V + E)
"""

from __future__ import annotations
from collections import deque
import math
from graph import FlightGraph


def min_hops_path(
    graph: FlightGraph,
    src: str,
    dst: str,
) -> tuple[int, list[str]]:
    """
    Find the path with the fewest flight legs from src to dst using BFS.

    Returns
    -------
    (hops, path)
        hops : int      — number of flight legs (edges) in the path
                          (math.inf if unreachable, returned as float for uniformity)
        path : list[str] — ordered airport codes including src and dst
                           (empty list if unreachable)

    Algorithm
    ---------
    BFS explores nodes level by level, where each level corresponds to one
    additional flight leg.  The first time dst is reached it is guaranteed to
    be via the fewest legs, because BFS never revisits a shorter-level path.

    Edge weights (fares) are IGNORED — every edge costs 1 hop.
    This is valid because "fewest stopovers" is an unweighted shortest-path
    problem on the same directed graph.

    Correctness: BFS processes nodes in non-decreasing hop-distance order.
    Once dst is dequeued its hop count equals the shortest-hop distance.
    (See §3 of the report for the full proof.)
    """
    if src == dst:
        return 0, [src]

    # visited tracks airports already enqueued (not just dequeued)
    # to avoid re-adding them at a worse hop count.
    visited: set[str] = {src}
    prev: dict[str, str | None] = {src: None}

    # deque entries: airport_code
    queue: deque[str] = deque([src])

    # --- Main BFS loop ---
    while queue:
        u = queue.popleft()

        for v, _fare in graph.neighbours(u):
            if v in visited:
                continue
            visited.add(v)
            prev[v] = u

            if v == dst:
                # Reconstruct immediately — this IS the shortest hop path
                path: list[str] = []
                node: str | None = dst
                while node is not None:
                    path.append(node)
                    node = prev[node]
                path.reverse()
                return len(path) - 1, path

            queue.append(v)

    # dst unreachable
    return math.inf, []
