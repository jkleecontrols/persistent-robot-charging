"""Slot-level execution of a schedule: robot states, charging-pad assignment, battery."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .delay import DelayResolution
from .ilp import Schedule

CHARGING, FLYING, WAITING = "C", "F", "W"


@dataclass
class Timeline:
    """States for slots t in [start, end); index with `state(i, t)`."""

    robots: list[int]
    start: int
    end: int
    states: dict[int, list[str]]
    stations: int
    delayed: tuple[int, int, int] | None = None  # (robot, scheduled_start, arrival)

    def state(self, i: int, t: int) -> str:
        return self.states[i][t - self.start]

    def occupancy(self, t: int) -> int:
        return sum(self.state(i, t) == CHARGING for i in self.robots)

    def flights(self) -> list[tuple[int, int, int]]:
        """Maximal flying runs (robot, first_slot, end_slot) fully inside the window."""
        out = []
        for i in self.robots:
            t = self.start
            while t < self.end:
                if self.state(i, t) != FLYING:
                    t += 1
                    continue
                e = t
                while e < self.end and self.state(i, e) == FLYING:
                    e += 1
                if t > self.start:
                    out.append((i, t, e))
                t = e
        return sorted(out, key=lambda x: (x[1], x[0]))

    def pad_assignment(self) -> dict[tuple[int, int], int]:
        """(robot, slot) -> pad index; each charging block keeps its pad."""
        pads: dict[tuple[int, int], int] = {}
        holder: dict[int, int] = {}
        for t in range(self.start, self.end):
            for i in list(holder):
                if self.state(i, t) != CHARGING:
                    del holder[i]
            for i in self.robots:
                if self.state(i, t) == CHARGING and i not in holder:
                    free = sorted(set(range(self.stations)) - set(holder.values()))
                    if not free:
                        raise RuntimeError(f"more than {self.stations} robots charging at slot {t}")
                    holder[i] = free[0]
            for i, pad in holder.items():
                pads[i, t] = pad
        return pads


def build_timeline(schedule: Schedule, start: int, end: int) -> Timeline:
    states = {i: [CHARGING if schedule.is_charging(i, t) else FLYING for t in range(start, end)]
              for i in schedule.selected}
    return Timeline(schedule.selected, start, end, states, schedule.stations)


def build_delayed_timeline(res: DelayResolution, original: Schedule, start: int, end: int) -> Timeline:
    """Original schedule until the robot is late, extra flight until arrival,
    waiting at the depot if needed, then the re-computed phase."""
    timeline = build_timeline(original, start, end)
    k = res.robot
    for t in range(max(start, res.scheduled_start), end):
        if t < res.arrival:
            s = FLYING
        elif t < res.new_start:
            s = WAITING
        else:
            s = CHARGING if res.schedule.is_charging(k, t) else FLYING
        timeline.states[k][t - start] = s
    timeline.delayed = (k, res.scheduled_start, res.arrival)
    return timeline


def battery_levels(timeline: Timeline, charging: tuple[int, ...], operation_max: tuple[int, ...],
                   steps_per_slot: int) -> dict[int, np.ndarray]:
    """Battery state of charge in [0, 1] at times start + k / steps_per_slot.

    Flying drains 1/f_i^max per slot (f_i^max = original operational time),
    charging adds 1/c_i per slot (empty to full in c_i slots) and saturates.
    Levels start full at `timeline.start`; use a warm-up window of at least
    one horizon so the displayed part is in periodic steady state.
    """
    dt = 1.0 / steps_per_slot
    levels = {}
    for i in timeline.robots:
        level = 1.0
        samples = []
        for t in range(timeline.start, timeline.end):
            s = timeline.state(i, t)
            for _ in range(steps_per_slot):
                samples.append(level)
                if s == FLYING:
                    level -= dt / operation_max[i]
                elif s == CHARGING:
                    level = min(1.0, level + dt / charging[i])
        samples.append(level)
        levels[i] = np.array(samples)
    return levels
