# legacy/

Original research code used while writing the paper, kept unchanged for reference.
New work should use the `pcsim` package (`pcsim --help`).

| Legacy file | Replaced by | Notes |
|---|---|---|
| `ilp/opti_np.py` | `pcsim min-stations` | Same optimum (m = 5 for its hard-coded instance) |
| `ilp/ILP_cplex_new.py` | `pcsim min-stations` | CPLEX version of `opti_np.py` |
| `ilp/opti.py` | — | Does not implement the paper model (nonlinear constraints) |
| `ilp/max_fly.py`, `ilp/noLCM.py` | `pcsim max-flight` | Identical code, different hard-coded instances (optimum 40 and 60 slots) |
| `waitingtime/*.ipynb` (Julia) | `pcsim reduce-horizon`, `pcsim min-stations` | Dijkstra-LCM + ILP before/after horizon reduction; `.jld` files load with `--jld` |
| `simulation/animation_ogline.py`, `animation_delayed_line.py` | `pcsim simulate` | Hard-coded schedule/routes; last version draws only UAV7's battery (indentation bug) |
| `simulation/animation*.py`, `og_anima.py`, `opti_top.py` | — | Early animation / GA prototypes |
| `simulation/plot_sites.py` | — | Scatter plot of the task sites; kept as-is and does not run (stray characters) |
| `simulation/gurobiprep.ipynb` | `pcsim simulate` | Hand-made routes used by the old animations |
| `routing/teamOrienteeringProblem_jackie.py` | `pcsim.routing` (different heuristic) | TOP meta-heuristic (Lee & Rathinam, SciTech 2024); unseeded, crashes at the final plot |
| `routing/Subtour_*` | — | Sub-tour routing experiments |

Local only (git-ignored): `simulation/videos/*.mp4`, `routing/Subtour_Scheduling_byNitesh.ipynb`, `ilp/cplex.py`.
