"""Ledger AI — automated eval runner (Phase 3, scores the P06 test suite).

Runs every case in evals/test_cases.json against a fresh Ledger AI
conversation for the right persona, then uses a separate Claude "judge" call
to score the answer against each case's must_include / must_not_include /
expected_behaviour criteria.

Why an LLM judge instead of plain substring matching: the eval cases'
must_include fields mix literal values (e.g. "$24,602.40") with descriptive
criteria that are meant to be satisfied in spirit (e.g. "GST breakdown",
"specific dollar amount"). A real answer will rarely contain those exact
phrases even when it correctly does the thing they describe, so a substring
check would fail good answers. A judge model can assess intent, not just
wording.

Usage:
    python src/eval_runner.py                 # run all 50 cases
    python src/eval_runner.py --limit=5        # smoke-test on the first 5
    python src/eval_runner.py --persona=cafe   # only this persona's cases
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from agent import LedgerAgent

BASE_DIR = Path(__file__).resolve().parent.parent
TEST_CASES_PATH = BASE_DIR / "evals" / "test_cases.json"
RESULTS_DIR = BASE_DIR / "evals" / "results"

# Deliberately a lighter/cheaper model than the agent under test. The judge's
# job is well-defined and doesn't need the agent's own reasoning budget.
JUDGE_MODEL = "claude-sonnet-4-6"
JUDGE_MAX_TOKENS = 4096

JUDGE_SYSTEM_PROMPT = """You are a strict evaluation judge for an AI finance assistant called Ledger AI, \
used by Australian small business owners.

You will be given: a user question, a description of what a good answer should do, a list of things \
the answer MUST include, a list of things the answer MUST NOT include, and the actual answer that was \
given.

Judge each must_include item as satisfied if the answer does that thing in spirit, even if it doesn't \
use the exact same words (e.g. "GST breakdown" is satisfied if the answer clearly separates a GST \
component from a total figure, even without using the words "GST breakdown"). Judge each \
must_not_include item as violated if the answer does that thing at all, even implicitly or partially.

Be especially careful with "invented figures" as a must_not_include criterion. A specific, granular \
number (e.g. a sub-total for one payment type, or a single transaction amount) is NOT automatically \
invented just because it wasn't spelled out in the question. Breaking a total down into components \
(e.g. revenue by source, expenses by category) is a core, expected feature of a grounded tool-use \
answer — this is the whole point of the app, not a red flag.

Your default assumption for any specific, plausible sub-total is that it is REAL, not invented. You \
may only mark "invented figures" as violated if you can show your work: actually perform the addition \
or ratio check yourself, write the specific numbers and the result in your reason, and confirm they do \
NOT reconcile (allowing normal cent-level rounding — a difference of one or two cents from rounding at \
each calculation step is expected, not evidence of fabrication). If you have not shown a specific, \
worked calculation that reveals a genuine mismatch, you must not conclude the figure is invented — \
"cannot be verified" or "not present in the question" are not valid reasons to fail this criterion on \
their own.

Worked example — do NOT fail this: an answer states total revenue $24,602.40, broken down as \
in-store $22,854.08 and Uber Eats $1,748.32. Check: $22,854.08 + $1,748.32 = $24,602.40 exactly. This \
reconciles, so these sub-totals are NOT invented, even though the question only asked for the total \
and the breakdown wasn't requested.

Before concluding that a must_include figure is missing or wrong because the answer states a \
different number, check whether the two numbers are the same real figure on a different GST basis. \
A figure expressed ex-GST is the inc-GST figure divided by 1.1 (and vice versa) — e.g. $2,420 \
inc-GST is exactly $2,200.00 ex-GST. An answer that consistently uses ex-GST framing throughout \
(e.g. its own table explicitly labelled "Ex-GST") and states $2,200 has not stated something \
different from a must_include criterion asking for "$2,420" — it has stated the same fact on a \
different, self-consistent basis. Do the division/multiplication yourself before judging this as \
missing or invented.

Your arithmetic check must stay INTERNAL to the answer's own numbers — checking that figures the \
answer presents together are mutually consistent (e.g. a stated GST + a stated ex-GST amount sums to \
a stated total; a stated net pay equals a stated gross pay minus a stated tax withheld). Do NOT invent \
an external formula or "should be" rate from your own general knowledge and treat a mismatch against \
that assumption as evidence of fabrication. For example, a stated superannuation amount is normally a \
figure retrieved directly from the business's own payroll records, not something the answer derives \
live using a textbook rate — you do not have access to that business's actual data, so you cannot know \
what rate they use, and assuming a standard rate (e.g. 11%) applies and flagging any different figure \
as wrong is not a valid basis to fail this criterion. Only check consistency between numbers the \
answer itself presents as related (e.g. components of a stated breakdown, or a stated formula the \
answer itself claims to have applied).

Only flag a figure as invented if it is inconsistent with the rest of the answer's own numbers by \
more than a trivial rounding margin (and you've shown that arithmetic), or is clearly fabricated \
context (e.g. a named person, invoice number, or event that has no basis in the question). Do not \
fail an answer for genuine precision; a grounded tool-use answer is expected to cite individual line \
items and sub-totals, not just headline figures.

The overall verdict is "pass" only if every must_include item is satisfied AND no must_not_include \
item is violated. Otherwise it is "fail".

Work through must_include_results and must_not_include_results FIRST, then compute verdict and \
overall_reason LAST, once you've actually finished reasoning through every criterion — this is why \
verdict is the last field in the schema below, not the first. Committing to a verdict before you've \
worked through the criteria is exactly what causes the mistake this ordering is designed to prevent: \
if you write your reasoning out and only then find your initial verdict doesn't match it, you must \
NOT write a second, corrected JSON object — instead, revise the verdict field itself before finishing \
your one and only response. Your entire response must be exactly one JSON object, with no other \
object, draft, or correction anywhere in the response.

Do all of your arithmetic checking and reasoning INSIDE the JSON's "reason" fields — never write \
narration, working, or explanation before or after the JSON object. Your entire response must be a \
single JSON object and nothing else, starting with { and ending with }. If you need to show a \
calculation, put it directly in the relevant criterion's "reason" string (e.g. "reason": "Check: \
$22,854.08 + $1,748.32 = $24,602.40, reconciles exactly").

Keep each "reason" field to one short sentence. You will be judging answers with several criteria at \
once; verbose reasoning per criterion risks running out of output space before the JSON is complete.

Respond with ONLY valid JSON, no other text, in exactly this shape — note that must_include_results \
and must_not_include_results come BEFORE verdict, since you should reason through every criterion \
before concluding the overall verdict, not the other way around:
{
  "must_include_results": [{"criterion": "...", "satisfied": true or false, "reason": "..."}],
  "must_not_include_results": [{"criterion": "...", "violated": true or false, "reason": "..."}],
  "verdict": "pass" or "fail",
  "overall_reason": "one sentence explaining the verdict"
}
"""


def load_test_cases() -> list[dict]:
    """Load evals/test_cases.json, tolerating a bare list or a wrapped object."""
    data = json.loads(TEST_CASES_PATH.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    return data.get("test_cases", data.get("cases", []))


def _extract_first_json_object(text: str) -> str:
    """Return the substring spanning the FIRST complete, balanced {...} object
    in text, tracking brace depth and skipping over braces inside quoted
    strings. This correctly isolates one JSON object even if the model wrote
    trailing prose, a second corrected attempt, or anything else after it —
    unlike a naive "first { to last }" slice, which would span across
    multiple objects and produce garbage.
    """
    start = text.find("{")
    if start == -1:
        return text
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return text[start:]  # unbalanced (likely truncated) — return what we have


def _recompute_verdict(parsed: dict) -> dict:
    """Recompute pass/fail deterministically from the judge's own itemised
    satisfied/violated booleans, rather than trusting its self-reported
    "verdict" field. The model can get every individual criterion right and
    still write an inconsistent overall verdict (observed directly: a case
    where every must_include was satisfied=true, every must_not_include was
    violated=false, the model's own overall_reason said "the verdict should
    be pass" — and it still wrote "verdict": "fail" anyway). The itemised
    booleans have been reliable throughout this project's testing; the
    summary field is not. Compute the real answer from the reliable part.
    """
    must_include_results = parsed.get("must_include_results", [])
    must_not_include_results = parsed.get("must_not_include_results", [])

    all_satisfied = all(r.get("satisfied") is True for r in must_include_results)
    none_violated = all(r.get("violated") is not True for r in must_not_include_results)
    computed_verdict = "pass" if (all_satisfied and none_violated) else "fail"

    model_verdict = parsed.get("verdict")
    if model_verdict != computed_verdict:
        parsed["model_reported_verdict"] = model_verdict  # kept for transparency/debugging
        parsed["overall_reason"] = (
            f"[Verdict corrected from the judge's own itemised results — model said "
            f"'{model_verdict}' but every must_include was satisfied and no must_not_include "
            f"was violated, so the deterministic verdict is '{computed_verdict}'.] "
            f"{parsed.get('overall_reason', '')}"
        )
    parsed["verdict"] = computed_verdict
    return parsed


def _judge_attempt(
    client: anthropic.Anthropic, user_prompt: str, retry_note: str = ""
) -> dict:
    """Make one judge API call and try to parse it. Raises json.JSONDecodeError
    on failure (caught by the retry loop in judge()), rather than swallowing
    the error here — the caller decides whether to retry or give up.
    """
    response = client.messages.create(
        model=JUDGE_MODEL,
        max_tokens=JUDGE_MAX_TOKENS,
        system=JUDGE_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt + retry_note}],
    )
    text = "".join(
        b.text for b in response.content if getattr(b, "type", None) == "text"
    ).strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    text = _extract_first_json_object(text)

    if getattr(response, "stop_reason", None) == "max_tokens":
        raise json.JSONDecodeError(
            f"truncated by max_tokens ({JUDGE_MAX_TOKENS})", text, len(text)
        )

    parsed = json.loads(text)  # let JSONDecodeError propagate to the caller
    return _recompute_verdict(parsed)


def judge(client: anthropic.Anthropic, case: dict, answer: str) -> dict:
    """Ask the judge model to grade one eval case's answer. Never raises —
    a malformed judge response is reported as a failed case with a reason,
    so one bad judge call can't take down the whole run.

    Retries once on a JSON parse failure before giving up. Malformed JSON
    (a stray unescaped quote, a missing comma) is usually a one-off slip
    rather than a repeatable pattern — a second attempt, with an explicit
    reminder of what broke, resolves most of these without needing yet
    another narrow prompt patch for each new syntax variant encountered.
    """
    user_prompt = (
        f"QUESTION:\n{case['question']}\n\n"
        f"EXPECTED BEHAVIOUR:\n{case.get('expected_behaviour', '')}\n\n"
        f"MUST INCLUDE (judge in spirit, not literal wording):\n"
        f"{json.dumps(case.get('must_include', []), indent=2)}\n\n"
        f"MUST NOT INCLUDE:\n{json.dumps(case.get('must_not_include', []), indent=2)}\n\n"
        f"ACTUAL ANSWER:\n{answer}\n"
    )

    last_error: json.JSONDecodeError | None = None
    for attempt in range(2):  # one initial attempt + one retry
        retry_note = ""
        if attempt > 0:
            retry_note = (
                f"\n\nYour previous response was not valid JSON ({last_error}). "
                f"Respond again with ONLY a single, strictly valid JSON object — "
                f"check every string is properly quoted and escaped, and every "
                f"array/object element is separated by a comma."
            )
        try:
            return _judge_attempt(client, user_prompt, retry_note)
        except json.JSONDecodeError as exc:
            last_error = exc
            continue
        except Exception as exc:  # noqa: BLE001 - must never crash the run
            return {"verdict": "fail", "overall_reason": f"Judge call failed: {exc}"}

    # Both attempts failed to parse — report clearly rather than crash the run.
    return {
        "verdict": "fail",
        "overall_reason": (
            f"Judge did not return valid JSON after a retry ({last_error}). "
            f"This is a tooling failure, not necessarily a reflection of the answer's quality."
        ),
    }


# "shared" cases (edge-case questions meant to be persona-agnostic) aren't a
# real dataset LedgerAgent can load — substitute an actual persona so the
# question still runs against real data, while keeping "shared" as the
# reported label so results stay correctly categorised.
SHARED_CASE_DEFAULT_PERSONA = "cafe"


def run_all(limit: int | None = None, persona_filter: str | None = None) -> list[dict]:
    """Run (a subset of) the eval suite and return one result dict per case."""
    load_dotenv(BASE_DIR / ".env")
    client = anthropic.Anthropic()

    cases = load_test_cases()
    if persona_filter:
        cases = [c for c in cases if c.get("persona") == persona_filter]
    if limit:
        cases = cases[:limit]

    results: list[dict] = []
    for i, case in enumerate(cases, start=1):
        persona = case["persona"]
        label = f"[{i}/{len(cases)}] {case['id']} ({persona}/{case.get('category')})"
        print(f"{label} ... ", end="", flush=True)

        # Fresh agent per case: each eval question is a standalone conversation,
        # not a multi-turn one, so no history should carry over between cases.
        try:
            agent_persona = SHARED_CASE_DEFAULT_PERSONA if persona == "shared" else persona
            agent = LedgerAgent(agent_persona)
            answer = agent.chat(case["question"])
        except Exception as exc:  # noqa: BLE001
            print(f"ERROR ({exc})")
            results.append({**case, "answer": None, "verdict": "error", "overall_reason": str(exc)})
            continue

        verdict = judge(client, case, answer)
        results.append({**case, "answer": answer, **verdict})
        print(verdict.get("verdict", "unknown"))

    return results


def summarise(results: list[dict]) -> None:
    """Print a pass-rate breakdown by overall total, persona, and category."""
    total = len(results)
    if not total:
        print("No cases run.")
        return

    passed = sum(1 for r in results if r.get("verdict") == "pass")
    print(f"\n{passed}/{total} passed ({passed / total:.0%})")

    def _breakdown(key: str, title: str) -> None:
        groups: dict[str, list[dict]] = {}
        for r in results:
            groups.setdefault(r.get(key, "unknown"), []).append(r)
        print(f"\nBy {title}:")
        for name, rs in sorted(groups.items()):
            p = sum(1 for r in rs if r.get("verdict") == "pass")
            print(f"  {name}: {p}/{len(rs)}")

    _breakdown("persona", "persona")
    _breakdown("category", "category")

    failed = [r for r in results if r.get("verdict") != "pass"]
    if failed:
        print(f"\nFailed cases ({len(failed)}):")
        for r in failed:
            print(f"  - {r['id']} ({r.get('persona')}/{r.get('category')}): "
                  f"{r.get('overall_reason', 'no reason given')}")


def main() -> None:
    limit: int | None = None
    persona_filter: str | None = None

    for arg in sys.argv[1:]:
        if arg.startswith("--limit="):
            limit = int(arg.split("=", 1)[1])
        elif arg.startswith("--persona="):
            persona_filter = arg.split("=", 1)[1]

    results = run_all(limit=limit, persona_filter=persona_filter)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_path = RESULTS_DIR / f"eval_run_{timestamp}.json"
    out_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    summarise(results)
    print(f"\nFull results written to {out_path.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
