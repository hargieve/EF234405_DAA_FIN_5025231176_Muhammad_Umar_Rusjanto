"""
demo.py — Interactive CLI demo for the Flight Journey Planner.

Shows both the min-cost (Dijkstra) and min-hops (BFS) routes
for a user-supplied origin and destination on a generated or
loaded flight network.

Usage
-----
    # On a generated network of 1000 airports:
    python demo.py --n 1000 --src CGK --dst LHR

    # On a real CSV dataset:
    python demo.py --csv data/flights.csv --src SIN --dst JFK

    # Interactive mode (prompts for src/dst):
    python demo.py --n 1000
"""

from __future__ import annotations
import argparse
import sys
import random

from graph import FlightGraph
from dijkstra import min_cost_path
from bfs import min_hops_path
from generator import generate_flight_network

SEED = 42


def print_route(label: str, metric_name: str, metric_val, path: list[str]) -> None:
    if not path:
        print(f"  {label}: No route found.")
        return
    route_str = " → ".join(path)
    stops = len(path) - 2
    stop_label = "direct" if stops == 0 else f"{stops} stop{'s' if stops != 1 else ''}"
    if isinstance(metric_val, float):
        print(f"  {label}: ${metric_val:,.2f}  |  {stop_label}  |  {route_str}")
    else:
        print(f"  {label}: {metric_val} leg{'s' if metric_val != 1 else ''}  |  {stop_label}  |  {route_str}")


def run_query(graph: FlightGraph, src: str, dst: str) -> None:
    print(f"\n  Route: {src} → {dst}")
    print(f"  Network: {graph.num_airports} airports, {graph.num_flights} flights\n")

    cost, dijk_path = min_cost_path(graph, src, dst)
    hops, bfs_path  = min_hops_path(graph, src, dst)

    print_route("Dijkstra  (min-cost)", "cost", cost, dijk_path)
    print_route("BFS       (min-hops)", "hops", hops, bfs_path)

    # Cross-check reachability
    dijk_reach = cost < float("inf")
    bfs_reach  = hops < float("inf")
    if dijk_reach != bfs_reach:
        print("\n  ⚠ WARNING: reachability disagreement between algorithms!")
    else:
        print(f"\n  ✓ Both algorithms agree on reachability: {'reachable' if dijk_reach else 'unreachable'}")

    if dijk_reach and bfs_reach:
        dijk_hops = len(dijk_path) - 1
        bfs_cost_on_bfs_path = "N/A (BFS ignores fares)"
        print(f"\n  Trade-off summary:")
        print(f"    Min-cost path: ${cost:,.2f}, {dijk_hops} leg(s)")
        print(f"    Min-hops path: {hops} leg(s)  (fare not minimised)")
        if dijk_hops > hops:
            print(f"    ↳ Cheapest route uses {dijk_hops - hops} more leg(s) to save on fare.")
        elif dijk_hops == hops:
            print(f"    ↳ Both routes use the same number of legs.")


def interactive_mode(graph: FlightGraph, airports: list[str]) -> None:
    print(f"\n  Flight network loaded: {graph.num_airports} airports.")
    print(f"  Sample airports: {', '.join(airports[:10])} ...")
    while True:
        print()
        src = input("  Enter origin airport code (or 'q' to quit): ").strip().upper()
        if src == "Q":
            break
        dst = input("  Enter destination airport code: ").strip().upper()
        if dst == "Q":
            break
        if src not in graph.airports():
            print(f"  ✗ '{src}' not found in network.")
            continue
        if dst not in graph.airports():
            print(f"  ✗ '{dst}' not found in network.")
            continue
        run_query(graph, src, dst)


def main() -> None:
    parser = argparse.ArgumentParser(description="Flight Journey Planner — DAA Capstone Demo")
    source_group = parser.add_mutually_exclusive_group()
    source_group.add_argument("--n",   type=int, default=1000,
                              help="Generate a random network with N airports (default: 1000)")
    source_group.add_argument("--csv", type=str,
                              help="Load flight network from a CSV file (columns: src,dst,fare)")
    parser.add_argument("--src",  type=str, help="Origin airport code")
    parser.add_argument("--dst",  type=str, help="Destination airport code")
    parser.add_argument("--seed", type=int, default=SEED, help="RNG seed (default: 42)")
    args = parser.parse_args()

    # --- Load or generate graph ---
    if args.csv:
        print(f"\n  Loading flight network from {args.csv} ...")
        graph = FlightGraph.from_csv(args.csv)
        airports = graph.airports()
    else:
        n = args.n
        print(f"\n  Generating random flight network (n={n}, seed={args.seed}) ...")
        graph, airports = generate_flight_network(n=n, seed=args.seed)

    # --- Run query or interactive mode ---
    if args.src and args.dst:
        src = args.src.upper()
        dst = args.dst.upper()
        if src not in graph.airports():
            print(f"  ✗ '{src}' not in network. Available sample: {airports[:5]}")
            sys.exit(1)
        if dst not in graph.airports():
            print(f"  ✗ '{dst}' not in network. Available sample: {airports[:5]}")
            sys.exit(1)
        run_query(graph, src, dst)
    else:
        interactive_mode(graph, airports)


if __name__ == "__main__":
    main()
