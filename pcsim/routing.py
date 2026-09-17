"""Routing for each flight window.

The paper decouples routing from scheduling: a robot flying for f_i^new
minutes gets a closed tour from the depot with length <= speed * f_i^new.
Sec. VI uses the meta-heuristic of Lee & Rathinam (SciTech 2024); here each
flight is an orienteering problem solved by prize-per-distance insertion with
2-opt, where a site's prize is the time since it was last visited
(persistent surveillance). Any fuel-constrained router can replace `plan_tour`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Flight:
    robot: int
    start: int                    # first flying slot
    end: int                      # first slot back on the ground
    tour: list[int]               # site indices, depot excluded
    waypoints: np.ndarray         # (k, 2) positions, depot first and last
    times: np.ndarray             # (k,) time at each waypoint [slots]

    def position(self, t: float) -> np.ndarray:
        if t <= self.times[0]:
            return self.waypoints[0]
        if t >= self.times[-1]:
            return self.waypoints[-1]
        k = int(np.searchsorted(self.times, t, side="right")) - 1
        span = self.times[k + 1] - self.times[k]
        a = 0.0 if span <= 0 else (t - self.times[k]) / span
        return (1 - a) * self.waypoints[k] + a * self.waypoints[k + 1]

    def site_times(self) -> list[tuple[int, float]]:
        return list(zip(self.tour, self.times[1:1 + len(self.tour)]))


def tour_length(points: np.ndarray, depot: np.ndarray, tour: list[int]) -> float:
    path = np.vstack([depot, *(points[j] for j in tour), depot]) if tour else np.vstack([depot, depot])
    return float(np.linalg.norm(np.diff(path, axis=0), axis=1).sum())


def two_opt(points: np.ndarray, depot: np.ndarray, tour: list[int]) -> list[int]:
    best, best_len = tour[:], tour_length(points, depot, tour)
    improved = True
    while improved:
        improved = False
        for a in range(len(best) - 1):
            for b in range(a + 1, len(best)):
                cand = best[:a] + best[a:b + 1][::-1] + best[b + 1:]
                cand_len = tour_length(points, depot, cand)
                if cand_len < best_len - 1e-9:
                    best, best_len, improved = cand, cand_len, True
    return best


def plan_tour(points: np.ndarray, depot: np.ndarray, prizes: np.ndarray, budget: float) -> list[int]:
    """Greedy prize/extra-distance insertion, re-optimized with 2-opt after each insertion."""
    tour: list[int] = []
    remaining = set(range(len(points)))
    while True:
        length = tour_length(points, depot, tour)
        best = None
        for j in sorted(remaining):
            for pos in range(len(tour) + 1):
                cand = tour[:pos] + [j] + tour[pos:]
                cand_len = tour_length(points, depot, cand)
                if cand_len > budget:
                    continue
                score = prizes[j] / max(cand_len - length, 1e-6)
                if best is None or score > best[0]:
                    best = (score, cand, j)
        if best is None:
            return tour
        tour = two_opt(points, depot, best[1])
        remaining.discard(best[2])


def plan_flights(windows: list[tuple[int, int, int]], points: np.ndarray, depot: np.ndarray,
                 units_per_slot: float, reuse: dict[tuple[int, int, int], Flight] | None = None,
                 holds: dict[tuple[int, int, int], int] | None = None) -> list[Flight]:
    """Plan windows in takeoff order, sharing site staleness between robots.

    `reuse` maps a window to an already planned flight (flights not affected by
    the delay keep their original routes). `holds` maps a window to extra slots
    the robot loiters at its last site before returning (the unforeseen delay);
    the route itself is planned with the nominal budget.
    """
    reuse = reuse or {}
    holds = holds or {}
    last_visit = np.full(len(points), -1e3)
    flights = []
    for window in sorted(windows, key=lambda w: (w[1], w[0])):
        robot, start, end = window
        if window in reuse:
            flight = reuse[window]
        else:
            hold = holds.get(window, 0)
            tour = plan_tour(points, depot, start - last_visit, (end - start - hold) * units_per_slot)
            flight = _timed_flight(robot, start, end, tour, points, depot, units_per_slot, hold)
        for j, t in flight.site_times():
            last_visit[j] = max(last_visit[j], t)
        flights.append(flight)
    return flights


def _timed_flight(robot, start, end, tour, points, depot, units_per_slot, hold) -> Flight:
    waypoints = [depot] + [points[j] for j in tour] + [depot]
    times = [float(start)]
    for k in range(1, len(waypoints)):
        times.append(times[-1] + float(np.linalg.norm(waypoints[k] - waypoints[k - 1])) / units_per_slot)
    if hold and tour:
        # Loiter at the last site for `hold` slots, then fly home.
        waypoints.insert(-1, waypoints[-2])
        times.insert(-1, times[-2] + hold)
        times[-1] += hold
    return Flight(robot, start, end, list(tour), np.array(waypoints, dtype=float), np.array(times))
