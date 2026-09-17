"""Managing delay (Sec. IV-B): re-schedule a tardy robot without touching the others."""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product

from .ilp import Schedule


def next_charge_start(schedule: Schedule, i: int, t: int) -> int:
    """Earliest slot >= t at which robot i begins a charging block."""
    return t + (-(schedule.phases[i] + t)) % schedule.cycle[i]


def with_phases(schedule: Schedule, new_phases: dict[int, int]) -> Schedule:
    return replace(schedule, phases=tuple(new_phases.get(i, p) for i, p in enumerate(schedule.phases)))


def feasible_phases(schedule: Schedule, robots: list[int]) -> list[tuple[int, ...]]:
    """All r*_k(0) for the robots in `robots` satisfying Eqs. 16-17.

    The remaining robots keep their phases. Exhaustive search over
    prod_k T_k combinations, which the paper notes is cheap enough for real time.
    """
    others = [i for i in schedule.selected if i not in robots]
    residual = [schedule.stations - sum(schedule.is_charging(i, t) for i in others)
                for t in range(schedule.horizon)]
    result = []
    for combo in product(*(range(schedule.cycle[k]) for k in robots)):
        trial = with_phases(schedule, dict(zip(robots, combo)))
        if all(sum(trial.is_charging(k, t) for k in robots) <= residual[t]
               for t in range(schedule.horizon)):
            result.append(combo)
    return result


@dataclass(frozen=True)
class DelayResolution:
    robot: int
    scheduled_start: int      # slot at which the robot should have taken a station
    arrival: int              # slot at which it actually reached the depot
    original_next_start: int  # earliest start keeping the old phase
    new_start: int            # earliest start over all feasible phases
    schedule: Schedule        # schedule with the tardy robot's new phase


def resolve_delay(schedule: Schedule, robot: int, scheduled_start: int, delay: int) -> DelayResolution:
    """Pick the feasible phase that gives the tardy robot the earliest charging slot."""
    arrival = scheduled_start + delay
    best_phase, best_start = None, None
    for (phase,) in feasible_phases(schedule, [robot]):
        start = next_charge_start(with_phases(schedule, {robot: phase}), robot, arrival)
        if best_start is None or start < best_start:
            best_phase, best_start = phase, start
    return DelayResolution(robot, scheduled_start, arrival,
                           next_charge_start(schedule, robot, arrival), best_start,
                           with_phases(schedule, {robot: best_phase}))
