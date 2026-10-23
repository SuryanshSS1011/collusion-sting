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
        self.client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], base_url=base_url, timeout=120, max_retries=0)
        self.effort = effort

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


def make_client(model: str, temperature: float, seed: Optional[int] = None) -> ModelWrapper:
    if model.startswith(CLAUDE_PREFIX):
        return ClaudeClient(model.removeprefix(CLAUDE_PREFIX))
    kwargs = {"temperature": temperature}
    if seed is not None:
        kwargs["seed"] = seed
    return upstream_get_client(model=model, **kwargs)
