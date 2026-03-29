"""
slm_backends.py
============================
Drop-in Anthropic-compatible client that routes to a local vLLM endpoint.

Design goal: Expert2Agent and Expert3Agent are NOT modified at all.
The full Agentic RAG loop (multi-round tool calling) is preserved.

This module translates:
  Anthropic-style params  →  OpenAI /v1/chat/completions request
  OpenAI response         →  Anthropic-style response objects

Supported Anthropic features used by E2 / E3:
  • system prompt string
  • multi-turn messages (user / assistant)
  • tools (function definitions with input_schema)
  • tool_choice {"type": "tool", "name": "..."} or {"type": "auto"}
  • response.content — list of TextBlock / ToolUseBlock
  • response.stop_reason — "end_turn" or "tool_use"
  • tool_result blocks inside user messages
  • text blocks inside user messages

Tested with: vLLM serving Llama-3.1-70B-Instruct (tool calling supported).

Usage:
    from council.slm_backends import VLLMChatClient, make_vllm_llm_backend

    client = VLLMChatClient(
        base_url = "http://localhost:8000",
        model    = "meta-llama/Meta-Llama-3.1-70B-Instruct",
    )

    # Pass directly to Expert2Agent / Expert3Agent:
    from expert2_agent import Expert2Agent
    result = Expert2Agent(client=client).assess(description)

    # Or pass to Expert3Agent:
    from expert3_agent import Expert3Agent
    result = Expert3Agent(client=client).assess(description, agent_id="sys-001")
"""

import json
import uuid
import urllib.request
import urllib.error
from typing import Any, Optional


# ── Anthropic-compatible response objects ─────────────────────────────────────

class _TextBlock:
    """Mimics anthropic.types.TextBlock."""
    __slots__ = ("type", "text")
    def __init__(self, text: str):
        self.type = "text"
        self.text = text
    def __repr__(self):
        return f"_TextBlock({self.text[:40]!r})"


class _ToolUseBlock:
    """Mimics anthropic.types.ToolUseBlock."""
    __slots__ = ("type", "id", "name", "input")
    def __init__(self, tool_id: str, name: str, arguments: str):
        self.type  = "tool_use"
        self.id    = tool_id
        self.name  = name
        try:
            self.input = json.loads(arguments)
        except (json.JSONDecodeError, TypeError):
            self.input = {}
    def __repr__(self):
        return f"_ToolUseBlock(name={self.name!r}, id={self.id!r})"


class _MessageResponse:
    """Mimics anthropic.types.Message."""
    __slots__ = ("content", "stop_reason")
    def __init__(self, content: list, stop_reason: str):
        self.content     = content
        self.stop_reason = stop_reason
    def __repr__(self):
        return f"_MessageResponse(stop_reason={self.stop_reason!r}, blocks={len(self.content)})"


# ── Format converters ─────────────────────────────────────────────────────────

def _tools_anthropic_to_oai(tools: list) -> list:
    """
    Convert Anthropic tool definitions → OpenAI function definitions.

    Anthropic:  {"name": ..., "description": ..., "input_schema": {...}}
    OpenAI:     {"type": "function", "function": {"name": ..., "description": ..., "parameters": {...}}}
    """
    oai_tools = []
    for t in tools:
        oai_tools.append({
            "type": "function",
            "function": {
                "name":        t["name"],
                "description": t.get("description", ""),
                "parameters":  t.get("input_schema", {"type": "object", "properties": {}}),
            },
        })
    return oai_tools


def _tool_choice_anthropic_to_oai(tool_choice: Any) -> Any:
    """
    Convert Anthropic tool_choice → OpenAI tool_choice.

    Anthropic {"type": "tool", "name": "x"}  →  OpenAI {"type": "function", "function": {"name": "x"}}
    Anthropic {"type": "auto"}               →  OpenAI "auto"
    Anthropic {"type": "any"}                →  OpenAI "required"
    None                                     →  "auto"
    """
    if tool_choice is None:
        return "auto"
    if isinstance(tool_choice, str):
        return tool_choice
    tc_type = tool_choice.get("type", "auto")
    if tc_type == "tool":
        return {"type": "function", "function": {"name": tool_choice["name"]}}
    if tc_type == "any":
        return "required"
    return "auto"


def _block_to_dict(block) -> dict:
    """Convert a response block object to a plain dict (for message history)."""
    if isinstance(block, dict):
        return block
    if hasattr(block, "type"):
        if block.type == "text":
            return {"type": "text", "text": getattr(block, "text", "")}
        if block.type == "tool_use":
            return {
                "type":  "tool_use",
                "id":    block.id,
                "name":  block.name,
                "input": block.input,
            }
    return {"type": "text", "text": str(block)}


def _messages_anthropic_to_oai(system: str, messages: list) -> list:
    """
    Convert Anthropic-style multi-turn message list → OpenAI messages list.

    Handles:
      - Plain string content
      - List content with text / tool_use / tool_result blocks
      - Python block objects in assistant messages (appended by E2/E3 agents)

    Tool results become separate role="tool" messages (OpenAI requirement).
    """
    oai = [{"role": "system", "content": system}]

    for msg in messages:
        role    = msg["role"]
        content = msg["content"]

        # ── Plain string ──────────────────────────────────────────────────────
        if isinstance(content, str):
            oai.append({"role": role, "content": content})
            continue

        # ── List of blocks ────────────────────────────────────────────────────
        if not isinstance(content, list):
            oai.append({"role": role, "content": str(content)})
            continue

        blocks = [_block_to_dict(b) for b in content]

        # ── assistant message: may contain tool_use blocks ────────────────────
        if role == "assistant":
            text_parts  = [b["text"] for b in blocks if b.get("type") == "text" and b.get("text")]
            tool_calls  = []
            for b in blocks:
                if b.get("type") == "tool_use":
                    tool_calls.append({
                        "id":       b["id"],
                        "type":     "function",
                        "function": {
                            "name":      b["name"],
                            "arguments": json.dumps(b.get("input", {}), ensure_ascii=False),
                        },
                    })
            oai_msg = {
                "role":    "assistant",
                "content": "\n".join(text_parts) if text_parts else None,
            }
            if tool_calls:
                oai_msg["tool_calls"] = tool_calls
            oai.append(oai_msg)
            continue

        # ── user message: may contain tool_result or text blocks ──────────────
        if role == "user":
            pending_text = []
            for b in blocks:
                btype = b.get("type", "text")

                if btype == "tool_result":
                    # Flush any accumulated text first
                    if pending_text:
                        oai.append({"role": "user", "content": "\n".join(pending_text)})
                        pending_text = []
                    # Emit a role="tool" message
                    result_content = b.get("content", "")
                    if isinstance(result_content, list):
                        result_content = "\n".join(
                            r.get("text", str(r)) if isinstance(r, dict) else str(r)
                            for r in result_content
                        )
                    oai.append({
                        "role":         "tool",
                        "tool_call_id": b["tool_use_id"],
                        "content":      result_content,
                    })

                elif btype == "text":
                    text = b.get("text", "")
                    if text:
                        pending_text.append(text)

            if pending_text:
                oai.append({"role": "user", "content": "\n".join(pending_text)})
            continue

        # Fallback
        oai.append({"role": role, "content": str(content)})

    return oai


def _oai_response_to_anthropic(data: dict) -> _MessageResponse:
    """
    Convert OpenAI /v1/chat/completions response → Anthropic _MessageResponse.
    """
    choice       = data["choices"][0]
    finish       = choice.get("finish_reason", "stop")
    message      = choice["message"]
    oai_content  = message.get("content") or ""
    oai_calls    = message.get("tool_calls") or []

    blocks: list = []

    if oai_content:
        blocks.append(_TextBlock(oai_content))

    for tc in oai_calls:
        fn = tc.get("function", {})
        blocks.append(_ToolUseBlock(
            tool_id   = tc.get("id", str(uuid.uuid4())[:8]),
            name      = fn.get("name", ""),
            arguments = fn.get("arguments", "{}"),
        ))

    stop_reason = "tool_use" if oai_calls else "end_turn"
    # vLLM sometimes returns "tool_calls" as finish_reason
    if finish in ("tool_calls", "tool_use"):
        stop_reason = "tool_use"

    return _MessageResponse(content=blocks, stop_reason=stop_reason)


# ── Core endpoint ─────────────────────────────────────────────────────────────

class _MessagesEndpoint:
    """
    Implements client.messages.create() with full tool-calling support.
    Converts Anthropic params ↔ OpenAI /v1/chat/completions.
    """
    def __init__(self, base_url: str, model: str, timeout: int = 300):
        self._base_url = base_url.rstrip("/")
        self._model    = model
        self._timeout  = timeout

    def create(
        self,
        model:       str,
        max_tokens:  int,
        system:      str,
        messages:    list,
        tools:       Optional[list] = None,
        tool_choice: Any            = None,
        **kwargs,
    ) -> _MessageResponse:
        """
        Drop-in for anthropic.Anthropic().messages.create().

        All parameters match Anthropic's API signature.
        Extra kwargs are silently ignored for forward compatibility.
        """
        oai_messages = _messages_anthropic_to_oai(system, messages)

        payload: dict = {
            "model":       model or self._model,
            "messages":    oai_messages,
            "max_tokens":  max_tokens,
            "temperature": 0.1,
        }

        if tools:
            payload["tools"]       = _tools_anthropic_to_oai(tools)
            payload["tool_choice"] = _tool_choice_anthropic_to_oai(tool_choice)

        raw_payload = json.dumps(payload, ensure_ascii=False).encode()

        req = urllib.request.Request(
            f"{self._base_url}/v1/chat/completions",
            data    = raw_payload,
            headers = {"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                data = json.loads(resp.read())
        except urllib.error.URLError as e:
            raise ConnectionError(
                f"vLLM endpoint unreachable at {self._base_url}: {e}\n"
                f"Make sure vLLM is running: vllm serve {self._model} --port 8000"
            ) from e

        return _oai_response_to_anthropic(data)


# ── Public client ─────────────────────────────────────────────────────────────

class VLLMChatClient:
    """
    Drop-in replacement for anthropic.Anthropic() for Expert 2 and Expert 3.

    Full Agentic RAG support: multi-round tool calling works identically to
    the Claude path. Expert2Agent and Expert3Agent require zero modification.

    Example:
        client = VLLMChatClient(
            base_url = "http://localhost:8000",
            model    = "meta-llama/Meta-Llama-3.1-70B-Instruct",
        )
        from expert2_agent import Expert2Agent
        result = Expert2Agent(client=client).assess(system_description)
    """
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        model:    str = "meta-llama/Meta-Llama-3.1-70B-Instruct",
        timeout:  int = 300,
    ):
        self.messages  = _MessagesEndpoint(base_url, model, timeout)
        self._model    = model
        self._base_url = base_url

    def __repr__(self) -> str:
        return f"VLLMChatClient(base_url={self._base_url!r}, model={self._model!r})"


# ── Expert-1 compatible LLMBackend ────────────────────────────────────────────

def make_vllm_llm_backend(
    base_url: str = "http://localhost:8000",
    model:    str = "meta-llama/Meta-Llama-3.1-70B-Instruct",
):
    """
    Returns an Expert-1-compatible VLLMBackend (from expert1_router).
    Requires sys.path to include the Expert 1 directory.
    """
    import sys
    import os
    _e1_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "unicc-ai-agent Team 1 Expert 1",
    )
    if _e1_dir not in sys.path:
        sys.path.insert(0, _e1_dir)

    from expert1_router import VLLMBackend
    return VLLMBackend(base_url=base_url, model=model)
