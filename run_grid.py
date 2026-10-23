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
    for model, cond, seed in itertools.product(grid["target_models"], grid["conditions"], grid["seeds"]):
        yield model, cond, seed


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
    for model, cond, seed in cells(grid):
        out = root / slug(model) / cond / f"seed{seed}"
        cfg = StingConfig(condition=cond, seed=seed, target_model=model, mock=a.mock, **base)
        plan.append((cfg, out, (out / "DONE").exists()))

    todo = [x for x in plan if not x[2]]
    calls_per_run = base["rounds"] * (base["n_targets"] + base["n_buyers"])
    print(
        f"{grid['name']}: {len(plan)} cells, {len(plan) - len(todo)} done, {len(todo)} to run, "
        f"~{calls_per_run} model calls per market, ~{calls_per_run * len(todo):,} calls in total."
    )
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
    if failures:
        print(f"{len(failures)} cells failed; rerun the same command to retry only those.")
        sys.exit(1)
    print("all cells done.")


if __name__ == "__main__":
    main()
