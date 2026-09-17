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

- Times are normalized by their GCD; the schedule horizon is the LCM of per-robot cycle lengths.
- An Integer Linear Program assigns, for every robot and time slot, whether it is charging, subject to cyclic charge/work patterns.
- Variants: minimize charging pads (`opti.py`, `opti_np.py`), fixed pads with maximum flying time (`max_fly.py`), and a formulation without the LCM horizon (`noLCM.py`).

## Repository structure

```
opti.py, opti_np.py          ILP: minimize number of charging pads (Gurobi)
max_fly.py                   ILP: maximize flight time with m charging pads
noLCM.py                     Variant without the LCM time horizon
ILP_cplex_new.py             CPLEX version of the ILP
Subtour_jackie.py            Subtour-elimination routing example
Subtour_Scheduling_byJackie.ipynb
gurobiprep.ipynb             Gurobi model prototyping
teamOrienteeringProblem_jackie.py   TOP routing combined with charging schedule
simulation/                  UAV charging-dock simulations and animations
waitingtime/                 Julia (JuMP + CPLEX) waiting-time comparison studies and datasets (.jld)
```

## Getting started

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python max_fly.py
```

The `waitingtime/` notebooks require Julia 1.10 with `JuMP`, `CPLEX`, `Plots`, and `JLD`.

## Status

Research code as used for the paper. A refactor (single configurable ILP module, reproducible experiment scripts) is in progress.

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
