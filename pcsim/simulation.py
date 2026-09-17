"""Sec. VI simulation of the RA-L 2025 persistent charging paper, end to end.

  parameters -> Dijkstra-LCM operational times (Sec. IV-A)
             -> max-flying-time ILP with m stations (Sec. III-C)
             -> delay re-scheduling of a tardy robot (Sec. IV-B)
             -> routing per flight window -> figures and video
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Callable

import numpy as np

from .config import SimConfig
from .delay import next_charge_start, resolve_delay
from .horizon import lcm, reduce_operational_times
from .ilp import solve_max_flight
from .render import Scenario, animate, plot_schedule, snapshot
from .routing import plan_flights, tour_length
from .timeline import FLYING, battery_levels, build_delayed_timeline, build_timeline

# Values reported in the paper (Sec. VI, Fig. 6) and its dataset repository.
PAPER_SEC_VI = {
    "f_new": [3, 5, 6, 5, 9, 8, 10],
    "selected": [1, 2, 7],
    "safety_margin_min": [1, 2, 4],
    "total_flight_min": 58,
    "horizon_min": 36,
    "delay_needs_station_minute": 1,
    "delay_arrival_minute": 3,
    "delay_original_minute": 10,
    "delay_new_minute": 3,
}


def run(cfg: SimConfig, out: Path, video: bool = True, frames_per_min: int = 6, fps: int = 12,
        log: Callable[[str], None] = print) -> dict:
    """Run the pipeline, write figures/video/summary.json to `out`, return the summary.

    `summary["reproduces_paper"]` is True when every check passes and the
    computed values equal `PAPER_SEC_VI` (only meaningful for the default config).
    """
    out.mkdir(parents=True, exist_ok=True)

    # 1. Safety margins / reduced scheduling horizon.
    f_new = reduce_operational_times(cfg.charging, cfg.operation, cfg.eps)
    horizon_before = lcm([c + f for c, f in zip(cfg.charging, cfg.operation)])

    # 2. Select and schedule robots on the available stations.
    t0 = time.perf_counter()
    schedule = solve_max_flight(cfg.charging, f_new, cfg.stations)
    ilp_seconds = time.perf_counter() - t0

    # 3. Delay of one robot at its first charging slot.
    k = cfg.delayed_robot
    t0 = time.perf_counter()
    res = resolve_delay(schedule, k, next_charge_start(schedule, k, 0), cfg.delay_slots)
    delay_ms = 1e3 * (time.perf_counter() - t0)

    # 4. Execute both scenarios; one horizon of warm-up reaches periodic steady state.
    start, end = -schedule.horizon, cfg.minutes + 1
    points, depot, ups = np.array(cfg.sites), np.array(cfg.depot), cfg.units_per_minute()

    tl_orig = build_timeline(schedule, start, end)
    flights_orig = plan_flights(tl_orig.flights(), points, depot, ups)
    tl_delay = build_delayed_timeline(res, schedule, start, end)
    reuse = {(f.robot, f.start, f.end): f for f in flights_orig}
    holds = {w: cfg.delay_slots for w in tl_delay.flights() if w[0] == k and w[2] == res.arrival}
    flights_delay = plan_flights(tl_delay.flights(), points, depot, ups, reuse=reuse, holds=holds)

    scenarios = []
    for title, tl, flights in (("original schedule", tl_orig, flights_orig),
                               (f"{cfg.name(k)} delayed {cfg.delay_slots} min", tl_delay, flights_delay)):
        levels = battery_levels(tl, cfg.charging, cfg.operation, frames_per_min)
        scenarios.append(Scenario(title, tl, flights, levels, frames_per_min, tl.pad_assignment()))

    # 5. Consistency checks.
    checks = {}
    for sc in scenarios:
        tl, name = sc.timeline, sc.title
        checks[f"[{name}] stations never exceeded"] = all(
            tl.occupancy(t) <= cfg.stations for t in range(start, end))
        checks[f"[{name}] battery never negative"] = min(float(v.min()) for v in sc.levels.values()) >= -1e-9
        checks[f"[{name}] routes within flight budget"] = all(
            tour_length(points, depot, f.tour) <= (f.end - f.start) * ups + 1e-6 and f.times[-1] <= f.end + 1e-6
            for f in sc.flights)
        checks[f"[{name}] robots are back before leaving the air"] = all(
            tl.state(f.robot, f.end) != FLYING for f in sc.flights if f.end < end)
    unchanged = [i for i in schedule.selected if i != k]
    checks["other robots' schedules and routes unchanged by the delay"] = (
        all(tl_orig.states[i] == tl_delay.states[i] for i in unchanged)
        and all(any(g is f for g in flights_delay) for f in flights_orig if f.robot in unchanged))

    computed = {
        "f_new": f_new,
        "selected": [i + 1 for i in schedule.selected],
        "safety_margin_min": [cfg.operation[i] - f_new[i] for i in schedule.selected],
        "total_flight_min": schedule.total_operation_time(),
        "horizon_min": schedule.horizon,
        "delay_needs_station_minute": res.scheduled_start + 1,
        "delay_arrival_minute": res.arrival + 1,
        "delay_original_minute": res.original_next_start + 1,
        "delay_new_minute": res.new_start + 1,
    }

    log(f"scheduling horizon: {horizon_before} -> {schedule.horizon} min (eps = {cfg.eps:.0%})")
    log(f"max-flight ILP: {ilp_seconds:.2f} s, delay re-scheduling: {delay_ms:.1f} ms")
    log(f"phases r_i(0): { {cfg.name(i): schedule.phases[i] for i in schedule.selected} }, "
        f"{cfg.name(k)} after delay: {res.schedule.phases[k]}")
    log("\npaper vs computed (minutes are 1-based as in the paper):")
    for key, want in PAPER_SEC_VI.items():
        got = computed[key]
        log(f"  {'OK  ' if got == want else 'DIFF'} {key:28s} paper={want}  computed={got}")
    log("\nchecks:")
    for key, ok in checks.items():
        log(f"  {'OK  ' if ok else 'FAIL'} {key}")

    # 6. Outputs.
    plot_schedule(scenarios, cfg, out / "charging_schedule.png")
    for minute in cfg.snapshot_minutes:
        # The paper's "t minutes" snapshot shows slot t-1 (e.g. at 4 min UAV2 is charging).
        snapshot(scenarios, cfg, minute - 0.5, out / f"snapshot_{minute:02d}min.png")
    if video:
        animate(scenarios, cfg, out / "simulation.mp4", frames_per_min, fps)

    summary = {
        "computed": computed,
        "paper": PAPER_SEC_VI,
        "checks": checks,
        "reproduces_paper": all(checks.values()) and computed == PAPER_SEC_VI,
        "phases": {cfg.name(i): schedule.phases[i] for i in schedule.selected},
        "delayed_phase": res.schedule.phases[k],
        "horizon_before_reduction": horizon_before,
        "routes": {sc.title: [{"robot": cfg.name(f.robot), "start": f.start, "end": f.end, "sites": f.tour,
                               "length_m": round(tour_length(points, depot, f.tour) * cfg.meters_per_unit, 1)}
                              for f in sc.flights if 0 <= f.start < cfg.minutes]
                   for sc in scenarios},
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2))
    log(f"\nwrote {out}/")
    return summary
