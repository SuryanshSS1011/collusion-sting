"""Copy the compact record of a finished grid (meta, events, usage) from results/ to results_final/.

uv run python scripts/compact_results.py open_weight_qwen
"""

import shutil
import sys
from pathlib import Path

for name in sys.argv[1:]:
    src, dst = Path("results") / name, Path("results_final") / name
    n = 0
    for meta in src.rglob("sting_meta.json"):
        d = meta.parent
        o = dst / d.relative_to(src)
        o.mkdir(parents=True, exist_ok=True)
        for f in ("sting_meta.json", "events.jsonl", "usage.json"):
            if (d / f).exists():
                shutil.copy2(d / f, o / f)
        n += 1
    if (src / "usage_total.json").exists():
        shutil.copy2(src / "usage_total.json", dst / "usage_total.json")
    print(f"{name}: {n} markets -> {dst}")
