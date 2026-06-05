"""
graph.py — FlightGraph: shared graph representation for both algorithms.

Adjacency list: dict[str, list[tuple[str, float]]]
  key   = IATA airport code (e.g. "CGK")
  value = list of (neighbour_code, fare_usd) tuples

Space complexity: O(V + E)
"""

from __future__ import annotations
import csv
from pathlib import Path


class FlightGraph:
    """Weighted directed graph representing a flight network."""

    def __init__(self) -> None:
        # adj[u] = [(v, w), ...] — outgoing edges from u
        self._adj: dict[str, list[tuple[str, float]]] = {}

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def add_airport(self, code: str) -> None:
        """Ensure airport exists as a vertex (even if isolated)."""
        if code not in self._adj:
            self._adj[code] = []

    def add_flight(self, src: str, dst: str, fare: float) -> None:
        """Add a directed edge src → dst with given fare."""
        if fare < 0:
            raise ValueError(f"Negative fare {fare} on {src}→{dst}; Dijkstra requires non-negative weights.")
        self.add_airport(src)
        self.add_airport(dst)
        self._adj[src].append((dst, fare))

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def neighbours(self, code: str) -> list[tuple[str, float]]:
        """Return list of (neighbour, fare) for outgoing edges from code."""
        return self._adj.get(code, [])

    def airports(self) -> list[str]:
        """Return sorted list of all airport codes (vertices)."""
        return sorted(self._adj.keys())

    @property
    def num_airports(self) -> int:
        return len(self._adj)

    @property
    def num_flights(self) -> int:
        return sum(len(nbrs) for nbrs in self._adj.values())

    # ------------------------------------------------------------------
    # I/O
    # ------------------------------------------------------------------

    @classmethod
    def from_csv(cls, path: str | Path) -> "FlightGraph":
        """
        Load from a CSV with columns: src,dst,fare
        Header row is expected and skipped.
        """
        g = cls()
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                g.add_flight(row["src"].strip(), row["dst"].strip(), float(row["fare"]))
        return g

    def to_csv(self, path: str | Path) -> None:
        """Serialise edge list to CSV."""
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["src", "dst", "fare"])
            for src, edges in self._adj.items():
                for dst, fare in edges:
                    writer.writerow([src, dst, fare])

    # ------------------------------------------------------------------
    # Dunder
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"FlightGraph(airports={self.num_airports}, flights={self.num_flights})"
