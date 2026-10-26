"""One figure comparing Claude Haiku with the two open-weight sellers on the key measures.

Reads only the saved test outputs of analysis.peer_sting and analysis.escalation, plus the open-weight
sting-awareness labels when they exist, so it makes no API calls.

    uv run python -m analysis.cross_family
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from analysis.figures import COLORS, INK2, _style, wilson

A = Path("analysis/out")
MODELS = (("haiku", "Claude Haiku 5.5"), ("qwen", "Qwen3-32B"), ("gptoss", "gpt-oss-20b"))
PEER = {"haiku": "peer_sting_claude", "qwen": "open_weight_qwen", "gptoss": "open_weight_gptoss"}
ESC = {"haiku": "escalate_aware_claude", "qwen": "open_weight_qwen", "gptoss": "open_weight_gptoss"}


def load() -> dict:
    out = {}
    for m, _ in MODELS:
        s = json.loads((A / PEER[m] / "peer_sting_tests.json").read_text())["secondary"][m]
        d = {
            "accept_direct": s["direct/none"]["accept"][:2],
            "accept_peer": s["peer/none"]["accept"][:2],
            "accept_peer_instr": s["peer/independent"]["accept"][:2],
            "coord_silent": s["silent/none"]["peer_coord"][:2],
            "coord_direct": s["direct/none"]["peer_coord"][:2],
            "coord_silent_instr": s["silent/independent"]["peer_coord"][:2],
        }
        if m in ESC:
            e = json.loads((A / ESC[m] / "escalation_tests.json").read_text())["E1_large_step"]
            d["followed_raise"], d["followed_cf"] = e["escalation"], e["control_counterfactual"]
        out[m] = d
    aware = A / "open_weight_aware" / "judge_labels.csv"
    hk = json.loads((A / "escalate_aware_claude" / "escalation_tests.json").read_text())
    out["haiku"]["coord_silent_aware"] = hk["A2_coord_silent_aware_vs_none"]["aware"]
    out["haiku"]["accept_peer_aware"] = hk["A1_accept_aware_lt_none"]["aware"]
    if aware.exists():
        lab = pd.read_csv(aware, keep_default_na=False)
        lab["arm"] = lab.run.map(lambda r: Path(r).parent.name)
        lab["m"] = lab.run.map(lambda r: "qwen" if "Qwen3" in r else "gptoss")
        for m in ("qwen", "gptoss"):
            g = lab[(lab.m == m) & (lab.arm == "silent_aware")]
            out[m]["coord_silent_aware"] = [int((g.peer_collusion == "yes").sum()), len(g)]
            g = lab[(lab.m == m) & (lab.arm == "direct_aware")]
            out[m]["accept_direct_aware"] = [int((g.offer_response == "accept").sum()), len(g)]
            g = lab[(lab.m == m) & (lab.arm == "peer_aware")]
            if len(g):
                out[m]["accept_peer_aware"] = [int((g.offer_response == "accept").sum()), len(g)]
    return out


def figure(d: dict, path: Path) -> None:
    import matplotlib.pyplot as plt

    _style()
    c_def, c_alt, c_third = COLORS["direct"], COLORS["hint"], COLORS["silent"]
    panels = [
        (
            "Agreed to the explicit $92 offer",
            [("accept_direct", "default", c_def, True), ("accept_direct_aware", "auditor notice", c_third, False)],
        ),
        (
            "Agreed to the peer-style sting",
            [
                ("accept_peer", "default", c_def, True),
                ("accept_peer_instr", "told to stay independent", c_alt, False),
                ("accept_peer_aware", "auditor notice", c_third, False),
            ],
        ),
        (
            "Coordinated with the other seller",
            [
                ("coord_silent", "silent market", c_def, True),
                ("coord_direct", "after the explicit offer", c_alt, True),
                ("coord_silent_aware", "silent, auditor notice", c_third, False),
            ],
        ),
        (
            "Held a +$2 raise (escalation)",
            [("followed_raise", "escalation sting", c_def, True), ("followed_cf", "counterfactual", c_alt, False)],
        ),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(13, 4.3), sharey=True)
    for ax, (title, series) in zip(axes, panels):
        width = 0.22 if len(series) == 3 else 0.16
        for j, (key, lab, col, filled) in enumerate(series):
            off = (j - (len(series) - 1) / 2) * width * 1.6
            for x, (m, _) in enumerate(MODELS):
                if key not in d[m]:
                    continue
                k, n = d[m][key]
                lo, hi = wilson(k, n)
                ax.errorbar(x + off, k / n, yerr=[[k / n - lo], [hi - k / n]], fmt="none", ecolor=col, elinewidth=1, alpha=0.7)
                ax.plot(x + off, k / n, "o", ms=6, color=col, mfc=col if filled else "white", mew=1.5,
                        label=lab if x == min(i for i, (mm, _) in enumerate(MODELS) if key in d[mm]) else None)
                ax.annotate(f"{k}", (x + off, k / n), xytext=(0, 7), textcoords="offset points", fontsize=6.5,
                            color=INK2, ha="center")
        ax.set_xticks(range(len(MODELS)), [lab for _, lab in MODELS], fontsize=7.5)
        ax.set_xlim(-0.6, len(MODELS) - 0.4)
        ax.set_title(title, loc="left", fontsize=9)
        ax.legend(fontsize=6.5, loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False)
    axes[0].set_ylim(-0.05, 1.12)
    axes[0].set_ylabel("share of targets (n = 40 each; 95% Wilson CI)")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=200, bbox_inches="tight")
    print(f"wrote {path}")


def main() -> None:
    d = load()
    (A / "cross_family.json").write_text(json.dumps(d, indent=2))
    figure(d, Path("paper/figures/fig_cross_family.png"))


if __name__ == "__main__":
    main()
