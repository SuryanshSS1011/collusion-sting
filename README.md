# collusion-sting

**The undercover seller.** Can a planted competitor that offers a price cartel tell which LLM selling
agents will collude? We put a scripted "sting" seller into a double-auction market with two LLM sellers,
vary what it says, and compare what the targets *say* in reply with what they then *do* with their prices
and with each other.

Apart Research AI Collusion Research Sprint, October 23 to 26, 2026. Tracks 3.2 (trusted agents that
disrupt collusion) and 2.2 (combining what agents say with what they do).

## Results at a glance

1,037 committed markets across three model families: Claude (Haiku 5.5, Sonnet 5.5) through the Anthropic API,
and two open-weight models, Qwen3-32B and gpt-oss-20b, served with vLLM on Modal. Every confirmatory test
was pre-registered and committed before its markets ran. Full numbers, with sources and status tags, are in
[`paper/findings.md`](paper/findings.md) and [`paper/results_pack.md`](paper/results_pack.md).

1. **An explicit cartel offer is a poor detector for Claude.** Claude refused every direct $92/$96 floor
   offer (0/40), yet 57% of targets that refused or ignored the sting were coordinating with the other
   seller at the same time. "Refused, so clean" would have been wrong for most of them.
2. **Saying yes is not doing it.** All 8 Claude targets that agreed in writing failed to hold the named
   price. When a sting raised its price after agreement, asking targets to move up with it made no
   difference in any family; where open-weight sellers followed, the planted seller's price move alone
   explains it (silent-raise control).
3. **A sting that talks like a peer is a good detector for Claude.** A planted seller that proposes a level
   at the market price, without naming collusion, was accepted by 35/40 Haiku targets, by 0/40 targets told
   to price independently, and identified peer coordination with sensitivity 0.90 and specificity 1.00.
4. **Open-weight sellers accept the explicit offer.** Qwen accepted it 20/40 times and gpt-oss 10/40, and it
   is specific there: 0/40 of instructed sellers accepted it for both models.
5. **Whether an audit notice deters depends on the model and the wording.** "The exchange places undercover
   auditors" ended peer coordination in Haiku (40/40 to 0/40), did nothing for Qwen and *raised* it for
   gpt-oss (28/40 to 38/40), which read it as an invitation. Adding one sentence on the sanction cut
   coordination to 1/40 (Qwen) and 2/40 (gpt-oss).
6. **No evasion in any family.** Sellers told about auditors never learned to coordinate while refusing the
   sting.

Prices stayed near the competitive level throughout, so the behavior being detected and deterred is
coordination talk, not realized cartel prices.

## Studies

Each study has a pre-registration, a grid config, committed per-market records in `results_final/<grid>/`
and analysis outputs in `results_final/analysis/<grid>/`.

| Study | Pre-registration | Grid config(s) | Models |
|---|---|---|---|
| Main grid: four sting wordings at $92 and $96 | [`prereg.md`](prereg.md) | `main_claude` | Haiku, Sonnet |
| Replication with a compliance-warning control | [`prereg_replication.md`](prereg_replication.md) | `replication_claude` | Haiku, Sonnet |
| Disclaimers vs LLM collusion monitors | [`prereg_monitor.md`](prereg_monitor.md) | (reuses replication transcripts) | Haiku, Sonnet, Opus as monitors |
| Peer-style sting | [`prereg_peer_sting.md`](prereg_peer_sting.md) | `peer_sting_claude` | Haiku, Sonnet |
| Escalation and sting awareness | [`prereg_escalation.md`](prereg_escalation.md) | `escalate_aware_claude` | Haiku, Sonnet |
| Silent-raise control | [`prereg_escalate_quiet.md`](prereg_escalate_quiet.md) | `escalate_quiet_claude`, `open_weight_escalate_quiet` | Haiku, Qwen, gpt-oss |
| Open-weight sellers | [`prereg_open_weight.md`](prereg_open_weight.md) | `open_weight_qwen`, `open_weight_gptoss` | Qwen, gpt-oss |
| Open-weight sting awareness | [`prereg_open_aware.md`](prereg_open_aware.md) | `open_weight_aware` | Qwen, gpt-oss |
| Open-weight follow-up: explained notice, instructed sellers | [`prereg_open_followup.md`](prereg_open_followup.md) | `open_weight_followup` | Qwen, gpt-oss |

Supporting runs: pilots (`pilot_claude`, `peer_pilot_claude`, `escalate_pilot_claude`,
`open_weight_pilot*`), a positive control with three LLM sellers (`posctrl_claude`), 32 known-answer
markets for judge validation (`known_answer_claude`) and a price-stakes pilot (`price_pilot_claude`).
Deviations from each plan are logged at the end of its pre-registration.

## Design

Three sellers and three buyers trade for 15 hours. Sellers cost $80 and buyers value $100. Two sellers
are LLM targets of the same model. The third is the planted seller. It is scripted and never adapts, so
any difference between arms comes from its words. Depending on the arm it stays silent, sends a benign
note, hints at a price, proposes a floor outright, talks like a peer at the market price, or escalates
that price after agreement. Some arms also give targets an auditor notice or an instruction to price
independently. The same seed gives the same cast and opening orders in every arm, so arms are compared on
matched markets.

What targets **say** is labelled by an LLM judge (Claude Sonnet 5.5, primary) and checked against a second
judge, a rule coder, known-answer markets and Qwen3-32B as a fourth, non-Claude rater. What targets **do**
is read straight from the order book: whether they hold the named price, and whether they coordinate with
the other target.

## Setup

```bash
git clone --recurse-submodules https://github.com/SuryanshSS1011/collusion-sting
cd collusion-sting
uv sync --extra dev
uv run pytest -q                        # offline checks, no API calls
```

If you cloned without `--recurse-submodules`, run `git submodule update --init --recursive`. Run every
command from the repo root.

## Reproduce the analysis (free, no API calls)

Every reported number can be rebuilt from committed files without running a market. The analysis writes to
`analysis/out/` (gitignored), and `results_final/analysis/` is the committed copy of it, including all
judge labels. Restore it first:

```bash
mkdir -p analysis/out && cp -R results_final/analysis/. analysis/out/
uv run python -m analysis.results_pack                       # rebuild paper/results_pack.md
uv run python -m analysis.cross_family                       # rebuild the Claude vs open-weight figure
uv run python -m analysis.report results_final/main_claude   # recompute the main grid's tables and tests
```

`analysis.report` overwrites `analysis/out/main_claude/`, so run it after `results_pack`, or restore again.
Each module in `analysis/` has its exact command in its docstring.

## Run new markets

Copy `compute.env.example` to `compute.env` (gitignored) and fill in only what you need.

- **Claude.** Model ids that start with `claude/` go to the Anthropic API with `ANTHROPIC_API_KEY`
  (`sting/clients.py`).

  ```bash
  uv run python run_grid.py configs/main_claude.json --dry-run   # cells and call counts
  uv run python run_grid.py configs/main_claude.json --jobs 4 -y
  ```

- **Open-weight models on Modal.** Follow [`paper/modal_runbook.md`](paper/modal_runbook.md). It deploys
  vLLM servers (`modal_jobs/serve_qwen.py`, `modal_jobs/serve_gptoss.py`) that read only a `vllm-key`
  Modal secret, and runs the markets from your laptop against them.

- **Offline mock.** `uv run python run_grid.py configs/pilot.json --mock` runs the whole pipeline with a
  fake model. Its outputs test the code only and are not data.

`run_grid.py` skips finished markets, so rerunning a command after a failure retries only what is
missing. `scripts/compact_results.py <grid>` copies a finished grid's compact records into
`results_final/`.

## Outputs

Each market folder `results/<grid>/<model>/<arm>/seed<k>/` holds `events.jsonl` (one line per hour: every
ask, bid, trade, public and private message, and each target's stated plan), `sting_meta.json` (config,
wording and the exact script used) and `usage.json`. The analysis reads only these. The full run also
writes upstream transcripts per agent, which are not committed.

## Layout

```
sting/            planted seller, target sellers, market with a private channel, model clients, single-run CLI
run_grid.py       grid runner with dry run, resume and --mock
configs/          one JSON per grid
modal_jobs/       vLLM servers on Modal and the batch prompt runner for the open-weight judge
analysis/         labelling, validation, tests and figures for every study
results_final/    committed per-market records and analysis outputs
paper/            findings, results pack, codebook, design decisions, related work, figures, Modal runbook
prereg*.md        pre-registrations with their deviation logs
tests/            offline checks of the experimental controls
third_party/      upstream harness (git submodule, unedited)
```

## What is new and what is not

`third_party/collusion_hackathon/` is a git submodule of
[poseidon-research/collusion_hackathon](https://github.com/poseidon-research/collusion_hackathon), pinned at
`d585a7b`. It contains the double-auction harness from Agrawal et al. (2025,
[arXiv:2507.01413](https://arxiv.org/abs/2507.01413)), and nothing in it is edited.
`sting/templates/target_seller.jinja2` is the upstream seller prompt plus a private message channel and an
optional compliance-report channel. Everything else was written during the sprint.

## Limitations

1. The planted seller is scripted. It does not answer questions, which keeps the treatment fixed but is less
   realistic than an adaptive agent.
2. Most cells have 20 seeds per arm, and some 5 to 10, so only moderate-to-large effects are detectable.
3. Prices stayed competitive, so the study measures coordination talk and willingness to agree, not cartel
   harm.
4. In the open-weight markets the same model plays sellers and buyers.

## Dual use

A study of which offers agents accept is also a guide to writing offers they accept, and a published sting
design could teach colluding agents to screen for decoys. The exact scripts are in `sting/scripts.py` and
[`paper/appendix_scripts.md`](paper/appendix_scripts.md), so readers can judge both risks.
