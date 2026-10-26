"""Send a file of prompts to the served open-weight model and save the raw answers (run on your laptop).

    uv run python modal_jobs/run_prompts.py data/modal/prompts.jsonl.gz data/modal/qwen_outputs.jsonl.gz

Reads VLLM_BASE_URL and VLLM_API_KEY from compute.env. Resumable: ids already in the output are skipped.
Thinking is off and temperature is 0, so the open-weight judge answers in one pass like the Claude judges.
"""

from __future__ import annotations

import argparse
import gzip
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

MODEL = "Qwen/Qwen3-32B-FP8"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("prompts")
    p.add_argument("out")
    p.add_argument("--concurrency", type=int, default=32)
    p.add_argument("--limit", type=int, default=0, help="only the first N prompts (smoke test)")
    a = p.parse_args()
    load_dotenv("compute.env")
    client = OpenAI(base_url=os.environ["VLLM_BASE_URL"], api_key=os.environ.get("VLLM_API_KEY", "EMPTY"), timeout=600)
    items = [json.loads(line) for line in gzip.open(a.prompts, "rt")]
    if a.limit:
        items = items[: a.limit]
    out = Path(a.out)
    done = set()
    if out.exists():
        done = {json.loads(line)["id"] for line in gzip.open(out, "rt")}
    todo = [i for i in items if i["id"] not in done]
    print(f"{len(items)} prompts, {len(done)} already answered, {len(todo)} to send")

    def ask(item):
        for attempt in range(5):
            try:
                r = client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": item["prompt"]}],
                    temperature=0,
                    max_tokens=400,
                    extra_body={"chat_template_kwargs": {"enable_thinking": False}},
                )
                return {"id": item["id"], "raw": r.choices[0].message.content}
            except Exception as e:  # noqa: BLE001
                err = str(e)
        return {"id": item["id"], "raw": None, "error": err[:300]}

    with gzip.open(out, "at") as f, ThreadPoolExecutor(a.concurrency) as pool:
        for n, fut in enumerate(as_completed([pool.submit(ask, i) for i in todo]), 1):
            f.write(json.dumps(fut.result()) + "\n")
            if n % 100 == 0:
                f.flush()
                print(f"  {n}/{len(todo)}")
    print("done ->", out)


if __name__ == "__main__":
    main()
