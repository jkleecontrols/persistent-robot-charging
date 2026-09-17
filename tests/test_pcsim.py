"""Regression tests against the published results (RA-L 2025) and internal invariants."""

from pathlib import Path

import numpy as np
import pytest

from pcsim.config import PAPER_CHARGING, PAPER_OPERATION, PAPER_SITES, SimConfig
from pcsim.datasets import load_jld
from pcsim.delay import feasible_phases, next_charge_start, resolve_delay
from pcsim.horizon import candidate_cycle_times, dijkstra_lcm, lcm, normalize, reduce_operational_times
from pcsim.routing import plan_flights, tour_length
from pcsim.timeline import CHARGING, battery_levels, build_delayed_timeline, build_timeline

gurobipy = pytest.importorskip("gurobipy")
from pcsim.cli import main  # noqa: E402
from pcsim.ilp import Schedule, solve_max_flight, solve_min_stations  # noqa: E402
from pcsim.simulation import run  # noqa: E402

REPO = Path(__file__).resolve().parents[1]

# Reduced_operational_time.txt of the paper's dataset repository, and Table I (eps = 10 %).
TABLE_I = [
    ([39, 36, 30, 25, 27, 34, 33, 38, 44, 35], [45, 36, 42, 44, 42, 35, 59, 31, 48, 49], 11592, 504),
    ([40, 42, 46, 39, 37, 35, 35, 50, 32, 43], [30, 42, 38, 27, 29, 35, 31, 34, 28, 41], 4620, 504),
    ([58, 71, 58, 68, 66, 71, 81, 52, 70, 74], [59, 72, 85, 75, 77, 72, 62, 47, 73, 69], 1287, 540),
    ([97, 73, 89, 60, 53, 71, 98, 67, 71, 69], [59, 70, 54, 96, 64, 85, 45, 76, 72, 48], 5148, 1287),
    ([29, 32, 39, 26, 43, 25, 46, 28, 28, 25], [37, 28, 36, 40, 32, 35, 44, 47, 32, 50], 9900, 900),
    ([38, 45, 48, 30, 50, 25, 32, 29, 48, 28], [49, 33, 39, 35, 37, 40, 46, 36, 30, 50], 11310, 504),
    ([26, 32, 25, 33, 25, 34, 50, 28, 48, 32], [30, 52, 38, 30, 41, 43, 38, 28, 36, 34], 5544, 504),
    ([50, 42, 41, 41, 25, 38, 50, 40, 39, 39], [49, 46, 31, 49, 47, 50, 38, 40, 49, 49], 7920, 792),
    ([66, 67, 86, 63, 78, 75, 59, 50, 61, 100], [42, 68, 49, 72, 57, 60, 49, 40, 89, 80], 2700, 540),
]


@pytest.mark.parametrize("charging, operation, horizon, reduced", TABLE_I)
def test_table_i_scheduling_horizon(charging, operation, horizon, reduced):
    cycle = [c + f for c, f in zip(charging, operation)]
    assert lcm(cycle) == horizon
    assert dijkstra_lcm(cycle, 0.1)[0] == reduced


def test_candidate_set_respects_eps():
    assert candidate_cycle_times(20, 0.1) == [18, 19, 20]
    assert candidate_cycle_times(7, 0.2) == [6, 7]


def test_simulation_operational_times_match_dataset():
    assert reduce_operational_times(PAPER_CHARGING, PAPER_OPERATION, 0.2) == [3, 5, 6, 5, 9, 8, 10]


@pytest.fixture(scope="module")
def paper_schedule():
    return solve_max_flight(PAPER_CHARGING, [3, 5, 6, 5, 9, 8, 10], stations=2)


def test_max_flight_reproduces_sec_vi(paper_schedule):
    s = paper_schedule
    assert [i + 1 for i in s.selected] == [1, 2, 7]
    assert s.total_operation_time() == 58
    assert s.horizon == 36
    assert s.phases == (0, 0, None, None, None, None, 14)
    assert max(s.occupancy(t) for t in range(s.horizon)) <= 2


def test_max_flight_without_tie_break_has_same_optimum():
    s = solve_max_flight(PAPER_CHARGING, [3, 5, 6, 5, 9, 8, 10], stations=2, lexicographic_tie_break=False)
    assert s.total_operation_time() == 58
    assert max(s.occupancy(t) for t in range(s.horizon)) <= 2


def test_min_stations_small_instance():
    assert solve_min_stations([2, 2], [2, 2]).stations == 1  # staggered robots share one pad
    assert solve_min_stations([3, 3], [2, 2]).stations == 2


def test_delay_reproduces_sec_vi(paper_schedule):
    start = next_charge_start(paper_schedule, 1, 0)
    res = resolve_delay(paper_schedule, robot=1, scheduled_start=start, delay=2)
    assert (res.scheduled_start, res.arrival, res.original_next_start, res.new_start) == (0, 2, 9, 2)
    assert (res.schedule.phases[1],) in feasible_phases(paper_schedule, [1])
    assert max(res.schedule.occupancy(t) for t in range(36)) <= 2


def test_timeline_and_routes(paper_schedule):
    res = resolve_delay(paper_schedule, 1, 0, 2)
    ups = 16 * 60 / 25
    points, depot = np.array(PAPER_SITES), np.array([50.0, 100.0])
    for tl in (build_timeline(paper_schedule, -36, 37), build_delayed_timeline(res, paper_schedule, -36, 37)):
        assert all(tl.occupancy(t) <= 2 for t in range(-36, 37))
        assert all(tl.state(i, t) == CHARGING for (i, t) in tl.pad_assignment())
        levels = battery_levels(tl, PAPER_CHARGING, PAPER_OPERATION, 4)
        assert min(v.min() for v in levels.values()) >= -1e-9
        for f in plan_flights(tl.flights(), points, depot, ups):
            assert tour_length(points, depot, f.tour) <= (f.end - f.start) * ups + 1e-6


def test_normalize_by_gcd():
    assert normalize([14, 14], [20, 20]) == (2, [7, 7], [10, 10])


@pytest.mark.parametrize("charging, operation, stations, flight", [
    ([14, 14, 14, 14], [20, 20, 20, 20], 2, 40),  # legacy/ilp/max_fly.py
    ([13, 13, 13], [20, 20, 20], 2, 60),          # legacy/ilp/noLCM.py
])
def test_max_flight_matches_legacy_scripts(charging, operation, stations, flight):
    _, c, f = normalize(charging, operation)
    assert solve_max_flight(c, f, stations).total_operation_time() == flight


def test_min_stations_matches_legacy_opti_np():
    _, c, f = normalize([5, 5, 5, 5, 5, 5, 10, 15, 20, 25], [20, 25, 20, 15, 25, 30, 30, 25, 30, 35])
    assert solve_min_stations(c, f).stations == 5


def test_load_jld_and_cli(capsys):
    pytest.importorskip("h5py")
    path = REPO / "legacy" / "waitingtime" / "data" / "data2.jld"
    c, f = load_jld(path)
    assert lcm([ci + fi for ci, fi in zip(c, f)]) == 4620
    assert main(["reduce-horizon", "--jld", str(path), "--eps", "0.1"]) == 0
    assert "reduced horizon   : 504" in capsys.readouterr().out


def test_simulation_reproduces_paper(tmp_path):
    summary = run(SimConfig(snapshot_minutes=(17,)), tmp_path, video=False, log=lambda _: None)
    assert summary["reproduces_paper"]
    assert (tmp_path / "charging_schedule.png").exists()


def test_charging_indicator_matches_eq_7():
    s = Schedule((2,), (3,), (4,), 1, 5)
    # phase 4 of a 5-slot cycle: position (4 + t) mod 5 < 2 -> charging at t = 1, 2, 6, 7
    assert [t for t in range(10) if s.is_charging(0, t)] == [1, 2, 6, 7]
