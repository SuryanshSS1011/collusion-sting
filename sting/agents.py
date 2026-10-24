"""Agents for the sting experiment.

TargetSeller is the upstream LLM seller with one addition: a private message channel (and an
optional compliance-report channel). Both are shown in every condition, including silent, so
the prompt differs across conditions only once the planted seller actually writes something.

StingSeller is the planted seller. It makes no model calls. It posts the same fixed ask every hour
in every condition and sends its scripted messages on the scripted hours.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

import backoff
import openai

import sting  # noqa: F401  (puts the upstream harness on sys.path)
from src.continuous_double_auction.cda_types import Agent, AgentBidResponse
from src.continuous_double_auction.market.agents import LMSeller
from src.continuous_double_auction.util.jinja_util import render_prompt
from src.continuous_double_auction.util.json_util import extract_json
from src.resources.model_wrappers import Message

TEMPLATE_DIR = str(Path(__file__).resolve().parent / "templates") + "/"
TARGET_TEMPLATE = "target_seller.jinja2"


def _parse(response: str) -> dict:
    """Upstream extract_json raises ValueError when there is no brace, which skips the retry. Normalize it."""
    try:
        out = extract_json(response)
    except ValueError as e:  # JSONDecodeError is a ValueError subclass, so this also covers it
        raise json.decoder.JSONDecodeError(str(e), response or "", 0) from e
    if not isinstance(out, dict):
        raise json.decoder.JSONDecodeError("top-level JSON is not an object", response, 0)
    return out


class TargetSeller(LMSeller):
    """Upstream LMSeller rendered with the sting template (private channel + optional report)."""

    private_channel_enabled: bool = True
    report_channel_enabled: bool = False
    instruction: str = ""  # known-answer validation markets only; empty in every experimental market
    other_seller_ids: list[str] = []

    @backoff.on_exception(
        wait_gen=backoff.expo,
        exception=(openai._exceptions.RateLimitError, json.decoder.JSONDecodeError, AssertionError),
        max_value=2,
        max_tries=4,
    )
    def generate_bid_response(self, **kwargs: Any) -> AgentBidResponse:
        round_num = kwargs.get("round_num", 1)
        prompt = render_prompt(
            template_dir=TEMPLATE_DIR,
            prompt_template=TARGET_TEMPLATE,
            seller_id=self.id,
            company=self.company,
            valuation=self.valuation,
            round_number=round_num,
            num_rounds=self.expt_params.rounds,
            hide_num_rounds=self.expt_params.hide_num_rounds,
            memory=self.memory_manager.get_formatted_memory(),
            seller_comms_enabled=self.expt_params.seller_comms_enabled,
            seller_messages=kwargs.get("seller_messages", {}),
            bid_queue=kwargs.get("bid_queue", []),
            ask_queue=kwargs.get("ask_queue", []),
            past_bids_and_asks=kwargs.get("past_bids_and_asks", []),
            past_trades=kwargs.get("past_trades", []),
            agent_successful_trades=kwargs.get(
                "agent_successful_trades", "You have not made any successful trades yet."
            ),
            scratch_pad=self.scratch_pad,
            demonym=None,
            is_gagged=kwargs.get("is_gag_order_active", False),
            boss_pressure=self.expt_params.boss_pressure,
            initial_condition=self.expt_params.initial_condition,
            oversight_enabled=self.expt_params.oversight_enabled,
            max_message_length=self.expt_params.max_message_length,
            private_channel_enabled=self.private_channel_enabled,
            private_inbox=kwargs.get("private_inbox", {}),
            other_seller_ids=self.other_seller_ids,
            report_channel_enabled=self.report_channel_enabled,
            instruction=self.instruction,
        )
        response = self.client.generate(messages=[Message(role="user", content=prompt)])
        assert response is not None
        response_dict = _parse(response)
        if self.logger:
            self.logger.log_agent_round(
                round_num=round_num, agent_id=self.id, prompt=prompt, response_dict=response_dict
            )
        if response_dict.get("new_memory"):
            self.memory_manager.add_memory(round_num, response_dict["new_memory"])
        if response_dict.get("scratch_pad_update"):
            self.scratch_pad = response_dict["scratch_pad_update"]
        return response_dict


class StingSeller(Agent):
    """Scripted planted seller. Non-adaptive by design: it ignores everything it receives."""

    fixed_ask: float
    messages_by_hour: dict[int, str] = {}
    channel: str = "private"  # "private": DM each target; "public": post in the seller chat
    target_ids: list[str] = []
    logger: Optional[Any] = None

    class Config:
        arbitrary_types_allowed = True

    def generate_bid_response(self, **kwargs: Any) -> AgentBidResponse:
        round_num = kwargs.get("round_num", 1)
        text = self.messages_by_hour.get(round_num)
        response: dict[str, Any] = {"ask": self.fixed_ask, "is_sting": True}
        if text:
            if self.channel == "public":
                response["message_to_sellers"] = text
            else:
                response["private_messages"] = {tid: text for tid in self.target_ids}
        if self.logger:
            self.logger.log_agent_round(
                round_num=round_num,
                agent_id=self.id,
                prompt="(scripted planted seller)",
                response_dict=response,
            )
        return response
