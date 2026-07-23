"""Ledger AI — CLI entry point (Phase 3).

Usage:
    python src/main.py --persona cafe
    python src/main.py --persona electrician
    python src/main.py --persona freelancer

Starts an interactive chat with Ledger AI for the chosen persona. Type your
question, press Enter, read the reply. Type 'exit' (or 'quit') to leave.
"""

from __future__ import annotations

import argparse
import sys

import anthropic

from agent import PERSONA_FILES, LedgerAgent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Ledger AI — a plain-English financial assistant for Australian SMEs.",
    )
    parser.add_argument(
        "--persona",
        required=True,
        choices=sorted(PERSONA_FILES),
        help="Which business dataset to load (cafe / electrician / freelancer).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    try:
        agent = LedgerAgent(args.persona)
    except (FileNotFoundError, ValueError) as exc:
        print(f"[startup error] {exc}", file=sys.stderr)
        return 1
    except anthropic.AnthropicError:
        print(
            "[auth error] No valid ANTHROPIC_API_KEY. Copy .env.example to .env "
            "and add your key, or export ANTHROPIC_API_KEY.",
            file=sys.stderr,
        )
        return 1

    print(f"\nLedger AI — {agent.business_name} ({args.persona})")
    print("Ask about income, expenses, cash flow, invoices, GST or payroll.")
    print("Type 'exit' to quit.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye.")
            return 0
        if not user_input:
            continue

        try:
            reply = agent.chat(user_input)
        except anthropic.APIStatusError as exc:
            print(f"[API error {exc.status_code}] {exc.message}\n", file=sys.stderr)
            continue
        except anthropic.APIConnectionError:
            print("[network error] Could not reach the API. Check your connection.\n", file=sys.stderr)
            continue
        except Exception as exc:  # last-resort guard so the REPL stays alive
            print(f"[unexpected error] {exc}\n", file=sys.stderr)
            continue

        print(f"\nLedger AI: {reply}\n")


if __name__ == "__main__":
    raise SystemExit(main())
