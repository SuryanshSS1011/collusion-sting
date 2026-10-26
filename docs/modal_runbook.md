# Running the open-weight model on Modal (laptop runbook)

This adds non-Claude models. Qwen3-32B (FP8, Apache-2.0) plays two roles, and gpt-oss-20b (OpenAI open
weights, Apache-2.0) is a second seller model on the core arms.

1. **A judge.** It relabels every Claude transcript and reruns the disclaimer monitor test, using 1,396
   prompts or more.
2. **The selling agents.** It runs the core peer-sting comparison (silent, direct, peer-style, and
   peer-style with the "stay independent" instruction), the +$2 escalation sting, and a 30-hour pressure
   check, 116 markets in all.

Everything runs from your laptop. The cloud workspace cannot reach Modal or Hugging Face. Expect about
$5 to $15 of Modal credit and 1 to 2 hours, mostly unattended. Run the steps in order.

## 0. One-time setup

1. Install `uv` (https://docs.astral.sh/uv/) and the Modal CLI (`pip install modal`).
2. Run `modal setup`, which opens a browser to log in.
3. Clone the repo:

```bash
git clone https://github.com/SuryanshSS1011/collusion-sting.git
cd collusion-sting
git checkout scaffold/sting-v0
git submodule update --init
uv sync
```

## 1. Start the model server

```bash
export VLLM_KEY=$(openssl rand -hex 24)
modal secret create vllm-key VLLM_API_KEY=$VLLM_KEY
modal deploy modal_jobs/serve_qwen.py
```

Modal prints a URL like `https://<you>--collusion-sting-qwen-serve.modal.run`. Then create
`compute.env` in the repo root. It is gitignored, so never commit it.

```bash
echo "VLLM_BASE_URL=https://<you>--collusion-sting-qwen-serve.modal.run/v1" >> compute.env
echo "VLLM_API_KEY=$VLLM_KEY" >> compute.env
```

Warm it up and check it. The first call downloads about 33 GB of weights and can take 5 to 10 minutes.
If it times out, run the same command again.

```bash
curl -s https://<you>--collusion-sting-qwen-serve.modal.run/v1/models -H "Authorization: Bearer $VLLM_KEY"
```

Both server scripts pin transformers, because an unpinned install pulled transformers 5.x and crashed vLLM
0.9.2 on import ("'aimv2' is already used by a Transformers config"). If a deploy still fails, send the
last lines of `modal app logs collusion-sting-qwen` to Claude rather than changing versions locally.

## 2. Smoke test (2 markets, a few minutes)

```bash
uv run python run_grid.py configs/open_weight_pilot.json -y --jobs 2
```

Both markets should print `ok`. If a market fails, paste the traceback to Claude. If both are fine, look
at one transcript before continuing.

```bash
head -c 1500 results/open_weight_pilot/vllm__Qwen__Qwen3-32B-FP8/floor92/peer_none/seed95/events.jsonl
```

## 3. The judge run (about 20 to 40 minutes)

Pull first, so you have the latest prompt file. It includes the escalation study once that study is
finished.

```bash
git pull
uv run python modal_jobs/run_prompts.py data/modal/prompts.jsonl.gz data/modal/qwen_outputs.jsonl.gz --limit 20
uv run python modal_jobs/run_prompts.py data/modal/prompts.jsonl.gz data/modal/qwen_outputs.jsonl.gz
```

The first command is a 20-prompt check. The run can be resumed, so if it stops, run the same command
again.

## 4. The open-weight markets (about 45 to 90 minutes)

```bash
uv run python run_grid.py configs/open_weight_qwen.json -y --jobs 8
```

The run can be resumed, because finished markets are skipped. If you see many failures, lower `--jobs` to 4.

## 4b. Second model: gpt-oss-20b (about 30 to 60 minutes, can run alongside step 4)

This uses the same secret, a second server and a cheaper load, because it is a mixture-of-experts model with
about 3.6B active parameters.

```bash
modal deploy modal_jobs/serve_gptoss.py
echo "VLLM_BASE_URL_GPTOSS=https://<you>--collusion-sting-gptoss-serve.modal.run/v1" >> compute.env
curl -s https://<you>--collusion-sting-gptoss-serve.modal.run/v1/models -H "Authorization: Bearer $VLLM_KEY"
uv run python run_grid.py configs/open_weight_pilot_gptoss.json -y --jobs 2
cat results/open_weight_pilot_gptoss/usage_total.json
uv run python run_grid.py configs/open_weight_gptoss.json -y --jobs 8
```

Check the pilot's `usage_total.json` before the full run. Divide output_tokens by calls. At low reasoning
effort this should be a few hundred tokens per call. If it is in the thousands, stop and tell Claude.
Another sprint team reported reasoning models producing 15,000 to 20,000 output tokens per call, which
would make the run slow and expensive. Calls are capped at 4,000 output tokens, so a runaway model would
also produce truncated, unparseable answers.

If gpt-oss markets fail with JSON errors, paste one traceback to Claude before rerunning. Its answers come
through vLLM's reasoning parser, so the final message should be plain JSON.

## 4c. Sting-awareness study on both open models (about 45 to 60 minutes, added Oct 25)

This is pre-registered in `prereg_open_aware.md`. It runs 100 markets (60 Qwen, 40 gpt-oss) and needs both
servers up. Both apps were stopped, so deploy them again and warm each one up with the curl checks above.

```bash
git pull
modal deploy modal_jobs/serve_qwen.py
modal deploy modal_jobs/serve_gptoss.py
uv run python run_grid.py configs/open_weight_aware_pilot.json -y --jobs 2
uv run python run_grid.py configs/open_weight_aware.json -y --jobs 8
uv run python scripts/compact_results.py open_weight_aware open_weight_aware_pilot
git add results_final/open_weight_aware results_final/open_weight_aware_pilot
git commit -m "Open-weight sting-awareness markets"
git push
modal app stop collusion-sting-qwen
modal app stop collusion-sting-gptoss
```

Then, with the gpt-oss server still up, run the gpt-oss escalation arm (20 markets, added Oct 25). It writes
into the existing `open_weight_gptoss` folder and skips the markets already there.

```bash
uv run python run_grid.py configs/open_weight_gptoss_escalate.json -y --jobs 8
uv run python scripts/compact_results.py open_weight_gptoss
git add results_final/open_weight_gptoss
git commit -m "gpt-oss escalation arm"
git push
```

The pilot is 2 markets (one per model, seed 95). Both should print `ok`. The pilot's transcripts should
contain "Notice from the exchange" in each target's prompt.

## 4d. Follow-up: explained notice and instructed sellers (about 60 to 75 minutes, added Oct 25, 23:06)

This is pre-registered in `prereg_open_followup.md`. It runs 120 markets, 60 per model, and needs both servers.

```bash
git pull
modal deploy modal_jobs/serve_qwen.py
modal deploy modal_jobs/serve_gptoss.py
# warm both up with the curl checks in sections 1 and 4b
uv run python run_grid.py configs/open_weight_followup.json -y --jobs 8
uv run python scripts/compact_results.py open_weight_followup
git add results_final/open_weight_followup
git commit -m "Open-weight follow-up markets"
git push
modal app stop collusion-sting-qwen
modal app stop collusion-sting-gptoss
```

If the run is cut short, push what finished. The analysis handles partial arms, and the run can be resumed.

## 4e. Silent-raise control (about 30 to 40 minutes, added Oct 26, 01:14)

This is pre-registered in `prereg_escalate_quiet.md`. It runs 40 markets, 20 per model, and needs both servers.

```bash
git pull
modal deploy modal_jobs/serve_qwen.py
modal deploy modal_jobs/serve_gptoss.py
# warm both up with the curl checks in sections 1 and 4b
uv run python run_grid.py configs/open_weight_escalate_quiet.json -y --jobs 8
uv run python scripts/compact_results.py open_weight_escalate_quiet
git add results_final/open_weight_escalate_quiet
git commit -m "Open-weight silent-raise control markets"
git push
modal app stop collusion-sting-qwen
modal app stop collusion-sting-gptoss
```

## 5. Hand the data back

```bash
uv run python scripts/compact_results.py open_weight_qwen open_weight_gptoss open_weight_pilot open_weight_pilot_gptoss
git add results_final/open_weight_qwen results_final/open_weight_gptoss results_final/open_weight_pilot results_final/open_weight_pilot_gptoss data/modal/qwen_outputs.jsonl.gz
git commit -m "Open-weight judge outputs and Qwen3-32B markets"
git push
```

Claude will then import the judge labels, add Qwen as a fourth rater, and rerun the validation and the
monitor test. It will also label the Qwen markets and run the same tests as the peer-sting study.

## 6. Stop billing

```bash
modal app stop collusion-sting-qwen
modal app stop collusion-sting-gptoss
```

The server also scales to zero after 10 idle minutes.

## Notes for the report

1. The Qwen markets are exploratory unless a pre-registration is committed before step 4. Claude can
   write one, like `prereg_peer_sting.md`, while the server warms up.
2. Qwen's thinking mode is off (`enable_thinking: false`), so its agents answer in one pass like the Claude
   agents. Temperature is 0.7 for the agents and 0 for the judge.
3. The same model plays sellers and buyers in the open-weight markets. The planted seller is scripted, as
   before.
