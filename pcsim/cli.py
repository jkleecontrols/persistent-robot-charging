"""Command line interface: `pcsim <command>` (or `python -m pcsim <command>`).

  simulate         Sec. VI simulation, figures and video
  min-stations     Sec. III-B ILP (replaces legacy opti_np.py, ILP_cplex_new.py)
  max-flight       Sec. III-C ILP (replaces legacy max_fly.py, noLCM.py)
  reduce-horizon   Sec. IV-A Dijkstra-LCM (Table I)
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path


def _add_instance_args(p: argparse.ArgumentParser) -> None:
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--charging", "-c", type=int, nargs="+", metavar="C", help="charging times c_i")
    src.add_argument("--jld", type=Path, help="Julia .jld file with a 2 x n matrix D")
    p.add_argument("--operation", "-f", type=int, nargs="+", metavar="F", help="operational times f_i")


def _instance(args) -> tuple[list[int], list[int]]:
    if args.jld:
        from .datasets import load_jld
        return load_jld(args.jld)
    if not args.operation or len(args.operation) != len(args.charging):
        sys.exit("--charging and --operation need the same number of values")
    return args.charging, args.operation


def _add_ilp_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--no-normalize", action="store_true", help="do not divide times by their GCD")
    p.add_argument("--time-limit", type=float, default=None, help="solver time limit [s]")
    p.add_argument("--verbose", action="store_true", help="show the Gurobi log")


def _print_schedule(schedule, g: int, seconds: float) -> None:
    flight = schedule.total_operation_time()
    print(f"slot length (GCD)     : {g}")
    print(f"scheduling horizon    : {schedule.horizon} slots = {schedule.horizon * g} time units")
    print(f"stations m            : {schedule.stations}")
    print(f"selected robots       : {[i + 1 for i in schedule.selected]}")
    print(f"initial phases r(0)   : {list(schedule.phases)}")
    print(f"operation per horizon : {flight} slots = {flight * g} time units")
    print(f"solve time            : {seconds:.2f} s")


def cmd_simulate(args) -> int:
    from .config import SimConfig
    from .simulation import run

    summary = run(SimConfig(), args.out, video=not args.no_video,
                  frames_per_min=args.frames_per_min, fps=args.fps)
    return 0 if summary["reproduces_paper"] else 1


def cmd_min_stations(args) -> int:
    from .horizon import normalize
    from .ilp import solve_min_stations

    c, f = _instance(args)
    g, cn, fn = (1, c, f) if args.no_normalize else normalize(c, f)
    t0 = time.perf_counter()
    schedule = solve_min_stations(cn, fn, time_limit=args.time_limit, verbose=args.verbose)
    _print_schedule(schedule, g, time.perf_counter() - t0)
    return 0


def cmd_max_flight(args) -> int:
    from .horizon import normalize
    from .ilp import solve_max_flight

    c, f = _instance(args)
    g, cn, fn = (1, c, f) if args.no_normalize else normalize(c, f)
    t0 = time.perf_counter()
    schedule = solve_max_flight(cn, fn, args.stations, lexicographic_tie_break=not args.no_tie_break,
                                time_limit=args.time_limit, verbose=args.verbose)
    _print_schedule(schedule, g, time.perf_counter() - t0)
    return 0


def cmd_reduce_horizon(args) -> int:
    from .horizon import dijkstra_lcm, lcm

    c, f = _instance(args)
    cycle = [ci + fi for ci, fi in zip(c, f)]
    reduced, chosen = dijkstra_lcm(cycle, args.eps, charging_times=c)
    print(f"horizon           : {lcm(cycle)}")
    print(f"reduced horizon   : {reduced}  (eps = {args.eps:.0%})")
    print(f"cycle times       : {cycle} -> {chosen}")
    print(f"operational times : {f} -> {[v - ci for v, ci in zip(chosen, c)]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pcsim", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("simulate", help="Sec. VI simulation")
    p.add_argument("--out", type=Path, default=Path("results/simulation"))
    p.add_argument("--no-video", action="store_true")
    p.add_argument("--frames-per-min", type=int, default=6)
    p.add_argument("--fps", type=int, default=12)
    p.set_defaults(func=cmd_simulate)

    p = sub.add_parser("min-stations", help="minimum number of charging stations (Sec. III-B)")
    _add_instance_args(p)
    _add_ilp_args(p)
    p.set_defaults(func=cmd_min_stations)

    p = sub.add_parser("max-flight", help="maximum operation time with m stations (Sec. III-C)")
    _add_instance_args(p)
    _add_ilp_args(p)
    p.add_argument("--stations", "-m", type=int, required=True)
    p.add_argument("--no-tie-break", action="store_true", help="accept any optimal solution")
    p.set_defaults(func=cmd_max_flight)

    p = sub.add_parser("reduce-horizon", help="Dijkstra-LCM horizon reduction (Sec. IV-A)")
    _add_instance_args(p)
    p.add_argument("--eps", type=float, default=0.1)
    p.set_defaults(func=cmd_reduce_horizon)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)
