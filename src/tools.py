"""Ledger AI — tool implementations for Claude tool use (Phase 3).

Each function queries a *loaded* persona dataset (a plain ``dict`` parsed from
one of the JSON files in ``data/``) and returns a JSON-serialisable ``dict``.

The three persona datasets do NOT share an identical schema, so this module
includes a small normalisation layer:

* Café invoices use ``supplier`` / ``date`` / ``total`` / ``gst``.
* Electrician & freelancer invoices use ``client_name`` / ``date_issued`` /
  ``amount_inc_gst`` / ``gst_amount`` / ``date_paid``.
* Café payroll is nested (``period`` -> ``entries`` with superannuation).
* Electrician payroll is a flat list of subcontractor payments (no super).
* Freelancer has no payroll at all.
* Monthly account-balance fields are ``total_income`` / ``total_expenses``
  (café) vs ``total_income_received`` / ``total_expenses_paid`` (others).

Every tool tolerates missing sections and returns a structured, explicit
result rather than raising — so Claude can explain gaps to the user instead of
receiving an opaque error.

``TOOL_DEFINITIONS`` holds the Anthropic tool schemas and ``execute_tool``
dispatches a tool-use request to the matching function.
"""

from __future__ import annotations

import re
from typing import Any, Optional

# --------------------------------------------------------------------------- #
# Date / month helpers
# --------------------------------------------------------------------------- #

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11,
    "december": 12, "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _extract_year_month(text: Optional[str]) -> tuple[Optional[int], Optional[int]]:
    """Best-effort parse of a year and/or month from a free-form string.

    Handles ISO forms (``2025-03``, ``2025-03-15``) and month names
    (``March``, ``March 2025``, ``Mar``). Returns ``(year, month)`` where
    either component may be ``None`` if not present in the string.
    """
    if not text:
        return (None, None)
    s = text.strip().lower()

    iso = re.match(r"(\d{4})-(\d{2})", s)
    if iso:
        return (int(iso.group(1)), int(iso.group(2)))

    year = None
    year_match = re.search(r"(20\d{2})", s)
    if year_match:
        year = int(year_match.group(1))

    month = None
    for name, num in _MONTHS.items():
        if re.search(r"\b" + name + r"\b", s):
            month = num
            break

    return (year, month)


def _month_matches(entry: Optional[str], query: Optional[str]) -> bool:
    """True if ``entry`` (e.g. ``"January 2025"``) matches the ``query`` period.

    A query component (month and/or year) only constrains the match if it is
    present in the query, so ``"March"`` matches any March and ``"2025-03"``
    matches only March 2025.
    """
    qy, qm = _extract_year_month(query)
    if qy is None and qm is None:
        return False
    ey, em = _extract_year_month(entry)
    if qm is not None and qm != em:
        return False
    if qy is not None and qy != ey:
        return False
    return True


def _pad_start(date_str: str) -> str:
    """Normalise a ``YYYY-MM`` start bound to the first day of the month."""
    return date_str + "-01" if len(date_str) == 7 else date_str


def _pad_end(date_str: str) -> str:
    """Normalise a ``YYYY-MM`` end bound to the last day of the month."""
    return date_str + "-31" if len(date_str) == 7 else date_str


def _in_range(date_str: Optional[str], start: Optional[str], end: Optional[str]) -> bool:
    """ISO date strings sort lexically, so plain string comparison is safe."""
    if not date_str:
        return False
    if start and date_str < _pad_start(start):
        return False
    if end and date_str > _pad_end(end):
        return False
    return True


def _round(value: Any) -> Any:
    """Round numeric values to cents; leave everything else untouched."""
    return round(value, 2) if isinstance(value, (int, float)) else value


# --------------------------------------------------------------------------- #
# Normalisation helpers
# --------------------------------------------------------------------------- #

def _normalise_invoice(inv: dict) -> dict:
    """Map a persona-specific invoice onto a single common shape.

    Important: the personas' invoice records point in OPPOSITE directions.
    Café invoices are supplier bills the business owes ("supplier" field) —
    accounts payable. Electrician/freelancer invoices are bills issued to
    clients ("client_name" field) — accounts receivable. Getting this
    backwards produces confidently wrong statements about who owes whom, so
    it's tracked explicitly rather than left for the model to guess.
    """
    amount_inc = inv.get("amount_inc_gst")
    if amount_inc is None:
        amount_inc = inv.get("total")  # café uses "total"
    gst = inv.get("gst_amount")
    if gst is None:
        gst = inv.get("gst")  # café uses "gst"

    is_payable = "supplier" in inv  # café-style: money the business owes
    direction = "payable" if is_payable else "receivable"

    return {
        "invoice_number": inv.get("invoice_number"),
        "counterparty": inv.get("client_name") or inv.get("supplier"),
        "direction": direction,
        "direction_note": (
            "This is a bill FROM a supplier that the business OWES (accounts payable)."
            if is_payable
            else "This is an invoice the business ISSUED to a client, so it's money OWED TO the business (accounts receivable)."
        ),
        "description": (
            inv.get("job_description")
            or inv.get("project_description")
            or inv.get("description")
        ),
        "date_issued": inv.get("date_issued") or inv.get("date"),
        "due_date": inv.get("due_date"),
        "amount_inc_gst": amount_inc,
        "gst_amount": gst,
        "status": inv.get("status"),
        "date_paid": inv.get("date_paid"),
        "invoice_type": inv.get("invoice_type"),  # freelancer only (retainer/project)
        "notes": inv.get("notes"),  # important context (e.g. solicitor referral, write-offs)
    }


# --------------------------------------------------------------------------- #
# Tools
# --------------------------------------------------------------------------- #

def get_transactions(
    data: dict,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    transaction_type: Optional[str] = None,
    **_: Any,
) -> dict:
    """Return transactions filtered by date range, category, and/or type.

    Args:
        data: Loaded persona dataset.
        start_date: Inclusive lower bound (``YYYY-MM-DD`` or ``YYYY-MM``).
        end_date: Inclusive upper bound (``YYYY-MM-DD`` or ``YYYY-MM``).
        category: Case-insensitive substring match on the category field.
        transaction_type: One of ``income``, ``expense`` (or ``note``).

    Returns:
        A dict with the matching ``transactions`` and roll-up totals.
    """
    txns = data.get("transactions", [])
    cat = category.lower() if category else None
    ttype = transaction_type.lower() if transaction_type else None

    matched = []
    for t in txns:
        if not _in_range(t.get("date"), start_date, end_date):
            continue
        if cat and cat not in (t.get("category") or "").lower():
            continue
        if ttype and (t.get("type") or "").lower() != ttype:
            continue
        matched.append(t)

    total_amount = _round(sum(t.get("amount", 0) or 0 for t in matched))
    total_gst = _round(sum(t.get("gst_amount", 0) or 0 for t in matched))

    # Cash-basis vs accrual distinction: an income transaction tied to an
    # invoice that hasn't actually been paid yet represents work invoiced,
    # not cash received. Cross-reference against the invoices list so
    # "how much did I bring in" can answer cash received by default, while
    # the full (accrual) total remains available if genuinely asked for.
    invoice_status_by_number = {
        inv.get("invoice_number"): (inv.get("status") or "").lower()
        for inv in data.get("invoices", [])
        if inv.get("invoice_number")
    }
    inv_pattern = re.compile(r"INV-\d{4}")

    not_yet_received = []
    for t in matched:
        if t.get("type") != "income":
            continue
        m = inv_pattern.search(t.get("description", ""))
        if not m:
            continue  # not tied to an invoice (e.g. daily takings) -> treated as cash received
        status = invoice_status_by_number.get(m.group(0))
        if status and status != "paid":
            t["_linked_invoice_status"] = status  # surfaced to the model, not hidden
            not_yet_received.append(t)

    cash_received_amount = _round(
        total_amount - sum(t.get("amount", 0) or 0 for t in not_yet_received)
    )

    return {
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "category": category,
            "transaction_type": transaction_type,
        },
        "count": len(matched),
        "total_amount": total_amount,
        "total_amount_note": (
            "This is the accrual total: it includes any income transaction tied to an "
            "invoice that has been issued but not yet paid. For 'how much did I actually "
            "bring in / receive' questions, use total_amount_cash_received instead."
        ),
        "total_amount_cash_received": cash_received_amount,
        "total_gst": total_gst,
        "not_yet_received_count": len(not_yet_received),
        "transactions": matched,
    }


def get_account_balance(
    data: dict,
    month: Optional[str] = None,
    **_: Any,
) -> dict:
    """Return monthly cash-account balances (opening/closing) for a period.

    Args:
        data: Loaded persona dataset.
        month: A month to filter by (``"March"``, ``"March 2025"`` or
            ``"2025-03"``). If omitted, all months are returned.

    Returns:
        A dict with normalised ``balances`` (income/expense field names are
        unified across personas).
    """
    balances = data.get("account_balances", [])

    normalised = []
    for b in balances:
        if month and not _month_matches(b.get("month"), month):
            continue
        normalised.append({
            "month": b.get("month"),
            "opening_balance": b.get("opening_balance"),
            "total_income": b.get("total_income", b.get("total_income_received")),
            "total_expenses": b.get("total_expenses", b.get("total_expenses_paid")),
            "closing_balance": b.get("closing_balance"),
            "outstanding_receivables": b.get("outstanding_receivables"),
            "notes": b.get("notes"),
        })

    if month and not normalised:
        return {
            "error": f"No account balance found for '{month}'.",
            "available_months": [b.get("month") for b in balances],
        }

    return {"filter_month": month, "count": len(normalised), "balances": normalised}


def get_invoices(
    data: dict,
    status: Optional[str] = None,
    **_: Any,
) -> dict:
    """Return invoices, optionally filtered by status.

    Args:
        data: Loaded persona dataset.
        status: One of ``paid``, ``outstanding``, ``overdue``. If omitted,
            all invoices are returned.

    Returns:
        A dict with normalised ``invoices`` and a status roll-up. Amounts are
        summed inc-GST so cash-flow questions ("how much am I owed?") work
        directly.
    """
    invoices = [_normalise_invoice(i) for i in data.get("invoices", [])]
    want = status.lower() if status else None

    matched = [i for i in invoices if not want or (i.get("status") or "").lower() == want]

    total_inc_gst = _round(sum(i.get("amount_inc_gst", 0) or 0 for i in matched))

    # Status breakdown across the whole invoice set for context.
    breakdown: dict[str, dict] = {}
    for i in invoices:
        key = (i.get("status") or "unknown").lower()
        entry = breakdown.setdefault(key, {"count": 0, "total_inc_gst": 0.0})
        entry["count"] += 1
        entry["total_inc_gst"] += i.get("amount_inc_gst", 0) or 0
    for entry in breakdown.values():
        entry["total_inc_gst"] = _round(entry["total_inc_gst"])

    return {
        "filter_status": status,
        "count": len(matched),
        "total_inc_gst": total_inc_gst,
        "status_breakdown": breakdown,
        "invoices": matched,
    }


def get_gst_summary(
    data: dict,
    quarter: Optional[str] = None,
    **_: Any,
) -> dict:
    """Return BAS-ready GST collected/paid/net for a quarter (or all quarters).

    Args:
        data: Loaded persona dataset.
        quarter: A quarter identifier such as ``"Q3"``, ``"Q4"``,
            ``"Jan-Mar"``, or ``"Apr-Jun"``. If omitted, all quarters return.

    Returns:
        A dict of matching ``quarters`` keyed by the dataset's BAS-quarter key
        (e.g. ``"Q3_FY2025_Jan_Mar"``).
    """
    gst = data.get("gst_summary", {})
    if not gst:
        return {"gst_available": False, "note": "No GST summary in this dataset."}

    if not quarter:
        return {"quarters": gst}

    q = quarter.strip().lower().replace(" ", "_").replace("-", "_")
    tokens = [t for t in q.split("_") if t]
    matched = {
        key: val
        for key, val in gst.items()
        if q in key.lower() or any(tok in key.lower() for tok in tokens)
    }

    if not matched:
        return {
            "error": f"No GST summary found for '{quarter}'.",
            "available_quarters": list(gst.keys()),
        }
    return {"filter_quarter": quarter, "quarters": matched}


def get_payroll_summary(
    data: dict,
    period: Optional[str] = None,
    **_: Any,
) -> dict:
    """Return payroll totals (wages + super, or subcontractor payments).

    The shape of ``payroll`` differs by persona, so this normalises:

    * Café — nested employee entries per month, including superannuation.
    * Electrician — a flat list of subcontractor payments (no super/PAYG).
    * Freelancer — no payroll section (solo operator); reported explicitly.

    Args:
        data: Loaded persona dataset.
        period: A month to filter by (``"March"`` / ``"2025-03"``).

    Returns:
        A dict describing the payroll for the period, tagged with
        ``payroll_type`` so the caller knows what shape it received.
    """
    payroll = data.get("payroll")
    if not payroll:
        return {
            "payroll_available": False,
            "note": (
                "This business has no payroll records — e.g. a solo operator "
                "with no employees or subcontractors."
            ),
        }

    first = payroll[0]

    # --- Café-style: employee wages with superannuation ------------------- #
    if "entries" in first:
        periods = []
        for month in payroll:
            if period and not _month_matches(month.get("period"), period):
                continue
            entries = month.get("entries", [])
            periods.append({
                "period": month.get("period"),
                "employee_count": len(entries),
                "total_hours": _round(sum(e.get("hours", 0) or 0 for e in entries)),
                "total_gross_pay": _round(sum(e.get("gross_pay", 0) or 0 for e in entries)),
                "total_tax_withheld": _round(sum(e.get("tax_withheld", 0) or 0 for e in entries)),
                "total_net_pay": _round(sum(e.get("net_pay", 0) or 0 for e in entries)),
                "total_superannuation": _round(sum(e.get("superannuation", 0) or 0 for e in entries)),
                "entries": entries,
            })

        if period and not periods:
            return {
                "error": f"No payroll found for '{period}'.",
                "available_periods": [m.get("period") for m in payroll],
            }

        return {
            "payroll_type": "employee_wages",
            "filter_period": period,
            "grand_total_gross_pay": _round(sum(p["total_gross_pay"] for p in periods)),
            "grand_total_superannuation": _round(sum(p["total_superannuation"] for p in periods)),
            "periods": periods,
        }

    # --- Electrician-style: subcontractor payments ------------------------ #
    if "subcontractor_name" in first:
        matched = [p for p in payroll if not period or _month_matches(p.get("date"), period)]
        return {
            "payroll_type": "subcontractor_payments",
            "filter_period": period,
            "count": len(matched),
            "total_ex_gst": _round(sum(p.get("amount_ex_gst", 0) or 0 for p in matched)),
            "total_gst": _round(sum(p.get("gst", 0) or 0 for p in matched)),
            "total_inc_gst": _round(sum(p.get("amount_inc_gst", 0) or 0 for p in matched)),
            "payments": matched,
            "note": (
                "These are payments to subcontractors (potentially TPAR-reportable), "
                "not employee wages — there is no PAYG withholding or superannuation."
            ),
        }

    # --- Unknown shape: return raw, filtered where possible --------------- #
    return {"payroll_type": "unknown", "payroll": payroll}


def get_expense_breakdown(
    data: dict,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    **_: Any,
) -> dict:
    """Return expenses grouped by category for a period.

    Derived from expense-type transactions (present and consistently shaped in
    every persona dataset), so the breakdown is comparable across personas.

    Args:
        data: Loaded persona dataset.
        start_date: Inclusive lower bound (``YYYY-MM-DD`` or ``YYYY-MM``).
        end_date: Inclusive upper bound (``YYYY-MM-DD`` or ``YYYY-MM``).

    Returns:
        A dict with categories sorted by total spend (largest first) and the
        overall expense total for the period.
    """
    txns = data.get("transactions", [])

    groups: dict[str, dict] = {}
    for t in txns:
        if (t.get("type") or "").lower() != "expense":
            continue
        if not _in_range(t.get("date"), start_date, end_date):
            continue
        cat = t.get("category") or "Uncategorised"
        g = groups.setdefault(cat, {"category": cat, "total": 0.0, "gst_total": 0.0, "count": 0})
        g["total"] += t.get("amount", 0) or 0
        g["gst_total"] += t.get("gst_amount", 0) or 0
        g["count"] += 1

    categories = sorted(groups.values(), key=lambda g: g["total"], reverse=True)
    for g in categories:
        g["total"] = _round(g["total"])
        g["gst_total"] = _round(g["gst_total"])

    total_expenses = _round(sum(g["total"] for g in categories))

    return {
        "period": {"start_date": start_date, "end_date": end_date},
        "total_expenses": total_expenses,
        "category_count": len(categories),
        "categories": categories,
    }


# --------------------------------------------------------------------------- #
# Tool registry + dispatch
# --------------------------------------------------------------------------- #

TOOL_FUNCTIONS = {
    "get_transactions": get_transactions,
    "get_account_balance": get_account_balance,
    "get_invoices": get_invoices,
    "get_gst_summary": get_gst_summary,
    "get_payroll_summary": get_payroll_summary,
    "get_expense_breakdown": get_expense_breakdown,
}

# Anthropic tool schemas. Property names match each function's keyword
# arguments so dispatch can call ``func(data, **tool_input)`` directly.
TOOL_DEFINITIONS: list[dict] = [
    {
        "name": "get_transactions",
        "description": (
            "Retrieve individual financial transactions, optionally filtered by "
            "date range, category, or type (income/expense). Use this to answer "
            "questions about specific spending or income, or to inspect activity "
            "in a period. All amounts are in AUD; each transaction carries its "
            "GST component. Dates are Australian financial-year context "
            "(1 Jul - 30 Jun)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Inclusive start date, YYYY-MM-DD or YYYY-MM.",
                },
                "end_date": {
                    "type": "string",
                    "description": "Inclusive end date, YYYY-MM-DD or YYYY-MM.",
                },
                "category": {
                    "type": "string",
                    "description": "Case-insensitive substring match on the category (e.g. 'rent', 'wages').",
                },
                "transaction_type": {
                    "type": "string",
                    "enum": ["income", "expense", "note"],
                    "description": "Filter to income or expense transactions.",
                },
            },
        },
    },
    {
        "name": "get_account_balance",
        "description": (
            "Retrieve the business cheque-account balance for a month: opening "
            "balance, total income, total expenses, and closing balance. Use "
            "this for cash-flow and liquidity questions. Omit 'month' to see "
            "every month in the dataset."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "month": {
                    "type": "string",
                    "description": "Month to report, e.g. 'March', 'March 2025', or '2025-03'.",
                },
            },
        },
    },
    {
        "name": "get_invoices",
        "description": (
            "Retrieve invoices, optionally filtered by status: 'paid', "
            "'outstanding' (within terms), or 'overdue' (past due date). Returns "
            "a status breakdown and totals inc GST, so you can answer 'how much "
            "am I owed and how overdue is it?'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["paid", "outstanding", "overdue"],
                    "description": "Invoice status to filter by.",
                },
            },
        },
    },
    {
        "name": "get_gst_summary",
        "description": (
            "Retrieve the BAS-ready GST summary (GST collected on sales, GST "
            "paid on purchases, net GST payable) for a quarter. Australian BAS "
            "quarters: Q1 Jul-Sep, Q2 Oct-Dec, Q3 Jan-Mar, Q4 Apr-Jun. Accepts "
            "'Q3', 'Q4', 'Jan-Mar', 'Apr-Jun'. Omit 'quarter' to see all "
            "available quarters."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "quarter": {
                    "type": "string",
                    "description": "BAS quarter, e.g. 'Q3', 'Q4', 'Jan-Mar', 'Apr-Jun'.",
                },
            },
        },
    },
    {
        "name": "get_payroll_summary",
        "description": (
            "Retrieve payroll totals for a period. Depending on the business "
            "this returns employee wages plus superannuation, or subcontractor "
            "payments (which have no PAYG/super and may be TPAR-reportable). If "
            "the business has no payroll (e.g. a solo operator) this is stated "
            "explicitly. Omit 'period' to see all periods."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "description": "Month to report, e.g. 'March', 'March 2025', or '2025-03'.",
                },
            },
        },
    },
    {
        "name": "get_expense_breakdown",
        "description": (
            "Retrieve total expenses grouped by category for a period, sorted "
            "largest first, with GST per category and an overall total. Use this "
            "for 'where is my money going?' and 'what was my biggest expense?' "
            "questions. Omit dates to cover the whole dataset."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Inclusive start date, YYYY-MM-DD or YYYY-MM.",
                },
                "end_date": {
                    "type": "string",
                    "description": "Inclusive end date, YYYY-MM-DD or YYYY-MM.",
                },
            },
        },
    },
]


def execute_tool(name: str, tool_input: dict, data: dict) -> dict:
    """Dispatch a Claude tool-use request to the matching function.

    Returns a structured dict. On an unknown tool name or a bad-shaped input,
    returns a dict with an ``error`` key rather than raising, so the caller can
    surface it to Claude as a tool-result error.
    """
    func = TOOL_FUNCTIONS.get(name)
    if func is None:
        return {"error": f"Unknown tool '{name}'."}
    try:
        return func(data, **(tool_input or {}))
    except TypeError as exc:
        return {"error": f"Bad arguments for tool '{name}': {exc}", "received": tool_input}