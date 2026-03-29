"""
slm_experts.py
============================
SLM wrappers for Expert 2 and Expert 3 — Agentic RAG preserved.

Both experts retain the full multi-round tool-calling RAG loop.
The only change: self.client is replaced by VLLMChatClient instead of
anthropic.Anthropic(), which routes calls to the local vLLM endpoint.

Format flow (identical to Claude path):
  system_description
    → Expert2Agent(client=vllm_client).assess()   [multi-round RAG via tool calls]
    → ChromaDB retrieval (same as always)
    → produce_assessment tool call
    → expert output dict with regulatory_citations and evidence

No changes to Expert2Agent or Expert3Agent internals.
"""

import os
import sys

from .slm_backends import VLLMChatClient

_COUNCIL_DIR  = os.path.dirname(os.path.abspath(__file__))
_CAPSTONE_DIR = os.path.dirname(_COUNCIL_DIR)

for _d in (
    os.path.join(_CAPSTONE_DIR, "Expert 2"),
    os.path.join(_CAPSTONE_DIR, "Expert 3"),
):
    if _d not in sys.path:
        sys.path.insert(0, _d)


def run_expert2_slm(system_description: str, client: VLLMChatClient) -> dict:
    """
    Run Expert 2 (Governance & Compliance) via vLLM with full Agentic RAG.

    Identical to Expert2Agent().assess() but uses local vLLM instead of Claude.
    Multi-round regulatory retrieval and tool calling are fully preserved.
    """
    from expert2_agent import Expert2Agent
    return Expert2Agent(client=client).assess(system_description)


def run_expert3_slm(
    system_description: str,
    agent_id: str,
    client: VLLMChatClient,
) -> dict:
    """
    Run Expert 3 (UN Mission Fit) via vLLM with full Agentic RAG.

    Identical to Expert3Agent().assess() but uses local vLLM instead of Claude.
    Multi-round UN principles retrieval and tool calling are fully preserved.
    """
    from expert3_agent import Expert3Agent
    return Expert3Agent(client=client).assess(system_description, agent_id=agent_id)
