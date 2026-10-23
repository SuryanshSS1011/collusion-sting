# collusion-sting

**The undercover seller.** Do LLM agents take a cartel offer from a planted competitor, and do the
ones that say yes actually follow through?

Apart Research AI Collusion Research Sprint, October 23 to 25, 2026. Tracks 3.2 (trusted agents that
disrupt collusion) and 2.2 (combining what agents say with what they do).

## What is new here and what is not

| Path | Status |
|---|---|
| `third_party/collusion_hackathon/` | **Preexisting.** Git submodule of [poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon), pinned at `d585a7b`. It contains the double-auction harness from Agrawal et al. (2025, [arXiv:2507.01413](https://arxiv.org/abs/2507.01413)). Nothing in it is edited. |
| `sting/templates/target_seller.jinja2` | Upstream seller prompt plus two new sections: a private message channel and an optional compliance-report channel. |
| everything else | **New sprint work**, written during the sprint (see commit history). |

## Design in one paragraph

Three sellers and three buyers trade for 15 hours. Two sellers are LLM targets using the same model.
The third is a scripted planted seller that asks $96 every hour in every condition and, depending on
the condition, privately messages each target in hours 1, 4 and 8. The conditions are **silent** (no
messages), **benign** (friendly, no prices), **hint** (names $96 and argues against undercutting) and
**direct** (proposes a $96 floor and asks who is in). The planted seller never adapts, so any
difference between conditions comes from its words. The same seed gives the same cast and opening
orders in every condition, so conditions are compared on matched markets. Full plan and tests:
[`prereg.md`](prereg.md).

## Setup

```bash
git clone --recurse-submodules https://github.com/SuryanshSS1011/collusion-sting
cd collusion-sting
uv sync --extra dev
cp compute.env.example compute.env      # then add OPENROUTER_API_KEY
uv run pytest -q                        # offline checks, no API calls
```

If you cloned without `--recurse-submodules`, run `git submodule update --init --recursive`.
Run every command from the repo root so `compute.env` is found. Check that the model ids in
`configs/*.json` still exist on OpenRouter before spending.

## Run order

```bash
# 0. Offline: the whole pipeline with a mock model. Free, about 30 seconds.
uv run python run_grid.py configs/grid.json --mock --jobs 4
uv run python -m analysis.judge results_mock/main --mock
uv run python -m analysis.report results_mock/main

# 1. Smoke test, one real market, 5 hours (about 25 calls).
uv run python -m sting.run --condition direct --seed 0 --rounds 5

# 2. Positive control on the upstream harness (3 LLM sellers, chat on, 3 seeds).
scripts/positive_control.sh openai/gpt-4.1-mini

# 3. Pilot: one seed of every condition. Read the transcripts, then freeze prereg.md.
uv run python run_grid.py configs/pilot.json
uv run python -m analysis.view results/pilot --all > pilot_transcripts.md

# 4. Main grid: 4 conditions x 2 models x 5 seeds = 40 markets, 75 calls each.
uv run python run_grid.py configs/grid.json --dry-run
uv run python run_grid.py configs/grid.json --jobs 4 -y

# 5. Analysis.
uv run python -m analysis.judge results/main
uv run python -m analysis.judge results/main --export-hand 50   # blinded sample to label by hand
uv run python -m analysis.judge results/main --kappa analysis/out/main/hand_labels.csv
uv run python -m analysis.report results/main                    # -> analysis/out/main/summary.md
```

Exploratory arms, run only if the main grid finishes early: `configs/explore_public.json` posts the
offer in the public seller chat instead of privately, and `configs/explore_report.json` gives targets
a confidential compliance-report channel.

`run_grid.py` skips finished cells, so rerunning the same command after a failure only retries what
is missing. The pilot and main grids write to different folders.

## Outputs

Each market folder (`results/<grid>/<model>/<condition>/seed<k>/`) holds:

1. `events.jsonl`, one line per hour with every ask, bid, trade, public message, private message,
   report, and each target's stated plan. The analysis reads only this file and `sting_meta.json`.
2. `sting_meta.json`, the config, wording, planted seller id and seat, and the exact script used.
3. Upstream files: one transcript per agent (`Seller <name>.md`), `auction_results.md`, `unified.log`
   and `collusion_metrics.json`.

`analysis/out/<grid>/` holds `summary.md`, the CSV tables and `figures/`.

## Layout

```
sting/            planted seller, target seller, market with private channel, frozen scripts, single-run CLI
run_grid.py       grid runner with dry-run, resume and --mock
configs/          pilot.json, grid.json and two exploratory arms
analysis/         load.py (tables), judge.py (verbal labels and validation), report.py (stats, figures),
                  view.py (readable timeline of a market)
scripts/          positive_control.sh
tests/            offline checks of the experimental controls
prereg.md         hypotheses, metrics, thresholds and the deviations log
```

## Known limitations of the design

1. The planted seller is scripted and does not reply to targets, so a target that asks a question
   gets no answer. This keeps the treatment fixed but is less realistic than an adaptive agent.
2. The planted seller asks $96 in every condition, including silent. Silent therefore means "a
   high-priced seller who says nothing", not "no planted seller". The positive control covers the
   all-LLM market.
3. Five seeds per cell detect only large effects. Results are a pilot.
4. The mock model in `sting/mock.py` exists only to test the pipeline. Its outputs are not data.

## Dual use

A study of which offers agents accept is also a guide to writing offers they accept, and a published
sting design could teach colluding agents to screen for decoys. The report appendix discusses both.
