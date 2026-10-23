"""Offline mock model for pipeline tests. It makes no network calls and its behavior is NOT data.

Mock sellers accept a priced private offer with probability ``accept_p`` and then hold their ask
at the named floor; otherwise they price competitively. Mock buyers bid uniformly. This exists so
the grid runner and the analysis can be exercised end to end before any money is spent.
"""

from __future__ import annotations

import json
import random
import re
from typing import Optional

import sting  # noqa: F401
from src.resources.model_wrappers import ModelWrapper

PRICE_RE = re.compile(r"\$(\d{2,3}(?:\.\d{1,2})?)")
OFFER_WORDS = ("floor", "agree", "undercut", "holding", "proposal", "price war")


class MockClient(ModelWrapper):
    is_remote = False

    def __init__(self, seed: int, accept_p: float = 0.5, fail_p: float = 0.0, messy: bool = False):
        super().__init__("mock", temperature=0.0)
        self.rng = random.Random(seed)
        self.accept_p = accept_p
        self.fail_p = fail_p  # chance a call returns unparseable text, to exercise error handling
        self.messy = messy  # reply with bare first names and string "null"s, like real models do
        self.holding_at: Optional[float] = None
        self.decided = False

    def generate(self, messages) -> str:
        prompt = messages[-1]["content"]
        if self.fail_p and self.rng.random() < self.fail_p:
            return "I'm sorry, I can't produce JSON right now."
        if "as a seller" in prompt:
            return json.dumps(self._seller(prompt))
        return json.dumps(self._buyer())

    def _seller(self, prompt: str) -> dict:
        private_block = prompt.split("# Private Messages Received (Previous Hour)")[-1].split("#")[0]
        offer = None
        if "Privately from" in private_block and any(w in private_block.lower() for w in OFFER_WORDS):
            prices = PRICE_RE.findall(private_block)
            sender = re.search(r"Privately from (.+?):", private_block)
            if prices and sender:
                offer = (sender.group(1).strip(), float(prices[0]))
        reply = {}
        if offer and not self.decided:
            self.decided = True
            to = offer[0].removeprefix("Seller ") if self.messy else offer[0]
            if self.rng.random() < self.accept_p:
                self.holding_at = offer[1]
                reply = {to: f"Agreed, I will hold at ${offer[1]:.0f}."}
            else:
                reply = {to: "No thanks, I set my own prices."}
        ask = self.holding_at if self.holding_at is not None else round(self.rng.uniform(90.5, 94.0), 2)
        return {
            "reflection": "mock",
            "plan_for_this_hour": f"Ask {ask}.",
            "ask": ask,
            "new_memory": f"Asked {ask}.",
            "plan_for_message": "none",
            "message_to_sellers": "null" if self.messy else None,
            "private_messages": reply if reply or not self.messy else "null",
            "scratch_pad_update": "#### Observations\nmock\n#### Thoughts\nmock\n#### Updated Strategy\nmock",
        }

    def _buyer(self) -> dict:
        bid = round(self.rng.uniform(88.0, 99.0), 2)
        return {
            "reflection": "mock",
            "plan_for_this_hour": f"Bid {bid}.",
            "bid": bid,
            "new_memory": f"Bid {bid}.",
            "scratch_pad_update": "mock",
        }
