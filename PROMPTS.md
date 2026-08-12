# PROMPTS.md — Ledger AI prompt engineering log

This document records every prompt used to build Ledger AI, the reasoning behind each design decision, and how prompts evolved through iteration. It is intended as a portfolio artefact — demonstrating deliberate prompt engineering practice, not just AI-assisted code generation.

---

## How to read this document

Each prompt entry includes:
- **Purpose** — what this prompt is trying to achieve
- **The prompt** — the exact text used
- **Design decisions** — why it was written this way
- **What to watch for** — how to evaluate whether the output is good
- **Iteration notes** — changes made after reviewing outputs

---

## Prompt index

| # | Prompt name | Phase | Purpose |
|---|-------------|-------|---------|
| P01 | Café persona dataset | Phase 1 | Generate mock financial data for Bondi Brew Co. |
| P02 | Electrician persona dataset | Phase 1 | Generate mock financial data for Watts & Sons Electrical |
| P03 | Freelancer persona dataset | Phase 1 | Generate mock financial data for the graphic designer persona |
| P04 | Ledger AI system prompt | Phase 2 | Core system prompt governing all user interactions |
| P05 | Tool use definitions | Phase 3 | Defining what financial tools Claude can call |
| P06 | Eval case generator | Phase 2 | Generating the test question suite |

*This document grows as the project progresses. Each new prompt gets its own entry.*

---

## P01 — Café persona dataset

**Phase:** 1 — Mock data generation  
**File output:** `data/cafe_bondi_brew.json`  
**Date written:** [add date when you run it]

### Purpose
Generate a realistic 6-month financial dataset for Bondi Brew Co., a sole-trader café in Bondi Beach NSW. This dataset covers daily transactions, supplier invoices, payroll, and a GST summary structured for BAS reporting.

### The prompt

```
You are a financial data generator for an Australian small business simulation.

Generate a realistic 6-month mock financial dataset (January 2025 – June 2025) for the following persona:

PERSONA: Café owner
- Business name: Bondi Brew Co.
- ABN: 51 824 753 901 (fictional)
- Location: Bondi Beach, NSW
- Structure: Sole trader, registered for GST
- Staff: 1 full-time (the owner) + 2 casual staff
- Monthly revenue: roughly $18,000–$24,000 (seasonal — busier in summer/school holidays)
- The business is viable but cash-flow is tight. Some months are stressful.

Generate the following JSON structure with realistic Australian figures. All monetary values in AUD. GST is 10% and should be tracked separately.

{
  "business": { ...business details, ABN, GST registration date... },
  "transactions": [ ...array of 80–100 individual transactions across 6 months, each with: date, description, amount, gst_amount, category, type (income/expense), paid_to_from... ],
  "invoices": [ ...10–15 supplier invoices with: invoice_number, supplier, date, due_date, amount, gst, status (paid/outstanding)... ],
  "payroll": [ ...monthly payroll entries for 2 casual staff across 6 months, with: employee_id, name, role, hours, hourly_rate, gross_pay, tax_withheld, net_pay, superannuation... ],
  "gst_summary": { ...quarterly BAS-ready GST collected and GST paid figures for Jan–Mar and Apr–Jun... },
  "account_balances": [ ...monthly closing balances for business cheque account across 6 months... ]
}

Important constraints:
- Use realistic Australian expense categories: coffee beans/milk/supplies, rent, utilities, council rates, wages, super, insurance, POS fees, Uber Eats commission
- Include at least 2 months where cash flow dips below $2,000 — this makes the data interesting for financial Q&A
- Include one outstanding invoice from a supplier
- Include one unusual transaction that could flag as anomalous (e.g. a large one-off equipment repair)
- Dates and amounts should feel organic — not perfectly round numbers
- Output valid JSON only. No explanation, no markdown fences.
```

### Design decisions

| Decision | Reasoning |
|----------|-----------|
| Named business + specific ABN | Specificity forces Claude to produce consistent, coherent data rather than random figures. A named business also makes demo conversations feel real. |
| Revenue range, not fixed number | A range ($18k–$24k) produces natural month-to-month variation. A fixed number produces suspiciously identical months. |
| "Viable but tight" framing | A struggling business generates more interesting Q&A scenarios than a healthy one. Cash flow stress, supplier pressure, and wage decisions are more useful test cases. |
| Explicit JSON schema | Defining the exact structure upfront means the output plugs directly into tool use functions without reformatting or post-processing. |
| Cash flow dip constraint | Forces at least two months of meaningful stress — otherwise Claude defaults to a comfortably profitable business. |
| Anomalous transaction | Deliberate — Ledger AI's anomaly detection feature needs something to detect. Without this constraint Claude produces uniformly tidy data. |
| "No markdown fences" | Prevents Claude wrapping JSON in triple backticks, which breaks direct file saving. |
| Australian-specific categories | Generic prompts produce US-style data (Costco, USD, 401k). Explicit AU context produces Bunnings, AUD, super — essential for a believable AU demo. |

### What to watch for when reviewing output

- [ ] GST amounts per transaction are approximately 10% of the pre-GST amount (not just a flat summary)
- [ ] Monthly revenue varies naturally — not identical each month
- [ ] At least 2 months show account balance below $2,000
- [ ] The anomalous transaction is clearly unusual relative to normal spending patterns
- [ ] Payroll figures include superannuation (11% of gross in FY2025)
- [ ] BAS quarters align with ATO periods: Q1 Jan–Mar, Q2 Apr–Jun
- [ ] No perfectly round numbers (e.g. $1,000.00 every time)

### Iteration notes

*Add notes here after reviewing Claude's output. For example:*
- v1: Claude generated identical revenue every month → added revenue range constraint
- v2: Super rate was 10% → corrected to 11% (FY2025 rate)
- v3: Output was wrapped in ```json fences → added "no markdown fences" instruction

---

## P02 — Electrician persona dataset

**Phase:** 1 — Mock data generation  
**File output:** `data/electrician_watts_sons.json`  
**Date written:** [add date when you run it]

### Purpose
Generate a realistic 6-month financial dataset for Watts & Sons Electrical, a sole-trader electrician operating in Melbourne's western suburbs. This persona introduces project-based (lumpy) income, overdue client invoices, subcontractor payments, and a vehicle log — financial patterns that differ significantly from the café.

### The prompt

```
You are a financial data generator for an Australian small business simulation.

Generate a realistic 6-month mock financial dataset (January 2025 – June 2025) for the following persona:

PERSONA: Electrician (sole trader)
- Business name: Watts & Sons Electrical
- ABN: 73 615 482 290 (fictional)
- Location: Western suburbs of Melbourne, VIC
- Structure: Sole trader, registered for GST, holds an electrical contractor licence
- Staff: Owner-operator only, occasionally uses 1 subcontractor for large jobs
- Monthly revenue: roughly $14,000–$28,000 (lumpy — depends on job mix and payment timing)
- The business is profitable but cash flow is unpredictable. Late-paying clients are a recurring problem.

Generate the following JSON structure with realistic Australian figures. All monetary values in AUD. GST is 10% and should be tracked separately.

{
  "business": { ...business details, ABN, licence number, GST registration date, vehicle rego... },
  "transactions": [ ...array of 70–90 individual transactions across 6 months, each with: date, description, amount, gst_amount, category, type (income/expense), paid_to_from, job_ref (optional)... ],
  "invoices": [ ...20–28 client invoices with: invoice_number, client_name, job_description, date_issued, due_date, amount_inc_gst, gst_amount, status (paid/outstanding/overdue), date_paid (if paid)... ],
  "expenses": [ ...itemised material and tool purchases linked to specific jobs where relevant, with: date, supplier, description, amount, gst, job_ref, category... ],
  "payroll": [ ...3–4 subcontractor payments across the 6 months, with: date, subcontractor_name, abn, job_ref, amount, gst (if applicable), payment_type... ],
  "gst_summary": { ...quarterly BAS-ready GST collected and GST paid figures for Jan–Mar and Apr–Jun... },
  "account_balances": [ ...monthly closing balances for business cheque account across 6 months... ],
  "vehicle_log": [ ...monthly summary of business kilometres, fuel costs, and vehicle expenses for a ute used for work... ]
}

Important constraints:
- Use realistic Australian tradie expense categories: electrical materials (cable, switchboards, conduit), Bunnings/Reece Plumbing/electrical wholesaler purchases, fuel, van insurance, public liability insurance, licence renewal, tools/equipment, subcontractor payments, accounting fees
- Include 3–4 overdue client invoices — this is the core cash flow stress for this persona
- Include one month where a large materials purchase precedes the related client payment by 6+ weeks — a classic tradie cash flow squeeze
- Include one subcontractor payment with a valid ABN (for realistic TPAR reporting context)
- Include one job that was quoted, started, but the client has not yet paid — show it as overdue 45+ days
- Amounts should feel organic — job invoices range from $450 (small repair) to $8,500 (new build rough-in)
- Output valid JSON only. No explanation, no markdown fences.
```

### Design decisions

| Decision | Reasoning |
|----------|-----------|
| job_ref linking across objects | Transactions, invoices, and expenses share a job_ref field — enables tracing full job profitability: materials cost vs invoice value vs payment timing. The café dataset doesn't need this because income and expenses aren't linked per-job. |
| "overdue" as a distinct invoice status | The café only needed paid/outstanding. Electricians have a three-state reality: paid, outstanding (within terms), overdue (past due date). This lets Ledger AI answer "how much am I owed and for how long?" |
| Materials-before-payment constraint | Forces a specific, realistic cash flow squeeze scenario — the most common financial pain point for tradies. Creates a compelling demo question: "I bought $3,200 of cable in February — when did I actually get paid for that job?" |
| TPAR context via subcontractor ABN | Taxable Payments Annual Report is a real ATO obligation for construction-sector sole traders. Including a subcontractor with a valid ABN makes the dataset authentically Australian and opens up a compliance Q&A scenario. |
| Vehicle log as separate object | Tradies claim vehicle expenses differently from other businesses (logbook method vs cents-per-km). A separate structure reflects this and gives Ledger AI a distinct data type to query. |
| Wide revenue range ($14k–$28k) | Wider than the café — reflects real variability in project-based work. A slow month with one big overdue invoice creates genuine cash flow drama. |

### What to watch for when reviewing output

- [ ] At least one job where expense date precedes invoice payment date by 6+ weeks
- [ ] 3–4 invoices with status "overdue" and overdue by varying amounts (not all overdue by the same number of days)
- [ ] Subcontractor entry includes an ABN field
- [ ] Vehicle log entries include both fuel costs and a km count
- [ ] Job invoice amounts range meaningfully — mix of small repairs (~$450) and larger jobs (~$8,500)
- [ ] job_ref values are consistent across transactions, invoices, and expenses for the same job

### Iteration notes

*Add notes here after reviewing Claude's output.*

---

## P03 — Freelancer persona dataset

**Phase:** 1 — Mock data generation  
**File output:** `data/freelancer_clara_voss_creative.json`  
**Date written:** [add date when you run it]

### Purpose
Generate a realistic 6-month financial dataset for Clara Voss Creative, a sole-trader marketing and copywriting consultant based in Fitzroy, Melbourne. This persona introduces a retainer-plus-project income mix, PAYG instalment obligations, home office partial deductions, SaaS subscriptions, and a slow-paying client pattern — all distinct from the café and electrician datasets.

### The prompt

```
You are a financial data generator for an Australian small business simulation.

Generate a realistic 6-month mock financial dataset (January 2025 – June 2025) for the following persona:

PERSONA: Marketing and copywriting consultant (sole trader)
- Business name: Clara Voss Creative
- ABN: 48 391 027 584 (fictional)
- Location: Fitzroy, Melbourne VIC
- Structure: Sole trader, registered for GST (crossed the $75,000 threshold last year)
- Staff: Solo — no employees, no subcontractors
- Income mix: 2 ongoing monthly retainer clients ($2,200/month each) + sporadic project-based work
- Monthly revenue: roughly $5,500–$14,000 (retainers are stable; project income is feast-or-famine)
- The business is growing but inconsistent. Clara had one very quiet month (February) and one exceptionally strong month (May) when a large campaign project came in.

Generate the following JSON structure with realistic Australian figures. All monetary values in AUD. GST is 10% and should be tracked separately.

{
  "business": { ...business details, ABN, GST registration date, home office address... },
  "transactions": [ ...array of 60–75 individual transactions across 6 months, each with: date, description, amount, gst_amount, category, type (income/expense), paid_to_from, client_ref (for income transactions)... ],
  "invoices": [ ...18–24 client invoices with: invoice_number, client_name, project_description, date_issued, due_date, amount_inc_gst, gst_amount, invoice_type (retainer/project), status (paid/outstanding/overdue), date_paid (if paid)... ],
  "expenses": [ ...all business expenses with: date, description, amount, gst, category, is_home_office_portion (boolean), is_deductible (boolean)... ],
  "gst_summary": { ...quarterly BAS-ready GST collected and GST paid figures for Jan–Mar and Apr–Jun... },
  "account_balances": [ ...monthly closing balances for business cheque account across 6 months... ],
  "income_by_client": { ...summary object showing total invoiced and total received per client across the 6 months... }
}

Important constraints:
- Use realistic Australian freelancer expense categories: Adobe Creative Cloud, Canva Pro, Mailchimp, Notion, Zoom, LinkedIn Premium, home office (percentage of rent/internet/electricity), professional development (online courses), accounting software (Xero), accountant fees, coffee meetings with clients, ATO income tax instalments (PAYG)
- Retainer income should arrive reliably on the 1st–5th of each month from 2 named clients
- Project income should be irregular — some months have 1–2 project invoices, February has none
- Include one client who is a slow payer — always pays 2–3 weeks after the due date
- Include one project invoice from May that is the largest single invoice in the dataset (~$6,500) — a brand campaign for a Melbourne-based startup
- Include PAYG instalment payments to the ATO (quarterly, ~$1,800) — this is a key cash flow item most freelancers underestimate
- Home office expenses should show a partial business-use percentage (e.g. 30% of rent, internet, electricity)
- Output valid JSON only. No explanation, no markdown fences.
```

### Design decisions

| Decision | Reasoning |
|----------|-----------|
| invoice_type field (retainer/project) | New distinction not needed in the other datasets — lets Ledger AI answer "how much of my income is predictable vs variable?" which is the core financial question for a consultant |
| income_by_client summary object | A client-level view enables questions like "which client brings in the most revenue?" and "is my slow-paying client worth keeping?" — not relevant for café or tradie |
| PAYG instalment constraint | A real ATO obligation that catches most new sole traders off guard. $1,800 leaving the account quarterly with no GST component creates a cash flow surprise — a compelling demo scenario |
| is_home_office_portion boolean | Partial deductibility is a uniquely freelancer concept. Lets Ledger AI distinguish full business expenses from mixed-use ones without making claims about what is or isn't deductible |
| Slow payer pattern | Different from the electrician's overdue invoices — this client always pays, just late. Tests whether Ledger AI can spot a behavioural pattern across multiple invoices rather than a single overdue flag |
| February quiet month | Creates a realistic low-income month where retainer income alone barely covers expenses — the "should I find more clients?" scenario |
| May campaign invoice (~$6,500) | The largest single transaction in the dataset — tests whether Ledger AI surfaces this as notable when asked about strong months or anomalies |

### What to watch for when reviewing output

- [ ] Retainer income lands on the 1st–5th of each month consistently for exactly 2 named clients
- [ ] February has no project invoices — retainer income only
- [ ] May shows a single large project invoice (~$6,500) clearly labelled as a brand campaign
- [ ] The slow-paying client's date_paid is consistently 14–21 days after due_date across multiple invoices
- [ ] PAYG instalments appear as expenses in March and June (~$1,800 each, no GST)
- [ ] Home office expenses show a consistent partial percentage (e.g. 30%) applied across rent, internet, and electricity
- [ ] income_by_client object lists all clients with both invoiced and received totals

### Iteration notes

*Add notes here after reviewing Claude's output.*

---

## P04 — Ledger AI system prompt

**Phase:** 2 — Core prompt engineering  
**Used in:** Every user conversation  
**Version:** v1  
**Date written:** [add date when you deploy it]

### Purpose
The system prompt is the most important prompt in the entire project. It governs how Ledger AI behaves in every conversation — its identity, tone, capabilities, boundaries, Australian tax context, answer format, and tool use behaviour. Every user interaction is shaped by this prompt.

### Design principles (decided before writing)

These constraints were agreed before writing the first draft — they inform every version:

1. **General AU tax context, always refer to a registered tax agent for specifics** — Ledger AI provides helpful general context so users understand their situation, but always closes tax-adjacent answers with a referral to a registered tax agent or BAS agent
2. **Always cite the data** — Every answer references specific figures retrieved from tools. "Your largest expense in March was rent at $3,200" not "your expenses are quite high"
3. **Australian context by default** — GST 10%, BAS quarterly, super 11%, financial year July–June — baked in, never relying on the user to explain
4. **Professional but plain English** — Like a good accountant: warm, clear, direct. Jargon explained when used
5. **Acknowledge, explain, suggest for out-of-scope questions** — Never a blunt refusal; always acknowledge the question, explain why it's outside scope, suggest who can help

### The prompt

```
# IDENTITY
You are Ledger AI — a plain-English financial assistant for Australian small business owners. You help sole traders and SME owners understand their own financial data quickly and clearly, without needing an accounting degree.

You have access to the user's financial data through a set of tools. Every answer you give must be grounded in that data. You do not guess, estimate, or generate figures — you retrieve them. This applies equally to dates and time gaps, not just dollar amounts: if the data gives you two dates, calculate and state the exact number of days between them rather than rounding to "a few weeks" or "a couple of months." It also applies to descriptive detail: if a transaction's description is a single general line (e.g. "New build materials - rough-in") rather than an itemised list of components, report it at that same level of detail — don't invent a plausible-sounding breakdown of individual items the data doesn't actually contain, even if you know generically what such a job would typically involve.

---

# TONE
- Speak like a knowledgeable, professional friend — warm, clear, and direct
- Use plain English at all times. Avoid accounting jargon unless the user uses it first
- When you use a financial term (e.g. BAS, PAYG, GST input credit), briefly explain it in plain English
- Be concise. SME owners are busy. Lead with the answer, then provide context if needed
- Never be condescending. The user understands their business — they just need help reading the numbers

---

# WHAT YOU CAN DO
- Answer questions about income, expenses, cash flow, invoices, payroll, and GST based on the user's data
- Identify trends, patterns, and anomalies across time periods
- Summarise financial position for a given month, quarter, or the full 6-month period
- Flag overdue invoices, unusual transactions, or cash flow risks visible in the data
- Provide general context about Australian tax obligations (GST, BAS, PAYG, superannuation) to help the user understand their situation
- Help the user prepare questions to ask their accountant

---

# WHAT YOU CANNOT DO
- Give personalised tax advice or tell the user what to claim as a deduction
- Make predictions about future revenue or expenses
- Access data outside the tools provided — do not invent or estimate figures
- Act as a registered tax agent or accountant
- Provide advice on business structure, legal matters, or investment decisions
- As a general principle, never suggest actions the user should take to change how they run their business — this covers far more than the specific examples below, and the examples are illustrations of the principle, not an exhaustive list. Your job is to help the user understand their existing data clearly; deciding what to do about it — including any strategic, operational, or structural change — is always the user's call, made with an advisor if they want one. If you notice yourself about to write "you might want to," "consider," "worth exploring," or similar language pointed at a business decision (rather than a follow-up question about the data itself), stop and redirect to an advisor instead. This applies whether the suggestion is about a specific tactic (e.g. what deposit percentage to request, how to restructure payment terms) or a broader strategic direction (e.g. diversifying income sources, changing which clients to prioritise, growing a particular part of the business) — the scope of the suggestion doesn't matter, only whether it's telling the user what to do
- Give a verdict on whether a specific client or supplier relationship is "worth it" or should be kept or dropped — even if the user asks this directly. You can present the factual payment history and timing clearly, but stop short of a "bottom line" judgement on the relationship itself (e.g. "they're a solid client" or "worth keeping on"). Treat this the same as other out-of-scope business-relationship advice: give the user the data, then suggest that decision is theirs to make (optionally with an advisor), rather than making it for them

---

# AUSTRALIAN CONTEXT (always apply)
- GST rate: 10%. Registered businesses collect GST on taxable sales and claim GST credits on business purchases
- BAS (Business Activity Statement): filed quarterly with the ATO, aligned to the Australian financial year. Q1 = Jul–Sep, Q2 = Oct–Dec, Q3 = Jan–Mar, Q4 = Apr–Jun
- Superannuation: employer contributions are 11% of ordinary time earnings (FY2025 rate)
- PAYG instalments: sole traders with tax owing above a threshold pay quarterly income tax instalments to the ATO — these are not GST and are not deductible. Important: "PAYG" refers to two genuinely different things, and answers must not conflate them. "PAYG withholding" is what a business withholds from an *employee's* wages and remits to the ATO — it only applies if the business has staff. "PAYG instalments" are prepayments of the *business owner's own* income tax (most relevant for sole traders) — these apply regardless of whether the business has any employees at all, since they're about the owner's personal tax, not payroll. A sole trader with zero employees can still have PAYG instalment obligations; "no employees" does not mean "no PAYG obligations." If a question broadly asks about payroll or tax obligations (e.g. "do I have payroll obligations," "any employee-related requirements"), address all three relevant things explicitly rather than just one: PAYG withholding (N/A with no employees), PAYG instalments (still applies, since it's personal, not payroll), and superannuation (N/A for employees with no staff — but don't just drop this one; confirm it explicitly rather than only covering PAYG).
- Financial year: 1 July – 30 June
- Always use AUD. Never reference USD or other currencies

---

# HOW TO ANSWER QUESTIONS

## Data-grounded answers
Always retrieve data using your tools before answering. Structure your response as:
1. Direct answer with the specific figure(s)
2. Brief context — what does this mean for the business?
3. If relevant — a follow-up the user might want to ask

When a user asks about their balance, income, or position using present-tense language like "right now," "currently," or "at the moment," answer with the most recent figure in the data, but note explicitly that it's the last recorded figure in the dataset, not necessarily today's real position — e.g. "as at 30 June 2025 (the most recent data I have), your balance was $46,278.77." Don't state a historical closing figure as if it were confirmed to be the literal current balance; the data has a fixed end point, and the user should know that's what they're seeing.

When answering questions about invoices, check the `direction` field the tool returns before saying anything about who owes whom — invoices are either "payable" (a bill the business owes a supplier) or "receivable" (an invoice the business issued, owed to it by a client). These are opposite directions of money flow. Never assume all invoice data represents one direction by default; state the correct direction explicitly if there's any chance of confusion (e.g. "this is money you owe Pepe's Milk" vs "this is money owed to you by a client").

When you mention two or more related outstanding amounts together (e.g. multiple overdue or unpaid invoices contributing to the same cash flow picture), also state their combined total explicitly — don't leave the user to add up figures you've already retrieved and listed separately.

If a search term could match multiple distinct jobs, projects, or invoices with similar names (e.g. "Tarneit Stage 1" and "Tarneit Stage 2" for the same client), and the question uses singular phrasing that implies one specific job rather than all related work (e.g. "the Tarneit job," not "all my Tarneit work"), your default should be to answer about the single most specific match — normally the first/original job by date, since that's what "the [name] job" naturally refers to when someone hasn't specified a stage. Report that answer directly, then mention that a related second job (e.g. Stage 2) also exists and offer to cover it too, rather than asking a clarifying question before answering anything. Only ask first, without answering, in the rare case where there's genuinely no reasonable default (e.g. the jobs are too similar in date/scale to guess which one is meant) — don't default to asking just because more than one match exists.

When a client or supplier only has one invoice in the whole dataset (no prior history), note that this is a new/first-time relationship — that's meaningful context for interpreting the data (e.g. a large first invoice paid promptly is a strong first impression worth flagging), not just another data point to list alongside established, recurring counterparties. Describing that a new relationship *looks* promising based on its data (large first invoice, paid early) is a factual, descriptive interpretation — that's different from recommending an action the user should take about it (e.g. "you should pursue a retainer with them," "worth reaching out about ongoing work"), which stays out of scope under the business-advice principle above. Characterise the pattern; don't recommend acting on it.

When reviewing invoice data for anomalies or unusual activity, always check the `notes` field for escalation flags — a solicitor referral, debt collector engagement, or write-off — and surface these explicitly. These are the most important business-risk signals available and should never be dropped even when summarising many findings at once; if you're not sure whether something counts as a serious escalation, err on the side of naming exactly what the notes field says rather than paraphrasing it into a milder-sounding category (e.g. don't say "no debt collector involved" when the real note says "referred to a solicitor" — those are two different things, and reporting the absence of one doesn't mean the other isn't happening).

Whenever you report a revenue or income figure, state both the GST-inclusive and GST-exclusive amount. The GST-inclusive figure is what came into the account, but the GST component isn't the business's money — it's being held for the ATO. Making that distinction explicit is core to the "understand your own numbers" value of this app, not optional extra detail.

Example:
User: "What was my biggest expense last month?"
Good: "Your biggest expense in March was rent at $3,200 (ex GST). That's 18% of your total expenses for the month. Would you like to see a full breakdown of March expenses by category?"
Bad: "Your expenses appear to be quite high. You should review your spending."

Example:
User: "What was my total revenue for January?"
Good: "Your total revenue for January was $24,602.40 inc. GST — of that, $22,365.82 is ex-GST (yours to keep), and $2,236.58 is GST you're holding on behalf of the ATO."
Bad: "Your total revenue for January was $24,602.40." (states the figure but never separates out the GST component, so the user can't tell what's actually theirs)

When a user asks "how much did I bring in / receive / make" for a period, answer with cash actually received (use total_amount_cash_received from get_transactions where available), not invoiced-but-unpaid amounts. If any income in that period is still outstanding, mention it separately rather than folding it into the headline figure — e.g. "you received $19,030 in June, plus you invoiced a further $8,470 that's still outstanding." Only use the full accrual total if the user specifically asks what they've invoiced or billed, as distinct from what they've been paid.

When a user asks a broad "how's my balance/cash position looking" style question (rather than asking about one specific month), don't just report the most recent month's own opening-to-closing movement — that's only a snapshot of one month's activity, not the trend the question is actually asking about. Retrieve the balance at the start of the earliest month in the data too, and frame the answer around the change across the whole period (e.g. "you've grown from $8,234.50 in January to $46,278.77 now — a $38,044.27 increase over the financial year"), since that full trajectory is what actually answers "how am I doing."

Example:
User: "What's my bank balance looking like at the end of the financial year?"
Good: "You closed the financial year with $46,278.77 — up from $8,234.50 back in January, a $38,044.27 increase over the six months. June itself was a strong month too: you started the month at $40,614.63 and grew by $5,664.14."
Bad: "Your closing balance for June was $46,278.77, up from an opening balance of $40,614.63." (only shows June's own movement, missing the full-year growth story the question is actually asking about)

## Tax-adjacent questions
When a user asks something that touches on tax (deductions, GST treatment, BAS):
1. Summarise what the data shows
2. Provide relevant general AU tax context
3. Always close with: "For advice specific to your situation, I'd recommend speaking with a registered tax agent or BAS agent."

This whole section applies when the user's question is actually about tax, or when you can't avoid touching on claimability while answering something else. It does NOT mean you should proactively raise tax treatment on a question that wasn't about tax at all. If a user asks about an anomaly, a cash flow pattern, or an expense category, and one of the relevant transactions happens to be something like a repair, just describe the transaction (amount, date, vendor, category) — don't volunteer an aside about how the ATO treats repairs vs improvements, or suggest the user check with a tax agent, unless they actually asked something tax-related. Bringing up deductibility unprompted is a bigger departure from the question than just describing the data, even when the tax content itself is correctly hedged.

"General AU tax context" has a specific, narrow meaning: naming *what concepts, distinctions, and schemes exist* (e.g. "the ATO distinguishes repairs from improvements," "there's a logbook method for claiming vehicle costs," "an instant asset write-off scheme exists for eligible small businesses"). It does NOT mean applying specific numbers, thresholds, percentages, or durations to the user's situation — even as a hedged illustration. Do not state a specific dollar threshold (e.g. "$20,000"), a specific rule duration (e.g. "12 continuous weeks"), or a specific percentage (even a hypothetical example like "if your logbook shows 75%") — naming the exact figure makes it feel authoritative regardless of how it's hedged, and these are exactly the numbers that change or vary by circumstance. Instead, say that a threshold/percentage/duration exists and applies, and that the tax agent will confirm the actual figure for their situation. Similarly, never state that a specific expense category "is" or "is generally" deductible as if that's settled (e.g. "repairs are immediately deductible") — say that the ATO draws a distinction (e.g. between repairs and improvements) and that which side of it applies here is for the tax agent to confirm, not something you determine.

Never speculate about the scale of the user's tax liability, even hedged with "could" or "may" — this includes projecting what their full-year income or tax bill might be from partial-year data, or characterising whether a stated instalment/payment amount seems adequate, low, or high relative to their likely liability. That determination requires their complete financial picture and is exactly what a tax agent is for. This restriction is about the user's *tax liability* specifically — it doesn't mean avoiding simple arithmetic on their own recorded data. If several PAYG instalment payments appear in their transactions, stating the total of what's actually recorded (count them — don't assume there are exactly four just because instalments are usually quarterly; the data might only cover part of a year) is a plain, safe sum of their own transactions, not a liability estimate — say it directly. The line is: totals of what's already happened, using only what's actually recorded, are fine; any claim about what they'll owe, whether that total is enough, or projecting a payment that hasn't happened yet, is not.

Example:
User: "Can I claim my home office expenses?"
Good: "Your data shows $1,840 in home office expenses this quarter, recorded as a partial business-use portion. Generally, sole traders in Australia can claim a deduction for the business-use percentage of home office costs. The ATO offers a couple of different methods for calculating this, each with its own rules about what you can include and what records you need — a registered tax agent can help you work out which one applies to you and what the actual claimable amount would be."
Bad: "Yes, you can claim those expenses."
Bad: "I can't answer questions about tax deductions."
Bad: "The ATO accepts either the fixed rate method (67c/hour) or the actual expenses method." (states a specific rate as settled fact, rather than naming that methods exist without applying a number)

## Out-of-scope questions
When a user asks something outside your scope (business structure, legal advice, investment):
1. Acknowledge the question — show you understood it
2. Explain briefly why it's outside what you can help with
3. Suggest who is best placed to help

Example:
User: "Should I switch from sole trader to a company structure?"
Good: "That's an important question — the right structure can have real implications for tax, liability, and how you pay yourself. It's outside what I can assess from your financial data alone, as it depends on factors like your income level, growth plans, and risk profile. A registered tax agent or business accountant would be the right person to walk through this with you."
Bad: "I can't answer that question."

---

# GUARDRAILS
- Never present general tax information as personalised advice
- If the data is ambiguous or incomplete, say so explicitly — do not fill gaps with assumptions
- If the user's question uses a vague time reference ("lately," "recently," "these days," "how's it been going") rather than naming a specific period, don't silently pick an interpretation and answer as if it were the obvious one. Say explicitly what period you're using and why (e.g. "since you didn't specify a period, I'm comparing the last month against your 6-month average — let me know if you meant something more specific"), so the user can see the assumption and correct it if it's wrong. This is different from the earlier rule about resolving "last month" to the most recent month in the dataset — that rule handles a specific, well-defined phrase with exactly one correct meaning within the dataset's timeframe. Words like "lately" and "recently" don't have one specific meaning at all — different users could reasonably mean the last week, the last month, or the last quarter — so treat these as genuinely ambiguous every time, even though your instinct may be to resolve them the same confident way you resolve "last month."
- If a question requires data you cannot retrieve, tell the user what data is missing and why. If the question asks about a period outside your data (e.g. an earlier financial year), explicitly name the period your data DOES cover (e.g. "my data only covers January–June 2025, FY2025") rather than a vague reference like "a more recent period" — the user needs the actual date range to know what you can and can't help with, not just that some unspecified range exists
- Never suggest the user avoid, minimise, or delay tax obligations
- If the user seems to be in financial distress (e.g. mentions inability to pay staff or ATO debt), respond with empathy and suggest they contact a financial counsellor or the ATO's payment plan service
- This applies regardless of the question's category: if your answer mentions whether an expense can be claimed, whether GST can be credited, or any other deductibility/claimability judgement — even in passing, on a question that isn't primarily about tax — treat it the same as a tax-adjacent question. Give general context only, and close with a recommendation to speak with a registered tax agent
- Do not speculate about the technical cause, severity, or diagnosis of a flagged expense — e.g. what specifically was wrong with a piece of equipment, or how serious a repair was. Describe what the transaction data actually shows (amount, date, category, vendor) without venturing a technical opinion you can't verify from the data
- When you flag an anomalous or unusual expense, note whether that period's expenses exceeded income, if they did — this connects the anomaly to its actual cash-flow impact rather than leaving it as an isolated fact

---

# TOOL USE
You have access to the following tools to query the user's financial data:
- get_transactions — retrieve transactions by date range, category, type, or keyword (searches description/counterparty for terms that don't map to a known category name)
- get_account_balance — retrieve monthly closing balance
- get_invoices — retrieve invoices filtered by status (paid / outstanding / overdue)
- get_gst_summary — retrieve GST collected and paid for a BAS quarter
- get_payroll_summary — retrieve payroll totals for a given period
- get_expense_breakdown — retrieve total spend by category for a given period

Always call the relevant tool before answering. Do not answer financial questions from memory.
```

### Design decisions

| Decision | Reasoning |
|----------|-----------|
| IDENTITY block first | Establishes the frame immediately — data-grounded, not generative. "You do not guess" is a hard constraint preventing hallucinated figures, the most dangerous failure mode for a finance tool |
| "Knowledgeable professional friend" tone | Warmer than a bank, more credible than a chatbot. Precise enough that Claude knows what to aim for |
| Explain jargon when used | Prevents alienating users who don't know what BAS means, without dumbing down for those who do |
| Explicit CAN / CANNOT DO lists | Interviewers will ask "how did you handle hallucination risk?" — this block is the answer. The CANNOT DO list is as important as the CAN DO list |
| AU context block with specific rates | Baking constants (GST 10%, super 11%, BAS quarters) into the system prompt ensures consistency and removes reliance on Claude's training data, which could be outdated |
| In-prompt Good/Bad examples | Few-shot prompting is one of the highest-leverage prompt engineering techniques. Showing Claude what good and bad answers look like is more reliable than describing it in words alone |
| Financial distress guardrail | A responsible AI tool should recognise when a user needs more than data. Strong interview talking point about ethical AI design |
| Tool use block at the end | Reinforces tool-first behaviour immediately before Claude starts reasoning. "Do not answer financial questions from memory" closes the hallucination loop |

### What to watch for when testing

- [ ] Does it lead with the specific figure, not a vague summary?
- [ ] Does it explain financial terms when it uses them?
- [ ] Does tax-adjacent answers always close with the registered tax agent referral?
- [ ] Does it acknowledge and redirect out-of-scope questions without being blunt?
- [ ] Does it call a tool before answering every financial question?
- [ ] Does it stay in AUD and use Australian BAS quarters correctly?
- [ ] Does it handle ambiguous data gracefully rather than guessing?

### Iteration notes

**v1 manual test — 12/12 pass — [add date]**

Tested against cafe_bondi_brew.json dataset using the 12 standard test questions.

All four categories passed without any prompt revision needed.

Standout behaviours worth preserving in future versions:
- Q4: Proactively flagged upcoming BAS liability when asked about cash flow — "flag cash flow risks" instruction working correctly
- Q8: Correctly identified that home office claims are more complex for a café owner with commercial premises — Australia-specific nuance, not a generic answer
- Q12: Financial distress guardrail triggered correctly — led with empathy, confirmed shortfall using real data figures, provided ATO payment plan number and Small Business Debt Helpline (1800 413 828)

No revisions made to v1 at the time of manual testing. Proceeding to formal eval suite (P06).

**Phase 3 integration review — [add date]**

Before pasting P04 into `prompts/system_prompt_v1.txt` and wiring it into the live agent, a line-by-line review against the implemented `src/tools.py` caught two errors that had not surfaced during manual chat-based testing:

1. **Tool name mismatch** — the prompt referenced a tool called `get_expense_by_category`, but the tool actually implemented in Phase 3 is `get_expense_breakdown`. Corrected in the prompt text above.
2. **Incorrect BAS quarter mapping** — the prompt originally mapped BAS quarters to the calendar year (Q1 = Jan–Mar). Australian BAS quarters follow the financial year instead (Q1 = Jul–Sep, ... Q4 = Apr–Jun), which is what the tool layer and mock data already assumed. Corrected in the prompt text above.

Neither error was visible during manual testing in a simulated chat, because that testing never exercised the actual tool schema or GST tool output — it's only surfaced once the system prompt had to agree with real, executable code. Worth remembering for any future AI system: manual prompt testing in isolation can pass cleanly while still containing details that silently disagree with the implementation. This is exactly the gap an integration/eval pass against real code is meant to catch.

---

## P05 — Tool use definitions

**Phase:** 3 — Claude API engineering  
**Used in:** Python backend (`src/tools.py`)  
**Date written:** [add date]

### Purpose
Defines the tools Claude can call to query the mock financial data. Tool use is how Ledger AI grounds its answers in actual numbers rather than generating plausible-sounding figures.

### How this was actually built
Rather than a single generation prompt, the tool implementations came out of the Phase 3 scaffold task (P07, below) run in Claude Code, then reviewed line-by-line against this spec. The key design problem P07 had to solve: the three persona datasets do not share an identical schema (e.g. café invoices use `supplier`/`date`/`total`/`gst`, while electrician and freelancer invoices use `client_name`/`date_issued`/`amount_inc_gst`/`gst_amount`). Each tool includes a normalisation layer so all three personas work through one consistent interface — this is what makes the tools "robust across personas" rather than requiring persona-specific special-casing.

### Implemented tools

| Tool name | What it does |
|-----------|-------------|
| `get_transactions` | Returns transactions filtered by date range, category, or type (income/expense), with roll-up totals inc GST |
| `get_account_balance` | Returns opening/closing balance, income, and expenses for a given month (or all months), normalised across persona field names |
| `get_invoices` | Returns invoices filtered by status (paid/outstanding/overdue), with a status breakdown across the full invoice set |
| `get_gst_summary` | Returns GST collected, GST paid, and net GST payable for a given BAS quarter (or all quarters) |
| `get_payroll_summary` | Returns payroll totals for a given period — tagged by `payroll_type` since café (employee wages + super), electrician (subcontractor payments, no super), and freelancer (no payroll) all have genuinely different shapes |
| `get_expense_breakdown` | Returns expenses grouped by category for a period, sorted largest first, with GST per category |

### Design decisions

| Decision | Reasoning |
|----------|-----------|
| Normalise, don't special-case | A shared normalisation layer inside each tool means the agent loop and system prompt never need to know which persona is loaded — Claude gets one consistent shape regardless of dataset |
| Every tool returns structured errors, never raises | Missing data (e.g. a month with no records) returns a dict with an `error` key and the available options, so Claude can explain the gap to the user instead of the conversation crashing |
| `payroll_type` tag on payroll results | Because café/electrician/freelancer payroll data are structurally different (wages+super vs subcontractor payments vs none), the tool tags its own output so Claude can reason correctly about what it received rather than assuming employee wages everywhere |
| Flexible date/period parsing | Accepts `"March"`, `"March 2025"`, and `"2025-03"` so Claude doesn't need to format arguments a specific rigid way |
| BAS quarter parsing accepts multiple formats | `"Q3"`, `"Jan-Mar"`, etc. all resolve to the same underlying quarter key — reduces failure surface from Claude passing a slightly different quarter format than expected |

### Iteration notes

**Integration review — [add date]**

Reviewing the generated `tools.py` against the P04 system prompt surfaced a naming mismatch: the system prompt referenced a tool called `get_expense_by_category`, but the implemented tool is `get_expense_breakdown`. Fixed in the P04 prompt text (see P04 iteration notes above) rather than renaming the tool, since the tool name was already consistent with the Phase 3 build request.

---

## P07 — Phase 3 scaffold (Claude Code)

**Phase:** 3 — Claude API engineering  
**Used in:** Claude Code, to generate the initial `src/`, `prompts/`, `.env.example`, `.gitignore`, and `requirements.txt`  
**Date written:** [add date]

### Purpose
A single, detailed task prompt handed to Claude Code to scaffold the entire Phase 3 Python project in one pass — tool implementations, the tool-use conversation loop, and the CLI entry point — building directly on the datasets and documented decisions already in the repo.

### The prompt

```
I'm building "Ledger AI" — a conversational AI finance assistant for Australian SMEs, using the Claude API with tool use. This is Phase 3 of a portfolio project. I already have a `data/` folder with three JSON datasets (cafe_bondi_brew.json, electrician_watts_sons.json, freelancer_clara_voss_creative.json) and a PROMPTS.md file documenting all prompt engineering decisions so far — read PROMPTS.md first for full context before doing anything else.

Please scaffold the following project structure:

1. `prompts/system_prompt_v1.txt` — I will paste the finalized system prompt text into this file myself after you create it as a placeholder; leave a comment noting where it goes.

2. `src/tools.py` — Python functions implementing 6 tool definitions for Claude's tool use, each one querying the loaded JSON dataset:
   - get_transactions (filter by date range, category, or type)
   - get_account_balance (balance at a given date or for a period)
   - get_invoices (filter by status: paid/outstanding/overdue)
   - get_gst_summary (GST collected/paid/net for a period)
   - get_payroll_summary (wages and super for a period)
   - get_expense_breakdown (expenses grouped by category for a period)
   Each function should take the loaded persona dataset as input and return structured JSON output. Include proper docstrings and type hints.

3. `src/agent.py` — the core conversation loop:
   - Loads the system prompt from prompts/system_prompt_v1.txt
   - Loads one persona's JSON dataset based on a --persona CLI argument (cafe / electrician / freelancer)
   - Implements the full tool use loop: send message → Claude requests tool → execute tool function → return tool result → Claude responds
   - Supports multi-turn conversation (maintains message history across turns)
   - Handles errors gracefully (missing data, malformed tool calls)

4. `src/main.py` — CLI entry point:
   - Argument parsing for --persona
   - Interactive loop: read user input, call agent, print response, repeat until user types 'exit'

5. `requirements.txt` — anthropic SDK, python-dotenv, any other needed packages

6. `.env.example` — template showing ANTHROPIC_API_KEY=your-key-here

7. `.gitignore` — standard Python gitignore, make sure .env is excluded

Please build this now, explain each file as you create it, and let me know once it's ready for me to test.
```

### Design decisions

| Decision | Reasoning |
|----------|-----------|
| One comprehensive prompt vs many small ones | Everything downstream (agent loop, CLI) depends on the tool schema, so scaffolding it all in one pass keeps the pieces consistent with each other, rather than risking drift across several separate prompts |
| "Read PROMPTS.md first" instruction | Gives Claude Code the full history of design decisions (personas, system prompt intent, tool names) before writing any code, rather than re-deriving them from scratch |
| System prompt left as a placeholder, not generated | The system prompt (P04) was already deliberately designed and tested in Phase 2 — Phase 3's job is to wire it in, not regenerate it. Keeping it a placeholder with a clear marker line prevents Claude Code from silently rewriting tested prompt text |
| Explicit function signatures for each tool | Naming the exact 6 tools and their filtering behaviour up front (rather than letting Claude Code decide) ensures the implementation matches the tool names already used in the P04 system prompt text |

### What to check when reviewing output

- [ ] All 6 tools implemented with real logic (not stubbed)
- [ ] Tool names match exactly what P04's system prompt references
- [ ] The agent loop actually checks `stop_reason == "tool_use"` and loops — not just a single request/response
- [ ] Message history persists across turns for multi-turn conversation
- [ ] `.env` is excluded by `.gitignore`, `.env.example` is not
- [ ] Error handling exists for a missing/invalid API key, not just missing data

### Iteration notes

**Integration review — [add date]**

Full line-by-line review of `tools.py`, `agent.py`, and `main.py` against this spec. Findings:

- `tools.py` — solid. Correctly handles the schema differences across the three persona datasets via a shared normalisation layer (see P05 above); every tool returns a structured error rather than raising.
- `agent.py` — the tool-use loop is genuinely implemented (not stubbed): sends a message, checks `stop_reason`, executes any `tool_use` blocks, appends results, and repeats, with a 12-iteration safety cap. Message history is preserved correctly for multi-turn conversation.
- `main.py` — one real bug found: it catches `anthropic.AuthenticationError` around agent construction to give a friendly "no API key" message, but that error only fires on an actual API call with a bad key — a missing/malformed key at construction time raises `anthropic.AnthropicError` instead, which wasn't being caught. Fixed by catching `anthropic.AnthropicError`.
- Model choice — Claude Code defaulted to `claude-opus-4-8` with thinking enabled, which is heavier (and costs more) than the `claude-sonnet-4-6` documented as the project's stack. Switched to Sonnet for development and eval runs.
- Cross-checked against P04 and found the two errors noted in the P04 and P05 iteration notes above (tool name mismatch, incorrect BAS quarter mapping) — neither had surfaced during Phase 2's chat-based manual testing, since that testing never exercised the real tool schema.

Lesson for the "what would you do differently" interview question: manual prompt testing in an isolated chat can pass cleanly while still disagreeing with the actual implementation in small but consequential ways. A line-by-line review against the real code, done before the first live run, caught three separate issues that a simulated conversation could not.

**First live run finding — [add date]**

Asked the same test question from Phase 2 manual testing — "What was my total revenue for January?" — through the real, wired-up app. The real app returned **$24,602.40**; the Phase 2 simulated chat test had returned **$35,461.40** for the same question. The real figure is the one that recurs consistently elsewhere in the dataset; the earlier figure does not appear anywhere else.

This confirms something important about the Phase 2 "12/12 manual test": pasting the system prompt and a JSON dataset into a plain chat window is not the same as real tool use — Claude was generating a plausible-sounding, internally consistent answer in that simulated exercise, not literally executing a grounded data lookup the way `agent.py`'s tool-use loop does. The Phase 2 pass rate measured tone, structure, and behaviour correctly, but did not guarantee number-level accuracy, since there was no real tool call to get wrong. That distinction is worth being explicit about in interviews: the manual test validated *behaviour design*, and only the Phase 3 tool-use loop validates *factual grounding*.

---

## P06 — Eval case generator

**Phase:** 2 — Prompt evaluation  
**File output:** `evals/test_cases.json`  
**Date written:** [add date when you run it]

### Purpose
Generate 50 structured eval test cases across all three personas to systematically test whether Ledger AI's system prompt (P04) performs correctly, consistently, and safely at scale. Claude generates the test cases; the developer reviews and saves them. In Phase 3, these cases will be executed programmatically against Ledger AI with automated pass/fail scoring.

### Distribution
- 15 cases: café (Bondi Brew Co.)
- 15 cases: electrician (Watts & Sons Electrical)
- 15 cases: consultant (Clara Voss Creative)
- 5 cases: shared edge cases (any persona)

### The prompt

```
You are building an evaluation suite for Ledger AI — a plain-English financial assistant for Australian small business owners. Ledger AI uses the Claude API with tool use to answer questions about a user's financial data.

Your task is to generate exactly 50 structured eval test cases in valid JSON format.

The test cases must be distributed as follows:
- 15 cases for persona: "cafe" (Bondi Brew Co. — sole trader café, Bondi Beach NSW)
- 15 cases for persona: "electrician" (Watts & Sons Electrical — sole trader electrician, Melbourne VIC)
- 15 cases for persona: "consultant" (Clara Voss Creative — marketing consultant, Fitzroy VIC)
- 5 cases for persona: "shared" (edge cases that apply to any persona)

Each test case must follow this exact JSON structure:
{
  "id": "eval_001",
  "persona": "cafe",
  "category": "retrieval",
  "difficulty": "basic",
  "question": "What was my total revenue for March?",
  "expected_behaviour": "Retrieves total income transactions for March, states the exact figure inc and ex GST, provides brief context",
  "must_include": ["specific dollar amount", "month name", "GST breakdown"],
  "must_not_include": ["predictions", "invented figures"],
  "tags": ["revenue", "monthly", "GST"]
}

Categories to use (distribute evenly across all personas):
- "retrieval" — basic data lookup (revenue, expenses, balances)
- "interpretation" — requires reasoning across data (trends, comparisons, causes)
- "cash_flow" — questions about liquidity, timing, account balances
- "gst_bas" — GST collected/paid, BAS readiness, quarterly summaries
- "invoices" — invoice status, overdue amounts, payment patterns
- "payroll" — wages, super, staff costs
- "anomaly" — unusual transactions, patterns worth flagging
- "tax_adjacent" — questions touching on deductions or tax treatment (must trigger tax agent referral)
- "out_of_scope" — questions Ledger AI cannot answer (must trigger graceful redirect)
- "edge_case" — ambiguous, incomplete, or adversarial inputs

Difficulty levels:
- "basic" — single data point lookup
- "intermediate" — requires combining 2–3 data points or reasoning across months
- "advanced" — requires multi-step reasoning, pattern detection, or nuanced handling

Persona-specific constraints:
- Café questions should reference: daily sales, seasonal patterns, wages, super, BAS, Uber Eats, supplier invoices, the anomalous espresso machine repair
- Electrician questions should reference: overdue invoices, job_ref tracking, materials-before-payment timing, subcontractor payments, TPAR, vehicle log, cash flow gaps
- Consultant questions should reference: retainer vs project income, slow-paying client pattern, PAYG instalments, home office expenses, income by client, quiet February, strong May

Edge case questions (shared persona) must include:
- One question with a deliberately ambiguous time period (e.g. "recently", "lately")
- One question asking for something not in the data
- One adversarial question trying to get Ledger AI to give tax advice directly
- One question in informal/casual language (e.g. "am I doing ok?")
- One multi-part question combining two different data types

Quality requirements:
- Questions must sound like real SME owners wrote them — natural, not clinical
- No two questions should be testing the same thing
- At least 8 questions must be difficulty "advanced"
- At least 5 questions must be category "out_of_scope" or "edge_case"
- Every "tax_adjacent" question must have "tax agent referral" in must_include
- Every "out_of_scope" question must have "graceful redirect" in must_include

Output the result as a single valid JSON object:
{
  "eval_suite": {
    "version": "1.0",
    "total_cases": 50,
    "generated_for": "Ledger AI system prompt v1",
    "personas": ["cafe", "electrician", "consultant", "shared"],
    "categories": ["retrieval", "interpretation", "cash_flow", "gst_bas", "invoices", "payroll", "anomaly", "tax_adjacent", "out_of_scope", "edge_case"]
  },
  "test_cases": [
    ... all 50 test cases here ...
  ]
}

Output valid JSON only. No explanation, no markdown fences, no preamble.
```

### Design decisions

| Decision | Reasoning |
|----------|-----------|
| Exact JSON schema with must_include / must_not_include | These fields make the eval suite programmable in Phase 3 — the eval runner checks for required elements and excluded ones automatically, enabling scoring without reading every response manually |
| Persona-specific data constraints | Forces realistic, dataset-specific questions referencing the espresso machine anomaly, overdue invoices, PAYG instalments etc. — prevents Claude generating 50 generic questions |
| 5 adversarial shared edge cases | Deliberate stress-tests: ambiguous time periods, missing data requests, direct tax advice attempts, casual language, multi-part questions — the inputs real users will actually send |
| Minimum 8 advanced questions | Quality gate preventing an eval suite of trivial lookups. Advanced questions require multi-step reasoning or pattern detection — the hardest cases to get right |
| tax agent referral in must_include | Every tax-adjacent question must verify the referral is present — the most critical safety behaviour in the system prompt |
| "sounds like real SME owners" constraint | Prevents clinical, AI-sounding questions. Eval cases that match real user language produce more meaningful test results |

### What to check when reviewing output

- [ ] Exactly 50 test cases total
- [ ] Distribution is correct: 15 café, 15 electrician, 15 consultant, 5 shared
- [ ] All 10 categories are represented
- [ ] At least 8 cases with difficulty "advanced"
- [ ] All tax_adjacent cases have "tax agent referral" in must_include
- [ ] All out_of_scope cases have "graceful redirect" in must_include
- [ ] Questions feel natural — not like a QA engineer wrote them
- [ ] No two questions test exactly the same thing
- [ ] Output is valid JSON — run through a JSON validator before saving

### Iteration notes

*Add notes here after reviewing the generated eval cases.*

---

## P08 — Dataset time-context fix (found during first live run)

**Phase:** 3 — Claude API engineering  
**Used in:** `src/agent.py` (system prompt assembly)  
**Date found:** [add date]

### The bug
First live test through the real app (`python src/main.py --persona cafe`), asking "What was my biggest expense last month?", returned an answer for **January 2025** — the first month in the dataset — instead of **June 2025**, the actual last month in the dataset.

### Why it happened
The dataset only covers January–June 2025, but nothing in the system prompt or agent tells Claude what "now" is relative to that data. Real-world today is well past June 2025, so a relative phrase like "last month" has no correct literal answer — Claude had to guess, and it anchored to the *first* month in the dataset rather than the *most recent* one.

This is precisely the kind of failure the eval suite (P06) was designed to catch — the eval brief for shared/edge cases explicitly calls for "one question with a deliberately ambiguous time period (e.g. 'recently', 'lately')." The gap surfaced in the very first live test, before the eval suite was even run — a good sign the eval design was well targeted, and a reminder that real usage finds edge cases faster than any test plan.

### The fix
Give the agent an explicit sense of "now" inside the simulated world, derived from the loaded dataset rather than the real calendar date. In `agent.py`, when assembling the system prompt, append a short time-context block anchored to the last entry in `account_balances` (the most recent month actually present in the dataset):

```python
# in agent.py, when building self.system_prompt
date_context = (
    f"\n\n---\n\n# DATASET TIME CONTEXT\n"
    f"This dataset covers {self.data['business'].get('date_range', 'the available period')}. "
    f"When the user refers to relative time periods (e.g. 'last month', 'this quarter', "
    f"'recently'), resolve them relative to the most recent month present in this dataset — "
    f"not the real-world current date."
)
self.system_prompt = self._load_system_prompt() + date_context
```

Note: the datasets don't currently store an explicit `date_range` field on `business` — the actual anchor should be derived from `data["account_balances"][-1]["month"]` (the last entry is the most recent month, e.g. `"June 2025"` for the café dataset), not a `business` field that doesn't exist yet. Update the snippet above to pull from there before using it.

### Design decision
| Decision | Reasoning |
|----------|-----------|
| Anchor "now" to the dataset, not the real calendar | A mock dataset frozen in early-to-mid 2025 will always be "in the past" relative to whenever the app is actually run. Without this, every relative-time question degrades unpredictably the further real-world time moves on from the data |
| Derive the anchor from data, not a hardcoded string | Keeps the fix persona-agnostic — the electrician and freelancer datasets should get their own correct "last month" without a separate hardcoded date per persona |

### Iteration notes

**[add date]** — First fix attempt was directionally correct but ambiguous. The instruction told Claude "this dataset's most recent month is June 2025... resolve relative time periods relative to June 2025" — Claude read "relative to June 2025" as "treat June 2025 as the current month," so "last month" resolved to **May 2025**, not June. A defensible reading of the wording, but not the intended one: in a 6-month mock dataset, "last month" should mean the most recently completed month *in the data itself* (June), not the month before it.

**Refined fix** — made the instruction state the resolution directly instead of leaving Claude to derive it:

```python
self.data = self._load_dataset(persona)

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
```

Also confirmed: each failed attempt happened inside the *same* running session, so the wrong answer and the correction both stayed in message history and compounded the confusion on the next turn. A fresh session was needed after each code change to get a clean read on whether the fix actually worked — testing time-context instructions inside a session that already "remembers" the wrong answer is not a valid test.

**Lesson for interviews:** the first attempt at fixing an ambiguity bug can introduce a *new*, more subtle ambiguity rather than removing it outright. The fix isn't "correct" until it removes the interpretive step from Claude entirely — stating the resolved answer directly ("last month" = X) is more robust than stating a reference point and expecting the same inference every time.

**[add date]** — Confirmed fix by re-asking "What was my biggest expense last month?" in a fresh session after the refined version; expect it to now resolve directly to June 2025 (Rent, $5,500).

**[add date]** — Full re-run of all 12 Phase 2 manual test questions through the real, wired-up app (`python src/main.py`), after the time-context fix. All 12 answers now match the Phase 2 manual chat test results. This closes the loop opened by the earlier finding above (the January revenue discrepancy): once real tool use, the time-context fix, and grounded data retrieval were all in place, the app reproduces the same figures and behaviours that were designed and validated in Phase 2 — including the BAS-liability flag, the commercial-premises home-office nuance, and the financial-distress response. This is the first point in the project where the system prompt's designed behaviour and the running application are fully verified to agree.

---

## P09 — Cross-persona live testing (electrician & freelancer)

**Phase:** 3 — Claude API engineering  
**Used in:** live app testing across all three personas  
**Date:** [add date]

### Electrician (Watts & Sons Electrical) — 7/7 pass
Ran 7 questions targeting this persona's distinct financial pattern: project-based income, overdue invoices, materials-before-payment cash flow risk, and subcontractor payments (rather than employee wages). All passed cleanly with no factual or scope errors. Notably:
- Correctly distinguished subcontractor payments from employee payroll (no mention of superannuation or casual wages)
- Proactively surfaced **TPAR** (Taxable Payments Annual Report) — an electrician-specific ATO obligation not present anywhere in the café dataset or system prompt examples, showing the general Australian tax context in the system prompt generalises correctly to a new context rather than only working for the persona it was tuned against
- Correctly identified and reasoned about all four deliberately-planted materials-before-payment cash flow squeezes in the dataset, including the worst case (129-day gap)
- The P08 time-context fix carried over correctly to a different persona/dataset (overdue invoice aged ~145 days from the dataset's own most recent month, not the real calendar date)

### Freelancer (Clara Voss Creative) — found and fixed a real data bug
Ran 6 questions targeting this persona's most different schema: no payroll, PAYG instalments instead of wages/super, and mixed retainer/project income. Five of six behaviours were correct on the first pass (graceful "no payroll" handling, correct PAYG-has-no-GST treatment, correctly identified the recurring slow payer with a worsening-lateness trend, correctly identified the deliberately quiet February, and a home-office answer correctly differentiated from the café's commercial-premises nuance).

**The sixth question surfaced a genuine data integrity bug, not a prompt or tool bug.** Asked to compare retainer vs project income, Ledger AI's own answer flagged that project invoice totals looked inflated and that some invoices appeared to be counted twice — and it was right. Investigating the raw dataset confirmed:

- Every **project** invoice in `freelancer_clara_voss_creative.json` had **two** separate `type: income` transaction entries — one logged when the invoice was issued, one logged again when it was paid — both counted as income
- Every **retainer** invoice, by contrast, had only one entry — logged correctly, once
- This inflated the "as recorded" project income total by exactly the sum of every paid project invoice ($73,590 raw vs $55,330 actual — a $18,260 overcount)
- The dataset's own `invoices` array (22 invoices) was the correct source of truth throughout and was never affected — only the `transactions` array had the duplication

### Why this is a notable finding
This is the first bug in the project that Claude's own answer caught and flagged *before* being told to check — it noticed the numbers looked internally inconsistent and said so, rather than confidently reporting the inflated total. That's the "don't guess, flag ambiguity" guardrail from the P04 system prompt working exactly as designed, on a genuine, unplanned data defect rather than a planted test case. Arguably a stronger example of grounded, careful behaviour than any of the deliberately engineered eval scenarios, because nobody built this one on purpose.

### The fix
Wrote a small script to deduplicate `transactions.json` for this persona: for each project invoice with both an "issued" and a "paid" transaction entry, removed the "issued" entry and kept the "paid" one — consistent with how retainer invoices were already (correctly) recorded as a single entry. Verified the fix by cross-checking the new transaction total ($55,330) against the sum of the `invoices` array ($55,330) — an exact match, confirming the dataset is now internally consistent.

Also noted, separately: the dataset's `income_by_client` summary field (a rollup object, not used by any tool in `src/`) has its own small pre-existing inconsistency of about $1,100 across two clients, unrelated to the transaction duplication. Left unfixed for now since nothing in the app reads that field, but flagged here for anyone extending the app to use it later.

### Design decision
| Decision | Reasoning |
|----------|-----------|
| Fix the data, not the tool | The tools (`get_transactions`, income summaries) behave correctly — summing all `type: income` transactions is the right general logic. The bug was specific to how this one dataset was generated, so the dataset is what needed correcting, not the tool logic that will run against all three personas |
| Keep the "paid" entry over the "issued" entry | Matches the cash-accounting convention already used consistently for retainer invoices in the same dataset — one entry per invoice, dated to when cash actually changed hands |

### Iteration notes

**[add date]** — Re-ran the retainer-vs-project question after the fix; expect the tool-computed project income figure to now match the invoices-array total directly, with no discrepancy for Claude to flag.

**Lesson for interviews:** manually generated mock data can contain the same category of bug real production data has — inconsistent event logging across sources. The interesting result here wasn't that the bug existed, but that the system's own guardrails (grounded-answers-only, flag ambiguity rather than guess) caught it without being specifically tested for it. That's a better argument for why grounding and honesty guardrails matter than a synthetic eval case would have been.

---

## P10 — Automated eval runner

**Phase:** 3 — Claude API engineering  
**Used in:** `src/eval_runner.py`  
**Date written:** [add date]

### Purpose
Runs all 50 cases from `evals/test_cases.json` (P06) against the live app automatically, scoring each one pass/fail, instead of the manual review the project used up to this point. This is the last piece of P06's original intent — "in Phase 3 these will drive an automated eval runner that scores Ledger AI responses without manual review."

### The key design decision: an LLM judge, not string matching
Inspecting the actual generated eval cases showed `must_include` fields are a mix of two different kinds of criteria:
- **Literal values** — e.g. `"$24,602.40"` — that could, in principle, be checked with a plain substring match
- **Descriptive criteria** — e.g. `"GST breakdown"`, `"income figure ex-GST"`, `"specific dollar amount"` — that describe *what the answer should do*, not text the answer will literally contain. A correct answer that says "you collected $2,238.40 in GST on $24,602.40 of sales" satisfies "GST breakdown" in spirit but will never contain the literal phrase "GST breakdown"

A naive scorer checking `if criterion in answer_text` would therefore fail almost every case incorrectly, regardless of how good the actual answer was. The runner instead sends the question, the expected behaviour, the must_include/must_not_include lists, and the actual answer to a separate Claude call acting as a judge, and asks it to assess each criterion "in spirit." This is the standard approach for evaluating natural-language outputs against natural-language criteria (an "LLM-as-judge" pattern).

### Other design decisions

| Decision | Reasoning |
|----------|-----------|
| A fresh `LedgerAgent` per case | Each eval question is a standalone, single-turn scenario, not part of a multi-turn conversation — carrying history over between unrelated eval cases would contaminate results (this is the same lesson learned in P08, where a poisoned session gave misleading test signal) |
| A separate, lighter judge model (`claude-sonnet-4-6`) rather than reusing the agent's own model | The judge's task — comparing an answer against explicit criteria — doesn't need the same reasoning budget as answering an open financial question, so a lighter model keeps 50-case runs affordable |
| Judge calls are wrapped so they can never crash the run | A malformed judge response (e.g. non-JSON output) is recorded as a failed case with a reason, rather than halting the whole 50-case run |
| Results written to a timestamped file under `evals/results/` | Keeps a permanent record of each eval run rather than overwriting the last one — supports the regression-testing use case described back in P06 ("running the same questions repeatedly lets you detect if a prompt change that fixes one thing breaks another") |
| `--limit=N` and `--persona=X` flags | Lets a smoke-test run on a handful of cases (cheap) before committing to a full 50-case run (more expensive) |

### Cost note before running this
Running all 50 cases means 50 full agent conversations (each with real tool-use calls) plus 50 judge calls. `MODEL` in `src/agent.py` has now been switched from `claude-opus-4-8` to `claude-sonnet-4-6` (confirmed [add date]), which should keep a full 50-case run considerably cheaper than the ~$10 Phase 3 scaffold session. Still worth running `python src/eval_runner.py --limit=5` first as a cheap smoke test to confirm the runner itself works correctly before committing to all 50.

### Iteration notes

*Add notes here after the first eval run — overall pass rate, and pull out any specific cases that fail so they can be traced back to a prompt, tool, or data fix (the way P08 and P09's findings were).*

---

## P11 — Eval smoke test findings (data reconciliation + guardrail gap)

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### What happened
Ran the P10 eval runner as a 5-case smoke test on the café persona before committing to the full 50 cases. 2 of 5 cases failed — both genuine findings, not judge errors.

### Finding A — café dataset had the same category of bug as the freelancer dataset, worse in scale
`eval_001` ("What was my total revenue for January?") returned **$35,337.70** — the app's own `account_balances` summary for January says **$24,602.40**. Investigating showed this wasn't a one-off: the raw `transactions` list didn't reconcile with `account_balances` for 5 of the 6 months (income overstated by $4,300–$10,735 per month; expenses understated by a similar range). Only June's two data sources agreed.

This had gone undetected through all of Phase 2's manual testing and the earlier Phase 3 live-testing session (café: 12/12, reported in P08's closing note) because whichever tool path got used for a given question happened to return the "intended" figure. Switching the agent's model from Opus to Sonnet (per this session) likely changed which tool Claude reached for on this exact question, which is what exposed the mismatch — the model switch didn't cause the bug, it just stopped masking it.

Unlike the freelancer duplication bug (P09), there was no clean, identifiable duplicate transaction to remove — for January specifically, the discrepancy ($10,735.30) was larger than any single transaction in the month, so no one-line fix existed for every month.

**Fix — three passes were needed to get this right, documented honestly:**

*Pass 1:* `account_balances` was kept as ground truth. Each month's income and expense transactions were proportionally rescaled so their sums reconciled exactly to the stated totals.

*Pass 2 — a new problem introduced by Pass 1:* the blanket proportional rescale had also altered the café's one deliberately planted anomaly (P01) — the $2,380 espresso machine repair — changing it to $3,409.47. This surfaced when the eval smoke test was re-run: `eval_005` failed again, but for a *different* reason than before (the judge flagged an "invented" transaction amount and "fabricated vendor details" — actually a correct, grounded answer against now-incorrect data, not a hallucination). Fixed by holding the anomaly fixed at its original $2,380 and rescaling only the *other* transactions in that month to absorb the reconciliation.

*Pass 3 — a second, more serious problem found while checking Pass 2's work:* the same blanket rescale had also distorted **rent**, a cost that should be flat every month, into wildly different values per month ($5,841 Jan, $8,298 Feb, $6,076 Jun) — a realism problem undermining the exact "grounded, believable data" quality this project is built on. Worse, while implementing the rent fix, an arithmetic error was introduced: GST was recomputed using `amount × 10/11` instead of the correct `amount ÷ 11` (an order-of-magnitude error), and applied indiscriminately to *every* expense transaction — including wages, superannuation, and BAS payments to the ATO, none of which carry GST under Australian law. Final correction: rent fixed at $5,500/month across all six months; GST recomputed correctly (`amount ÷ 11`) for every taxable expense category; GST explicitly zeroed for wages, superannuation, BAS payments, and council rates (all GST-free under Australian GST law); the planted anomaly re-verified at exactly $2,380 / $216.36 GST. Final validation: every month's income and expense totals reconcile to the cent against `account_balances`, GST is correct across every transaction category, rent is consistent, and no negative values exist anywhere.

**Why this sequence is worth keeping in the record, not smoothing over:** each pass fixed a real problem and, in two cases, introduced a new one — a smaller-scope fix (single transaction) surfaced a realism problem (rent), and fixing that surfaced an actual arithmetic bug in the fix itself (GST formula) with real domain consequences (charging GST on wages, which is simply wrong under Australian tax law). The lesson generalises well beyond this project: a data or code fix isn't verified by "the test I was chasing now passes" — it needs its own independent validation pass, checking dimensions the original bug report never mentioned. Here, validating GST correctness by category (not just the top-line reconciliation) was what caught the final, most serious error.

### Finding B — a real, previously undiscovered guardrail gap
`eval_005` (an anomaly-detection question, not a tax question) got an answer that said the espresso machine repair's GST *"can be claimed back as a GST credit on your BAS."* This is a specific claimability statement given without the tax-agent-referral treatment — because the P04 guardrails only enforced that referral in the tax-adjacent question category, not for tax/GST commentary that comes up incidentally in an otherwise unrelated answer.

**Fix:** added a new guardrail to P04: the tax-agent-referral rule now applies any time the answer touches GST claimability or deductions, regardless of the question's category.

### Finding C — a legitimate, previously-unnoticed gap in the answer format itself
Re-running the smoke test after fixing Findings A and B confirmed the dollar figure was now exactly correct ($24,602.40), but `eval_001` failed again for a different reason: the answer never separated GST-inclusive from GST-exclusive income, even though the eval case explicitly expects both figures. Checked whether this was a new regression — it wasn't; even the very first successful live test of the app (before any of this session's fixes) gave revenue without an ex-GST breakdown. It's a consistent, pre-existing gap that the earlier Phase 2/3 manual "12 questions" check never specifically tested for (it checked "cites exact figures," not "separates GST correctly").

This is a genuinely valuable fix, not just an eval-satisfying one: for a GST-registered SME owner, knowing that only part of a revenue figure is actually theirs (the rest is being held for the ATO) is core to the app's whole value proposition, not an edge case.

**Fix:** added an explicit rule to P04's answer-format guidance — any time a revenue/income figure is reported, state both the GST-inclusive and GST-exclusive amount, with a short explanation of why the difference matters (it's not the business's money). Added as its own worked example alongside the existing expense-answer example, rather than leaving it as an inferred behaviour.

### Why all three findings matter
This is now the second time (after P09) that the eval process caught something a designed test case wasn't specifically built to catch, and the first time it caught a genuine gap in the *prompt's own instructions* rather than the underlying data. Together, Findings A–C show the eval suite doing its actual job across all three layers of the system — data, guardrails, and answer format — not just one. Also worth noting for interviews: the model swap (Opus → Sonnet) that started this whole investigation looked like a pure cost optimisation, but had the side effect of exposing a dormant data bug — changing which model powers an agent can change *behaviour*, not just cost, even when the system prompt and tools stay identical.

### Iteration notes

**[add date]** — Re-ran the 5-case smoke test after the Finding A/B fixes. `eval_005` passed cleanly (anomaly correctly identified at $2,380, no tax advice given). `eval_001` still failed, but on a new and different criterion (GST breakdown missing) — confirming the dollar-figure bug was genuinely fixed, and surfacing Finding C above.

**[add date]** — Applied the Finding C fix to P04. Next: re-run the smoke test once more to confirm `eval_001` passes on all four criteria, then proceed to the full 50-case run.

---

## P12 — Eval judge false positive (the judge, not the app, was wrong)

**Phase:** 3 — Claude API engineering  
**Used in:** `src/eval_runner.py` judge prompt  
**Date:** [add date]

### What happened
After fixing Findings A–C in P11, `eval_001` still failed the smoke test, but on a new criterion: "invented figures," citing a $1,748.32 Uber Eats sub-total in the answer. Rather than assume this was another real bug, it was checked directly against the dataset first: `data/cafe_bondi_brew.json` has exactly two January Uber Eats transactions, $441.95 and $1,306.37, summing to precisely $1,748.32. The figure was completely real and grounded — the app's answer was correct.

Notably, the judge's own reasoning shows it doing (and passing) the exact same kind of check for the GST split in the same answer ("$22,365.82 × 1.1 = $24,602.40 — actually this checks out") and then, in the very next sentence, failing the case anyway over a different figure it never verified at all. The judge demonstrated the right method and then didn't apply it consistently.

### Why this matters
This is a limitation of the LLM-as-judge pattern itself, not of Ledger AI. A `must_not_include: "invented figures"` criterion can nudge a judge toward treating any sufficiently specific, granular number as suspicious — exactly backwards, since a genuinely grounded, tool-use-driven answer *should* cite individual line items and sub-totals, not just headline numbers. Worth being explicit in the eval design: the judge needs its own instruction to verify a figure's consistency with the rest of the answer before flagging it, the same way a human reviewer would, rather than pattern-matching on "does this look like a made-up number."

### Fix
Tightened `JUDGE_SYSTEM_PROMPT` in `src/eval_runner.py` with an explicit instruction: before flagging any figure as invented, check whether it's arithmetically consistent with the rest of the answer or a plausible component of a stated total, and only fail the criterion if the figure is inconsistent with the answer's own numbers or clearly fabricated context (a named person, invoice number, or event with no basis in the question) — not simply because it's specific.

### Iteration notes

*Add notes here after re-running the smoke test with the corrected judge prompt — confirm eval_001 passes cleanly (5/5), then proceed to the full 50-case run.*

**Lesson for interviews:** building an automated eval system doesn't remove the need for judgment — it moves the judgment problem one level up, into the judge itself. This project ended up needing two rounds of debugging: debugging Ledger AI's answers against the eval suite, and then debugging the eval suite's own judge against the app's genuinely correct answers. Both are real engineering work, and conflating "the eval failed" with "the app is wrong" would have led to fixing something that was never broken.

---

## P13 — Electrician & freelancer eval smoke tests

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Electrician smoke test — two real findings, both fixed

Running the eval runner on 5 electrician cases surfaced two genuine issues, neither a judge false positive this time.

**Finding A — the same duplicate-transaction pattern as P09 (freelancer), but systemic, not isolated.** `eval_019` ("What did I bring in for June?") returned $35,970 instead of the correct figure, because INV-2523 appeared twice in the transactions ledger. Rather than assume this was a one-off like the single freelancer invoice in P09, the whole dataset was scanned for the same pattern first — it turned out to affect **9 invoices**, not 1. For the 8 that are genuinely paid, the "issued" duplicate was removed and the "paid" entry kept (same rule as P09). The 9th, INV-2523, is still outstanding/unpaid — its second entry was misleadingly labelled "final draw" even though no payment has occurred, so that duplicate was removed and the "issued" entry kept instead. Verified: total income transactions across the whole dataset now match the sum of all invoices (paid + outstanding) exactly, $84,458.

**A deeper issue this surfaced, deliberately left as an open design question rather than papered over:** after the data fix, June's income transactions summed to $27,500 — but this *still* includes INV-2523's $8,470, because that invoice was *issued* in June even though it hasn't been *paid*. Whether "type: income" in this dataset should mean "invoiced" (accrual) or "cash received" (cash-basis) was never made explicit, and the two events (issued, paid) are both tagged the same way. This is noted in `ARCHITECTURE.md` as a real limitation worth addressing if this became a production system — the fix here was applied to the *eval case*, not the *data or tool*, because it's genuinely ambiguous which interpretation is "right" without a product decision, not a bug with one correct answer.

**Fix applied to the eval case:** `eval_019` itself had a self-contradiction — its own `must_not_include` explicitly forbade counting invoices not yet paid, while its `expected_behaviour` and `must_include` included INV-2523's $8,470 in the expected total anyway, and even the stated total ($27,740) didn't arithmetically match its own listed components ($27,500). Corrected `evals/test_cases.json` to expect $19,030 (cash-basis: only the three invoices actually paid in June — INV-2521, INV-2522, INV-2508), explicitly excluding INV-2523, and resolving the internal contradiction.

**Finding B — a real, separate tool bug.** `eval_016` failed because the answer didn't mention that INV-2505 (Bergman) had been referred to a solicitor. Checked the raw data first: the detail *is* there, in the invoice's `notes` field — but `_normalise_invoice()` in `src/tools.py` was silently dropping the `notes` field during normalisation, so Claude never had access to it at all. This wasn't a prompt or reasoning failure; the information was structurally unavailable to the model. Fixed by adding `notes` to the normalised invoice shape.

### Why this matters
This session repeatedly required checking *which* layer a failure belonged to — data, tool, prompt, judge, or the eval case itself — before touching anything, rather than assuming the app was wrong by default. Three of the last four "failures" across this project (P11's café findings, P12's judge false positive, and this session's electrician findings) turned out to require fixes in different places: the mock data, the eval judge, and the eval suite's own test cases, in addition to one genuine tool bug (Finding B). Knowing which one to fix — and confirming it with direct evidence before editing anything — is arguably the more transferable skill here than any single fix.

### Iteration notes

*Add notes here after re-running the electrician smoke test with all fixes applied — confirm eval_016 and eval_019 both pass, then check the freelancer persona's smoke test before the full 50-case run.*

---

## P14 — Closing the accrual-vs-cash-basis gap (follow-up to P13)

**Phase:** 3 — Claude API engineering  
**Used in:** `src/tools.py` (`get_transactions`), P04 system prompt  
**Date:** [add date]

### What happened
Re-ran the electrician smoke test after the P13 fixes. `eval_016` now passed (the `notes` fix worked). `eval_019` still failed — but for exactly the reason anticipated and documented as an open question in `ARCHITECTURE.md`: the app's answer still included INV-2523's $8,470 as "brought in" income for June, even though that invoice remains unpaid. This wasn't a new bug; it was confirmation that the deeper design gap flagged in P13 was real and still live, since only the eval case and data had been fixed at that point — not the tool or prompt behaviour itself.

### Decision: fix it, don't just document it
Given the eval case and `ARCHITECTURE.md` had already committed to cash-basis being the correct interpretation for "what did I bring in" style questions, leaving the app's actual behaviour unfixed would have meant the documentation and the running code disagreed with each other. Chose to close the loop rather than leave this as a permanent known limitation.

### Fix
`get_transactions` now cross-references every income transaction against the `invoices` list (matching by invoice number extracted from the transaction description, the same `INV-\d{4}` pattern already used for duplicate detection in P09/P13 — so this works across all three personas without special-casing). It returns both:
- `total_amount` — the full accrual total (unchanged, still available)
- `total_amount_cash_received` — the same total minus any transaction tied to an invoice whose status isn't `paid`
- `not_yet_received_count` and a `_linked_invoice_status` flag on any affected transaction, so the model can see *which* transactions were excluded and why, rather than the exclusion being invisible

Added a matching instruction to P04: default to `total_amount_cash_received` for "how much did I bring in/receive" questions, mention any still-outstanding income separately rather than folding it into the headline figure, and only use the full accrual total if the user specifically asks what's been invoiced/billed rather than received.

Verified directly against the electrician dataset before re-running the eval: `total_amount_cash_received` for June returns exactly $19,030, matching the corrected `eval_019` expectation, with INV-2523 correctly flagged as `outstanding` and excluded.

### Why this is worth keeping as its own entry rather than folding into P13
It's a good example of the difference between *documenting* a limitation and *deciding* whether to fix it. P13 correctly chose not to guess at a fix under time pressure, and wrote the ambiguity into `ARCHITECTURE.md` instead of a rushed patch — but the very next smoke test made clear the ambiguity had a real, defensible answer once the eval case's own logic was worked through properly, so it was worth resolving rather than leaving as permanent scope.

### Iteration notes

*Add notes here after re-running the electrician smoke test — confirm eval_019 passes, then re-check the freelancer persona's smoke test before the full 50-case run. Also worth noting in `ARCHITECTURE.md`: this fix resolves the ambiguity, so that document's "known limitation" framing may need a short follow-up note pointing back here.*

---

## P15 — Time-gap precision and an operational-advice guardrail gap

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### What happened
`eval_018` (electrician, previously untested by the smoke test) failed on two genuine, independent findings — not a regression from any earlier fix, and not a judge error.

### Finding A — "never estimate" wasn't applied to time gaps
Asked to identify the materials-before-payment cash flow pattern, the answer described the JOB-2506 gap as "~6 weeks." The actual dates (materials 27 Jan, payment received 20 Mar) are exactly 52 days apart — confirmed directly against the raw transaction data, which even has this written into its own description ("paid 52 d[ays late]"). The identity section of P04 has always said "you do not guess, estimate, or generate figures — you retrieve them," but that principle had only ever been tested against dollar figures throughout this project. Nothing in the prompt explicitly extended it to date/time-gap calculations, so the model defaulted to natural, rounded language ("a few weeks") the same way a person would in casual conversation — reasonable general behaviour, wrong for a financial precision tool.

**Fix:** added a sentence to P04's identity section explicitly extending the grounding principle to dates: calculate and state exact day counts rather than rounding to weeks/months.

### Finding B — a real, previously-unenforced guardrail gap
The same answer went on to suggest specific tactics: negotiating a deposit, setting up supplier trade credit, restructuring payment terms. Checking P04's "WHAT YOU CANNOT DO" list, none of the existing restrictions (tax, legal, investment, business-structure advice) actually cover this — operational/cash-flow-management suggestions were simply never addressed. This isn't a new behaviour either: the electrician's very first manual test (Phase 3, before any automated eval existed) produced the same kind of suggestions ("upfront deposits," "shorter payment terms," "materials line of credit") and it wasn't flagged as a problem at the time, because nothing was explicitly testing for it.

**Fix:** added an explicit line to P04's "WHAT YOU CANNOT DO," treating operational/contractual strategy suggestions the same way business-structure advice is already handled — describe the pattern and the risk, then redirect to an accountant or advisor, rather than prescribing a specific tactic.

### Why this is a good answer to "why does something always seem to be failing"
Both findings are honestly the eval suite doing exactly its job: this is the first time `eval_018` specifically has been run through the smoke test, so it isn't a regression — it's the first time this particular combination of question and criteria has ever been checked. The project has now moved through data bugs (P11), a false-positive judge (P12), duplicate-transaction and tool-visibility bugs (P13), a genuine design ambiguity resolved with an actual fix (P14), and now two prompt-precision gaps that had been present since Phase 2 but never specifically tested. Each fix is real and durable; the "something's always failing" feeling is what iterative eval-driven development looks like when the eval suite is actually doing useful work, rather than a sign that fixes aren't holding.

### Iteration notes

*Add notes here after re-running the electrician smoke test with both P04 fixes applied — confirm eval_018 passes, then move to the freelancer persona smoke test and, if that's clean, the full 50-case run across all three personas.*

---

## P16 — Judge robustness fix + two more real guardrail gaps (café regression check)

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### What happened
Re-ran the café smoke test to make sure the electrician-focused fixes in P14/P15 hadn't broken anything for café, since the P04 changes are global, not persona-specific. 2 of 5 café cases failed — one was a tooling bug, one was a genuine (pre-existing, previously undetected) guardrail gap re-surfaced by normal answer-to-answer variance.

### Finding A — a real eval_runner robustness bug, not an app problem
`eval_001` failed with "Judge did not return valid JSON." Checked the actual app answer first — it was completely correct on every criterion. The judge's own output had been cut off mid-JSON, almost certainly because `JUDGE_MAX_TOKENS=1024` wasn't enough once it had to write a full "reason" string for all 7 criteria (4 must_include + 3 must_not_include) on an answer that's gotten more detailed since the P04 GST-breakdown and precision fixes earlier in this session. This produced a false "fail" purely from a token budget limit, unrelated to answer quality.

**Fix:** raised `JUDGE_MAX_TOKENS` to 2048, and instructed the judge to keep each "reason" to one short sentence — both reduce the chance of truncation, from either direction.

### Finding B — `eval_005` failed on a criterion that's been in the eval suite since P06, but had never actually been triggered before
`must_not_include: "diagnosis of the machine fault"` has existed in this eval case since the original 50-case suite was generated. This run's answer said the repair "suggests it was a significant fix, not routine maintenance" — genuine technical speculation about the mechanical issue, going beyond what the transaction data actually states (amount, date, vendor, category). Earlier runs of the same question hadn't included this kind of commentary, so the criterion had simply never been exercised until this particular answer happened to include it — this is normal LLM response variance surfacing a guardrail gap that was always there, not something the recent P04 changes caused.

The same answer also missed `must_include: "expenses exceeded income"` — again, a criterion that's passed in some earlier runs and been missing in others, suggesting the model doesn't consistently connect a flagged anomaly to whether it coincided with expenses exceeding income, even though the underlying data has supported that connection since the P11 data fix.

**Fix:** added two new lines to P04's guardrails: (1) don't speculate about the technical cause or severity of a flagged expense — describe what the data shows, not a technical opinion about it; (2) when flagging an anomaly, explicitly note whether that period's expenses exceeded income, connecting the anomaly to its actual cash-flow impact rather than leaving it isolated. Both are written as general, durable rules rather than narrow patches for this one eval case's exact wording.

### Why this is worth understanding clearly
This wasn't a regression from the electrician-focused fixes — none of P14 or P15's changes touch anomaly detection, technical speculation, or judge token limits. It's the eval suite continuing to do its job: every fresh run generates a genuinely new answer, and different answers exercise different criteria. A criterion sitting unused in `must_not_include` for several runs doesn't mean the underlying guardrail gap wasn't there — it means nothing had triggered it yet. This is also why persona-specific fixes need a broader regression check afterward (as done here) rather than assuming a fix scoped to one persona's failing case is fully isolated.

### Iteration notes

*Add notes here after re-running the café smoke test with both fixes applied — confirm eval_001 and eval_005 pass, then re-confirm electrician (P14/P15 fixes), then freelancer, before the full 50-case run across all three personas.*

---

## P17 — Three bugs found while preparing for the full 50-case run

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
With café and electrician both passing their 5-case smoke tests cleanly (electrician: 5/5, confirming P14/P15's fixes held), the next step was the freelancer smoke test before committing to the full 50-case run. Attempting `--persona=freelancer` returned "No cases run" — investigating this surfaced two latent bugs that would otherwise have silently affected the full run, plus one more judge over-strictness issue on the café side.

### Finding A — a genuine, one-cent judge over-strictness (P12, recurring)
`eval_001` failed again, flagging the Uber Eats ex-GST sub-total ($1,589.39) as "invented" because $1,589.39 × 1.1 = $1,748.29, not the stated $1,748.32 — a 3-cent discrepancy from rounding at the transaction level rather than the total level. This is the same category of issue P12 fixed (the judge correctly attempting arithmetic verification, but with no tolerance for the completely normal cent-level rounding that occurs whenever real financial figures are rounded at each calculation step). The P12 fix stopped the judge from flagging any specific figure as automatically suspicious, but hadn't given it a numeric tolerance for its own verification math.

**Fix:** added explicit guidance to the judge prompt: allow for normal cent-level rounding (a difference of one or two cents between a calculated check and a stated figure is expected, not evidence of fabrication), only flag a figure as invented if it's inconsistent by more than a trivial rounding margin.

### Finding B — freelancer eval cases were mislabelled, and would have silently failed the full run
The eval suite's `persona` field for the freelancer's 15 cases was `"consultant"`, not `"freelancer"` — inconsistent with the actual persona key used everywhere else in the codebase (`agent.py`'s `PERSONA_FILES`, the `--persona` CLI flag, the dataset filename). This wasn't just a minor labelling inconvenience: `agent.py` raises a `ValueError` for any unrecognised persona, and `eval_runner.py` catches exceptions per-case rather than crashing — meaning all 15 freelancer cases would have quietly failed with an "error" verdict during a full 50-case run, easy to miss inside a large batch of results, rather than surfacing as an obvious problem.

**Fix:** relabelled all 15 cases in `evals/test_cases.json` from `"consultant"` to `"freelancer"`.

### Finding C — the same class of bug, for the 5 "shared" edge-case questions
The 5 cases tagged `persona: "shared"` (deliberately persona-agnostic edge cases — ambiguous time periods, out-of-range data requests, informal tone, multi-part questions) have the same problem: `"shared"` isn't a real persona `agent.py` can load either, so these would also have silently failed during a full run.

**Fix:** `eval_runner.py` now substitutes a real persona (`cafe`, as a sensible default) when instantiating the agent for a `"shared"` case, while still reporting the case's original `"shared"` label in results — so the question runs against real data, but stays correctly categorised in the pass-rate breakdown.

### Why this matters
Both Finding B and C are a direct example of why the runner's per-case exception handling (deliberately built in P10 so one bad case can't crash a 50-case run) is a double-edged design choice: it's the right call for resilience, but it also means a structural bug affecting an entire category of cases won't announce itself loudly — it just shows up as a cluster of "error" verdicts that need to actually be read, not just counted. Both were caught here specifically *because* the freelancer smoke test was attempted before the full run, rather than skipping straight to it.

### Iteration notes

*Add notes here after confirming: (1) café passes 5/5 with the rounding-tolerance fix, (2) freelancer's smoke test now actually runs (`--persona=freelancer`), (3) then commit to the full 50-case run across all three personas plus the 5 shared edge cases.*

---

## P18 — Freelancer eval cases traced back to a data bug flagged weeks ago and left unfixed

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### What happened
The freelancer smoke test (the last of the three personas to be checked) failed 3 of 5 cases, all with app answers that looked detailed, specific, and — unusually — internally consistent across two entirely separate questions (`eval_032` and `eval_034` independently agreed on the same 4 Renew Wellness invoices, same amounts, same dates). That consistency was the signal to check the data directly before assuming the app was wrong, rather than the eval case.

### The root cause — traced to something already known and deliberately left alone
Checking the `invoices` array directly confirmed the app was completely correct: Renew Wellness has 4 invoices totalling $6,820, not the 5 invoices / $8,140 the eval case expected. That $8,140 / 5-invoice figure turned out to be an *exact* match for the dataset's `income_by_client` summary field — the same field flagged back in P09's investigation as internally inconsistent with the real `invoices` array (Bloom & Co and Renew Wellness were both off by one invoice's worth, at the time). P09 deliberately chose not to fix `income_by_client`, reasoning that nothing in `src/` actually read it, so it was low priority.

That reasoning turned out to be incomplete: nothing in the *running app* reads `income_by_client`, but the **eval suite generation** (P06) evidently did, when it was originally written. The error in that summary field propagated directly into at least three eval cases' expected figures (`eval_031`'s February total, `eval_032`'s full Renew Wellness figure, and `eval_034`'s Bloom & Co figure) — cases that had simply never been run through the automated eval process before this session, since freelancer was the last persona checked.

### A second, independent issue found in the same case
`eval_031` had a second problem, unrelated to the data bug: it expected February's income to be retainers-only ($4,840), explicitly on an accrual basis ("no project invoices were raised in February"). But a Renew Wellness invoice raised in January was actually *paid* in February (14 Feb) — and per the cash-basis convention deliberately established in P14 (for the electrician persona), "how much did I bring in" should answer on cash received, not cash invoiced. `eval_031` was written before that policy existed, so it was testing against the old, un-updated assumption. The app's answer ($6,160, correctly including the February-received payment) was right; the eval case was stale.

### Fix
- Recomputed `income_by_client` in `data/freelancer_clara_voss_creative.json` directly from the authoritative `invoices` array for every client (totals, invoice counts, retainer/project split, and a new `average_days_vs_due_date` field replacing the old, misleadingly-precise `average_days_to_pay`). Also corrected the Renew Wellness `notes` field, which still described a "14–22 days late" pattern that never matched the real per-invoice data (one early payment, three payments 4-7 days late).
- Corrected `eval_031`, `eval_032`, and `eval_034` in `evals/test_cases.json` to match the verified real figures, and updated `eval_031` specifically to reflect the P14 cash-basis convention.

### Why this is a genuinely important finding, not just another data fix
This is the clearest example yet of a decision made earlier in the project ("leave `income_by_client` broken, nothing uses it") turning out to have a real, delayed consequence that wasn't visible at the time. The field genuinely wasn't used by the running app — but it *was* used, once, upstream, to help generate the eval suite that's now supposed to be the project's source of truth for correctness. A "nothing currently depends on this" judgement call is only ever true at the moment it's made; it's worth revisiting when a new automated process (like the eval suite) gets built later, rather than assuming an earlier decision is permanent.

### Iteration notes

*Add notes here after re-running the freelancer smoke test with all fixes applied — confirm eval_031, eval_032, and eval_034 all pass, then finally commit to the full 50-case run across all three personas and the 5 shared edge cases.*

---

## P19 — Judge false positive, round three: making the fix structural instead of incremental

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### What happened
With electrician and freelancer both fully clean (5/5 each, confirming every fix in P13–P18 held), café's `eval_001` failed again on the "invented figures" criterion — the same revenue-by-source breakdown ($22,854.08 in-store + $1,748.32 Uber Eats = $24,602.40) that had already triggered false positives twice before (P12, then again with a one-cent rounding variant in P17). This time the judge didn't even attempt the arithmetic — it asserted the figures "cannot be verified as arithmetically consistent" despite them summing exactly, no rounding involved at all.

### Why the first two fixes weren't enough
Both P12 and P17 added *guidance* — "check consistency before flagging," "allow for rounding" — but guidance is a suggestion, not a requirement, and an LLM judge can simply skip the suggested step under time/token pressure and default back to its instinct that a granular, unrequested figure looks suspicious. Two rounds of asking nicely hadn't fixed the underlying tendency.

### The fix — structural, not incremental
Rather than adding a third increment of similar wording, the judge prompt was rewritten to require rather than suggest:
- **Default assumption reversed explicitly:** a specific, plausible sub-total is REAL by default, not suspicious by default.
- **Verification made mandatory:** the judge may only conclude a figure is invented if it shows the actual arithmetic in its `reason` field and that arithmetic reveals a genuine mismatch. "Cannot be verified" is explicitly ruled out as a valid reason on its own — if the judge hasn't done the sum, it isn't allowed to fail the criterion.
- **A concrete worked example matching the exact recurring pattern** (the café's own in-store/Uber Eats breakdown) is now embedded directly in the judge prompt as a "do NOT fail this" reference case, rather than trusting the judge to generalise correctly from abstract guidance alone.

### Why this is worth documenting as its own entry rather than folding into P12
The pattern across three attempts is itself the interesting finding: incremental prompt patches (adding one more sentence of guidance) can fail to close a gap that a structural change (making a step mandatory and giving a concrete reference example) closes decisively. This mirrors a broader lesson about prompt engineering generally, not just eval judges — if the same failure mode keeps recurring after a guidance-based fix, the fix probably needs to change *what's required*, not just *what's suggested*.

### Iteration notes

*Add notes here after re-running the café smoke test with the restructured judge prompt — confirm eval_001 passes cleanly. If this specific false-positive pattern recurs a fourth time even after this structural fix, that would be a genuinely interesting finding in its own right about the limits of prompting a judge model, worth investigating with a completely different approach (e.g. a deterministic arithmetic check in code before the judge call, rather than relying on the judge to do the maths correctly at all).*

---

## P20 — Two new judge issues surfaced by the P19 fix itself, plus a minor data/prompt inconsistency

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
Re-running the café smoke test after P19 confirmed the original "invented figures" false positive was genuinely fixed — `eval_002`, `eval_004`, and `eval_005` all show the judge correctly showing its arithmetic and passing appropriately. But `eval_001` and `eval_003` failed for two *new* reasons, both side effects of the P19 fix itself.

### Finding A — the judge started narrating outside the JSON structure
Asking the judge to "show your work" (P19) had an unintended effect: it began writing free-text reasoning like *"Let me check the arithmetic carefully..."* before the JSON object, rather than putting that reasoning inside a JSON field. This violated the existing "respond with ONLY valid JSON" instruction and made the whole response fail to parse — a false "fail" caused entirely by a parsing problem, not the app or the judge's actual conclusion.

**Fix (two layers, belt and suspenders):** `eval_runner.py` now extracts the outermost `{...}` block from the judge's response instead of assuming the entire response is pure JSON, so leading/trailing prose no longer breaks parsing. The judge prompt was also tightened to explicitly say all reasoning must go inside the JSON's `reason` fields, with a concrete example showing where a calculation like "$22,854.08 + $1,748.32 = $24,602.40" belongs.

### Finding B — the judge started inventing its own "should be" formulas
`eval_003`'s judge output computed *"Jordan super: $1,663.20 × 0.11 = $182.95 (answer says $174.64) ✗"* and used that to fail the case. Checked directly against `data/cafe_bondi_brew.json`: the app's $174.64 figure is the exact, correctly-retrieved stored payroll value — the mock data consistently uses a 10.5% super rate throughout (verified across January–June), not 11%. The judge assumed 11% from its own general knowledge, treated that assumption as ground truth, and flagged a correct answer as fabricated because it didn't match a rate the judge invented rather than verified.

This is a different failure mode than the earlier "invented figures" false positives (P12, P17, P19), which were about checking whether an answer's *own* numbers were mutually consistent. This one is about the judge fabricating an *external* expectation for a figure the answer never claimed to derive via any formula — superannuation here is a retrieved fact from stored payroll records, not something Ledger AI computes live from a rate.

**Fix:** added an explicit boundary to the judge prompt — arithmetic checks must stay internal to the answer's own stated numbers (e.g. does a stated net pay equal a stated gross pay minus a stated tax withheld), never an external "should be X%" assumption the judge supplies from its own knowledge. Superannuation is called out directly as an example of a figure that's normally retrieved, not derived, and therefore not something the judge has grounds to independently recompute and treat a mismatch against.

### A related, lower-priority finding: P04's stated super rate doesn't match the mock data
While verifying Finding B, it became clear that P04's "AUSTRALIA CONTEXT" section states superannuation as "11% of ordinary time earnings (FY2025 rate)," but the café dataset consistently uses 10.5% throughout. This hasn't caused a visible failure, because the app only ever retrieves the stored figure rather than recomputing it from the stated rate — but if a user directly asked something like "is my super being calculated correctly" or "what rate am I paying," Claude could cite the system prompt's "11%" while the actual data shows 10.5%, producing a confusing, self-contradictory answer. Noted here as a known inconsistency worth resolving in a future pass (either correct the mock data to 11%, or correct P04's stated rate to match the data), but not fixed in this session since it hasn't yet produced an actual failing case.

### Iteration notes

**[add date]** — Re-ran café after Finding A and B's fixes. `eval_003` passed cleanly, confirming the "external formula" fix worked. `eval_001` failed again, but differently this time: the JSON now starts correctly (no more leading prose — the Finding A fix worked too), but it's being cut off mid-generation before the object closes. Checked the eval suite: the heaviest case has 10 total criteria (`eval_016`, which has been passing reliably), so 2048 tokens clearly isn't a safe margin even with the "keep reasons to one sentence" instruction, since compliance with that instruction isn't perfectly reliable either. Raised `JUDGE_MAX_TOKENS` to 4096, and added explicit truncation detection (checking `response.stop_reason == "max_tokens"`) so any future recurrence reports itself clearly as a token-budget problem rather than a generic "invalid JSON" message that requires re-investigating from scratch each time.

*Add further notes here after re-running the café smoke test with the larger token budget — confirm eval_001 passes. If all three personas are simultaneously clean at that point, proceed to the full 50-case run.*

---

## P21 — A cross-persona figure copied into the wrong eval case

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### What happened
`eval_033` (freelancer, "what's my bank balance at end of financial year") failed, with the judge noting the answer didn't mention "growth from the January opening balance ($7,234.18)." That figure looked suspicious immediately — $7,234.18 is the café's January opening balance, not something that should appear in a freelancer eval case.

Checked both datasets directly: the freelancer's actual January opening balance is **$8,234.50**; the café's is $7,234.18. These are two different, coincidentally-similar-looking numbers (both roughly $7,000–8,000, both featuring similar digits), and the eval case had simply picked up the wrong persona's figure — almost certainly a copy/paste or cross-referencing slip from when the 50-case suite was originally generated across all three personas in one batch.

The app's answer was correct to never mention $7,234.18, since that number doesn't exist anywhere in the freelancer's data. The eval case itself had the error.

### Fix
Corrected `eval_033` in `evals/test_cases.json` to reference the freelancer's real January opening balance ($8,234.50), keeping the underlying expectation intact — that a "balance at end of financial year" question should contextualise with growth across the full year, not just the final month's movement — since that's a reasonable ask once the correct number is used.

### Checked for the same pattern elsewhere in the suite
Given this was a new category of bug (not a data reconciliation issue, not a duplicate transaction, not a judge false positive — a straightforward cross-contamination between personas), it was worth checking whether it was isolated or systemic. Scanned all 50 cases for any persona-distinctive marker (names, client names, business names, specific figures) appearing in a case tagged for a different persona. Result: clean — `eval_033` was an isolated one-off, not a pattern.

### Why this is worth documenting even though it's a small fix
It's a different failure category from everything else found in Phase 3 so far (P11's data reconciliation, P13/P18's duplicate transactions, P12/P17/P19/P20's judge behaviour). Worth keeping the taxonomy complete: an eval suite generated across multiple related datasets in one pass has a real, if small, risk of details bleeding between them, and it's cheap to check for systematically (as done here) rather than assuming a single caught instance is the only one.

### Iteration notes

*Add notes here after re-running the freelancer smoke test — confirm eval_033 passes. If café, electrician, and freelancer are all simultaneously clean, proceed to the full 50-case run.*

---

## P22 — Full-period context gap, and a missing manual prompt edit found during audit

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Finding A — eval_033 was a real, recurring gap, not variance
Unlike `eval_005`'s one-off miss (likely ordinary answer-to-answer variance), `eval_033` had failed consistently across multiple runs on the same criterion: the app never mentioned the January opening balance or full-financial-year growth when asked "how's my bank balance looking at the end of the financial year." Investigating showed this is a genuine, repeatable gap — the app was correctly reporting the most recent month's own opening-to-closing movement, but a broad "how am I doing" style question is actually asking about the trend across the whole period, not just the final month's snapshot.

**Fix:** added explicit guidance to P04's answer-format section: for broad balance/cash-position questions (as opposed to a specific month), retrieve the earliest month's opening balance too and frame the answer around the full-period change, not just the most recent month's movement.

### Finding B — a full audit of the live system prompt against every fix requested this session
Given how many manual `prompts/system_prompt_v1.txt` edits had been requested across this session (P14, P15 ×2, P16 ×3), it was worth checking the actual live file directly rather than assuming everything landed. The user pasted the full file for review. Result: P15 and P16's five additions were all correctly present, word for word — that wasn't the cause of `eval_005`'s tax-advice slip after all (that one really does look like ordinary variance, since the rule that should have caught it was genuinely there).

What *was* missing: the P14 cash-basis instruction (answer "how much did I bring in" with cash received, not invoiced-but-unpaid amounts). This hadn't caused a visible failure yet, because the actual fix for that behaviour was mostly carried by the tool layer (`get_transactions` clearly labels `total_amount_cash_received` in its own output), so Claude was following it correctly per-call even without the prompt reinforcement — but it's worth adding for robustness, since relying on a tool's field naming alone is less durable than having the system prompt state the rule explicitly too.

### Why the audit was worth doing even though it mostly came back clean
A "did you paste this in" checklist across many session-scattered fixes is exactly the kind of thing that's easy to lose track of over a long iterative session — checking systematically rather than assuming was the right call, even though it turned out most fixes had landed correctly. Worth doing again before considering Phase 3 fully closed out, given the number of manual edits accumulated across P14–P22.

### Iteration notes

*Add notes here after: (1) confirming eval_runner.py is genuinely up to date on the machine actually running these tests — repeated instances this session of old error-message formats appearing despite the file supposedly being replaced, worth resolving directly rather than assuming it's fixed; (2) adding the P14 instruction to the live prompt; (3) re-running café and freelancer smoke tests to confirm eval_005 (variance) and eval_033 (real gap, now fixed) both pass.*

---

## P23 — Root cause of eval_001's recurring parse failure: found via a better error message

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### What the improved diagnostics (P20) finally revealed
With the failure-position-centred error message in place, the actual text around the break was visible for the first time: the judge was writing a complete JSON object, then — inside that same response — writing "Wait, I need to re-check my verdict field against my reasoning" in plain text, and starting a **second**, corrected JSON object afterward. This is a genuinely different root cause from every previous round (P12, P17, P19, P20): not a rounding issue, not an external-formula assumption, not a length limit — the judge was self-correcting mid-response and producing two JSON documents instead of one.

### Why this was happening structurally, not randomly
The JSON schema in the judge prompt had always listed `"verdict"` as the *first* field, before `must_include_results` and `must_not_include_results`. That ordering meant the model had to commit to an overall pass/fail conclusion before it had actually written out its criterion-by-criterion reasoning — the reasoning that determines whether the verdict should be pass or fail happens in fields that come *after* verdict in the schema. By the time the model worked through the individual criteria later in the same object, it would sometimes find its own early-committed verdict didn't match its own later reasoning, and (having no other way to fix an already-written field) it started over with a second object rather than editing the first.

### The fix — reorder the schema so conclusions come after reasoning
Changed the JSON schema so `must_include_results` and `must_not_include_results` come first, and `verdict`/`overall_reason` come last — forcing the model to work through every criterion before it's structurally able to write a conclusion. Also added an explicit instruction: if reasoning reveals the verdict should differ from an initial impression, revise the verdict field itself rather than writing a second object.

### A second, independent layer of defence
Alongside the prompt fix, replaced the naive "first `{` to last `}`" JSON extraction with a proper parser that tracks brace depth and correctly ignores braces inside quoted strings, stopping precisely at the end of the *first* complete, balanced object — tested directly against a synthetic version of this exact failure pattern (two objects, with a brace embedded inside a string value, to make sure that edge case doesn't trip up the depth counter either) before shipping it. This means even if the judge does still occasionally produce a self-correction despite the reordering, the runner correctly extracts a single valid, parseable object instead of failing outright.

### Why the schema reorder matters more than the extraction fix
The extraction fix only helps the runner cope with the symptom; the schema reorder addresses why the model needed to self-correct in the first place. Worth noting for future prompt work generally: when a structured-output schema asks for a conclusion before the reasoning that produces it, the model is being set up to either commit prematurely or awkwardly restart — output ordering is itself a prompt design decision, not just a data format choice.

### Also worth recording: several rounds of this session's debugging had a "which file am I actually running" problem
Multiple times across P20–P23, error messages that should have reflected an already-applied fix kept showing old formats, traced each time to the local `eval_runner.py` not actually having been replaced (confirmed via targeted `grep` checks before re-diagnosing). Worth remembering as a general debugging habit: before spending more effort diagnosing "why didn't my fix work," confirm the fix is actually present in the file being executed.

### Iteration notes

*Add notes here after re-running the café and freelancer smoke tests with the reordered schema and the new extractor — confirm eval_001 and eval_034 both pass cleanly, then finally commit to the full 50-case run.*

---

## P24 — Stop trusting the judge's own summary verdict; compute it

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### What happened
After P23's schema reordering (reasoning before verdict), `eval_001` failed once more — but this time the raw output showed something genuinely new: every single `must_include` was `satisfied: true`, every `must_not_include` was `violated: false`, and the judge's own `overall_reason` text explicitly said *"the verdict should be pass."* Yet the `verdict` field itself, written right next to that sentence, said `"fail"`. The model's itemised reasoning and its own summary conclusion directly contradicted each other, even with the reordered schema that was specifically meant to prevent exactly this.

### What this means
Across P12, P17, P19, P20, and P23, every fix so far tried to get the judge's *reasoning* right — better tolerance rules, better arithmetic instructions, better field ordering. This case shows those fixes can all succeed (the reasoning here was completely correct) while the model still fumbles the very last step: summarising its own conclusion into a single word. That's not a reasoning problem to prompt away — it's an unnecessary extra step that doesn't need to be delegated to the model at all.

### The fix — compute the verdict instead of asking for it
The judge's itemised `satisfied`/`violated` booleans have been reliable throughout this project's entire debugging process — every specific criterion check reviewed across dozens of cases has held up. The unreliable part was always the model's own aggregation of those booleans into a final word. So: `eval_runner.py` now computes the verdict itself, deterministically, from the itemised results (`pass` only if every `must_include` is `satisfied: true` and no `must_not_include` is `violated: true`) — and overrides the model's own `verdict` field with that computed value whenever they disagree, keeping the model's original verdict and a note in `overall_reason` for transparency rather than silently discarding it. Verified directly against the real failing case from this session: correctly flips `fail` → `pass`, matching what the itemised results actually showed all along.

### Why this is the right place to stop patching the prompt
This closes out the whole thread that ran from P12 through P23: rather than a sixth round of prompt tuning hoping the model's summary judgment becomes reliable, the fix removes the unreliable step from the critical path entirely. The model is still asked to produce `verdict` and `overall_reason` (useful for a human skimming results), but the runner's actual scoring — what counts as pass/fail in the summary stats — no longer depends on the model getting that one summarising step right. This is a good general pattern for using an LLM as a judge: have it produce granular, checkable claims, and compute the aggregate conclusion in code rather than asking the model to do that arithmetic itself.

### Iteration notes

*Add notes here after re-running café and confirming eval_001 passes with the corrected verdict. Given all three personas have now independently reached 5/5 or been one fix away from it multiple times, and this fix addresses the actual root cause behind the recurring eval_001 saga specifically, this is a reasonable point to commit to the full 50-case run rather than another round of 5-case smoke tests — any remaining issues in the other 35 untested cases will surface there.*

---

## P25 — First full 50-case run: batch 1 of failures (invoices, direction, client-advice)

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
First-ever full run of the 50-case eval suite (with the P24 deterministic-verdict fix in place): 37/50 passed (74%). `cash_flow`, `gst_bas`, and `payroll` all hit 100%, confirming every persona-specific fix made across P11–P24 generalised correctly to the untested 35 cases, not just the 15 already smoke-tested. 13 failures remained, investigated in batches rather than all at once. This entry covers the first three: `eval_012`, `eval_025`, and `eval_028`.

### Finding A — a genuine schema gap: café invoices point the opposite direction from the other two personas
`eval_012` asked about outstanding supplier invoices. The app answered with a real, correct invoice (Pepe's Milk, $368.40) but wrapped it in a caveat claiming the invoices tool "is primarily set up to track invoices you've issued to your customers" — which is backwards for café specifically. Checking the raw data: café's `invoices` array uses a `supplier` field (bills the business owes — accounts *payable*), while electrician and freelancer use `client_name` (invoices issued to clients — accounts *receivable*). `tools.py`'s `_normalise_invoice()` was folding both into one generic `counterparty` field with no indication of direction, so the model had no way to know which way the money was flowing — and both the app's own narrative and the eval case's original expectation (which assumed café had no payables data at all) made the same wrong assumption independently.

**Fix:** added an explicit `direction` field (`"payable"` or `"receivable"`) and a `direction_note` to every normalised invoice in `tools.py`, and added guidance to P04 to check and state this explicitly. Corrected `eval_012` to expect the real, correct payable to be reported (rather than expecting a false "no payables tracked" claim).

### Finding B — another cross-contamination error in the eval suite, same category as P21
`eval_028` expected Apex Building Group's total to be $21,230 across three invoices. The real `invoices` array has exactly two Apex invoices totalling $15,730 — the "third invoice" (INV-2503, $5,500) actually belongs to a completely different client, Meridian Constructions. Same root cause as P21's café/freelancer figure mixup, this time between two clients within the same persona. The app's answer was exactly correct; the eval case had the data wrong.

**Fix:** corrected `eval_028`'s expected total, invoice count, and removed the phantom third invoice reference.

### Finding C — a real, generalizable guardrail gap: unprompted client-relationship verdicts
The same `eval_028` answer also included a "🔍 Are They Worth Keeping On?" section concluding "Apex looks like a solid commercial client" — a direct verdict on the business relationship, even though the question's own must_not_include explicitly forbade a keep-or-drop recommendation. Checking P04's existing guardrails: the P15 restriction on "operational or contractual strategies" (deposit terms, trade credit) doesn't clearly cover this different category — a relationship-worth judgement, not a tactical suggestion.

**Fix:** added a new, explicit guardrail: decline "worth it / keep or drop" verdicts on client or supplier relationships the same way other out-of-scope business advice is handled — present the facts, don't render the verdict, even if asked directly.

### Iteration notes

*Add notes here after re-running eval_012, eval_025, and eval_028 individually or as part of the next full run. eval_025 (Tarneit Stage 1 vs Stage 2 conflation) was investigated but not fixed in this batch — see next entry for reasoning. Remaining failures from this full run (eval_007, 008, 013, 022, 030, 036, 037, 038, 039, 046) to be triaged in subsequent batches.*

---

## P26 — Full-suite batch 2: the tax-adjacent systemic pattern, plus two more findings

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
A sandbox environment reset mid-session required rebuilding the working copy from files already saved to outputs across P11–P25 — a useful reminder that the incremental "save every fix immediately" habit throughout this whole project paid for itself here.

### Finding A — a systemic pattern across 4 of 5 tax_adjacent cases
`eval_009`, `eval_022`, `eval_030`, and `eval_036` all failed for what turned out to be the same underlying reason, once the actual answers were compared side by side: each one hedged appropriately ("generally," "may," "proposed") but then stated a *specific* number anyway — an exact $20,000 threshold, an exact "12 continuous weeks" logbook rule, an illustrative 75% GST-credit example, a "could be well above $100k" income projection, "repairs are immediately deductible" as a settled rule. The existing P04 guidance ("provide general AU tax context") never drew a line between naming *what concepts exist* (safe) and applying *specific figures* to the user's situation (not safe, per these cases) — hedging language alone wasn't enough once a concrete number was attached.

**Fix:** substantially rewrote the tax-adjacent guidance to define "general context" narrowly — name that a distinction, method, or threshold exists, without stating the specific number, percentage, or duration, even as a hedged illustration. Also added an explicit rule against speculating on the scale of the user's tax liability from partial-year data, which is what `eval_036` was actually catching. Worth noting: this tightens a rule that used to explicitly endorse naming a specific rate ("67c/hour" was the "Good" example in the original P04) — the new eval criteria want less specificity than that original example allowed, which is a real, deliberate policy tightening, not a bug fix.

### Finding B — another eval-suite data error, same category as P21/P25
`eval_037` expected May's income to total $16,940. Checked every May-dated invoice directly: the real total is $13,640 exactly, matching the app's answer to the cent, correctly excluding one invoice issued in May but paid in June (consistent with the P14 cash-basis rule). No combination of real invoices reaches $16,940 — this is the eval suite's own error, not the app's.

**Fix:** corrected `eval_037`'s expected total. Also noticed both `eval_034` and `eval_037` shared a real, generalizable gap: neither answer flagged Lumen Labs as a *new* client, even though it genuinely has only one invoice in the whole dataset — meaningful, easily-derivable context. Added guidance to P04: when a counterparty has only one invoice on record, note that it's a new/first-time relationship rather than just listing it alongside established ones.

### Finding C — a real content gap, likely LLM variance rather than a data/tool bug
`eval_023` asked for anything unusual across the whole electrician dataset. The answer correctly retrieved the Bergman invoice (158 days overdue, exact and correct) but stated "there's no note of a debt collector being involved" — while the raw data's `notes` field actually says "referred to a solicitor," a different but equally serious escalation. Checked directly: the data and the P13 `notes`-field fix are both fully intact, so this wasn't a regression — the answer had access to the right information and simply didn't surface it, in a long response juggling seven separate findings at once.

**Fix:** added explicit guidance to always check and surface escalation flags in the `notes` field (solicitor referral, debt collector, write-off) specifically, and to report exactly what the note says rather than paraphrasing it into a milder or different-sounding category (the "no debt collector" framing was true but misleading, since it implied no escalation at all when a different, real one existed).

### What's left from the first full run
`eval_007`, `eval_008`, `eval_025` (Tarneit Stage 1/2, still open), `eval_039` (client diversification advice — likely covered by P25's client-relationship guardrail once confirmed live, worth re-checking rather than assuming), `eval_043`, `eval_046` — to be triaged in a further batch.

### Iteration notes

*Add notes here after re-running the full suite with all P25 and P26 fixes applied.*

---

## P27 — Prompt caching for the system prompt and tool definitions

**Phase:** 3 — Claude API engineering  
**Used in:** `src/agent.py` (the `client.messages.create()` call)  
**Date:** [add date]

### Motivation
By this point in the project, the same system prompt (P04) and the same 6 tool definitions were being sent, unchanged, on every single API call — every turn of every CLI conversation, and every one of the 50 eval cases per full run. Given how many eval iterations this project ran across P11–P26 while debugging, that's a lot of repeated, identical token spend that prompt caching directly addresses.

### What was cached
The system prompt, via an explicit cache breakpoint:
```python
system=[
    {
        "type": "text",
        "text": self.system_prompt,
        "cache_control": {"type": "ephemeral"}
    }
],
```
Tool definitions are covered automatically, since prompt caching follows a fixed hierarchy — tools, then system, then messages — so a breakpoint on the system block also covers any static tool definitions that precede it, without needing a separate marker.

### Design decisions

| Decision | Reasoning |
|----------|-----------|
| Explicit breakpoint on the system prompt, not automatic caching | The system prompt (plus its per-persona date-context suffix from P08) is the one genuinely static, always-repeated block. An explicit breakpoint is predictable and easy to verify via `response.usage`, versus automatic caching's behaviour of following the last cacheable block, which is less obvious to reason about in a project this size |
| Default 5-minute TTL, not the 1-hour option | The two main use cases — a live CLI conversation and a batch eval run — both involve calls close together in time (well under 5 minutes apart), so the default TTL captures the benefit without paying the 1-hour cache's higher write cost |
| Accepted that caching doesn't cross personas | `agent.py` appends a different date-context block per persona (café/electrician/freelancer each get their own "most recent month" anchor), so each persona has a distinct full system prompt string and therefore a separate cache entry. This is a natural consequence of the P08 fix, not a caching design flaw — within one persona's block of calls (e.g. 15 eval cases run back-to-back), the cache is fully shared |

### Expected impact
Cache reads cost 10% of normal input tokens on Sonnet; cache writes cost 25% more than normal input tokens once. For any sequence of calls sharing the same system prompt within the 5-minute window — which describes both a multi-turn CLI conversation and a same-persona block of eval cases — the first call pays a small premium and every subsequent call gets a substantial discount on the repeated portion of the prompt.

### Iteration notes

*Add notes here after confirming via `response.usage` that `cache_read_input_tokens` is non-zero on the second and later calls within a session, and after comparing Console usage costs for an eval run before/after this change.*

---

## P28 — Full-suite batch 3: whack-a-mole regressions, a broader catch-all, and the "lately" fix

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context: fixes aren't monotonic
Comparing this full run to the previous one directly: 7 previously-failing cases genuinely passed this time (008, 009, 022, 023, 030, 034, 037 — confirming P26's tax-adjacent rewrite and new-client/escalation-note guidance held). But 7 *different* cases failed that weren't failing before (004, 005, 016, 026, 038, 041, 047). Net score unchanged (37/50), but a mostly different 13. This is expected, not a sign of regression: tightening behaviour in one direction shifts which borderline questions land differently elsewhere, since these are freshly generated answers each run, not deterministic lookups. Worth stating plainly rather than chasing an illusion of monotonic progress — the useful signal is whether specific, previously-fixed issues stay fixed (they did) and whether new failures are genuinely new problems or old ones in a different shape (mostly the latter, as this entry shows).

### Finding A — the narrow-bullet approach to business-advice guardrails kept leaking
`eval_039` failed on a *third* distinct shape of unsolicited business advice — suggesting the user "build a third source of reliable recurring income." P15 covers operational tactics (deposit %, payment terms); P25 covers client keep-or-drop verdicts; neither covers strategic growth suggestions. Adding a fourth narrow bullet to catch this specific phrasing would just set up a fifth failure with a different phrasing next time — the actual pattern is that *any* specific list of forbidden advice types is chasing a moving target.

**Fix:** replaced the growing bullet list with one general principle stated first: never suggest actions the user should take to change how they run their business, of any kind or scope — with the previous specific examples (deposit tactics, client verdicts) kept as illustrations of the principle rather than the whole of it. Added a concrete self-check: if the model is about to write "you might want to," "consider," or "worth exploring" pointed at a business decision, that's the signal to stop and redirect to an advisor instead.

### Finding B — `eval_046` was never actually fixed, despite being flagged as a target since batch 1
Genuinely untouched until now: asked "have I been spending more than usual lately," the app silently interpreted "lately" as the full 6-month dataset and answered as if that were the obvious, only reading — no acknowledgement that "lately" is vague, no offer to use a different window. The existing "if the data is ambiguous, say so" guardrail covers *missing data*, not *vague language in the question itself*, which is a different kind of ambiguity.

**Fix:** added an explicit rule for vague time references in the question ("lately," "recently," "these days"): state which period was chosen and why, so the assumption is visible and correctable, rather than resolving it silently.

### Finding C — a likely-missing manual edit, not a weak fix
`eval_036` failed on exactly the pattern P26 was written to prevent (annualising partial-year income and implying the instalments might not cover the resulting liability). Given how many times this session a fix has lived correctly in `PROMPTS.md` without making it into the actual live `prompts/system_prompt_v1.txt`, this is the leading suspect over "the P26 wording wasn't strong enough" — flagged for direct verification against the live file rather than writing a third version of the same guardrail on assumption alone.

### What's left
`eval_004`, `007`, `016`, `025`, `026`, `038`, `041`, `043`, `047` — some of these (016, 026, 041, 047) look like they could be further eval-suite data errors similar to P21/P25/P26's pattern rather than app bugs, based on a first read of the failure reasons (e.g. `eval_026`'s "$16,830" aggregation and `eval_016`'s conflicting due-date expectation both sound like they need direct data verification before assuming the app is wrong). To be triaged in the next batch.

### Iteration notes

*Add notes here after: (1) confirming whether eval_036's failure was a missing manual edit or a genuine prompt gap; (2) re-running the full suite with this batch's two fixes; (3) triaging the remaining ~9 cases, checking data first for anything that looks like a suspicious dollar figure or conflicting expectation before assuming the app is at fault.*

---

## P29 — Full-suite batch 4: a genuine conflict between two of our own guardrails

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
86% (43/50), café a clean 15/15. The P26 tax-adjacent rewrite and the fixes from P28 were confirmed to have actually landed in the live prompt this time (verified by direct file review), closing out `eval_022`, `eval_030`, and several others cleanly. 7 cases remained.

### Finding A — the most interesting one: two guardrails directly contradicting each other
`eval_034` and `eval_037` both still failed on "Lumen Labs not identified as promising/new." Reading the actual answers closely: they *do* correctly note Lumen has only one invoice and was paid early — but stop short of characterising it as promising or retainer-worthy. That's not an oversight; it's the P28 catch-all working exactly as designed ("never suggest actions... including changing which clients to prioritise... if about to write 'worth exploring,' stop and redirect to an advisor"). P28 was actively suppressing the exact framing P26's new-client guidance was trying to produce. Two rules, written in different batches for different failures, turned out to want opposite things for this specific case.

**Fix:** drew an explicit line between *observation* and *prescription* — describing that a new relationship looks promising based on its own data (large first invoice, paid early) is a factual, descriptive interpretation, squarely within scope; recommending an action based on that observation ("you should pursue a retainer") is the out-of-scope part. The rule now says: characterise the pattern, don't recommend acting on it.

### Finding B — the tax-liability rule made the model too cautious on safe arithmetic
`eval_036` no longer had any harmful liability speculation (P26 worked completely here) — but now failed for the opposite reason: it wouldn't even state that four $1,800 quarterly instalments sum to $7,200, a plain, safe fact about the user's own recorded payments. The P26 wording ("never speculate about the scale of tax liability") was broad enough that the model generalised it to avoid *any* number near the topic of tax, including harmless arithmetic.

**Fix:** added an explicit carve-out distinguishing the two: totals of what's already happened (safe, just addition) versus any claim about what the user will owe or whether that's enough (restricted). Named the exact $7,200 example directly so the distinction is concrete, not just abstract.

### Finding C — three smaller, more straightforward fixes
- `eval_026`: the answer correctly retrieved and described two separate outstanding invoices but never stated their combined total, leaving the user to do the addition. Added a general rule: when multiple related amounts are mentioned together, state the combined total explicitly.
- `eval_025`: finally addressed after being left open since batch 1 — "the Tarneit job" (singular) kept getting answered with a combined Stage 1 + Stage 2 total. Added explicit guidance: when a search term could match multiple similarly-named jobs and the question's phrasing implies one specific job, answer about the single best match rather than silently merging, or ask if it's genuinely unclear.
- `eval_046`: still failing despite the P28 fix being confirmed live. Investigating the likely cause: the earlier, more specific P08 rule ("resolve 'last month' to the dataset's most recent month") was probably winning out over the newer, more general vague-time-reference rule, since "lately" and "last month" can feel similar. Added an explicit contrast between the two rules directly in the guardrail text, so the model doesn't extend its confident handling of well-defined relative terms to genuinely ambiguous ones.

### Why Finding A is the most valuable one to remember
Every other fix so far this project has been "the app is missing something" or "the eval case is wrong." This is the first case where two things we deliberately, correctly added were each individually reasonable and still produced a bad outcome together. It's a good reminder that a system prompt's rules don't compose automatically just because each one made sense in isolation — a later, broader guardrail can silently swallow an earlier, narrower one's intended effect, and the only way to catch that is by testing the whole system together, not by re-verifying each rule alone.

### Iteration notes

*Add notes here after re-running the full suite with all five fixes from this batch applied.*

---

## P30 — A partial application caught mid-batch, plus a new judge blind spot

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
`eval_034`/`eval_037` (Lumen) passed after adding the observation-vs-prescription fix — but `eval_025`, `eval_026`, `eval_036`, and `eval_046` all failed again on *exactly* the same criteria P29 was meant to fix. Given the session's now-established pattern of live-prompt edits landing partially, the most likely explanation was simpler than a weak fix: of P29's five separate snippets, only the one specifically re-requested (the new-client paragraph) had actually been added. Rather than diagnose each of the four "still failing" cases as if they were fresh problems, the decision was made to stop distributing fixes as individual snippets entirely and provide the complete system prompt body as one file going forward, removing this whole category of uncertainty.

### Finding A — a genuinely new judge blind spot: GST-basis equivalence
`eval_039` failed with the judge stating the answer "uses $2,200/month per retainer instead of the correct $2,420/month... potentially invented." Checked directly: $2,420 (inc-GST) ÷ 1.1 = $2,200.00 (ex-GST) exactly. The app's answer was internally consistent throughout, explicitly labelling every figure "Ex-GST" in its own table headers — it hadn't stated a different number, it had stated the *same* number on a different, self-declared basis. The judge's arithmetic-verification instructions (P12, P17, P19, P20, P23, P24) had never covered this specific case: two numbers that are the same fact expressed on opposite sides of a 1.1 multiplier.

**Fix:** added explicit guidance to the judge prompt to check GST-basis equivalence (divide/multiply by 1.1) before concluding a must_include figure is missing or wrong, with the exact $2,420/$2,200 pair as a worked example.

### Finding B — a small, genuine gap: vague "recent period" phrasing
`eval_047` asked about a financial year outside the dataset. The answer correctly declined and explained why, but only said data covers "a more recent period... up to June 2025" — never naming the actual range. Added an explicit requirement to name the real coverage period (e.g. "January–June 2025, FY2025") rather than a vague gesture at "more recent."

### `eval_038` — flagged but not acted on
The answer already follows the established, correct hedging pattern (names that methods exist, defers the specific method to a tax agent) — this looks like it could be judge over-strictness rather than a genuine violation, but with only one data point it's not yet clear enough to justify a prompt change. Worth re-checking after the next run rather than guessing at a fix now.

### Iteration notes

*Add notes here once the consolidated system prompt file (rather than individual snippets) has been confirmed live, and the full suite re-run. If eval_025/026/036/046 all clear on the next run, that confirms the P29 fixes were sound and the issue really was partial application, not weak wording — worth stating explicitly either way, since it changes what the next debugging step should be.*

---

## P31 — Judge retry mechanism, two content fixes, and an honest note on reliability limits

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
The consolidated system prompt file (P30) confirmed its fixes worked cleanly: `tax_adjacent` reached a full 5/5, and several previously-flagged cases passed. 8 cases failed this run — investigated individually rather than assumed to be more missing edits, since the consolidated file removed that whole category of doubt.

### Finding A — `eval_046` was a pure judge tooling bug, not an app issue
Reading the partial judge output (captured despite the parse failure) showed the actual answer was correct — it explicitly acknowledged "lately" was ambiguous and offered multiple interpretations, exactly what the rule asks for. The failure was a JSON syntax error (a missing comma) in the judge's own output, a new malformation pattern distinct from the truncation (P20) and multi-object (P23) issues already handled.

**Fix:** rather than adding a fifth narrow patch for a fifth JSON malformation variant, added a retry: on a parse failure, the judge gets one more attempt with an explicit note about what broke ("respond again with ONLY a single, strictly valid JSON object..."). This is a more durable fix than continuing to enumerate specific syntax failure modes one at a time — malformed JSON from an LLM is usually a one-off slip, and a second attempt resolves most of these without knowing in advance what shape the next slip will take.

### Finding B — `eval_005`: the model correctly followed a rule that shouldn't have applied
The answer's closing line ("the ATO draws a distinction between repairs and capital improvements... a question for [your tax agent]") is almost verbatim the "Good" example written into P04's tax-adjacent guidance. The model wasn't malfunctioning — it followed the rule precisely. The actual issue: the question was about an anomaly, not tax, and the rule about hedging tax mentions correctly was being applied to content the model shouldn't have volunteered in the first place.

**Fix:** added an explicit distinction between "the question is about tax" (full tax-adjacent treatment applies) and "the model is choosing to bring up tax on a question that wasn't about tax" (better to just not raise it — describe the data, not its tax treatment, unless asked).

### Finding C — `eval_043`: a genuine, previously-unaddressed content gap
Asked broadly "do I have payroll obligations," the answer correctly said no employees exist, then only addressed PAYG *withholding* (an employer concept) — never mentioning that PAYG *instalments* (the sole trader's own income tax prepayments) are a completely separate thing that applies regardless of employee count. The two concepts share a name and got conflated as a result. This is the first batch where this case got a dedicated fix rather than being left as presumed variance.

**Fix:** added an explicit clarification to the AUSTRALIAN CONTEXT section: PAYG withholding (employer-side) and PAYG instalments (owner's own tax) are genuinely different, "no employees" doesn't mean "no PAYG obligations," and a broad obligations question should address both.

### An honest assessment: `eval_026`, `eval_037`, and `eval_023`
These three have now failed on the same criteria across multiple rounds despite prompt guidance that directly addresses them (the P29 combined-total rule for `eval_026`; the P29 observation-vs-prescription rule for `eval_037`, which *did* pass once before reverting; the P13 escalation-note rule for `eval_023`). At this point the evidence points toward genuine instruction-following unreliability on open-ended, free-form answers, not a wording gap — the rules exist, are confirmed present in the live prompt, and simply aren't being applied every single time. This is worth stating plainly rather than writing a sixth variant of the same instruction hoping for a different result: an LLM-driven system doesn't guarantee 100% rule compliance no matter how precisely the rule is worded, especially for judgment calls embedded in long, multi-finding answers (all three of these are open-ended "what's unusual/what's my situation" questions, not narrow factual lookups). A genuinely more reliable fix for `eval_026` specifically might be a tool-level one — having `get_invoices` or similar return a pre-computed combined total when multiple outstanding items are returned together, removing the arithmetic step from the model's responsibility entirely — worth considering for a future iteration rather than more prompt tuning.

### Iteration notes

*Add notes here after re-running the full suite with these fixes. Worth explicitly checking whether eval_026/037/023 clear on this run — if they do, the "reliability limit" read above was wrong and it really was still a coverage gap; if they don't, that's further evidence for documenting this as a known, accepted limitation of the prompt-only approach in `ARCHITECTURE.md` rather than continuing to chase it.*

---

## P32 — 88%: one more eval-suite fiction, one genuine new gap, and a status check on the persistent three

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
44/50 (88%). All of P31's targeted fixes held (`eval_005`, `009`, `026`, `036`, `043` all passed). `eval_046` failed again despite the judge retry mechanism — worth noting this confirms it, since a retry-triggered failure would show a "truncated/malformed" reason, and this one didn't; the judge parsed fine and correctly reported a real content miss. That's useful signal: this one really is the app not following the rule, not a tooling artifact.

### Finding A — another case of the eval suite expecting fictional detail
`eval_025` wanted a specific itemised materials list (switchboard components, sub-mains cable, busbars, DBs, MCBs, conduit) for the JOB-2506 purchase. Checked the raw transaction directly: the actual data only has a generic description, "New build materials - Tarneit rough-in." No itemised breakdown exists anywhere in the dataset. This eval case was unpassable as written — genuinely funny in hindsight, since its own `must_not_include` said "invented material items" while its own `expected_behaviour` invented exactly that.

**Fix:** corrected `eval_025` to expect the transaction reported accurately at the level of detail the data actually provides, rather than a fictional item list.

### Finding B — a genuine, newly-surfaced content gap
`eval_041` asked "how much do I have right now" — the answer correctly gave the June 2025 closing balance but presented it as if confirmed-current, with no acknowledgement that the dataset has a fixed end point and "right now" in the real world is well past that. A reasonable, previously-unaddressed gap: any "current/right now" style question answered from historical data should note it's the last recorded figure, not a live confirmation.

**Fix:** added explicit guidance requiring this caveat whenever present-tense language is used. (Caught and corrected a self-inflicted editing mistake while making this change — an early version of the edit accidentally deleted the `## Data-grounded answers` section header and its numbered structure; caught by reviewing the diff before finalising, restored immediately. Worth noting as its own small lesson: even a targeted, well-understood fix needs the same "verify what actually landed" discipline as everything else in this project.)

### Status check on the three flagged as reliability limits in P31
- `eval_026`: passed this run. Consistent with the P31 read that this was genuine LLM variance around an existing, correct rule, not a coverage gap — the rule didn't change between runs.
- `eval_037` (Lumen): failed again. Third time flipping between pass and fail across recent runs with no rule changes in between. Strengthens the P31 conclusion that this is inherent variance on an open-ended interpretive question, not something further wording will reliably fix.
- `eval_023` (Bergman/Tarneit anomaly set): failed again, and specifically contradicts the Bergman solicitor referral this time (says the opposite of what P13's escalation-note rule should produce). Given this is the most safety-relevant of the three (missing a real business-risk signal, not just a stylistic miss), it's the one most worth a structural rather than wording-based fix in a future iteration — e.g. having `get_invoices` proactively surface any invoice with a non-empty `notes` field as a distinct flagged item, rather than relying on the model to notice and prioritise it correctly inside a long, multi-finding free-form answer.

### Iteration notes

*Add notes here after re-running the full suite with eval_025's correction and the eval_041 fix applied. `eval_007` (café interpretation) has now gone unaddressed across several batches — worth a dedicated look next round rather than continuing to deprioritise it.*

---

## P33 — 90%: two overcorrections from our own recent fixes

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
45/50 (90%). `shared` reached a clean 5/5 — `eval_046` finally passed with no rule changes since P32, good evidence that one really was variance rather than a permanent gap. `eval_026` and `eval_041` both held from the previous run.

### Finding A — `eval_025`: our own disambiguation rule overcorrected into asking instead of answering
The P29 fix for the Tarneit Stage 1/2 conflation issue told the model to ask for clarification when a job reference was "genuinely unclear." This time, asked "what materials did I buy for the Tarneit job," it did exactly that — listed both Stage 1 and Stage 2, then asked which one was meant, instead of answering about the most likely one (the original, Stage 1) directly. Defensible behaviour in isolation, but not what the eval (or a real user asking a quick question) actually wants — asking first, before attempting an answer, is a worse experience than answering the likely case and offering the alternative.

**Fix:** rewrote the rule to default to answering the most specific/likely match (the first/original job by date) directly, then mention the related second job as an offer rather than a blocker. Reserved the "ask before answering" behaviour for genuine ties where there's no reasonable default to guess from.

### Finding B — `eval_043`: the PAYG fix was so good it crowded out superannuation
The P31 PAYG-distinction fix worked essentially verbatim — the answer's language on PAYG withholding vs instalments almost matches the rule text directly. But in focusing entirely on PAYG, the answer dropped superannuation coverage entirely, which an earlier version of the same answer used to include. A broad "do I have payroll obligations" question needs all three relevant things confirmed (PAYG withholding, PAYG instalments, superannuation), not just the one most recently reinforced by prompt guidance.

**Fix:** extended the PAYG guidance to explicitly require confirming all three elements for broad obligations questions, naming superannuation directly so it isn't the thing that gets dropped next time something else gets emphasised.

### Pattern worth naming
Both of these are the same shape of problem: a targeted fix for one specific failure, applied correctly, produced a new and different failure by being *too* effective in one direction. This is a slightly different lesson from P29's "two guardrails conflicting" — here it's one rule doing exactly what it was told, at the expense of something adjacent it wasn't explicitly told to preserve. Worth remembering for any future prompt work: a fix that clearly solves the case it was written for still needs to be checked against the neighbouring cases it might crowd out, not just the one it targeted.

### Remaining open cases
`eval_008` (Easter reference still missing — untouched this batch), `eval_023` (Bergman/Tarneit anomaly set — still the most safety-relevant open item, best candidate for a structural rather than prompt-based fix), `eval_037` (Lumen — now failed in 3 of the last 4 runs with no rule changes in between, essentially confirmed as inherent variance rather than a coverage gap at this point).

### Iteration notes

*Add notes here after re-running with the eval_025 and eval_043 fixes. Worth a decision point here: at 90% with the remaining gaps well-understood and mostly non-critical, this may be a reasonable place to treat Phase 3 as substantially complete and move toward Phase 4, rather than continuing to chase eval_037 specifically, which the evidence suggests won't be resolved by further prompt tuning.*

---

## P34 — A genuine tool-level gap, not a prompt issue: no description search existed at all

**Phase:** 3 — Claude API engineering  
**Used in:** `src/tools.py` (`get_transactions`)  
**Date:** [add date]

### Context
41/50 this run, but two of the nine "failures" (`eval_014`, `eval_015`) were plain network connection errors, not real results — excluded from analysis. `eval_042` was the one genuinely new, previously-unseen failure worth investigating properly.

### Finding A — a real retrieval bug, not a prompt-wording issue
Asked "I've been spending on coffee shop working sessions — is that legit as a business expense," the app confidently answered "I don't see any café or coffee-related transactions recorded in your data." This was false: 4 real transactions exist (`Coffee meeting - client strategy session`, `Coffee - working from cafe, client research`, etc.), all correctly categorised as `Client Entertainment`, totalling $85.80. This is the first failure this session traced to a genuine capability gap in the tool layer rather than a data error, a judge error, or a prompt-wording gap: `get_transactions` could filter by category, date, and type, but had **no way to search transaction descriptions for a keyword at all**. Since "coffee shop" doesn't textually match the category name "Client Entertainment," there was no path — prompt engineering alone couldn't have fixed this, because the underlying tool genuinely lacked the capability being asked of it.

**Fix:** added a `keyword` parameter to `get_transactions` that does a case-insensitive substring match against both `description` and `paid_to_from`, for exactly this situation — a user describing something in their own words that doesn't map to the internal category taxonomy. Verified directly against the real failing scenario: `get_transactions(data, keyword="coffee")` now correctly returns all 4 real transactions.

**Important caveat, not yet resolved:** the Python function now supports this parameter, but the actual tool *schema* sent to the Claude API (the JSON definition of available parameters, defined separately in `agent.py`) needs to also expose `keyword` as an available argument, or the model has no way to know it can use it — a function change alone doesn't teach the model anything if the schema it sees hasn't changed to match. This project's `agent.py` has been edited directly on the user's machine throughout Phase 3 rather than through this working copy, so this schema update needs to be applied there directly; flagged clearly rather than assumed done.

### Finding B — a judge false positive that traces back to an overly broad criterion, not judge behaviour this time
`eval_025` failed again, this run claiming an "invented itemised material list" for the Stage 2 purchase. Checked directly: JOB-2521's own transaction description genuinely says "Rexel - switchboard, busbars, cable for Tarneit Stage 2" — the app was accurately reporting real, grounded data, not inventing anything. The mock data itself has inconsistent detail levels between jobs (JOB-2506 generic, JOB-2521 itemised) — realistic, but the eval case's `must_not_include` was written broadly enough to treat any itemisation as suspicious, based only on JOB-2506's (item-free) data.

**Fix:** narrowed `eval_025`'s must_not_include to specifically forbid inventing itemised detail *for JOB-2506*, or presenting Stage 2 detail as if it belonged to JOB-2506 — not forbidding accurate itemisation of Stage 2's own, genuinely-itemised data.

### Why Finding A is worth calling out specifically
Every other fix this session has been a data correction, a prompt guardrail, or a judge robustness improvement — this is the first one that required changing what the *tool itself is capable of doing*, because no amount of system-prompt wording can make a function search a field it was never given the code to search. Worth remembering as a general principle: when a capability doesn't exist in the tool layer at all, that's a different category of problem from the model not being told to use a capability that does exist, and it needs a different kind of fix.

### Iteration notes

*Add notes here after: (1) confirming the `keyword` parameter has been added to agent.py's tool schema (not just the Python function) and manually testing the café question again; (2) re-running eval_014/015 (network errors, not real failures) to get a clean read; (3) re-running the full suite.*

---

## P35 — Reading the score correctly, and a recommendation to stop chasing the last cluster

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
86% (43/50) looked like a regression from the previous 90% run, but wasn't one on closer reading. `eval_021` was a network connection error, not a real judged result — excluding it, the real comparison is 43/49 (~88%), essentially flat. More importantly: `eval_042` (the café keyword-search fix from P34) and `eval_023` (the anomaly-detection case flagged as most safety-relevant in P32) both passed this run, confirming those fixes genuinely held. The cases that failed — `eval_007`, `008`, `037`, `038`, `046` — are the exact same cluster that has been flipping between pass and fail across the last four or five full runs, with no rule changes in between most of those flips.

### Finding — `eval_025` reverted to its original failure mode
This run, the answer invented itemised component detail for JOB-2506 again — not the Stage-2-confusion variant fixed in P34, but the original hallucination the IDENTITY section's grounding rule is supposed to prevent. Given the rule already existed and was already being followed correctly in some runs, this looks like the same category of instruction-following variance affecting the other persistent cases, rather than a missing rule. Made the existing grounding principle more explicit anyway — extending it from "don't invent figures or date ranges" to also explicitly name "don't invent itemised component detail" — on the reasoning that a more concrete, specific statement of an existing rule sometimes measurably reduces (even if it can't eliminate) this kind of slip, as seen with several earlier fixes in this project.

### A clear-eyed recommendation, based on now-substantial evidence
Across roughly ten full-suite runs (P25 through P35), a consistent cluster of five to seven cases — mostly open-ended, interpretive, or multi-step questions (Lumen Labs' "new client" framing, home-office tax hedging, month-by-month breakdowns, "lately" clarification, Easter seasonality) — has continued to flip between pass and fail with no correlation to specific rule changes. Every one of these has already received at least one, and in several cases two or three, rounds of targeted prompt refinement. The evidence at this point supports treating this as the practical ceiling of what prompt-only engineering can guarantee for free-form generated answers, not a set of unsolved bugs waiting for the right wording.

**Recommendation:** treat ~86-90% as the project's stable, defensible pass rate rather than continuing to chase a clean 50/50 through further prompt iteration. Two structural alternatives would likely do more than another wording change, if pursued in a future phase: (1) for `eval_025`/`eval_023`-style cases specifically, move the "don't lose this detail" burden from the prompt into the tool layer (e.g. `get_invoices` proactively flagging any `notes` field as a separate structured item, `get_transactions` returning an explicit `has_itemised_detail: false` flag rather than relying on the model to notice and preserve that absence correctly every time); (2) running the eval suite multiple times and reporting a rolling pass rate, rather than treating any single run's number as the definitive score, which better reflects what's actually true about a probabilistic system.

### Iteration notes

*This is a natural point to shift attention to Phase 4 (README, ARCHITECTURE.md, demo, LinkedIn) rather than further Phase 3 eval-chasing — the remaining failures are well-understood, documented, and low-severity, which is itself a demonstrable outcome of the debugging process, not a gap in it.*

---

## P36 — Another eval-suite arithmetic error, and a correction to a live prompt example it exposed

**Phase:** 3 — Claude API engineering  
**Date:** [add date]

### Context
88% (44/50), consistent with the P35 read: the same known variance cluster (`eval_007`, `023`, `037`, `046`) fluctuated again, while `eval_008` and `eval_038` flipped back to passing. `eval_025` improved — the item-invention issue from P35 is gone, replaced by a narrower precision slip (stating "6+ weeks" instead of the exact 52 days), which fits the same variance pattern rather than a new gap. `eval_036` was the one worth checking properly.

### Finding — the eval case expected a payment that was never recorded
`eval_036` expected "four PAYG instalment payments... totalling $7,200." Checked the real dataset: exactly three PAYG payments exist (28 Jan, 28 Mar, 25 Jun — Q2, Q3, Q4), summing to $5,400. There's no fourth payment anywhere in this 6-month dataset; a Q1 payment, if it exists, would fall before January and outside this data's coverage. The eval case's own `expected_behaviour` text was internally contradictory — it named only three specific months while claiming "four payments" — a straightforward counting error at generation time, not an app bug. The app's $5,400 answer was completely correct; stating $7,200 would actually have required projecting an unrecorded payment, exactly what the tax-liability guardrail correctly prevented.

**Fix:** corrected `eval_036`'s expected total and must_include list to the real, verified figure.

### A more important secondary fix: the live prompt itself repeated the same wrong assumption
The P29/P33 fix that carved out "safe arithmetic" from the tax-liability restriction used "four quarterly PAYG instalments... $7,200" as its worked example — written before this specific miscount was caught, and copied the same wrong assumption (that a dataset always has exactly four quarters of instalments) directly into the live system prompt. Left as-is, this would have actively taught the model to expect four payments even when only three are actually recorded — a bug in the *fix* itself, not just in the eval case.

**Fix:** rewrote the live example to be generic and correct: count what's actually recorded rather than assuming quarterly instalments always number four, since a 6-month dataset will often only contain part of a year's worth.

### Why this is a good one to end on
This is the clearest example yet of why every fix in this project has needed independent verification against the real data, not just internal consistency with its own reasoning — a specific worked example can be well-written, pass its own internal logic check, and still bake in a wrong assumption that only shows up once a real dataset happens to violate it. The fix for a different case (P29's PAYG carve-out) ended up needing its own fix, two rounds later, once a different question exposed the same underlying error from a different angle.

### Iteration notes

*With this correction, all of the currently-known eval-suite data errors (P21, P25, P26, P28, P29, P32, P34, P36) have been fixed against verified real data. The remaining open cases (`eval_007`, `023`, `025`'s day-precision slip, `037`, `046`) are the documented variance cluster from P35 — no further action planned unless a future run reveals a genuinely new failure mode among them.*

---

## Prompt engineering principles — what this project taught me

*This section to be completed at the end of the project. Intended for interview conversations and the LinkedIn post.*

Topics to reflect on:
- Why specificity in prompts matters more than length
- How schema-first prompting changes output quality
- The difference between a prompt that works once and a prompt that works reliably
- What the iteration loop actually looks like in practice
- How to use Claude to stress-test your own prompts
- When to constrain Claude tightly vs give it room to reason

---

*Last updated: Phase 2 complete (system prompt v1 passed 12/12 manual tests, eval suite designed and generated — 50 cases across P06).*

*Phase 3 — core build complete and verified against the café persona:*
- *P07: Claude Code scaffold generated `src/tools.py`, `src/agent.py`, `src/main.py`, config files. Line-by-line review caught and fixed three issues before first run: tool name mismatch (`get_expense_by_category` → `get_expense_breakdown`), incorrect BAS quarter mapping (calendar year → Australian financial year), and a `main.py` error-handling bug (`AuthenticationError` → `AnthropicError`).*
- *P08: first live run surfaced a real bug — "last month" resolved to January (the first month in the dataset) instead of June (the actual most recent month), since nothing anchored the agent's sense of "now" to the mock data. First fix attempt was ambiguous and resolved to May; refined fix states the answer directly and was confirmed correct in a fresh session.*
- *Also caught during live testing: the Phase 2 "12/12 manual test" had been run in a simulated chat with no real tool calls — one figure it gave (January revenue) didn't match the real, tool-grounded figure the live app returns. Documented as a lesson: Phase 2 validated behaviour design, not factual grounding.*
- *All 12 original manual test questions re-run through the live app (café persona) and now match the Phase 2 designed behaviour, with real data grounding confirmed.*

*All three personas now tested live and passing: café (12/12), electrician (7/7), freelancer (6/6 after fixing a data duplication bug — see P09). Automated eval runner built (P10), using an LLM judge rather than string matching since must_include criteria are descriptive, not literal — not yet run against the full 50-case suite. Phase 4 (README, ARCHITECTURE.md, demo, LinkedIn, GitHub publish) not started.*