"""Check that every model in a grid config exists on OpenRouter and supports what the harness sends.

    uv run python scripts/check_models.py configs/grid.json

The harness asks for JSON mode (response_format) and passes a seed. OpenRouter silently ignores
parameters a provider does not support, so a model without `seed` will run but will not be
reproducible. Report that in the write-up if it applies.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

URL = "https://openrouter.ai/api/v1/models"


def main() -> None:
    grid = json.loads(Path(sys.argv[1] if len(sys.argv) > 1 else "configs/grid.json").read_text())
    wanted = sorted(set(grid["target_models"]) | {grid["base"]["buyer_model"]})
    with urllib.request.urlopen(URL, timeout=30) as r:
        models = {m["id"]: m for m in json.load(r)["data"]}
    ok = True
    for mid in wanted:
        if mid.startswith("claude/"):
            print(f"skip     {mid:40s} (Anthropic API, not OpenRouter; the smoke test checks it)")
            continue
        m = models.get(mid)
        if m is None:
            print(f"MISSING  {mid}")
            ok = False
            continue
        params = set(m.get("supported_parameters") or [])
        price = m.get("pricing", {})
        pin = float(price.get("prompt", 0)) * 1e6
        pout = float(price.get("completion", 0)) * 1e6
        flags = [f"{p}={'yes' if p in params else 'NO'}" for p in ("response_format", "seed", "temperature")]
        print(f"ok       {mid:40s} ${pin:.2f}/M in  ${pout:.2f}/M out  {'  '.join(flags)}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
