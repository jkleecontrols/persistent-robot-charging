"""Scheduling horizon (Sec. III-A) and its reduction with safety margins (Sec. IV-A)."""

from __future__ import annotations

import heapq
import math
from functools import reduce
from typing import Sequence


def lcm(values: Sequence[int]) -> int:
    """Scheduling horizon T = LCM(T_1, ..., T_n) (Eq. 3)."""
    return reduce(lambda a, b: a * b // math.gcd(a, b), (int(v) for v in values), 1)


def normalize(charging: Sequence[int], operation: Sequence[int]) -> tuple[int, list[int], list[int]]:
    """Divide all times by their GCD so one slot is as long as possible.

    Returns (g, charging / g, operation / g); schedules computed on the
    normalized instance are valid for the original one with slots of length g.
    """
    g = reduce(math.gcd, [int(v) for v in (*charging, *operation)])
    return g, [int(c) // g for c in charging], [int(f) // g for f in operation]


def candidate_cycle_times(cycle_time: int, eps: float) -> list[int]:
    """T_i^set = {V in Z+ : (1 - eps) T_i <= V <= T_i} (Eq. 14)."""
    lower = max(1, math.ceil((1.0 - eps) * cycle_time - 1e-9))
    return list(range(lower, cycle_time + 1))


def dijkstra_lcm(cycle_times: Sequence[int], eps: float | Sequence[float],
                 charging_times: Sequence[int] | None = None) -> tuple[int, list[int]]:
    """Algorithm 1: Dijkstra on the layered candidate graph with path cost = LCM.

    Layer i holds the candidate cycle times of robot i; every vertex of layer i
    is connected to every vertex of layer i+1, plus a source and a sink with
    value 1. The label of a vertex is the LCM of the values along the path.

    If `charging_times` is given, candidates with f_new = V - c_i < 1 are
    dropped (f_new must be a positive integer, Eq. 13).

    Note: LCM is not a monotone path cost in the Dijkstra sense, so this is a
    heuristic, exactly as in the paper; it does not guarantee the minimum LCM.
    """
    n = len(cycle_times)
    eps_list = [eps] * n if isinstance(eps, (int, float)) else list(eps)
    layers = []
    for i, t in enumerate(cycle_times):
        cands = candidate_cycle_times(int(t), eps_list[i])
        if charging_times is not None:
            cands = [v for v in cands if v - charging_times[i] >= 1]
        layers.append(cands)

    # Vertex = (layer, value). Source is layer -1, sink is layer n.
    cost = {(-1, 1): 1}
    pred: dict[tuple[int, int], tuple[int, int] | None] = {(-1, 1): None}
    visited: set[tuple[int, int]] = set()
    pq: list[tuple[int, int, int]] = [(1, -1, 1)]
    while pq:
        min_cost, layer, value = heapq.heappop(pq)
        u = (layer, value)
        if u in visited:
            continue
        if layer == n:
            path = []
            node = pred[u]
            while node is not None and node[0] >= 0:
                path.append(node[1])
                node = pred[node]
            return min_cost, path[::-1]
        visited.add(u)
        next_values = layers[layer + 1] if layer + 1 < n else [1]
        for w in next_values:
            v = (layer + 1, w)
            new_cost = min_cost * w // math.gcd(min_cost, w)
            if new_cost < cost.get(v, math.inf):
                cost[v] = new_cost
                pred[v] = u
                heapq.heappush(pq, (new_cost, layer + 1, w))
    raise ValueError("sink not reachable")


def reduce_operational_times(charging: Sequence[int], operation: Sequence[int],
                             eps: float | Sequence[float]) -> list[int]:
    """Return f_i^new (Eq. 13) chosen by Algorithm 1; c_i is kept fixed."""
    cycle = [c + f for c, f in zip(charging, operation)]
    _, chosen = dijkstra_lcm(cycle, eps, charging_times=charging)
    return [v - c for v, c in zip(chosen, charging)]
