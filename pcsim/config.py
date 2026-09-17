"""Parameters of the Sec. VI simulation.

Robot parameters come from the dataset repository cited in the paper
(github.com/Nitesh-mk/Persistent-Scheduling-Problem-Data-Set,
Simulation_selecting_drones.txt). Site coordinates are the 50 points used for
the published snapshots (Fig. 7); the paper text says 30 locations.
"""

from __future__ import annotations

from dataclasses import dataclass

PAPER_CHARGING = (3, 4, 6, 7, 9, 10, 8)      # c_i [min]
PAPER_OPERATION = (4, 7, 8, 7, 10, 10, 14)   # f_i [min]
PAPER_EPS = 0.2
PAPER_STATIONS = 2

PAPER_SITES = (
    (61.5, 63.4), (33.4, 74.9), (4.2, 59.6), (33.8, 26.9), (64.1, 18.4),
    (83.4, 21.7), (57.2, 80.9), (35.4, 29.4), (73.8, 29.6), (52.8, 57.4),
    (1.1, 19.9), (89.7, 12.9), (49.7, 14.6), (64.5, 63.3), (74.3, 2.8),
    (27.9, 64.7), (17.7, 5.2), (95.1, 71.4), (44.6, 60.5), (85.4, 69.1),
    (84.7, 77.8), (7.9, 31.6), (36.1, 48.6), (17.3, 10.1), (70.2, 71.9),
    (81.0, 4.5), (52.6, 16.7), (27.0, 36.4), (82.1, 81.5), (8.3, 67.6),
    (75.6, 52.4), (57.6, 51.2), (21.6, 38.1), (61.7, 59.6), (79.6, 18.1),
    (56.8, 62.8), (72.8, 69.9), (7.4, 39.3), (26.7, 2.0), (88.7, 97.4),
    (24.7, 42.5), (13.1, 86.4), (89.9, 73.4), (26.4, 72.0), (61.8, 78.4),
    (88.1, 37.3), (2.8, 30.4), (97.4, 68.9), (49.1, 86.8), (90.2, 18.4),
)


@dataclass(frozen=True)
class SimConfig:
    charging: tuple[int, ...] = PAPER_CHARGING
    operation: tuple[int, ...] = PAPER_OPERATION
    eps: float = PAPER_EPS
    stations: int = PAPER_STATIONS
    depot: tuple[float, float] = (50.0, 100.0)
    sites: tuple[tuple[float, float], ...] = PAPER_SITES
    speed_mps: float = 16.0
    # Map is drawn in 0..100 units; 25 m per unit makes the original hand-made
    # routes use exactly their flight budgets at 16 m/s.
    meters_per_unit: float = 25.0
    # Delay scenario of Sec. VI: UAV2 (index 1) reaches the depot 2 slots late.
    delayed_robot: int = 1
    delay_slots: int = 2
    minutes: int = 36
    snapshot_minutes: tuple[int, ...] = (4, 11, 17, 30)

    def name(self, i: int) -> str:
        return f"UAV{i + 1}"

    def units_per_minute(self) -> float:
        return self.speed_mps * 60.0 / self.meters_per_unit
