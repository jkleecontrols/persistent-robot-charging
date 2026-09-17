# Persistent Robot Charging for Long-Duration Autonomy

Code accompanying the IEEE RA-L paper:

> **The Persistent Robot Charging Problem for Long-Duration Autonomy**
> Nitesh Kumar, Jaekyung Jackie Lee, Sivakumar Rathinam, Swaroop Darbha, P.B. Sujit, Rajiv Raman
> *IEEE Robotics and Automation Letters*, vol. 10, no. 3, pp. 2191–2198, 2025

This repository contains **my (Jackie Lee's) implementation and experiments** for the paper: the ILP charging-schedule models, the waiting-time comparison studies, and the UAV simulations/animations.

## Problem

A fleet of *n* heterogeneous robots must periodically recharge. Given each robot's charging time and working (flying) time, find a recharging schedule that **minimizes the number of charging stations** needed, by choosing each robot's optimal initial partial charge.
The formulation is generalized to **maximize robot servicing time when charging stations are limited**, and compared against the thrift-price scheduling algorithm from the literature.

## Method

- Times are normalized by their GCD; the scheduling horizon is the LCM of the robots' cycle times (Sec. III-A).
- An ILP chooses each robot's initial cycle position r_i(0) to minimize the charging stations (Sec. III-B), or selects robots to maximize operation time on m stations (Sec. III-C).
- Safety margins shorten operational times so the LCM horizon shrinks, via Dijkstra on candidate cycle times with LCM path cost (Sec. IV-A).
- A tardy robot is re-scheduled by searching its feasible initial states while the other robots keep theirs (Sec. IV-B).

## Repository structure

```
pcsim/                  Python package
  horizon.py            LCM horizon, GCD normalization, Dijkstra-LCM (Sec. III-A, IV-A)
  ilp.py                min-stations and max-flight ILPs, Schedule (Sec. III-B, III-C)
  delay.py              tardy-robot re-scheduling, Eqs. 16-17 (Sec. IV-B)
  timeline.py           slot-level execution: states, pad assignment, battery
  routing.py            per-flight orienteering routes
  render.py             schedule chart, snapshots, video
  simulation.py         Sec. VI pipeline and paper checks
  config.py             Sec. VI parameters
  datasets.py           .jld loader
  cli.py                `pcsim` command line
tests/                  regression tests against Table I, Sec. VI and the legacy scripts
legacy/                 original scripts, notebooks and Julia studies (see legacy/README.md)
handoff/STATUS.md       work log
```

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"            # Gurobi's pip wheel includes a size-limited license
pytest                              # checks against the published numbers
```

Video export needs `ffmpeg` on `PATH`. ILPs larger than the size-limited license (e.g. Table I instances) need a full Gurobi academic license.

## Usage

```bash
pcsim simulate                                   # Sec. VI -> results/simulation/ (--no-video for figures only)
pcsim min-stations -c 5 5 10 15 -f 20 25 30 25   # minimum number of charging stations
pcsim max-flight   -c 14 14 14 14 -f 20 20 20 20 -m 2
pcsim reduce-horizon --jld legacy/waitingtime/data/data2.jld --eps 0.1
```

`pcsim simulate` runs the whole Sec. VI pipeline from the robot parameters:
Dijkstra-LCM safety margins → max-flying-time ILP on 2 stations → re-scheduling of the delayed UAV2 →
routing per flight → schedule chart, snapshots and video.
It prints the published values next to the computed ones and exits non-zero if they differ.

The Julia notebooks in `legacy/waitingtime/` require Julia 1.10 with `JuMP`, `CPLEX`, `Plots`, and `JLD`.

## Related work

- UAV–UGV FOV-aware area coverage (ICUAS 2025): [uav-ugv-area-coverage](https://github.com/jkleecontrols/uav-ugv-area-coverage)

## Citation

```bibtex
@article{kumar2025persistent,
  title   = {The Persistent Robot Charging Problem for Long-Duration Autonomy},
  author  = {Kumar, Nitesh and Lee, Jaekyung Jackie and Rathinam, Sivakumar and Darbha, Swaroop and Sujit, P. B. and Raman, Rajiv},
  journal = {IEEE Robotics and Automation Letters},
  volume  = {10},
  number  = {3},
  pages   = {2191--2198},
  year    = {2025}
}
```
