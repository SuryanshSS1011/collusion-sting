"""Read one market as a timeline: asks, trades, every message, and each target's stated plan.

    uv run python -m analysis.view results/pilot/openai__gpt-4.1-mini/direct/seed0
    uv run python -m analysis.view results/pilot --all > pilot_transcripts.md   # every market, one file

Use this to read the pilot before freezing prereg.md, and to sanity-check judge labels.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from analysis.load import find_runs, load_run


def short(name: str) -> str:
    return name.removeprefix("Seller ").removeprefix("Buyer ")


def render(run_dir: Path, plans: bool = True) -> str:
    meta, events = load_run(run_dir)
    cfg = meta["config"]
    sting, targets = meta["sting_id"], meta["target_ids"]
    tag = {sting: f"{short(sting)}*", **{t: short(t) for t in targets}}
    lines = [
        f"## {cfg['target_model']} | {cfg['condition']} | seed {cfg['seed']} | wording {meta['wording']}",
        f"Planted seller: {sting} (marked *), fixed ask ${cfg['fixed_ask']:.2f}. Targets: {', '.join(targets)}.",
        f"Competitive ${meta['competitive_price']:.0f}, cartel ${meta['cartel_price']:.0f}.",
        "",
    ]
    for e in events:
        asks = "  ".join(f"{tag.get(s, short(s))} {a:.2f}" for s, a in sorted(e["seller_asks"].items()))
        trades = ", ".join(f"{short(t['seller_id'])}@{t['price']:.2f}" for t in e["trades"]) or "none"
        lines.append(f"### Hour {e['round']}   asks: {asks}   trades: {trades}")
        for m in e["private_sent"]:
            lines.append(f"- [private] {tag.get(m['from'], m['from'])} -> {tag.get(m['to'], m['to'])}: {m['text']}")
        for s, msg in e["public_messages"].items():
            lines.append(f"- [public] {tag.get(s, s)}: {msg}")
        for r in e.get("reports", []):
            lines.append(f"- [REPORT] {tag.get(r['from'], r['from'])}: {r['text']}")
        for d in e.get("private_dropped", []):
            lines.append(f"- [dropped, unknown recipient '{d['to_raw']}'] {tag.get(d['from'], d['from'])}: {d['text']}")
        for a, err in e.get("errors", {}).items():
            lines.append(f"- [call failed] {short(a)}: {err}")
        if plans:
            for t in targets:
                plan = e["responses"].get(t, {}).get("plan_for_this_hour")
                if plan:
                    lines.append(f"  - plan {short(t)}: {plan}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("path")
    p.add_argument("--all", action="store_true", help="render every finished market under path")
    p.add_argument("--no-plans", action="store_true")
    a = p.parse_args()
    runs = find_runs(Path(a.path)) if a.all else [Path(a.path)]
    print("\n\n".join(render(r, plans=not a.no_plans) for r in runs))


if __name__ == "__main__":
    main()
