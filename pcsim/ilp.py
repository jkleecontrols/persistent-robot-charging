"""ILP formulations of Sec. III-B (minimize stations) and Sec. III-C (maximize flying time).

Decision variables r[i, j] in {0, 1} encode r_i(0) = e_j. Using Eq. 10,
z_i(t) = p_i^T A_i^t r_i(0) = sum_j [ (j + t) mod T_i < c_i ] r[i, j].
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import gurobipy as gp
from gurobipy import GRB

from .horizon import lcm


@dataclass(frozen=True)
class Schedule:
    """Cyclic schedule: robot i starts at phase `phases[i]` (None = not deployed)."""

    charging: tuple[int, ...]
    operation: tuple[int, ...]
    phases: tuple[int | None, ...]
    stations: int
    horizon: int

    @property
    def cycle(self) -> tuple[int, ...]:
        return tuple(c + f for c, f in zip(self.charging, self.operation))

    @property
    def selected(self) -> list[int]:
        return [i for i, p in enumerate(self.phases) if p is not None]

    def is_charging(self, i: int, t: int) -> bool:
        """z_i(t) (Eq. 10)."""
        p = self.phases[i]
        return p is not None and (p + t) % self.cycle[i] < self.charging[i]

    def occupancy(self, t: int) -> int:
        return sum(self.is_charging(i, t) for i in self.selected)

    def total_operation_time(self) -> int:
        """sum_t sum_i y_i(t) over one horizon (Eqs. 11-12)."""
        return sum(self.horizon // self.cycle[i] * self.operation[i] for i in self.selected)


def charges_at(phase: int, t: int, cycle: int, charging: int) -> bool:
    return (phase + t) % cycle < charging


def _build(model: gp.Model, charging, operation, horizon):
    n = len(charging)
    cycle = [c + f for c, f in zip(charging, operation)]
    r = {(i, j): model.addVar(vtype=GRB.BINARY, name=f"r[{i},{j}]")
         for i in range(n) for j in range(cycle[i])}
    occupancy = [gp.quicksum(r[i, j] for i in range(n) for j in range(cycle[i])
                             if charges_at(j, t, cycle[i], charging[i]))
                 for t in range(horizon)]
    return r, cycle, occupancy


def _extract(r, cycle, n):
    phases = []
    for i in range(n):
        chosen = [j for j in range(cycle[i]) if r[i, j].X > 0.5]
        phases.append(chosen[0] if chosen else None)
    return tuple(phases)


def _new_model(name: str, time_limit: float | None, verbose: bool) -> gp.Model:
    model = gp.Model(name)
    model.Params.OutputFlag = int(verbose)
    model.Params.Seed = 0
    if time_limit:
        model.Params.TimeLimit = time_limit
    return model


def solve_min_stations(charging: Sequence[int], operation: Sequence[int],
                       time_limit: float | None = None, verbose: bool = False) -> Schedule:
    """m_min = min m  s.t. Eq. 4 and Eq. 9 (Sec. III-B)."""
    n = len(charging)
    horizon = lcm([c + f for c, f in zip(charging, operation)])
    model = _new_model("min_stations", time_limit, verbose)
    r, cycle, occupancy = _build(model, charging, operation, horizon)
    m = model.addVar(vtype=GRB.INTEGER, lb=0, name="m")
    for i in range(n):
        model.addConstr(gp.quicksum(r[i, j] for j in range(cycle[i])) == 1)  # Eq. 4
    for t in range(horizon):
        model.addConstr(occupancy[t] <= m)  # Eq. 9
    model.setObjective(m, GRB.MINIMIZE)
    model.optimize()
    if model.SolCount == 0:
        raise RuntimeError(f"min_stations: no solution (status {model.Status})")
    return Schedule(tuple(charging), tuple(operation), _extract(r, cycle, n),
                    int(round(m.X)), horizon)


def solve_max_flight(charging: Sequence[int], operation: Sequence[int], stations: int,
                     lexicographic_tie_break: bool = True,
                     time_limit: float | None = None, verbose: bool = False) -> Schedule:
    """max sum_t sum_i y_i(t)  s.t. Eq. 9 with m fixed and Eq. 15 (Sec. III-C).

    The optimum is generally not unique (for the Sec. VI instance both robot
    sets {1,2,7} and {2,5,7} give 58 min). With `lexicographic_tie_break`
    the solver additionally prefers lower robot indices, then the
    lexicographically smallest phases. This rule is not stated in the paper;
    it is the deterministic tie-break that reproduces the published schedule.
    """
    n = len(charging)
    horizon = lcm([c + f for c, f in zip(charging, operation)])
    model = _new_model("max_flight", time_limit, verbose)
    r, cycle, occupancy = _build(model, charging, operation, horizon)
    u = model.addVars(n, vtype=GRB.BINARY, name="u")
    for i in range(n):
        model.addConstr(gp.quicksum(r[i, j] for j in range(cycle[i])) == u[i])  # Eq. 15
    for t in range(horizon):
        model.addConstr(occupancy[t] <= stations)  # Eq. 9
    # sum_t y_i(t) = sum_t q_i^T A_i^t r_i(0); count the flying slots of each phase.
    flying = gp.quicksum(
        sum(not charges_at(j, t, cycle[i], charging[i]) for t in range(horizon)) * r[i, j]
        for i in range(n) for j in range(cycle[i]))
    model.ModelSense = GRB.MAXIMIZE
    if not lexicographic_tie_break:
        model.setObjective(flying)
    else:
        # Hierarchical objectives, higher priority is optimized first.
        priority = 2 * n + 1
        model.setObjectiveN(flying, index=0, priority=priority, name="flying")
        for i in range(n):
            priority -= 1
            model.setObjectiveN(u[i], index=1 + i, priority=priority, name=f"select_{i}")
        for i in range(n):
            priority -= 1
            phase = gp.quicksum(j * r[i, j] for j in range(cycle[i]))
            model.setObjectiveN(phase, index=1 + n + i, priority=priority, weight=-1.0,
                                name=f"phase_{i}")
    model.optimize()
    if model.SolCount == 0:
        raise RuntimeError(f"max_flight: no solution (status {model.Status})")
    return Schedule(tuple(charging), tuple(operation), _extract(r, cycle, n), stations, horizon)
