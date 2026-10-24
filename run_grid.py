"""Run a grid of sting markets from a JSON config. Finished cells are skipped, so it is safe to rerun.

    uv run python run_grid.py configs/pilot.json --dry-run      # list cells and call counts
    uv run python run_grid.py configs/pilot.json --mock         # free offline run of the whole grid
    uv run python run_grid.py configs/pilot.json                # real run (asks before spending)
    uv run python run_grid.py configs/grid.json --jobs 4 -y     # main grid, 4 markets at a time

Layout: results/<grid name>/<model slug>/<condition>/seed<k>/
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from sting.run import StingConfig, run_one


def slug(model: str) -> str:
    return model.replace("/", "__")


def cells(grid: dict):
    """Optional "floors": a list of offer prices. Each floor sets both the named price and the planted ask.

    Optional "known_answer": a list of {name, condition, instruction, expect_offer, expect_peer}. Each entry
    replaces "conditions" with a validation arm whose correct labels are fixed by the instruction.

    Optional "arms": a list of {name, condition, instruction?, overrides?, target_models?, seeds?}. Each entry
    replaces "conditions"; "overrides" sets StingConfig fields for that arm only, and an arm's own
    "target_models" or "seeds" replace the grid-level lists for that arm.
    """
    floors = grid.get("floors", [None])
    arms = grid.get("arms") or grid.get("known_answer") or [{"name": c, "condition": c} for c in grid["conditions"]]
    for arm in arms:
        models = arm.get("target_models", grid["target_models"])
        seeds = arm.get("seeds", grid["seeds"])
        for model, floor, seed in itertools.product(models, floors, seeds):
            yield model, floor, arm, seed


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("config")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--mock", action="store_true", help="offline mock model; writes to results_mock/")
    p.add_argument("--jobs", type=int, default=1, help="markets run concurrently")
    p.add_argument("-y", "--yes", action="store_true", help="skip the confirmation prompt")
    a = p.parse_args()

    grid = json.loads(Path(a.config).read_text())
    root = Path("results_mock" if a.mock else "results") / grid["name"]
    base = grid["base"]
    plan = []
    for model, floor, arm, seed in cells(grid):
        sub = root / slug(model) if floor is None else root / slug(model) / f"floor{floor:g}"
        out = sub / arm["name"] / f"seed{seed}"
        over = {} if floor is None else {"floor": float(floor), "fixed_ask": float(floor)}
        if "instruction" in arm:
            over |= {"instruction": arm["instruction"]}
        if "expect_offer" in arm or "expect_peer" in arm:
            over |= {
                "known_answer": arm["name"],
                "expect_offer": arm.get("expect_offer", ""),
                "expect_peer": arm.get("expect_peer", ""),
            }
        over |= arm.get("overrides", {})
        cfg = StingConfig(condition=arm["condition"], seed=seed, target_model=model, mock=a.mock, **{**base, **over})
        plan.append((cfg, out, (out / "DONE").exists()))

    todo = [x for x in plan if not x[2]]
    n_calls = sum(c.rounds * (c.n_targets + c.n_buyers) for c, _, _ in todo)
    print(f"{grid['name']}: {len(plan)} cells, {len(plan) - len(todo)} done, {len(todo)} to run, ~{n_calls:,} calls.")
    for cfg, out, done in plan:
        print(f"  {'done' if done else 'todo'}  {out}  (wording {cfg.resolved_wording()})")
    if a.dry_run or not todo:
        return
    if not (a.mock or a.yes):
        if not sys.stdin.isatty() or input("Spend API credits on this? [y/N] ").strip().lower() not in (
            "y",
            "yes",
        ):
            sys.exit("aborted (pass -y to skip this prompt)")

    failures = []

    def work(item):
        cfg, out, _ = item
        out.parent.mkdir(parents=True, exist_ok=True)
        run_one(cfg, out)
        return out

    with ThreadPoolExecutor(max_workers=max(1, a.jobs)) as pool:
        futs = {pool.submit(work, item): item for item in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            out = futs[fut][1]
            try:
                fut.result()
                print(f"[{i}/{len(todo)}] ok   {out}")
            except Exception:  # noqa: BLE001
                failures.append(out)
                print(f"[{i}/{len(todo)}] FAIL {out}\n{traceback.format_exc()}")
    total = {}
    for _, out, _ in plan:
        f = out / "usage.json"
        if f.exists():
            for model, row in json.loads(f.read_text()).items():
                t = total.setdefault(model, {"calls": 0, "input_tokens": 0, "output_tokens": 0, "usd_list_price": 0.0})
                for k in t:
                    t[k] += row.get(k, 0)
    if total:
        (root / "usage_total.json").write_text(json.dumps(total, indent=2))
        spend = sum(t["usd_list_price"] for t in total.values())
        print(f"Claude usage for this grid so far: ~${spend:.2f} at list price -> {root / 'usage_total.json'}")
    if failures:
        print(f"{len(failures)} cells failed; rerun the same command to retry only those.")
        sys.exit(1)
    print("all cells done.")


if __name__ == "__main__":
    main()
