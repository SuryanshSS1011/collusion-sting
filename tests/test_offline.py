"""Offline checks of the experimental controls. No network; uses the mock model.

uv run pytest -q
"""

import json
from pathlib import Path

import pytest

from sting.run import StingConfig, run_one
from sting.scripts import CONDITIONS, OFFER_HOURS, schedule, wording_for_seed


def _run(tmp_path: Path, condition: str, seed: int = 0, rounds: int = 6, **kw):
    out = tmp_path / condition / f"seed{seed}"
    out.parent.mkdir(parents=True, exist_ok=True)
    cfg = StingConfig(
        condition=condition, seed=seed, target_model="mock", buyer_model="mock", rounds=rounds, mock=True, **kw
    )
    run_one(cfg, out)
    meta = json.loads((out / "sting_meta.json").read_text())
    events = [json.loads(line) for line in (out / "events.jsonl").read_text().splitlines()]
    return meta, events


def test_wording_rule_and_schedule():
    assert wording_for_seed(0) == "A" and wording_for_seed(3) == "B"
    assert schedule("silent", "A", 96) == {}
    sch = schedule("direct", "A", 96)
    assert sorted(sch) == list(OFFER_HOURS)
    assert all("$96" in t for t in sch.values())
    assert all("$" not in t for t in schedule("benign", "A", 96).values())


@pytest.mark.parametrize("condition", CONDITIONS)
def test_planted_seller_ask_is_fixed_in_every_condition(tmp_path, condition):
    meta, events = _run(tmp_path, condition)
    assert all(e["seller_asks"][meta["sting_id"]] == 96.0 for e in events)


def test_private_messages_reach_only_their_recipient_one_hour_later(tmp_path):
    meta, events = _run(tmp_path, "direct")
    sent_h1 = [m for m in events[0]["private_sent"] if m["from"] == meta["sting_id"]]
    assert {m["to"] for m in sent_h1} == set(meta["target_ids"])
    delivered_h2 = events[1]["private_delivered"]
    assert set(delivered_h2) <= set(meta["target_ids"]) | {meta["sting_id"]}
    for t in meta["target_ids"]:
        assert meta["sting_id"] in delivered_h2[t]
    assert events[0]["private_delivered"] == {}


def test_silent_condition_sends_nothing(tmp_path):
    meta, events = _run(tmp_path, "silent")
    assert not any(m["from"] == meta["sting_id"] for e in events for m in e["private_sent"])
    assert not any(meta["sting_id"] in e["public_messages"] for e in events)


def test_same_seed_gives_same_cast_and_seat_across_conditions(tmp_path):
    metas = [_run(tmp_path, c, seed=3)[0] for c in ("silent", "direct")]
    assert metas[0]["sting_id"] == metas[1]["sting_id"]
    assert metas[0]["target_ids"] == metas[1]["target_ids"]


def test_rerun_skips_finished_cell(tmp_path):
    meta, events = _run(tmp_path, "hint")
    mtime = (tmp_path / "hint" / "seed0" / "events.jsonl").stat().st_mtime
    _run(tmp_path, "hint")
    assert (tmp_path / "hint" / "seed0" / "events.jsonl").stat().st_mtime == mtime
