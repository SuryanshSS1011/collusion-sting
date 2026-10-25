"""Qwen3-32B as a fourth, non-Claude rater of the Claude transcripts.

Qwen answered the codebook judge prompt (the one Opus used) and the three monitor-test prompts on Modal
(analysis/open_judge.py). This script reports, without any API calls,

1. agreement of Qwen's labels with Sonnet (study prompt), Opus or the Sonnet codebook rerun, and the rules coder;
2. the known-answer accuracy of Qwen's labels;
3. the key tests of every study recomputed with Qwen's labels;
4. the disclaimer monitor test with Qwen as the monitor.

The 3-rater majority used elsewhere is unchanged; Qwen is reported beside it, not folded into it.

    uv run python -m analysis.qwen_rater
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

import analysis.validation as V
from analysis.judge import cohen_kappa, items_for, out_dir
from analysis.monitor_test import TESTS, boot_diff, mcnemar_one_sided
from analysis.rules import norm, rule_offer, rule_peer

ROOT = Path("results")
OUT = Path("analysis/out/validation")


def qwen(root: Path) -> pd.DataFrame:
    q = pd.read_csv(out_dir(root) / "judge_labels_qwen.csv", keep_default_na=False)
    q = q.rename(columns={"offer_response": "offer_qwen", "peer_collusion": "peer_qwen"})[
        ["run", "target", "offer_qwen", "peer_qwen"]
    ]
    for c in ("offer_qwen", "peer_qwen"):
        q[c] = q[c].map(norm)
    return q


def raters(root: Path) -> pd.DataFrame:
    """Every available rater's labels for one grid, one row per target-market."""
    od = out_dir(root)
    items = items_for(root)
    df = pd.DataFrame(
        [
            {
                "run": i["run"],
                "target": i["target"],
                "offer_rules": rule_offer(i),
                "peer_rules": rule_peer(i),
                "has_reply": bool(i["to_sting"]),
                "has_peer_text": bool(i["to_other_target"] or i["public"]),
            }
            for i in items
        ]
    )
    for name, fname in (
        ("sonnet", "judge_labels.csv"),
        ("opus", "judge_labels_opus.csv"),
        ("sonnetcb", "judge_labels_sonnet_codebook.csv"),
    ):
        p = od / fname
        if p.exists():
            lab = pd.read_csv(p, keep_default_na=False)
            cols = {"offer_response": f"offer_{name}", "peer_collusion": f"peer_{name}"}
            lab = lab.rename(columns=cols)[["run", "target", *[c for c in cols.values() if c in lab.rename(columns=cols)]]]
            df = df.merge(lab, on=["run", "target"], how="left")
    df = df.merge(qwen(root), on=["run", "target"], how="left")
    for c in [c for c in df.columns if c.startswith(("offer_", "peer_"))]:
        df[c] = df[c].fillna("").map(norm)
    return df


def agreement(df: pd.DataFrame, grid: str) -> list[dict]:
    rows = []
    for label, mask in (("offer", "has_reply"), ("peer", "has_peer_text")):
        sub = df[df[mask]]
        for other in ("sonnet", "opus", "sonnetcb", "rules"):
            a, b = f"{label}_qwen", f"{label}_{other}"
            if b not in sub:
                continue
            s = sub[(sub[a] != "") & (sub[b] != "")]
            if not len(s):
                continue
            rows.append(
                {
                    "grid": grid,
                    "label": label,
                    "vs": other,
                    "n": len(s),
                    "raw": round(float((s[a] == s[b]).mean()), 3),
                    "kappa": round(cohen_kappa(list(s[a]), list(s[b])), 3),
                }
            )
    return rows


def fisher(k1, n1, k2, n2, alt):
    return float(fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative=alt)[1])


def arm(run: str) -> str:
    return Path(run).parts[-2]


def model(run: str) -> str:
    return "sonnet" if "sonnet" in run else "haiku" if "haiku" in run else "other"


def study_tests() -> list[dict]:
    """Primary tests of the peer-sting and escalation studies, with Sonnet and with Qwen labels."""
    rows = []
    specs = [
        ("peer_sting_claude", "P1 accept: peer_none > direct_none", "offer", "accept", "peer_none", "direct_none", "greater"),
        ("peer_sting_claude", "P2 accept: peer_none > peer_independent", "offer", "accept", "peer_none", "peer_independent", "greater"),
        ("peer_sting_claude", "P4 coord: peer_independent > silent_independent", "peer", "yes", "peer_independent", "silent_independent", "greater"),
        ("peer_sting_claude", "deterrence coord: direct_none < silent_none", "peer", "yes", "direct_none", "silent_none", "less"),
        ("escalate_aware_claude", "A1 accept: peer_aware < peer_none", "offer", "accept", "peer_aware", "peer_none", "less"),
        ("escalate_aware_claude", "A2 coord: silent_aware vs silent_none", "peer", "yes", "silent_aware", "silent_none", "two-sided"),
    ]
    cache = {}
    for grid, name, label, val, a, b, alt in specs:
        if grid not in cache:
            cache[grid] = raters(ROOT / grid)
        df = cache[grid]
        df = df[df.run.map(model) == "haiku"]
        for src in ("sonnet", "qwen"):
            col = f"{label}_{src}"
            ga, gb = df[(df.run.map(arm) == a) & (df[col] != "")], df[(df.run.map(arm) == b) & (df[col] != "")]
            k1, n1, k2, n2 = int((ga[col] == val).sum()), len(ga), int((gb[col] == val).sum()), len(gb)
            rows.append(
                {"test": name, "labels": src, "a": f"{k1}/{n1}", "b": f"{k2}/{n2}", "p": fisher(k1, n1, k2, n2, alt)}
            )
    # P3: acceptance predicts coordination in the pooled Haiku peer arms.
    df = cache["peer_sting_claude"]
    df = df[(df.run.map(model) == "haiku") & df.run.map(arm).isin(["peer_none", "peer_independent"])]
    for src in ("sonnet", "qwen"):
        d = df[(df[f"offer_{src}"] != "") & (df[f"peer_{src}"] != "")]
        acc, coord = (d[f"offer_{src}"] == "accept").values, (d[f"peer_{src}"] == "yes").values
        tab = [[int((acc & coord).sum()), int((acc & ~coord).sum())], [int((~acc & coord).sum()), int((~acc & ~coord).sum())]]
        sens = tab[0][0] / max(1, tab[0][0] + tab[1][0])
        spec = tab[1][1] / max(1, tab[1][1] + tab[0][1])
        rows.append(
            {
                "test": "P3 accept predicts coord (peer arms)",
                "labels": src,
                "a": f"sens {sens:.2f}",
                "b": f"spec {spec:.2f}",
                "p": float(fisher_exact(tab, alternative="greater")[1]),
            }
        )
    return rows


def main_tests() -> pd.DataFrame:
    """The main and replication key tests from analysis.validation, with Qwen's labels."""
    frames = []
    for g in ("main_claude", "replication_claude"):
        t = V.with_targets(ROOT / g).merge(qwen(ROOT / g), on=["run", "target"], how="left").fillna({"offer_qwen": "", "peer_qwen": ""})
        frames.append(t)
    V.SOURCES = ("sonnet", "qwen")
    return V.key_tests(*frames)


def known_answer() -> list[dict]:
    root = ROOT / "known_answer_claude"
    df, _ = V.known_answer(root)
    df = df.merge(qwen(root), on=["run", "target"], how="left").fillna({"offer_qwen": "", "peer_qwen": ""})
    rows = []
    for label in ("offer", "peer"):
        for subset, g in (("all", df), ("complied", df[df.complied])):
            row = {"label": label, "subset": subset, "n": len(g)}
            for src in ("sonnet", "opus", "rules", "qwen"):
                if f"{label}_{src}" in g:
                    row[src] = round(float((g[f"{label}_{src}"] == g[f"expect_{label}"]).mean()), 3)
            rows.append(row)
    return rows


def monitor() -> list[dict]:
    df = pd.read_csv("analysis/out/monitor_test/monitor_calls_qwen.csv", keep_default_na=False)
    rows = []
    for prompt, g in df.groupby("prompt"):
        for name, s, va, vb in TESTS:
            wide = g[g.set == s].pivot_table(index=["run", "target"], columns="version", values="flag", aggfunc="first")
            if va not in wide or vb not in wide:
                continue
            wide = wide[(wide[va] != "") & (wide[vb] != "")]
            a_only, b_only, p = mcnemar_one_sided(wide[va], wide[vb])
            d, lo, hi = boot_diff(wide[va], wide[vb])
            rows.append(
                {
                    "prompt": prompt,
                    "test": name,
                    "n_pairs": len(wide),
                    "rate_a": round(float((wide[va] == "yes").mean()), 3),
                    "rate_b": round(float((wide[vb] == "yes").mean()), 3),
                    "a_only": a_only,
                    "b_only": b_only,
                    "p_one_sided": p,
                    "diff": round(d, 3),
                    "ci": [round(lo, 3), round(hi, 3)],
                }
            )
    return rows


def main() -> None:
    agree = []
    for g in ("main_claude", "replication_claude", "known_answer_claude", "peer_sting_claude", "escalate_aware_claude"):
        agree += agreement(raters(ROOT / g), g)
    res = {
        "agreement": agree,
        "known_answer_accuracy": known_answer(),
        "main_key_tests": main_tests().to_dict("records"),
        "study_tests": study_tests(),
        "monitor_test": monitor(),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "qwen_rater.json").write_text(json.dumps(res, indent=2, default=lambda x: None if x != x else x))
    pd.set_option("display.width", 200)
    for k, v in res.items():
        print(f"\n== {k}")
        print(pd.DataFrame(v).to_string(index=False))


if __name__ == "__main__":
    main()
