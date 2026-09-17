# legacy/

Original research code used while writing the paper, kept unchanged for reference.
New work should use the `pcsim` package (`pcsim --help`).

| Legacy file | Replaced by | Notes |
|---|---|---|
| `ilp/opti_np.py` | `pcsim min-stations` | Same optimum (m = 5 for its hard-coded instance) |
| `ilp/ILP_cplex_new.py` | `pcsim min-stations` | CPLEX version of `opti_np.py` |
| `ilp/opti.py` | — | Does not implement the paper model (nonlinear constraints) |
| `ilp/max_fly.py`, `ilp/noLCM.py` | `pcsim max-flight` | Identical code, different hard-coded instances (optimum 40 and 60 slots) |
| `waitingtime/reduced_operation_time/` (Julia) | `pcsim reduce-horizon`, `pcsim min-stations` | Table I study: shorten operational times by up to 10 %, ILP before/after; `data*.jld` load with `--jld` |
| `waitingtime/waiting_time/` (Julia) | — | Same study, but cycle times lengthened by waiting up to 5 %; different instances (c, f in 50–128) |
| `simulation/animation_ogline.py`, `animation_delayed_line.py` | `pcsim simulate` | Hard-coded schedule/routes; last version draws only UAV7's battery (indentation bug) |
| `simulation/animation*.py`, `og_anima.py`, `opti_top.py` | — | Early animation / GA prototypes |
| `simulation/plot_sites.py` | — | Scatter plot of the task sites; kept as-is and does not run (stray characters) |
| `simulation/gurobiprep.ipynb` | `pcsim simulate` | Hand-made routes used by the old animations |
| `routing/teamOrienteeringProblem_jackie.py` | `pcsim.routing` (different heuristic) | TOP meta-heuristic (Lee & Rathinam, SciTech 2024); unseeded, crashes at the final plot |
| `routing/Subtour_*` | — | Sub-tour routing experiments |

Local only (git-ignored): `simulation/videos/*.mp4`, `routing/Subtour_Scheduling_byNitesh.ipynb`.

The Julia notebooks read `data*.jld` from their own folder and need Julia 1.10 with JuMP, CPLEX, Plots and JLD.
The pre-2025 git history (including the animation versions used for the paper figures, e.g. `2f6428e`)
is archived outside the repo at `~/research/_archive/ral_opticharge_git_old_history`
(`git --git-dir=<that path> show 2f6428e:simulation/animation_ogline.py`).
