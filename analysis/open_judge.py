"""A non-Claude rater: export prompts for an open-weight judge, then import its answers.

Export (here): writes paper/modal/prompts.jsonl.gz with
1. the codebook judge prompt (the one Opus used) for every target-market in the Claude grids, and
2. the monitor-test prompts (study, naive and hardened) for every edited transcript.

Run (on a laptop with the Modal endpoint, see paper/modal_runbook.md):
    uv run python modal_jobs/run_prompts.py paper/modal/prompts.jsonl.gz paper/modal/qwen_outputs.jsonl.gz

Import (here): parses the answers into analysis/out/<grid>/judge_labels_qwen.csv and
analysis/out/monitor_test/monitor_calls_qwen.csv, in the same formats as the Claude raters.

uv run python -m analysis.open_judge export
uv run python -m analysis.open_judge import paper/modal/qwen_outputs.jsonl.gz
"""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import pandas as pd

from analysis.judge import PROMPT_CODEBOOK, _fmt, items_for, out_dir
from analysis.monitor_test import ANSWER_KEY, build_sets, parse, render
from src.continuous_double_auction.util.json_util import extract_json

GRIDS = ("main_claude", "replication_claude", "known_answer_claude", "peer_sting_claude", "escalate_aware_claude")
PROMPTS = Path("paper/modal/prompts.jsonl.gz")


def tail(run: str) -> str:
    """The part of a run path below the grid folder, which is the same in results/ and results_final/."""
    parts = Path(run).parts
    for g in GRIDS:
        if g in parts:
            return "/".join(parts[parts.index(g) + 1 :])
    return run


def judge_prompt(it: dict) -> str:
    return PROMPT_CODEBOOK.format(
        target=it["target"],
        sting=it["sting"],
        other=it["other"],
        offers=_fmt(it["offers"]),
        to_sting=_fmt(it["to_sting"]),
        to_other=_fmt(it["to_other_target"]),
        public=_fmt(it["public"]),
    )


def export(root_dir: str) -> None:
    rows = []
    for g in GRIDS:
        root = Path(root_dir) / g
        if not root.exists():
            print(f"skip {g} (not found)")
            continue
        for it in items_for(root):
            rows.append({"id": f"judge|{g}|{tail(it['run'])}|{it['target']}", "prompt": judge_prompt(it)})
    for r in build_sets():
        for p in ANSWER_KEY:
            rid = f"monitor|{r['set']}|{r['version']}|{tail(r['run'])}|{r['target']}|{p}"
            rows.append({"id": rid, "prompt": render(p, r["item"])})
    PROMPTS.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(PROMPTS, "wt") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
    n_j = sum(r["id"].startswith("judge|") for r in rows)
    print(f"wrote {len(rows)} prompts ({n_j} judge, {len(rows) - n_j} monitor) -> {PROMPTS}")


def import_outputs(path: str, root_dir: str) -> None:
    outs = [json.loads(line) for line in gzip.open(path, "rt")]
    judge, monitor = {}, []
    for o in outs:
        kind, *rest = o["id"].split("|")
        if kind == "judge":
            grid, run_tail, target = rest
            ans = extract_json(o.get("raw") or "{}") or {}
            off = str(ans.get("reply_to_planted", "")).strip().lower()
            peer = str(ans.get("coordinates_with_peer", "")).strip().lower()
            judge.setdefault(grid, []).append(
                {
                    "run_tail": run_tail,
                    "target": target,
                    "offer_response": off,
                    "peer_collusion": peer,
                    "rationale": str(ans.get("reason", ""))[:400],
                    "source": "qwen3-32b",
                }
            )
        else:
            s, version, run_tail, target, prompt = rest
            flag, reason = parse(prompt, o.get("raw"))
            monitor.append(
                {
                    "set": s,
                    "version": version,
                    "run_tail": run_tail,
                    "target": target,
                    "monitor_model": "qwen",
                    "prompt": prompt,
                    "flag": flag,
                    "reason": reason[:400],
                }
            )
    for grid, rows in judge.items():
        root = Path(root_dir) / grid
        df = pd.DataFrame(rows)
        # Map back to the run paths the Claude label files use, so the files merge on (run, target).
        runs = {tail(i["run"]): i["run"] for i in items_for(root)}
        df.insert(0, "run", df.run_tail.map(runs))
        df.drop(columns="run_tail").to_csv(out_dir(root) / "judge_labels_qwen.csv", index=False)
        print(f"{grid}: {len(df)} labels, {int((df.peer_collusion == '').sum())} unparsed")
    if monitor:
        df = pd.DataFrame(monitor)
        runs = {tail(r["run"]): r["run"] for r in build_sets()}
        df.insert(0, "run", df.run_tail.map(runs))
        out = Path("analysis/out/monitor_test/monitor_calls_qwen.csv")
        df.drop(columns="run_tail").to_csv(out, index=False)
        print(f"monitor test: {len(df)} calls, {int((df.flag == '').sum())} unparsed -> {out}")


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=("export", "import"))
    p.add_argument("path", nargs="?", default="")
    p.add_argument("--root", default="results")
    a = p.parse_args()
    if a.action == "export":
        export(a.root)
    else:
        import_outputs(a.path, a.root)


if __name__ == "__main__":
    main()
