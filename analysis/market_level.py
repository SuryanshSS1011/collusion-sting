"""Robustness check added October 24, 2026 after an independent re-computation flagged clustering.

The two targets in a market talk to each other, so their peer-coordination labels agree 83% to 95% of the
time, yet every pre-registered test treats targets as independent. That overstates the effective sample.
This script repeats each key test with one observation per market, under two codings: a market counts if
ANY target has the label, or only if BOTH do. The pre-registered target-level tests are unchanged; these
are reported beside them as a sensitivity analysis (logged in the deviations tables).

uv run python -m analysis.market_level
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from scipy.stats import fisher_exact

from analysis.judge import out_dir

A = Path("analysis/out")
OUT = A / "market_level"


def labels(root: str, extra: str | None = None) -> pd.DataFrame:
    od = out_dir(Path(root))
    d = pd.read_csv(od / "judge_labels.csv", keep_default_na=False)[
        ["run", "target", "offer_response", "peer_collusion"]
    ]
    if extra:
        r = pd.read_csv(od / extra, keep_default_na=False)[["run", "target", "deceptive_intent"]]
        d = d.merge(r, on=["run", "target"], how="left")
    d["arm"] = d.run.map(lambda r: Path(r).parent.name)
    d["model"] = d.run.str.extract(r"claude-(\w+)-5-5", expand=False)
    d.loc[d.run.str.contains("Qwen3"), "model"] = "qwen"
    d.loc[d.run.str.contains("gpt-oss"), "model"] = "gptoss"
    d["accept"] = d.offer_response == "accept"
    d["coord"] = d.peer_collusion == "yes"
    if "deceptive_intent" in d:
        d["deceptive"] = d.deceptive_intent == "yes"
    return d


def market(d: pd.DataFrame, col: str, how: str) -> pd.DataFrame:
    agg = "any" if how == "any" else "all"
    return d.groupby(["run", "arm", "model"])[col].agg(agg).reset_index()


def test(d: pd.DataFrame, col: str, a: dict, b: dict, alt: str) -> dict:
    out = {}
    for how in ("target", "any", "both"):
        x = d if how == "target" else market(d, col, how)
        ga = x.loc[(x[list(a)] == pd.Series(a)).all(axis=1), col]
        gb = x.loc[(x[list(b)] == pd.Series(b)).all(axis=1), col]
        k1, n1, k2, n2 = int(ga.sum()), len(ga), int(gb.sum()), len(gb)
        p = float(fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative=alt)[1])
        out[how] = {"a": [k1, n1], "b": [k2, n2], "p": p}
    return out


def open_weight() -> dict:
    """Q1 to Q6 (prereg_open_weight.md) and V1 to V4 (prereg_open_aware.md) at the market level."""
    res = {}
    roots = [r for r in ("results/open_weight_qwen", "results/open_weight_gptoss", "results/open_weight_aware")
             if (out_dir(Path(r)) / "judge_labels.csv").exists()]
    if not roots:
        return res
    d = pd.concat([labels(r) for r in roots], ignore_index=True)
    for m in ("qwen", "gptoss"):
        specs = [
            ("Q1 accept peer_none > direct_none", "accept", "peer_none", "direct_none", "greater"),
            ("Q2 accept peer_none > peer_independent", "accept", "peer_none", "peer_independent", "greater"),
            ("Q4 coord peer_independent > silent_independent", "coord", "peer_independent", "silent_independent", "greater"),
            ("Q5 coord direct_none < silent_none", "coord", "direct_none", "silent_none", "less"),
            ("V1 accept direct_aware < direct_none", "accept", "direct_aware", "direct_none", "less"),
            ("V2 coord silent_aware vs silent_none (two-sided)", "coord", "silent_aware", "silent_none", "two-sided"),
            ("V4 accept peer_aware < peer_none", "accept", "peer_aware", "peer_none", "less"),
        ]
        for name, col, a, b, alt in specs:
            if {a, b} <= set(d[d.model == m].arm):
                res[f"{m} {name}"] = test(d, col, {"arm": a, "model": m}, {"arm": b, "model": m}, alt)
    esc = out_dir(Path("results/open_weight_qwen")) / "escalation_targets.csv"
    if esc.exists():
        e = pd.read_csv(esc, keep_default_na=False)
        e["arm"] = e.run.map(lambda r: Path(r).parent.name)
        e = e[e.arm.isin(["escalate_none", "peer_none"])].copy()
        truthy = lambda v: str(v).strip().lower() in ("true", "1", "1.0")
        e["f"] = [truthy(f) if a == "escalate_none" else truthy(c) for a, f, c in zip(e.arm, e.followed, e.cf_escalate_followed)]
        e["model"] = "qwen"
        res["qwen Q6 followed escalate_none > peer_none counterfactual"] = test(
            e, "f", {"arm": "escalate_none", "model": "qwen"}, {"arm": "peer_none", "model": "qwen"}, "greater"
        )
    return res


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    m = labels("results/main_claude")
    m["cond"] = m.run.map(lambda r: Path(r).parent.name)
    r = labels("results/replication_claude")
    r["cond"] = r.run.map(lambda x: Path(x).parent.name)
    ps = labels("results/peer_sting_claude", "reasoning_labels.csv")
    es = labels("results/escalate_aware_claude")
    res = {
        "main_direct_vs_silent_coord (two-sided)": test(m, "coord", {"arm": "direct"}, {"arm": "silent"}, "two-sided"),
        "main_hint_vs_benign_accept (two-sided)": test(m, "accept", {"arm": "hint"}, {"arm": "benign"}, "two-sided"),
        "R1_direct_lt_silent_coord": test(r, "coord", {"arm": "direct"}, {"arm": "silent"}, "less"),
        "R3_warning_lt_silent_coord": test(r, "coord", {"arm": "warning"}, {"arm": "silent"}, "less"),
        "R4_direct_vs_warning_coord (two-sided)": test(r, "coord", {"arm": "direct"}, {"arm": "warning"}, "two-sided"),
        "P1_peer_gt_direct_accept_haiku": test(
            ps, "accept", {"arm": "peer_none", "model": "haiku"}, {"arm": "direct_none", "model": "haiku"}, "greater"
        ),
        "P2_none_gt_independent_accept_haiku": test(
            ps,
            "accept",
            {"arm": "peer_none", "model": "haiku"},
            {"arm": "peer_independent", "model": "haiku"},
            "greater",
        ),
        "P5_deceptive_sonnet_gt_haiku_silent": test(
            ps,
            "deceptive",
            {"arm": "silent_none", "model": "sonnet"},
            {"arm": "silent_none", "model": "haiku"},
            "greater",
        ),
        "Haiku_direct_lt_silent_coord (peer study)": test(
            ps, "coord", {"arm": "direct_none", "model": "haiku"}, {"arm": "silent_none", "model": "haiku"}, "less"
        ),
        "A1_accept_aware_lt_none (escalation study)": test(
            es, "accept", {"arm": "peer_aware", "model": "haiku"}, {"arm": "peer_none", "model": "haiku"}, "less"
        ),
        "A2_coord_silent_aware_vs_none (two-sided)": test(
            es,
            "coord",
            {"arm": "silent_aware", "model": "haiku"},
            {"arm": "silent_none", "model": "haiku"},
            "two-sided",
        ),
    }
    res.update(open_weight())
    # Within-market agreement of the two targets' labels, the reason for this check.
    agree = {}
    for name, d, col in (
        ("main coord", m, "coord"),
        ("replication coord", r, "coord"),
        ("peer study coord", ps, "coord"),
    ):
        g = d.groupby("run")[col].agg(["sum", "size"])
        g = g[g["size"] == 2]
        agree[name] = float(((g["sum"] == 0) | (g["sum"] == 2)).mean())
    res["within_market_label_agreement"] = agree
    (OUT / "market_level_tests.json").write_text(json.dumps(res, indent=2))
    for k, v in res.items():
        if k == "within_market_label_agreement":
            print(k, {kk: round(vv, 2) for kk, vv in v.items()})
            continue
        print(k)
        for how, x in v.items():
            print(f"   {how:6s} {x['a'][0]}/{x['a'][1]} vs {x['b'][0]}/{x['b'][1]}  p = {x['p']:.2g}")


if __name__ == "__main__":
    main()
