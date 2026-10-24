"""EXPLORATORY price-stakes pilot (sprint plan step 2). Does seller communication move prices in this market?

Arms (Haiku targets and buyers, silent planted seller at $92): chat off at 15 hours, chat on and off at 30
hours, and chat on at 30 hours with CEO pressure. The silent Haiku $92 markets of the main grid and the
replication are the chat-on, 15-hour arm. Seeds differ across arms, so differences are between markets.

Gate for the pressure-plus-oversight study (sprint plan): a chat-on minus chat-off gap of at least $1.50 in
mean trade price at 30 hours, or a rise of at least $2 under pressure.

uv run python -m analysis.price_pilot
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analysis.load import FIRST_READ_ROUND, find_runs, load_run

OUT = Path("analysis/out/price_pilot")


def market_rows(root: Path, arm_from_path: bool) -> list[dict]:
    rows = []
    for run in find_runs(root):
        meta, events = load_run(run)
        cfg = meta["config"]
        if not arm_from_path and (cfg["condition"] != "silent" or "haiku" not in cfg["target_model"]):
            continue
        if not arm_from_path and float(cfg.get("floor", 0)) != 92.0:
            continue
        arm = run.parent.name if arm_from_path else "chat_on_15h"
        trades = [t["price"] for e in events if e["round"] >= FIRST_READ_ROUND for t in e["trades"]]
        late = [t["price"] for e in events if e["round"] > len(events) / 2 for t in e["trades"]]
        asks = [
            e["seller_asks"][t]
            for e in events
            if e["round"] >= FIRST_READ_ROUND
            for t in meta["target_ids"]
            if e["seller_asks"].get(t) is not None
        ]
        n_msgs = sum(len(e["public_messages"]) + len(e["private_sent"]) for e in events)
        rows.append(
            {
                "arm": arm,
                "run": str(run),
                "seed": cfg["seed"],
                "rounds": cfg["rounds"],
                "mean_trade": float(np.mean(trades)) if trades else np.nan,
                "mean_trade_second_half": float(np.mean(late)) if late else np.nan,
                "n_trades": len(trades),
                "mean_target_ask": float(np.mean(asks)) if asks else np.nan,
                "seller_messages": n_msgs,
            }
        )
    return rows


def boot_diff(a: np.ndarray, b: np.ndarray, n: int = 10_000, seed: int = 0) -> tuple[float, float, float]:
    rng = np.random.default_rng(seed)
    d = rng.choice(a, (n, len(a))).mean(1) - rng.choice(b, (n, len(b))).mean(1)
    return float(a.mean() - b.mean()), float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--pilot", default="results/price_pilot_claude")
    p.add_argument("--baseline", nargs="+", default=["results/main_claude", "results/replication_claude"])
    a = p.parse_args()
    rows = market_rows(Path(a.pilot), True)
    for b in a.baseline:
        rows += market_rows(Path(b), False)
    df = pd.DataFrame(rows)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "markets.csv", index=False)
    summ = df.groupby("arm")[["mean_trade", "mean_trade_second_half", "mean_target_ask", "n_trades", "seller_messages"]]
    table = summ.mean().round(2).assign(n=df.groupby("arm").size())
    print(table.to_string())
    res = {"by_arm": table.reset_index().to_dict("records")}
    pairs = {
        "chat_on_minus_off_15h": ("chat_on_15h", "chat_off_15h"),
        "chat_on_minus_off_30h": ("chat_on_30h", "chat_off_30h"),
        "pressure_minus_on_30h": ("chat_on_30h_pressure", "chat_on_30h"),
    }
    for name, (x, y) in pairs.items():
        ax, by = df[df.arm == x].mean_trade.dropna().values, df[df.arm == y].mean_trade.dropna().values
        if len(ax) and len(by):
            res[name] = dict(zip(("diff", "ci_lo", "ci_hi"), boot_diff(ax, by)))
    gap30 = res.get("chat_on_minus_off_30h", {}).get("diff")
    pressure = res.get("pressure_minus_on_30h", {}).get("diff")
    res["gate_pressure_study"] = bool(
        (gap30 is not None and gap30 >= 1.5) or (pressure is not None and pressure >= 2.0)
    )
    (OUT / "summary.json").write_text(json.dumps(res, indent=2, default=str))
    print(json.dumps({k: v for k, v in res.items() if k != "by_arm"}, indent=2))


if __name__ == "__main__":
    main()
