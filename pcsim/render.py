"""Figures and video for the Sec. VI simulation, generated from the computed schedule."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.animation import FFMpegWriter, FuncAnimation  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

from .config import SimConfig  # noqa: E402
from .routing import Flight  # noqa: E402
from .timeline import CHARGING, FLYING, WAITING, Timeline  # noqa: E402

STATE_COLORS = {CHARGING: "#2e9d4a", FLYING: "#d6453d", WAITING: "#9e9e9e"}


@dataclass
class Scenario:
    title: str
    timeline: Timeline
    flights: list[Flight]
    levels: dict[int, np.ndarray]
    steps_per_slot: int
    pads: dict[tuple[int, int], int]


def robot_color(i: int):
    return plt.get_cmap("tab10")(i % 10)


def plot_schedule(scenarios: list[Scenario], cfg: SimConfig, path: Path) -> None:
    """Gantt chart of charging (green) / flying (red) / waiting (grey) slots."""
    n_rows = len(scenarios[0].timeline.robots)
    fig, axes = plt.subplots(len(scenarios), 1, figsize=(11, 0.9 + 0.55 * n_rows * len(scenarios)),
                             squeeze=False)
    for ax, sc, label in zip(axes[:, 0], scenarios, "abcdefgh"):
        tl = sc.timeline
        robots = tl.robots[::-1]
        for row, i in enumerate(robots):
            for t in range(cfg.minutes):
                s = tl.state(i, t)
                ax.barh(row, 1, left=t, color=STATE_COLORS[s], edgecolor="white", linewidth=0.8)
                if s == CHARGING:
                    ax.text(t + 0.5, row, str(sc.pads[i, t] + 1), ha="center", va="center",
                            fontsize=7, color="white")
        if tl.delayed:
            k, sched, arr = tl.delayed
            row = robots.index(k)
            ax.annotate("", xy=(arr, row + 0.5), xytext=(sched, row + 0.5),
                        arrowprops=dict(arrowstyle="->", color="black"))
        ax.set_yticks(range(len(robots)), [cfg.name(i) for i in robots])
        ax.set_xlim(0, cfg.minutes)
        ax.set_xticks(range(0, cfg.minutes + 1, 2))
        ax.set_title(f"({label}) {sc.title}", loc="left")
    axes[-1, 0].set_xlabel("time [min]   (number in a green cell = charging pad)")
    handles = [Patch(color=STATE_COLORS[s], label=n)
               for s, n in ((CHARGING, "charging"), (FLYING, "flying"), (WAITING, "waiting"))]
    fig.legend(handles=handles, loc="upper right", ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(path, dpi=200)
    plt.close(fig)


def _active_flight(sc: Scenario, i: int, t: float) -> Flight | None:
    return next((f for f in sc.flights if f.robot == i and f.start <= t < f.end), None)


def draw_scenario(ax_map, ax_bat, sc: Scenario, cfg: SimConfig, t: float) -> None:
    tl = sc.timeline
    slot = int(np.floor(t))
    sites = np.array(cfg.sites)
    depot = np.array(cfg.depot)

    # Sites coloured by time since last visit.
    last = np.full(len(sites), -np.inf)
    for f in sc.flights:
        for j, tv in f.site_times():
            if tv <= t:
                last[j] = max(last[j], tv)
    age = np.clip(t - last, 0, cfg.minutes)
    ax_map.scatter(sites[:, 0], sites[:, 1], c=age, cmap="viridis_r", vmin=0, vmax=cfg.minutes,
                   s=28, edgecolors="black", linewidths=0.3, zorder=2)
    ax_map.add_patch(plt.Rectangle(depot - [5, 3], 10, 6, color="black", zorder=3))

    for i in tl.robots:
        flight = _active_flight(sc, i, t)
        if flight is None:
            continue
        color = robot_color(i)
        pos = flight.position(t)
        trail = np.vstack([flight.waypoints[flight.times <= t], pos])
        ax_map.plot(flight.waypoints[:, 0], flight.waypoints[:, 1], ":", color=color, lw=0.8, zorder=1)
        ax_map.plot(trail[:, 0], trail[:, 1], "-", color=color, lw=1.8, zorder=4)
        ax_map.plot(*pos, marker="^", ms=11, color=color, mec="black", zorder=5)
        ax_map.annotate(cfg.name(i), pos, xytext=(6, 6), textcoords="offset points", fontsize=8)
    ax_map.set_xlim(-2, 102)
    ax_map.set_ylim(-2, 106)
    ax_map.set_aspect("equal")
    ax_map.set_xlabel(f"X [x{cfg.meters_per_unit:g} m]")
    ax_map.set_ylabel(f"Y [x{cfg.meters_per_unit:g} m]")
    ax_map.set_title(f"{sc.title}   t = {t:4.1f} min", fontsize=10)

    # Charging pads and battery bars (axes coordinates: x in [0, 1]).
    n = len(tl.robots)
    ax_bat.set_xlim(0, 1)
    ax_bat.set_ylim(-0.8, n + 1.6)
    ax_bat.axis("off")
    pad_y = n + 0.7
    ax_bat.text(0.0, pad_y + 0.5, "charging pads", fontsize=9)
    for p in range(cfg.stations):
        user = next((i for i in tl.robots if sc.pads.get((i, slot)) == p), None)
        x = 0.12 + 0.24 * p
        ax_bat.plot(x, pad_y, "o", ms=18, mec="black",
                    mfc=STATE_COLORS[CHARGING] if user is not None else "white")
        if user is not None:
            ax_bat.text(x, pad_y, str(user + 1), ha="center", va="center", fontsize=8, color="white")
    idx = min(int(round((t - tl.start) * sc.steps_per_slot)), len(next(iter(sc.levels.values()))) - 1)
    for row, i in enumerate(tl.robots[::-1]):
        level = float(sc.levels[i][idx])
        ax_bat.text(0.0, row + 0.35, cfg.name(i), va="bottom", fontsize=9, color=robot_color(i))
        ax_bat.add_patch(plt.Rectangle((0.0, row - 0.2), 0.62, 0.4, fill=False, ec="black"))
        ax_bat.add_patch(plt.Rectangle((0.0, row - 0.2), 0.62 * max(level, 0.0), 0.4,
                                       color=STATE_COLORS[tl.state(i, slot)]))
        ax_bat.text(0.68, row, f"{100 * level:3.0f}%", va="center", fontsize=9)


def _figure(n_scenarios: int, cfg: SimConfig):
    fig = plt.figure(figsize=(6.6 * n_scenarios, 5.6))
    grid = fig.add_gridspec(2, 2 * n_scenarios, width_ratios=[3, 1] * n_scenarios,
                            height_ratios=[1, 0.035], wspace=0.25, hspace=0.3)
    axes = [(fig.add_subplot(grid[0, 2 * k]), fig.add_subplot(grid[0, 2 * k + 1]))
            for k in range(n_scenarios)]
    cax = fig.add_subplot(grid[1, 1:2 * n_scenarios - 1])
    mappable = plt.cm.ScalarMappable(cmap="viridis_r", norm=plt.Normalize(0, cfg.minutes))
    fig.colorbar(mappable, cax=cax, orientation="horizontal",
                 label="site colour: minutes since last visit")
    return fig, axes


def snapshot(scenarios: list[Scenario], cfg: SimConfig, t: float, path: Path) -> None:
    fig, axes = _figure(len(scenarios), cfg)
    for (ax_map, ax_bat), sc in zip(axes, scenarios):
        draw_scenario(ax_map, ax_bat, sc, cfg, t)
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def animate(scenarios: list[Scenario], cfg: SimConfig, path: Path, frames_per_min: int = 6,
            fps: int = 12) -> None:
    fig, axes = _figure(len(scenarios), cfg)

    def update(t):
        for (ax_map, ax_bat), sc in zip(axes, scenarios):
            ax_map.clear()
            ax_bat.clear()
            draw_scenario(ax_map, ax_bat, sc, cfg, float(t))
        return []

    anim = FuncAnimation(fig, update, frames=np.arange(0, cfg.minutes, 1.0 / frames_per_min), blit=False)
    anim.save(path, writer=FFMpegWriter(fps=fps, bitrate=2400), dpi=110)
    plt.close(fig)
