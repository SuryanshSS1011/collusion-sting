"""Report figures, built from the tables that analysis.report writes. Rerun after any relabelling.

    uv run python -m analysis.report results/main_claude
    uv run python -m analysis.figures results/main_claude [--replication results/replication_claude]

Palette: the validated reference categorical palette (dataviz skill), assigned to conditions in a fixed
order and never cycled. Light-mode slots 3 to 5 sit below 3:1 contrast on white, so every mark also
carries a direct value label and a distinct marker shape.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from analysis.judge import out_dir  # noqa: E402
from analysis.behavior import is_joint_proposal  # noqa: E402
from analysis.load import FIRST_READ_ROUND, find_runs, load_run  # noqa: E402
from sting.scripts import OFFER_HOURS  # noqa: E402

COND_ORDER = ["direct", "hint", "benign", "silent", "warning"]
COLORS = {"direct": "#2a78d6", "hint": "#eb6834", "benign": "#1baf7a", "silent": "#eda100", "warning": "#e87ba4"}
MARKERS = {"direct": "o", "hint": "s", "benign": "^", "silent": "D", "warning": "v"}
INK, INK2, GRID, SURFACE = "#0b0b0b", "#52514e", "#e4e3df", "#ffffff"
MODEL_LABEL = {"claude/claude-haiku-5-5": "Claude Haiku 5.5", "claude/claude-sonnet-5-5": "Claude Sonnet 5.5"}


def _style() -> None:
    plt.rcParams.update(
        {
            "font.size": 9,
            "axes.edgecolor": GRID,
            "axes.labelcolor": INK2,
            "axes.titlesize": 10,
            "axes.titleweight": "bold",
            "axes.titlecolor": INK,
            "xtick.color": INK2,
            "ytick.color": INK2,
            "axes.grid": True,
            "grid.color": GRID,
            "grid.linewidth": 0.6,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "legend.frameon": False,
            "savefig.dpi": 200,
            "savefig.bbox": "tight",
        }
    )


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    den = 1 + z**2 / n
    c = (p + z**2 / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (c - h, c + h)


def _rate_panel(ax, t: pd.DataFrame, model: str, conds: list[str], col: str, positive, title: str) -> None:
    g = t[t.target_model == model]
    for i, c in enumerate(conds):
        s = g[g.condition == c][col]
        k, n = int(positive(s).sum()), len(s)
        if n == 0:
            continue
        lo, hi = wilson(k, n)
        p = k / n
        ax.errorbar(i, p, yerr=[[p - lo], [hi - p]], fmt=MARKERS[c], ms=8, color=COLORS[c], ecolor=COLORS[c], lw=2)
        ax.annotate(f"{k}/{n}", (i, p), xytext=(10, 0), textcoords="offset points", va="center", color=INK, fontsize=8)
    ax.set_xticks(range(len(conds)), conds)
    ax.set_xlim(-0.5, len(conds) - 0.3)
    ax.set_ylim(-0.03, 1.05)
    ax.set_title(title)


def fig_peer(t: pd.DataFrame, path: Path, conds: list[str], suptitle: str) -> None:
    models = [m for m in MODEL_LABEL if m in set(t.target_model)]
    fig, axes = plt.subplots(1, len(models), figsize=(3.4 * len(models), 3.0), sharey=True, squeeze=False)
    for ax, m in zip(axes[0], models):
        _rate_panel(ax, t, m, conds, "peer_collusion", lambda s: s == "yes", MODEL_LABEL[m])
    axes[0][0].set_ylabel("share of targets coordinating with peer")
    fig.suptitle(suptitle, x=0.01, y=1.06, ha="left", fontsize=10, color=INK)
    fig.savefig(path)
    plt.close(fig)


def fig_joint(t: pd.DataFrame, path: Path, conds: list[str], suptitle: str) -> None:
    models = [m for m in MODEL_LABEL if m in set(t.target_model)]
    fig, axes = plt.subplots(1, len(models), figsize=(3.4 * len(models), 3.0), sharey=True, squeeze=False)
    rng = np.random.default_rng(0)
    for ax, m in zip(axes[0], models):
        g = t[t.target_model == m]
        for i, c in enumerate(conds):
            x = g[g.condition == c].n_joint_proposals.to_numpy(float)
            if len(x) == 0:
                continue
            ax.scatter(i + rng.uniform(-0.15, 0.15, len(x)), x, s=10, color=COLORS[c], alpha=0.45, linewidths=0)
            ax.plot([i - 0.25, i + 0.25], [x.mean()] * 2, color=INK, lw=2)
            ax.annotate(f"{x.mean():.1f}", (i + 0.27, x.mean()), va="center", fontsize=8, color=INK)
        ax.set_xticks(range(len(conds)), conds)
        ax.set_title(MODEL_LABEL[m])
    axes[0][0].set_ylabel("joint-proposal messages per target")
    fig.suptitle(suptitle, x=0.01, y=1.06, ha="left", fontsize=10, color=INK)
    fig.savefig(path)
    plt.close(fig)


def fig_outcomes(t: pd.DataFrame, path: Path) -> None:
    """What a sting operator would see vs what was happening, for targets that received an offer."""
    sub = t[t.condition.isin(["direct", "hint"])].copy()
    cats = [
        ("accepted, then did not hold the price", "#2a78d6"),
        ("refused or ignored, but coordinating with peer", "#eb6834"),
        ("refused or ignored, no peer coordination", "#c3c2b7"),
    ]

    def cat(r):
        if r.offer_response == "accept":
            return cats[0][0] if r.hold_rate < 0.5 else "accepted and held"
        return cats[1][0] if r.peer_collusion == "yes" else cats[2][0]

    sub["outcome"] = sub.apply(cat, axis=1)
    rows = [(MODEL_LABEL[m], c) for m in MODEL_LABEL for c in ("direct", "hint")]
    fig, ax = plt.subplots(figsize=(7.0, 2.6))
    for y, (mlabel, cond) in enumerate(rows):
        g = sub[(sub.target_model.map(MODEL_LABEL) == mlabel) & (sub.condition == cond)]
        left = 0.0
        for name, color in cats:
            v = (g.outcome == name).mean() if len(g) else 0
            if v > 0:
                ax.barh(y, v, left=left, color=color, edgecolor=SURFACE, linewidth=2, height=0.62)
                if v >= 0.08:
                    ax.text(
                        left + v / 2,
                        y,
                        f"{int(round(v * len(g)))}",
                        ha="center",
                        va="center",
                        fontsize=8,
                        color=INK if color == "#c3c2b7" else SURFACE,
                    )
            left += v
    ax.set_yticks(range(len(rows)), [f"{m.replace('Claude ', '')}, {c}" for m, c in rows])
    ax.invert_yaxis()
    ax.set_xlim(0, 1)
    ax.set_xlabel("share of targets that received the offer (n = 20 per row)")
    ax.grid(axis="y", visible=False)
    ax.legend(
        handles=[plt.Rectangle((0, 0), 1, 1, color=c) for _, c in cats],
        labels=[n for n, _ in cats],
        loc="upper center",
        bbox_to_anchor=(0.5, -0.32),
        ncol=1,
        fontsize=8,
    )
    fig.savefig(path)
    plt.close(fig)


def fig_asks(root: Path, path: Path, conds: list[str]) -> None:
    rows = []
    for d in find_runs(root):
        meta, events = load_run(d)
        cfg = meta["config"]
        for e in events:
            for tid in meta["target_ids"]:
                a = e["seller_asks"].get(tid)
                if a is not None:
                    rows.append(
                        {"m": cfg["target_model"], "f": cfg["floor"], "c": cfg["condition"], "h": e["round"], "a": a}
                    )
    df = pd.DataFrame(rows)
    panels = [(m, f) for m in MODEL_LABEL if m in set(df.m) for f in sorted(df.f.unique())]
    fig, axes = plt.subplots(1, len(panels), figsize=(2.6 * len(panels), 2.8), sharey=True, squeeze=False)
    for ax, (m, f) in zip(axes[0], panels):
        for c in conds:
            g = df[(df.m == m) & (df.f == f) & (df.c == c)].groupby("h").a.mean()
            if len(g):
                ax.plot(g.index, g.values, color=COLORS[c], lw=2, marker=MARKERS[c], ms=3, label=c)
        ax.axhline(90, color=INK2, lw=0.8, ls=":")
        ax.axhline(f, color=INK2, lw=0.8, ls="--")
        ax.axvline(FIRST_READ_ROUND, color=GRID, lw=1)
        ax.set_title(f"{MODEL_LABEL[m].replace('Claude ', '')}, offer ${f:g}")
        ax.set_xlabel("hour")
    axes[0][0].set_ylabel("mean target ask ($)")
    axes[0][-1].legend(fontsize=7, loc="lower right")
    fig.text(
        0.01,
        -0.12,
        "Dotted line: competitive price $90. Dashed line: offer price and planted ask.",
        fontsize=7.5,
        color=INK2,
    )
    fig.savefig(path)
    plt.close(fig)


def fig_timing(root: Path, path: Path, conds: list[str], suptitle: str) -> None:
    """Joint-proposal messages between targets per market-hour. Hour 1 is before any message is read."""
    rows = []
    for d in find_runs(root):
        meta, events = load_run(d)
        tids = meta["target_ids"]
        for e in events:
            n = sum(
                is_joint_proposal(m["text"]) for m in e["private_sent"] if m["from"] in tids and m["to"] in tids
            ) + sum(is_joint_proposal(txt) for sid, txt in e["public_messages"].items() if sid in tids)
            rows.append(
                {"m": meta["config"]["target_model"], "c": meta["config"]["condition"], "h": e["round"], "n": n}
            )
    df = pd.DataFrame(rows)
    models = [m for m in MODEL_LABEL if m in set(df.m)]
    fig, axes = plt.subplots(1, len(models), figsize=(3.6 * len(models), 2.8), sharey=True, squeeze=False)
    for ax, m in zip(axes[0], models):
        for c in conds:
            g = df[(df.m == m) & (df.c == c)].groupby("h").n.mean()
            if len(g):
                ax.plot(g.index, g.values, color=COLORS[c], lw=2, marker=MARKERS[c], ms=3, label=c)
        for h in OFFER_HOURS:
            ax.axvline(h + 1, color=GRID, lw=1)
        ax.set_title(MODEL_LABEL[m])
        ax.set_xlabel("hour")
    axes[0][0].set_ylabel("joint proposals per market-hour")
    axes[0][-1].legend(fontsize=7)
    fig.suptitle(suptitle, x=0.01, y=1.06, ha="left", fontsize=10, color=INK)
    fig.text(
        0.01,
        -0.12,
        "Vertical lines: hours in which the planted seller's messages are read (2, 5, 9).",
        fontsize=7.5,
        color=INK2,
    )
    fig.savefig(path)
    plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("root")
    p.add_argument("--replication", default=None)
    a = p.parse_args()
    _style()
    root = Path(a.root)
    od = out_dir(root)
    figdir = Path("paper/figures")
    figdir.mkdir(parents=True, exist_ok=True)
    t = pd.read_csv(od / "targets.csv")
    main_conds = ["direct", "hint", "benign", "silent"]
    fig_peer(
        t, figdir / "fig_peer_main.png", main_conds, "Main grid: peer coordination by condition (judge, 95% Wilson CI)"
    )
    fig_joint(t, figdir / "fig_joint_main.png", main_conds, "Main grid: joint-proposal language (judge-free)")
    fig_outcomes(t, figdir / "fig_sting_outcomes.png")
    fig_asks(root, figdir / "fig_asks_main.png", main_conds)
    if a.replication:
        rroot = Path(a.replication)
        rt = pd.read_csv(out_dir(rroot) / "targets.csv")
        rc = ["direct", "warning", "silent"]
        fig_peer(rt, figdir / "fig_peer_replication.png", rc, "Replication: peer coordination (judge, 95% Wilson CI)")
        fig_joint(rt, figdir / "fig_joint_replication.png", rc, "Replication: joint-proposal language (judge-free)")
        fig_timing(rroot, figdir / "fig_timing_replication.png", rc, "Replication: when targets propose coordination")
    print(f"wrote figures to {figdir}")


if __name__ == "__main__":
    main()
