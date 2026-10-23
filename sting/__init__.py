"""Undercover-seller sting experiments on top of the Agrawal et al. (2025) double auction.

The upstream harness lives, unmodified, in the pinned submodule at
third_party/collusion_hackathon/llm-agent-collusion. Its modules are imported as
``src.continuous_double_auction...``, so this package puts that directory on sys.path once.
Everything in this package is new sprint work; nothing upstream is edited.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_DIR = REPO_ROOT / "third_party" / "collusion_hackathon" / "llm-agent-collusion"

if not (UPSTREAM_DIR / "src").is_dir():
    raise ImportError(f"Upstream harness not found at {UPSTREAM_DIR}. Run: git submodule update --init --recursive")
if str(UPSTREAM_DIR) not in sys.path:
    sys.path.insert(0, str(UPSTREAM_DIR))
