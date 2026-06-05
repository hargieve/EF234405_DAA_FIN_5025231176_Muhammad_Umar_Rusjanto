"""
generator.py — Synthetic flight-network generator for benchmarking.

Produces reproducible random directed graphs that mimic real flight networks:
  - Hub-and-spoke topology: a small set of hub airports with many connections,
    plus spoke airports connected mostly through hubs.
  - Edge multiplicity: multiple airlines may operate the same route at different fares.
  - Directed: a route CGK→SIN does not imply SIN→CGK.

Usage
-----
    from generator import generate_flight_network
    g, airports = generate_flight_network(n=1000, seed=42)
"""

from __future__ import annotations
import random
import string
from graph import FlightGraph


def _make_codes(n: int, rng: random.Random) -> list[str]:
    """
    Generate n unique 3-letter airport-style codes.
    Real IATA codes are 3 uppercase letters; we mimic that format.
    """
    pool: set[str] = set()
    letters = string.ascii_uppercase
    while len(pool) < n:
        code = "".join(rng.choices(letters, k=3))
        pool.add(code)
    return sorted(pool)


def generate_flight_network(
    n: int,
    seed: int = 42,
    hub_fraction: float = 0.05,
    spokes_per_hub: int = 8,
    random_edge_factor: float = 2.0,
    fare_min: float = 50.0,
    fare_max: float = 1500.0,
) -> tuple[FlightGraph, list[str]]:
    """
    Generate a random directed flight network with n airports.

    Parameters
    ----------
    n               : number of airports (vertices)
    seed            : RNG seed for reproducibility (MUST be fixed in benchmarks)
    hub_fraction    : fraction of airports designated as hubs
    spokes_per_hub  : each hub gets ~this many spoke connections (bidirectional)
    random_edge_factor : extra random edges ≈ random_edge_factor * n
    fare_min/max    : uniform random fare range in USD

    Returns
    -------
    (FlightGraph, list[str]) — the graph and the sorted list of airport codes
    """
    rng = random.Random(seed)
    airports = _make_codes(n, rng)

    num_hubs = max(1, int(n * hub_fraction))
    hubs = airports[:num_hubs]
    spokes = airports[num_hubs:]

    g = FlightGraph()
    for a in airports:
        g.add_airport(a)

    def add_bidirectional(src: str, dst: str) -> None:
        fare_fwd = round(rng.uniform(fare_min, fare_max), 2)
        fare_bwd = round(rng.uniform(fare_min, fare_max), 2)
        g.add_flight(src, dst, fare_fwd)
        g.add_flight(dst, src, fare_bwd)

    # 1. Connect all hubs to each other (complete hub subgraph)
    for i, h1 in enumerate(hubs):
        for h2 in hubs[i + 1:]:
            add_bidirectional(h1, h2)

    # 2. Connect each spoke to a random subset of hubs
    for spoke in spokes:
        connected_hubs = rng.sample(hubs, k=min(2, len(hubs)))
        for hub in connected_hubs:
            add_bidirectional(spoke, hub)

    # 3. Add random long-haul edges between spokes (simulates direct routes)
    num_random = int(random_edge_factor * n)
    for _ in range(num_random):
        src, dst = rng.sample(airports, k=2)
        fare = round(rng.uniform(fare_min, fare_max), 2)
        g.add_flight(src, dst, fare)

    return g, airports
