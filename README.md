# Ledger AI

**A plain-English finance assistant for Australian small business owners — ask
questions about your cash flow, expenses, invoices, and GST, and get instant,
grounded answers.**

Built AI-first with the Claude API: I designed the architecture, the personas,
the system prompt, and the eval suite; Claude Code wrote the implementation
from my task prompts. Every prompt, every bug found, and every fix is
documented in [`PROMPTS.md`](./PROMPTS.md) — 36 entries and counting.

---

## The problem

Australian SMEs generate a lot of financial data through platforms like Xero
and MYOB, but reading it back out requires accounting knowledge most owners
don't have time to develop. The result: either an expensive call to the
accountant for a basic question, or the numbers get ignored entirely.

Ledger AI sits on top of that data and answers in plain English — with
Australian context (GST, BAS, PAYG, superannuation) built in — so a business
owner can ask "how much did I actually bring in last month?" or "is anything
unusual in my expenses?" and get a specific, grounded answer instead of a
spreadsheet.

## What makes this different from a typical portfolio project

Most AI-assisted projects show the finished code. This one also shows the
*process* — every prompt iteration, every bug caught and why, every eval
failure traced back to a real cause before being fixed:

- **[`PROMPTS.md`](./PROMPTS.md)** — every prompt written for this project, the
  design decisions behind each one, and a running log of every bug found
  during testing (data errors, tool gaps, guardrail conflicts, even bugs in
  the automated eval judge itself) with the reasoning behind each fix.
- **[`ARCHITECTURE.md`](./ARCHITECTURE.md)** — how the system is built, why key
  design decisions were made, and an honest account of what still doesn't
  work reliably and why (an LLM-driven system has a real reliability ceiling
  that no amount of prompt tuning removes — see the Known Limitations
  section).
- **A 50-case automated eval suite**, graded by a second Claude call acting as
  a judge — not just a handful of manually-checked questions.

## Features

- Plain-English Q&A over income, expenses, cash flow, invoices, GST, and
  payroll
- Full Australian tax context: GST, BAS quarters, PAYG withholding vs.
  instalments, superannuation — built in, always current, never guessed
- Grounded answers only — every figure comes from a real tool call against
  real data, never generated from memory
- Cash-basis vs. accrual awareness: "how much did I bring in" answers with
  cash actually received, not just what's been invoiced
- Guardrails against giving personalised tax or business-strategy advice —
  states what the data shows, defers judgement calls to the user or their
  accountant
- Three realistic SME personas with genuinely different financial patterns
  (a café's daily takings, a tradesperson's project-based cash flow squeezes,
  a freelancer's mixed retainer/project income)

## Tech stack

Python · Claude API (`claude-sonnet-4-6`) · tool use · multi-turn
conversation · prompt caching

## Quick start

```bash
git clone https://github.com/avni-solanki/ledger-ai
cd ledger-ai
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # then add your ANTHROPIC_API_KEY
python src/main.py --persona cafe    # or electrician / freelancer
```

You'll need an API key from [console.anthropic.com](https://console.anthropic.com)
— usage is pay-as-you-go and inexpensive for casual use of this app.

## Example

```
Ledger AI — Bondi Brew Co. (cafe)
Ask about income, expenses, cash flow, invoices, GST or payroll.
Type 'exit' to quit.

You: What was my total revenue for January?

Ledger AI: Your total revenue for January 2025 was $24,602.40 inc. GST —
of that, $22,365.82 is ex-GST (yours to keep), and $2,236.58 is GST you're
holding on behalf of the ATO.

January was your strongest month — no surprise given it's peak Bondi summer
tourist season. Would you like to compare it to another month?
```

## Running the eval suite

```bash
python src/eval_runner.py                  # full 50-case suite
python src/eval_runner.py --persona=cafe    # one persona only
python src/eval_runner.py --limit=5         # quick smoke test
```

Each case is graded by a second Claude call acting as an automated judge,
scoring the answer against `must_include`/`must_not_include` criteria in
spirit rather than by literal string matching. Results are written to
`evals/results/` with a full pass/fail breakdown by persona and category.
The project currently sits at a stable ~88% pass rate; see `PROMPTS.md`
(entry P35) for why 100% isn't the right target for a system that generates
free-form answers, and which specific gaps remain open and why.

## Project structure

```
ledger-ai/
├── data/                          # Mock Xero-style financial data, 3 personas
├── src/
│   ├── main.py                    # CLI entry point
│   ├── agent.py                   # Claude API conversation loop
│   ├── tools.py                   # Tool definitions (transactions, invoices, GST...)
│   └── eval_runner.py             # Automated eval suite runner + LLM judge
├── evals/
│   ├── test_cases.json            # 50 structured test cases
│   └── results/                   # Timestamped eval run outputs
├── prompts/
│   └── system_prompt_v1.txt       # The live system prompt
├── PROMPTS.md                     # Full prompt engineering decision log
├── ARCHITECTURE.md                # System design, tradeoffs, known limitations
└── Diligence Statement.md         # AI-collaboration disclosure
```

## What's next

- Replace the mock data layer with a live Xero or MYOB API connection — the
  architecture is designed for this as a direct next step, with a consistent
  JSON schema modelled on real Xero export formats
- A simple web interface on top of the CLI, for a broader demo audience
- Move a couple of the free-form anomaly-detection behaviours (see
  `ARCHITECTURE.md`, Known Limitations) from the prompt layer into the tool
  layer for more reliable detection of things like invoice escalation notes

## About this project

Built as a portfolio project to demonstrate AI-first software development:
directing Claude Code with precise, well-scoped task prompts, reviewing
generated code and data critically rather than accepting it at face value,
and treating prompt quality as an engineering discipline with the same rigour
as the code itself — designed, tested, debugged, and documented.