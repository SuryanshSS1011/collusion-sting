"""Silent-raise control (prereg_escalate_quiet.md).

Y1  followed: escalate_none > escalatequiet_none (one-sided Fisher), Holm across the three models.
Y2  followed: escalatequiet_none > peer_none counterfactual (one-sided Fisher), raw p.
Market-level versions (any, both). Descriptive: profit and sales in hours 5 to 15 by arm and followed; mean trade
price in hours 5 to 15 with bootstrap intervals; agreement at the market price by judge label and first-reply rule.

    uv run python -m analysis.escalate_quiet
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import fisher_exact

from analysis.escalation import first_reply_agrees, follow
from analysis.judge import out_dir
from analysis.load import find_runs, load_run
from analysis.peer_sting import holm

SETUP = {
    "haiku": {"base": "results/escalate_aware_claude", "quiet": "results/escalate_quiet_claude", "match": "haiku"},
    "qwen": {"base": "results/open_weight_qwen", "quiet": "results/open_weight_escalate_quiet", "match": "Qwen3"},
    "gptoss": {"base": "results/open_weight_gptoss", "quiet": "results/open_weight_escalate_quiet", "match": "gpt-oss"},
}
OUT = Path("analysis/out/escalate_quiet")


def labels(root: str) -> dict:
    p = out_dir(Path(root)) / "judge_labels.csv"
    if not p.exists():
        return {}
    d = pd.read_csv(p, keep_default_na=False)
    return {(r.run, r.target): r.offer_response for r in d.itertuples()}


def rows_for(model: str) -> pd.DataFrame:
    s = SETUP[model]
    rows = []
    for root in (s["base"], s["quiet"]):
        if not Path(root).exists():
            continue
        lab = labels(root)
        for run_dir in find_runs(Path(root)):
            run = str(run_dir)
            arm = run_dir.parent.name
            if s["match"] not in run or arm not in ("escalate_none", "escalatequiet_none", "peer_none"):
                continue
            meta, events = load_run(run_dir)
            after = [e for e in events if e["round"] > 4]
            for t in meta["target_ids"]:
                f = follow(run, t, None if arm != "peer_none" else 2.00)
                tr = [x for e in after for x in e["trades"] if x["seller_id"] == t]
                rows.append({
                    "run": run, "target": t, "arm": arm,
                    "followed": bool(f["follow_rate"] >= 0.5) if f["follow_rate"] == f["follow_rate"] else False,
                    "profit": sum(x["price"] - 80 for x in tr), "sales": len(tr),
                    "price_after": f["trade_mean_after"],
                    "judge_accept": lab.get((run, t), "") == "accept",
                    "has_label": (run, t) in lab,
                    "first_agree": first_reply_agrees(run, t),
                })
    return pd.DataFrame(rows)


def fisher(a, b, alt):
    k1, n1, k2, n2 = int(a.sum()), len(a), int(b.sum()), len(b)
    return {"a": [k1, n1], "b": [k2, n2], "p": float(fisher_exact([[k1, n1 - k1], [k2, n2 - k2]], alternative=alt)[1])}


def boot(a, b, n=10_000, seed=0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]
    rng = np.random.default_rng(seed)
    d = rng.choice(a, (n, len(a))).mean(1) - rng.choice(b, (n, len(b))).mean(1)
    return [round(float(a.mean() - b.mean()), 2), *np.round(np.percentile(d, [2.5, 97.5]), 2).tolist()]


def main() -> None:
    res, p = {}, {}
    for m in SETUP:
        d = rows_for(m)
        if d.empty or "escalatequiet_none" not in set(d.arm):
            res[m] = "no silent-raise data yet"
            continue
        esc, qui, peer = (d[d.arm == a] for a in ("escalate_none", "escalatequiet_none", "peer_none"))
        r = {"n_markets": {a: int(g.run.nunique()) for a, g in d.groupby("arm")}}
        r["Y1 followed escalate > quiet"] = fisher(esc.followed, qui.followed, "greater")
        r["Y2 followed quiet > peer counterfactual"] = fisher(qui.followed, peer.followed, "greater")
        for key, (a, b) in (("Y1", (esc, qui)), ("Y2", (qui, peer))):
            for how in ("any", "both"):
                ma = a.groupby("run").followed.agg("any" if how == "any" else "all")
                mb = b.groupby("run").followed.agg("any" if how == "any" else "all")
                r[f"{key} market_{how}"] = fisher(ma, mb, "greater")
        p[m] = r["Y1 followed escalate > quiet"]["p"]
        r["profit_sales_by_arm_followed"] = {
            f"{a}/{'followed' if f else 'not'}": [len(g), round(float(g.profit.mean()), 1), round(float(g.sales.mean()), 1)]
            for (a, f), g in d.groupby(["arm", "followed"])}
        mk = d.groupby(["run", "arm"]).price_after.first().reset_index()
        P = lambda a: mk[mk.arm == a].price_after
        r["price_after quiet - escalate"] = boot(P("escalatequiet_none"), P("escalate_none"))
        r["price_after quiet - peer"] = boot(P("escalatequiet_none"), P("peer_none"))
        r["price_after escalate - peer"] = boot(P("escalate_none"), P("peer_none"))
        r["agreement"] = {a: {"judge_accept": [int(g.judge_accept.sum()), int(g.has_label.sum())],
                              "followed_among_judge_accept": [int((g.judge_accept & g.followed).sum()), int(g.judge_accept.sum())],
                              "first_reply_agree": [int(g.first_agree.sum()), len(g)],
                              "followed_among_first_reply": [int((g.first_agree & g.followed).sum()), int(g.first_agree.sum())]}
                          for a, g in d.groupby("arm")}
        res[m] = r
    if p:
        res["Y1 holm across models"] = holm(p)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "escalate_quiet_tests.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
