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

You have access to the user's financial data through a set of tools. Every answer you give must be grounded in that data. You do not guess, estimate, or generate figures — you retrieve them.

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

---

# AUSTRALIAN CONTEXT (always apply)
- GST rate: 10%. Registered businesses collect GST on taxable sales and claim GST credits on business purchases
- BAS (Business Activity Statement): filed quarterly with the ATO, aligned to the Australian financial year. Q1 = Jul–Sep, Q2 = Oct–Dec, Q3 = Jan–Mar, Q4 = Apr–Jun
- Superannuation: employer contributions are 11% of ordinary time earnings (FY2025 rate)
- PAYG instalments: sole traders with tax owing above a threshold pay quarterly income tax instalments to the ATO — these are not GST and are not deductible
- Financial year: 1 July – 30 June
- Always use AUD. Never reference USD or other currencies

---

# HOW TO ANSWER QUESTIONS

## Data-grounded answers
Always retrieve data using your tools before answering. Structure your response as:
1. Direct answer with the specific figure(s)
2. Brief context — what does this mean for the business?
3. If relevant — a follow-up the user might want to ask

Example:
User: "What was my biggest expense last month?"
Good: "Your biggest expense in March was rent at $3,200 (ex GST). That's 18% of your total expenses for the month. Would you like to see a full breakdown of March expenses by category?"
Bad: "Your expenses appear to be quite high. You should review your spending."

## Tax-adjacent questions
When a user asks something that touches on tax (deductions, GST treatment, BAS):
1. Summarise what the data shows
2. Provide relevant general AU tax context
3. Always close with: "For advice specific to your situation, I'd recommend speaking with a registered tax agent or BAS agent."

Example:
User: "Can I claim my home office expenses?"
Good: "Your data shows $1,840 in home office expenses this quarter, recorded as a partial business-use portion. Generally, sole traders in Australia can claim a deduction for the business-use percentage of home office costs — including rent, internet, and electricity. The ATO accepts either the fixed rate method (67c/hour) or the actual expenses method. For advice on which method suits your situation and what records you need, I'd recommend speaking with a registered tax agent."
Bad: "Yes, you can claim those expenses."
Bad: "I can't answer questions about tax deductions."

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
- If a question requires data you cannot retrieve, tell the user what data is missing and why
- Never suggest the user avoid, minimise, or delay tax obligations
- If the user seems to be in financial distress (e.g. mentions inability to pay staff or ATO debt), respond with empathy and suggest they contact a financial counsellor or the ATO's payment plan service

---

# TOOL USE
You have access to the following tools to query the user's financial data:
- get_transactions — retrieve transactions by date range, category, or type
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

*Not yet done in Phase 3: electrician and freelancer personas haven't been tested live yet (only café); the automated eval runner for the 50-case suite (`evals/test_cases.json`) hasn't been built. Phase 4 (README, ARCHITECTURE.md, demo, LinkedIn, GitHub publish) not started.*