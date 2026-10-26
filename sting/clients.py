"""Model routing. One function builds every client the experiment uses.

Model ids:
1. "claude/<anthropic model id>" goes straight to the Anthropic API with ANTHROPIC_API_KEY, for
   example "claude/claude-haiku-5-5" or "claude/claude-sonnet-5-5".
2. Anything else goes through the upstream OpenRouter client with OPENROUTER_API_KEY, for example
   "openai/gpt-4.1-mini".

Claude 5.5 models reject temperature and top_p and have no seed, so the Claude client sends neither.
It turns thinking down to the lowest setting each model allows and asks for low effort, which keeps
these calls comparable to the non-reasoning models and cheap. Record this in the write-up.
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

import sting  # noqa: F401
from src.continuous_double_auction.util.misc import get_client as upstream_get_client
from src.resources.model_wrappers import Message, ModelWrapper

CLAUDE_PREFIX = "claude/"
log = logging.getLogger(__name__)

# Lowest thinking setting each model accepts (Anthropic effort docs, checked 2026-10-23).
# Haiku 5.5 accepts {"type": "disabled"} at high effort or below. Sonnet 5.5 rejects "disabled";
# {"type": "between_tools"} is its lowest setting. Opus 5.5 always thinks, so the field is omitted.
# List prices in USD per million tokens (input, output), platform.claude.com pricing page, 2026-10-23.
CLAUDE_PRICES = {"claude-haiku-5-5": (0.10, 0.50), "claude-sonnet-5-5": (2.0, 10.0), "claude-opus-5-5": (4.0, 20.0)}

THINKING_FLOOR = {
    "claude-haiku-5-5": {"type": "disabled"},
    "claude-sonnet-5-5": {"type": "between_tools"},
}


def _load_keys() -> None:
    root = Path(sting.REPO_ROOT)
    for name in ("compute.env", ".env"):
        if (root / name).exists():
            load_dotenv(root / name, override=False)


class ClaudeClient(ModelWrapper):
    is_remote = True

    def __init__(self, model_name: str, effort: str = "low", max_tokens: int = 2000, **kwargs):
        super().__init__(model_name, max_tokens=max_tokens, **kwargs)
        _load_keys()
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise RuntimeError("ANTHROPIC_API_KEY is not set. Put it in compute.env.")
        from anthropic import Anthropic

        # Pin the public endpoint. Some environments export ANTHROPIC_BASE_URL for their own tooling,
        # and the SDK would silently follow it.
        base_url = os.environ.get("STING_ANTHROPIC_BASE_URL", "https://api.anthropic.com")
        # Personal keys that are not scoped to one workspace must name a workspace on every request.
        headers = {}
        if os.environ.get("ANTHROPIC_WORKSPACE_ID"):
            headers["anthropic-workspace-id"] = os.environ["ANTHROPIC_WORKSPACE_ID"]
        self.client = Anthropic(
            api_key=os.environ["ANTHROPIC_API_KEY"],
            base_url=base_url,
            default_headers=headers or None,
            timeout=120,
            max_retries=0,
        )
        self.effort = effort
        self.usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0}

    def generate(self, messages: list[Message]) -> Optional[str]:
        from anthropic import APIConnectionError, APIStatusError, RateLimitError

        system = None
        if messages and messages[0]["role"] == "system":
            system, messages = messages[0]["content"], messages[1:]
        params = {
            "model": self.model_name,
            "max_tokens": self.max_tokens,
            "messages": messages,
            "output_config": {"effort": self.effort},
        }
        if system:
            params["system"] = system
        if self.model_name in THINKING_FLOOR:
            params["thinking"] = THINKING_FLOOR[self.model_name]
        for attempt in range(6):
            try:
                resp = self.client.messages.create(**params)
                u = getattr(resp, "usage", None)
                self.usage["calls"] += 1
                self.usage["input_tokens"] += int(getattr(u, "input_tokens", 0) or 0)
                self.usage["output_tokens"] += int(getattr(u, "output_tokens", 0) or 0)
                return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
            except RateLimitError as e:
                log.warning(f"{self.model_name} rate limited (attempt {attempt + 1}): {e}")
            except APIStatusError as e:
                if e.status_code in (400, 401, 403, 404):  # our request is wrong; retrying will not help
                    raise
                log.warning(f"{self.model_name} API error {e.status_code} (attempt {attempt + 1}): {e}")
            except APIConnectionError as e:
                log.warning(f"{self.model_name} connection error (attempt {attempt + 1}): {e}")
            time.sleep(min(30, 2**attempt))
        return None


VLLM_PREFIX = "vllm/"


class VLLMClient(ModelWrapper):
    """An open-weight model served by vLLM's OpenAI-compatible server (see modal/serve_qwen.py).

    Reads VLLM_BASE_URL (for example https://<workspace>--collusion-sting-qwen-serve.modal.run/v1) and
    VLLM_API_KEY. Qwen3 thinking is switched off so every agent answers in one pass, like the Claude agents.
    """

    is_remote = True

    def __init__(self, model_name: str, temperature: float = 0.7, max_tokens: int = 2000, **kwargs):
        super().__init__(model_name, max_tokens=max_tokens, **kwargs)
        _load_keys()
        # One server per model: gpt-oss reads VLLM_BASE_URL_GPTOSS, every other model reads VLLM_BASE_URL.
        url_var = "VLLM_BASE_URL_GPTOSS" if "gpt-oss" in model_name else "VLLM_BASE_URL"
        if not os.environ.get(url_var):
            raise RuntimeError(f"{url_var} is not set. Put it in compute.env (see docs/modal_runbook.md).")
        from openai import OpenAI

        self.client = OpenAI(base_url=os.environ[url_var], api_key=os.environ.get("VLLM_API_KEY", "EMPTY"), timeout=300)
        self.temperature = temperature
        self.usage = {"calls": 0, "input_tokens": 0, "output_tokens": 0}

    def _reasoning_args(self) -> dict:
        """Lowest reasoning each open model allows, like the Claude agents: Qwen3 thinking off, gpt-oss effort low."""
        if "gpt-oss" in self.model_name:
            return {"reasoning_effort": "low", "max_tokens": max(self.max_tokens, 4000)}
        return {"extra_body": {"chat_template_kwargs": {"enable_thinking": False}}}

    def generate(self, messages: list[Message]) -> Optional[str]:
        for attempt in range(6):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    temperature=self.temperature,
                    **({"max_tokens": self.max_tokens} | self._reasoning_args()),
                )
                u = getattr(resp, "usage", None)
                self.usage["calls"] += 1
                self.usage["input_tokens"] += int(getattr(u, "prompt_tokens", 0) or 0)
                self.usage["output_tokens"] += int(getattr(u, "completion_tokens", 0) or 0)
                return resp.choices[0].message.content
            except Exception as e:  # noqa: BLE001  cold starts and overload: back off and retry
                log.warning(f"{self.model_name} call failed (attempt {attempt + 1}): {e}")
                time.sleep(min(60, 5 * 2**attempt))
        return None


def make_client(model: str, temperature: float, seed: Optional[int] = None) -> ModelWrapper:
    if model.startswith(CLAUDE_PREFIX):
        return ClaudeClient(model.removeprefix(CLAUDE_PREFIX))
    if model.startswith(VLLM_PREFIX):
        return VLLMClient(model.removeprefix(VLLM_PREFIX), temperature=temperature)
    kwargs = {"temperature": temperature}
    if seed is not None:
        kwargs["seed"] = seed
    return upstream_get_client(model=model, **kwargs)


def usage_summary(clients) -> dict:
    """Token use and list-price cost for the Claude clients among `clients`, keyed by model."""
    out: dict[str, dict] = {}
    for c in clients:
        if not isinstance(c, (ClaudeClient, VLLMClient)):
            continue
        row = out.setdefault(c.model_name, {"calls": 0, "input_tokens": 0, "output_tokens": 0})
        for k in row:
            row[k] += c.usage[k]
    for model, row in out.items():
        pin, pout = CLAUDE_PRICES.get(model, (0.0, 0.0))  # open-weight models are paid by GPU time, not tokens
        row["usd_list_price"] = round(row["input_tokens"] / 1e6 * pin + row["output_tokens"] / 1e6 * pout, 4)
    return out
