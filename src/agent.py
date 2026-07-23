"""Ledger AI — core conversation loop (Phase 3).

Wires the Claude API to the Phase 3 tools:

1. Loads the system prompt from ``prompts/system_prompt_v1.txt``.
2. Loads one persona's dataset chosen by ``--persona`` (cafe / electrician /
   freelancer).
3. Runs the full tool-use loop: send message -> Claude may request a tool ->
   execute the tool against the loaded dataset -> return the result -> Claude
   responds. Repeats until Claude is done.
4. Maintains message history across turns for multi-turn conversation.
5. Handles missing data, malformed tool calls, and API errors gracefully.

Uses the Anthropic Python SDK with Claude Opus 4.8 and adaptive thinking.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import anthropic
from dotenv import load_dotenv

from tools import TOOL_DEFINITIONS, execute_tool

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 16000

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SYSTEM_PROMPT_PATH = BASE_DIR / "prompts" / "system_prompt_v1.txt"

PERSONA_FILES = {
    "cafe": "cafe_bondi_brew.json",
    "electrician": "electrician_watts_sons.json",
    "freelancer": "freelancer_clara_voss_creative.json",
}


class LedgerAgent:
    """A single, stateful Ledger AI conversation for one persona."""

    def __init__(self, persona: str, model: str = MODEL) -> None:
        if persona not in PERSONA_FILES:
            raise ValueError(
                f"Unknown persona '{persona}'. Choose from: {', '.join(PERSONA_FILES)}."
            )
        # Loads ANTHROPIC_API_KEY from a .env file if present.
        load_dotenv(BASE_DIR / ".env")

        self.persona = persona
        self.model = model
        self.client = anthropic.Anthropic()
        self.data = self._load_dataset(persona)
        # Anchor "now" to the most recent month actually present in this dataset,
        # since the mock data is frozen in early-to-mid 2025.
        balances = self.data.get("account_balances", [])
        latest_month = balances[-1]["month"] if balances else "the most recent period in this dataset"
        self.system_prompt = self._load_system_prompt() + (
            f"\n\n---\n\n# DATASET TIME CONTEXT\n"
            f"Treat today's date as if it is the start of the month immediately after "
            f"{latest_month} — i.e. {latest_month} is the most recently completed month "
            f"of data available. When the user asks about 'last month', they mean "
            f"{latest_month}. When they ask about 'this quarter' or 'recently', resolve "
            f"relative to that same anchor point, not the real-world current date."
        )
        self.messages: list[dict[str, Any]] = []

    # -- loading ----------------------------------------------------------- #

    def _load_system_prompt(self) -> str:
        """Read the system prompt, stripping the leading ``#`` header block."""
        if not SYSTEM_PROMPT_PATH.exists():
            raise FileNotFoundError(
                f"System prompt not found at {SYSTEM_PROMPT_PATH}. "
                "Create prompts/system_prompt_v1.txt and paste the P04 prompt."
            )
        raw = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")

        # Drop the comment header (lines starting with '#') and the marker line.
        body_lines: list[str] = []
        started = False
        for line in raw.splitlines():
            if not started:
                if line.strip().startswith("#") or not line.strip():
                    continue
                started = True
            body_lines.append(line)
        prompt = "\n".join(body_lines).strip()

        if not prompt:
            print(
                "[warning] prompts/system_prompt_v1.txt has no prompt text yet — "
                "paste your P04 prompt below the marker line. Using a minimal "
                "fallback prompt for now."
            )
            prompt = (
                "You are Ledger AI, a plain-English financial assistant for "
                "Australian small business owners. Always ground answers in the "
                "user's data by calling the provided tools before answering."
            )
        return prompt

    def _load_dataset(self, persona: str) -> dict:
        """Parse the persona's JSON dataset from ``data/``."""
        path = DATA_DIR / PERSONA_FILES[persona]
        if not path.exists():
            raise FileNotFoundError(f"Dataset not found: {path}")
        try:
            with path.open(encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Dataset {path} is not valid JSON: {exc}") from exc

    @property
    def business_name(self) -> str:
        return self.data.get("business", {}).get("name", self.persona)

    # -- conversation ------------------------------------------------------ #

    def chat(self, user_message: str) -> str:
        """Send a user message and return Ledger AI's final text reply.

        Runs the tool-use loop to completion, appending every turn (including
        Claude's thinking/tool_use blocks and our tool results) to the message
        history so context is preserved across calls.
        """
        self.messages.append({"role": "user", "content": user_message})

        # Guard against a runaway tool loop.
        for _ in range(12):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=MAX_TOKENS,
                system=self.system_prompt,
                thinking={"type": "adaptive"},
                tools=TOOL_DEFINITIONS,
                messages=self.messages,
            )

            # Preserve the assistant turn verbatim (thinking + tool_use blocks
            # must be echoed back unchanged on the next request).
            self.messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "tool_use":
                self.messages.append(
                    {"role": "user", "content": self._run_tools(response.content)}
                )
                continue

            if response.stop_reason == "pause_turn":
                # Server-side pause; re-send to let Claude resume.
                continue

            if response.stop_reason == "refusal":
                return (
                    "I'm sorry — I can't help with that request. If you rephrase "
                    "or ask about your financial data, I'm happy to help."
                )

            return self._extract_text(response)

        return (
            "I wasn't able to finish that — I made several tool calls without "
            "reaching an answer. Could you try narrowing the question?"
        )

    def _run_tools(self, content: list[Any]) -> list[dict]:
        """Execute every tool_use block in an assistant turn, collecting results."""
        results: list[dict] = []
        for block in content:
            if getattr(block, "type", None) != "tool_use":
                continue
            result = execute_tool(block.name, block.input, self.data)
            is_error = isinstance(result, dict) and "error" in result
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(result, default=str),
                "is_error": is_error,
            })
        return results

    @staticmethod
    def _extract_text(response: Any) -> str:
        """Join the text blocks of a final assistant response."""
        parts = [b.text for b in response.content if getattr(b, "type", None) == "text"]
        text = "\n".join(parts).strip()
        return text or "(no text response)"
