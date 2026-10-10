# AI Sales & Distribution Management Expert

## Project Architecture Document

**Project type:** MBA academic mini-project (demonstration, not production)  
**Domain:** Sales and Distribution Management  
**Intended stack (later implementation):** Python + Pandas + CrewAI + Streamlit  
**Current status:** Architecture only. The Streamlit application is **not** built in this phase.

---

## 1. Project Objective

The objective of this project is to design a **domain-specific multi-agent AI system** that helps a sales manager:

1. Upload sales and distribution data.
2. Obtain **numerically reliable** business metrics from Python/Pandas.
3. Receive **specialized AI analysis** from four agents (Sales, Distribution, Strategy, Management).
4. Get **actionable management recommendations** that a viva examiner can trace back to data.

The system is not meant to replace a sales manager. It is meant to show how:

- Python can do the arithmetic correctly.
- Specialized AI agents can interpret those numbers in a sales-and-distribution context.
- A final advisor can turn analysis into a management briefing.

**Simple viva line:**  
*Python calculates. Agents interpret. Management Advisor recommends. Hypotheses are never treated as facts.*

---

## 2. Business Problem

Sales managers often have spreadsheets that contain revenue, units, targets, regions, products, distributors, inventory, channels, and returns. The business problem is **not lack of data**. The problem is **lack of structured managerial interpretation**.

Typical difficulties:

- Actual sales vs target is calculated inconsistently.
- Regional and product performance are mixed together, so the real issue is unclear.
- Weak distributors, stockouts, and high returns are noticed late.
- Spreadsheet numbers are not converted into prioritized actions.
- AI tools (if used casually) invent causes that the file does not prove.

This project addresses that gap with a **fixed analytical pipeline**:

1. Validate the uploaded file.
2. Calculate standard sales and distribution metrics in Python.
3. Let a Sales Analyst and a Distribution Analyst interpret those metrics.
4. Let a Strategy Analyst combine and prioritize problems.
5. Let a Management Advisor produce recommendations, KPIs, and risks.

The system must always separate three types of information:

| Type | Meaning | Allowed use |
|---|---|---|
| **A. Reported** | A value that already exists in the uploaded dataset (for example, a listed sales target or inventory quantity). | Can be stated as a fact from the file. |
| **B. Calculated** | A metric produced by Python/Pandas (for example, target achievement %, return rate). | Can be stated as a fact derived by formula. |
| **C. Hypothesis** | A possible explanation suggested by an AI agent that the file does not prove (for example, “weak sales may be due to poor field force coverage”). | Must be labelled as hypothesis. Never presented as a confirmed fact. |

---

## 3. Agent Descriptions

The system uses **four specialized CrewAI agents**. Each agent has one job. No agent does another agent’s job.

### 3.1 Sales Analyst Agent

**Role:** Sales performance analysis expert.  
**Audience:** Internal analytical team (feeds Strategy Analyst).  
**Core idea:** Read Python sales metrics and explain *what happened* in sales performance.

This agent does **not** invent totals, percentages, or rankings. It must use the Python metrics pack.

### 3.2 Distribution Analyst Agent

**Role:** Distribution and channel management expert.  
**Audience:** Internal analytical team (feeds Strategy Analyst).  
**Core idea:** Read Python distribution metrics and explain *how well the channel and inventory system is working*.

This agent also does **not** recalculate important numbers. It interprets distributor, inventory, channel, returns, and order-pattern metrics.

### 3.3 Strategy Analyst Agent

**Role:** Business strategy consultant.  
**Audience:** Internal synthesis layer (feeds Management Advisor).  
**Core idea:** Combine Sales + Distribution findings, rank problems by business impact, and separate confirmed issues from guesses.

This agent does **not** produce the final action plan. It produces a prioritized problem map.

### 3.4 Management Advisor Agent

**Role:** Senior management advisor.  
**Audience:** Sales manager / examiner (final user-facing output).  
**Core idea:** Convert the strategy map into a concise management note: what to do, when, with which KPIs, and with which risks.

This agent does **not** redo sales arithmetic. It recommends.

---

## 4. Agent Responsibilities

### 4.1 Sales Analyst Agent

Responsibilities:

- Interpret **total revenue** (calculated).
- Interpret **units sold** (calculated).
- Compare **actual sales against sales targets** (reported target vs calculated actual).
- Interpret **target achievement percentage** (calculated).
- Interpret **regional performance**.
- Interpret **product performance**.
- Interpret **monthly sales trends**.
- Identify **high-performing and low-performing products** using Python rankings.
- Identify **regions performing below target**.
- Identify **significant changes** in sales (month-to-month or region-to-region) using calculated deltas.

Must **not**:

- Recalculate revenue, units, or achievement percentages in free text if Python already supplied them.
- Blame people, competitors, or market conditions unless those fields exist in the file.
- Present a hypothesis as a sales fact.

### 4.2 Distribution Analyst Agent

Responsibilities:

- Interpret **distributor performance**.
- **Compare distributors** using calculated sales, returns, and inventory indicators.
- Identify **weak distributors** (bottom performers from Python).
- Interpret **inventory levels**.
- Flag **potential stockout risks** (calculated, for example low inventory relative to recent units sold).
- Interpret **channel performance**.
- Identify **distribution gaps** (regions or channels with weak coverage or weak sales relative to others).
- Identify **regions with weak distribution performance**.
- Interpret **returns and order patterns**.

Must **not**:

- Claim a stockout has already happened unless inventory is zero/missing in the data.
- Assume a distributor is “unethical” or “incompetent”; only report performance numbers and patterns.
- Invent logistics costs or delivery times if they are not in the file.

### 4.3 Strategy Analyst Agent

Responsibilities:

- Combine Sales Analyst and Distribution Analyst findings.
- Identify the **most important business problems**.
- **Prioritize problems by business impact** (revenue at risk, target miss, stockout risk, high returns, concentration risk).
- Suggest **possible root causes**, clearly labelled.
- Distinguish **confirmed findings** from **hypotheses**.
- Identify **opportunities** (strong products, strong regions, strong distributors that can be scaled).
- Decide **which problems management should address first**.

Must **not**:

- Ignore either sales or distribution; both lenses are required.
- Flatten every issue to “need more marketing.”
- Treat an unproven cause as the official diagnosis.

### 4.4 Management Advisor Agent

Responsibilities:

- Convert findings into **actionable recommendations**.
- Prioritize each recommendation as **High / Medium / Low**.
- Recommend **short-term actions** (this week / this month).
- Recommend **medium-term actions** (this quarter).
- Recommend **relevant KPIs**.
- State **expected business impact** in managerial language, tied to calculated gaps where possible.
- Identify **implementation risks**.
- Produce a **concise executive summary**.

Must **not**:

- Give generic MBA slogans with no link to the metrics.
- Hide data limitations.
- Recommend actions that require data the file does not contain (for example, “cut advertising spend by 12%” if advertising is not in the dataset).

---

## 5. Agent Workflow

The runtime sequence is **sequential and easy to draw on a viva board**.

```text
User Business Question
        ↓
Data Upload (CSV / Excel)
        ↓
Python Data Validation
        ↓
Python Business Metrics
        ↓
Sales Analyst Agent          Distribution Analyst Agent
        \                          /
         \                        /
          \                      /
           Strategy Analyst Agent
                    ↓
        Management Advisor Agent
                    ↓
        Management Recommendations
```

### Stage-by-stage explanation

1. **User Business Question**  
   The manager types a question, for example: “Which regions are below target and what should we do?”

2. **Data Upload**  
   A sales-and-distribution file is uploaded. The later Streamlit UI will collect the question and the file.

3. **Python Data Validation**  
   Python checks required columns, data types, missing values, negative quantities, duplicate rows, and whether optional columns (inventory, returns, channel) exist.

4. **Python Business Metrics**  
   Pandas calculates the metric pack. This pack is the **single source of numerical truth**.

5. **Sales Analyst + Distribution Analyst**  
   These two agents run on the **same metric pack**. They can run one after the other for simplicity (recommended for the mini-project).  
   - Sales Analyst writes a sales findings note.  
   - Distribution Analyst writes a distribution findings note.

6. **Strategy Analyst**  
   Reads both notes plus the metric pack. Produces a prioritized problem list, opportunities, confirmed findings, and hypotheses.

7. **Management Advisor**  
   Reads the strategy output and writes the final 11-section management report.

**CrewAI mapping (simple):**

| CrewAI idea | Use in this project |
|---|---|
| Agent | One specialist with a role and backstory |
| Task | One written analytical note with a defined expected output |
| Crew | One sequential process: Sales → Distribution → Strategy → Management |
| Tools | Optional later: a read-only tool that returns the Python metric pack. Agents should not run arbitrary code. |

**Why sequential, not a debate loop:**  
An MBA examiner can follow the chain. Parallel debate, memory stores, and multi-round criticism add complexity without improving the academic story.

---

## 6. Data Flow

### 6.1 Expected input file (flexible, not rigid ERP)

The system should accept a table with **common sales and distribution columns**. Names may vary slightly; validation should map them if possible.

**Core columns (strongly expected):**

| Logical field | Example column names | Used for |
|---|---|---|
| Date | `date`, `month`, `order_date` | Monthly trends |
| Region | `region`, `zone`, `state` | Regional sales |
| Product | `product`, `sku`, `item` | Product sales |
| Units | `units`, `quantity`, `qty` | Volume |
| Revenue | `revenue`, `sales`, `amount` | Value |
| Target | `target`, `sales_target` | Achievement |

**Distribution columns (used if present):**

| Logical field | Example column names | Used for |
|---|---|---|
| Distributor | `distributor`, `dealer`, `partner` | Distributor comparison |
| Channel | `channel`, `route_to_market` | Channel performance |
| Inventory | `inventory`, `stock`, `closing_stock` | Stockout risk |
| Returns | `returns`, `returned_units`, `return_value` | Return rate |
| Orders | `orders`, `order_id`, `order_count` | Order patterns |

If a column is missing, Python must **not invent it**. The metric pack should say `not_available`, and agents must treat related comments as limited.

### 6.2 Data flow objects

```text
raw_file
   → dataframe (Pandas)
      → validation_report          [Reported issues about the file itself]
      → metrics_pack               [Calculated]
         → sales_findings          [Agent interpretation]
         → distribution_findings   [Agent interpretation]
            → strategy_brief       [Prioritized problems + hypotheses]
               → management_report [Final 11-section output]
```

### 6.3 Contents of `metrics_pack` (conceptual)

The metric pack is a structured dictionary / JSON-like object, for example:

- `reported`: column list, date range, number of rows, unique regions/products/distributors (from the file).
- `calculated`: all function outputs listed in Section 7.
- `unavailable`: list of analyses skipped because columns were missing.
- `warnings`: missing values, negative numbers, target missing for some rows.

Agents receive:

1. The user question.
2. The validation report.
3. The metric pack.
4. Previous agent notes (from Strategy onward).

Agents do **not** receive a second unofficial spreadsheet. One dataframe → one metric pack.

### 6.4 Information tagging rule (applies to every agent)

Every material statement in agent output should be mentally classifiable as:

- **Reported:** “The file contains 4 regions: North, South, East, West.”
- **Calculated:** “East region achievement is 72%.”
- **Hypothesis:** “East weakness *may* be due to fewer active distributors; this is not proven.”

The Management Advisor must keep this distinction visible in Sections 3, 5, and 6 of the final report.

---

## 7. Python Analytical Functions

All important numbers are calculated in Python/Pandas. Function names below are the **design contract** for later coding. They operate on the validated dataframe.

### 7.1 Design rules

- Use Pandas (`sum`, `groupby`, `mean`, period grouping). Do not ask the LLM to add columns.
- Return structured results (dictionaries / small tables), not long prose.
- If a required column is missing, return `{ "status": "not_available", "reason": "..." }`.
- Percentages should be rounded consistently (for example, 1 decimal place) in later implementation.
- Rankings should include both the name and the metric used.

### 7.2 Function catalogue

#### `total_revenue(df)`

- **Purpose:** Company-level sales value.
- **Method:** Sum of the revenue column.
- **Type:** Calculated.
- **Used by:** Sales Analyst, Strategy, Management Advisor.

#### `total_units(df)`

- **Purpose:** Company-level volume.
- **Method:** Sum of the units column.
- **Type:** Calculated.
- **Used by:** Sales Analyst.

#### `target_achievement(df)`

- **Purpose:** Actual vs target.
- **Method:**  
  - Actual = sum of revenue (or units, if the target is volume-based; default is revenue if both exist).  
  - Target = sum of target.  
  - Achievement % = `(actual / target) * 100` when target > 0.
- **Also returns:** Absolute gap (`actual - target`).
- **Type:** Calculated from reported targets and calculated actuals.
- **Used by:** Sales Analyst (overall, and similarly after grouping for region/product if targets exist at that grain).

#### `regional_sales(df)`

- **Purpose:** Sales by region.
- **Method:** Group by region; sum revenue and units; compute share of total; compute achievement if regional targets exist.
- **Type:** Calculated.
- **Used by:** Sales Analyst; Distribution Analyst for weak-distribution regions.

#### `product_sales(df)`

- **Purpose:** Sales by product.
- **Method:** Group by product; sum revenue and units; share of total; achievement if product targets exist.
- **Type:** Calculated.
- **Used by:** Sales Analyst (high/low products).

#### `distributor_sales(df)`

- **Purpose:** Sales by distributor.
- **Method:** Group by distributor; sum revenue and units; share of total; optional return rate and inventory if columns exist.
- **Type:** Calculated.
- **Used by:** Distribution Analyst.

#### `monthly_sales(df)`

- **Purpose:** Time trend.
- **Method:** Group by year-month; sum revenue and units; period-to-period change and % change.
- **Type:** Calculated.
- **Used by:** Sales Analyst (significant changes).

#### `inventory_analysis(df)`

- **Purpose:** Stock health and stockout risk.
- **Method (simple, academic):**  
  - Latest or average inventory by product/region/distributor (depending on available grain).  
  - Compare inventory with recent units sold.  
  - Flag **potential stockout risk** when inventory is very low relative to recent sales, or inventory is zero.
- **Type:** Calculated flags, not a confirmed warehouse visit.
- **Used by:** Distribution Analyst.
- **Label:** “Potential stockout risk” is a calculated warning, not proof that customers already faced empty shelves, unless inventory is reported as zero.

#### `return_rate(df)`

- **Purpose:** Quality / channel leakage signal.
- **Method:**  
  - If returns are units: `returned_units / units_sold`.  
  - If returns are value: `return_value / revenue`.
- **Type:** Calculated.
- **Used by:** Distribution Analyst; Strategy (possible quality or overselling issues — as hypothesis unless a reason column exists).

#### `channel_performance(df)`

- **Purpose:** Compare channels (for example retail, wholesale, online, general trade, modern trade).
- **Method:** Group by channel; revenue, units, share, optional returns.
- **Type:** Calculated.
- **Used by:** Distribution Analyst.

#### `top_performers(df, dimension, n=5)`

- **Purpose:** Best products, regions, distributors, or channels.
- **Method:** Rank by revenue (default); return top `n`.
- **Type:** Calculated.
- **Used by:** Sales Analyst and Distribution Analyst.

#### `bottom_performers(df, dimension, n=5)`

- **Purpose:** Weak products, regions, distributors, or channels.
- **Method:** Rank by revenue (default); return bottom `n`. Optional second ranking by achievement % if targets exist.
- **Type:** Calculated.
- **Used by:** Sales Analyst and Distribution Analyst.

### 7.3 Suggested helper calculations (same Python layer, not extra agents)

These can live inside the functions above or as small helpers:

- `validation_report(df)` — columns present/missing, row count, nulls.
- `below_target_regions(df)` — filter regional achievement < 100% (or a chosen threshold such as 90%).
- `significant_sales_changes(df)` — months with large % change (for example absolute change above a simple threshold).
- `distribution_gaps(df)` — regions with sales but few distributors, or distributors with unusually high returns / low stock.

Keep helpers simple. Do not add machine learning models.

---

## 8. Expected Outputs

### 8.1 Intermediate outputs (internal)

**Validation report**

- Rows, columns, date range.
- Missing columns.
- Data-quality warnings.

**Metric pack**

- All calculated tables/summaries from Section 7.
- Unavailable analyses.

**Sales findings note**

- Sales performance vs target.
- Regional and product picture.
- Trend highlights.
- High/low performers.
- Tagged reported vs calculated statements.

**Distribution findings note**

- Distributor comparison.
- Weak distributors.
- Inventory / stockout flags.
- Channel picture.
- Returns and order-pattern comments.
- Distribution gaps.

**Strategy brief**

- Combined problem list, ranked.
- Opportunities.
- Confirmed findings vs hypotheses.
- “Address first” recommendation for management.

### 8.2 Final output: Management Advisor report

The user-facing report has **eleven fixed sections**. This is the academic deliverable format.

#### 1. Executive Summary

5–8 sentences. What is the overall sales health, the main distribution issue, and the single most important management action?

#### 2. Key Findings

Bullet list of the most important points (mix of sales and distribution). Each bullet should be supportable.

#### 3. Data-Supported Findings

Only **Reported** and **Calculated** items. No guesses.

Example style:

- Reported: “The dataset covers Jan–Jun and includes 3 channels.”
- Calculated: “Overall target achievement is 86.4%.”

#### 4. Calculated Metrics

A compact metric snapshot, for example:

- Total revenue
- Total units
- Target achievement %
- Best and worst region
- Best and worst product
- Weakest distributor (if available)
- Return rate (if available)
- Number of stockout-risk items (if available)

#### 5. Potential Root Causes

Causes that are **logically linked to the data** but not fully proven. Must still be cautious.

Example: “The same region is below target *and* has the weakest distributor sales; a distribution constraint is a plausible root cause.”

#### 6. Hypotheses

Explicit guesses. Prefix with “Hypothesis:”.

Example: “Hypothesis: Low East sales may reflect weaker brand presence, but the file has no brand-awareness field.”

#### 7. Priority Problems

Ranked list (P1, P2, P3…). Each problem states:

- Why it matters (impact).
- Whether it is confirmed or partly hypothesized.
- Why it outranks the next problem.

#### 8. Recommended Actions

Each action:

- Priority: **High / Medium / Low**
- Linked problem
- Owner suggestion in generic terms (for example Regional Manager, Distributor Manager) — not fake employee names
- Short-term or medium-term tag

#### 9. Implementation Plan

- **Short-term (0–30 days):** diagnose, reallocate stock, review weak distributors, focus sales calls on below-target regions.
- **Medium-term (30–90 days):** reset targets if needed, channel mix changes, inventory policy, distributor capability review.

No long-term transformation programme. This is a mini-project.

#### 10. KPIs to Monitor

A short scorecard, for example:

- Target achievement % (overall and by region)
- Revenue and units by product
- Distributor share of sales
- Return rate
- Inventory cover / stockout-risk count
- Monthly sales growth

#### 11. Risks and Limitations

Must include:

- Data gaps (missing columns, missing months, missing targets).
- Implementation risks (pushing volume may raise returns; focusing on one region may neglect another).
- Analytical limits (no customer-level data, no competitor data, no cost/profit data unless present).
- Reminder that hypotheses are unproven.

---

## 9. Example Business Questions

These questions match the domain and the four-agent split. The later Streamlit app can offer them as samples.

1. Which regions are below sales target, and what should management do first?
2. Which products are high performers and which are dragging down revenue?
3. How is overall target achievement, and where is the largest gap?
4. Which distributors are weak, and is the issue sales, returns, or inventory?
5. Are there products or regions with potential stockout risk?
6. How do channels compare, and where are the distribution gaps?
7. What changed in monthly sales, and is the change concentrated in one region or product?
8. Is the main problem a sales problem, a distribution problem, or both?
9. Where should we focus short-term effort this month?
10. What KPIs should a sales manager watch after this review?

**Question routing (simple, no extra agents):**

- If the question is mainly sales (targets, products, months, regions) → still run **all four agents**, because Strategy needs Distribution as well.
- If the question is mainly distribution (stock, distributors, channels, returns) → still run all four agents, because stockouts show up in sales too.
- Always run the full pipeline. Do not add a classifier agent. This is easier to explain in a viva.

---

## 10. Limitations

This is an academic demonstration. Honest limitations are part of the design.

1. **Not a production decision system.** Outputs are advisory for teaching and evaluation.
2. **Quality depends on the uploaded file.** Missing targets, inventory, or distributors reduce what can be said.
3. **No profit, cost, or margin engine** unless those columns exist. Revenue is not profit.
4. **No customer, competitor, pricing-power, or macroeconomic data** unless uploaded.
5. **No causal proof.** Python shows patterns. Agents may hypothesize causes.
6. **LLM language risk.** Agents might still over-claim; prompts and the three-type rule are the control, not a guarantee.
7. **Simple stockout logic.** Inventory vs recent sales is a teaching proxy, not a full MRP/forecasting model.
8. **No memory across sessions** in the planned mini-project (no database of past questions).
9. **No vector database, RAG, fine-tuning, Docker, Kubernetes, or microservices.** Those would not help an MBA viva.
10. **API/model dependency.** CrewAI will call an LLM; without a valid model/API key, agents cannot write narrative (Python metrics can still run).
11. **Small data assumption.** Designed for a class-sized spreadsheet, not millions of rows.
12. **Human remains accountable.** A manager must check numbers before acting.

---

## 11. Why This Qualifies as a Domain-Specific Multi-Agent AI System

A viva examiner may ask: *Is this just ChatGPT with a spreadsheet?* The answer is **no**, for the following reasons.

### 11.1 It is domain-specific

- The domain is **Sales and Distribution Management**, not generic Q&A.
- Metrics are the standard SDM toolkit: target achievement, regional/product mix, distributors, channels, inventory, returns.
- Recommendations are managerial (short-term vs medium-term, KPIs, implementation risk), not generic chatbot advice.
- Agents are forbidden from using tools outside this domain (no code generation, no unrelated research).

### 11.2 It is multi-agent, not one prompt

- **Four roles** with different responsibilities, like a small consulting team.
- **Sales** and **Distribution** are separated because a sales miss and a stockout are different management problems.
- **Strategy** exists so the system does not dump two unrelated reports on the manager.
- **Management Advisor** exists so analysis is converted into decisions, KPIs, and risks.
- Information is **handed off** along a defined workflow. That is a multi-agent architecture, even though it is simple.

### 11.3 It is AI plus analytics, not AI instead of analytics

- Numerical work is **deterministic Python**.
- Language work is **specialized agents**.
- This hybrid is the academic contribution: *keep the calculator out of the LLM, and keep judgment out of the spreadsheet formulas.*

### 11.4 It enforces an epistemological rule (important for MBA)

The three-way split **Reported / Calculated / Hypothesis** is a governance rule. A domain expert system must know what it knows. A generic chatbot does not.

### 11.5 What this is not (so the claim stays honest)

| Not this | Why we avoided it |
|---|---|
| RAG / vector database | No policy manual to retrieve; the source of truth is the uploaded table + formulas |
| Fine-tuning | Unnecessary for a class demo; prompts + metrics are enough |
| Microservices / Docker / Kubernetes | Operations complexity, not SDM insight |
| One mega-agent | Would mix sales, distribution, and advice, and be harder to justify as “multi-agent” |

### 11.6 One-paragraph viva answer

> This project is a domain-specific multi-agent AI system because it solves a Sales and Distribution Management problem with four specialist agents, each with a distinct role. Python/Pandas compute the business metrics. The Sales Analyst and Distribution Analyst interpret those metrics. The Strategy Analyst prioritizes problems and separates facts from hypotheses. The Management Advisor turns that into recommendations, KPIs, and risks. The system is multi-agent because work is divided and sequenced; it is domain-specific because the metrics, roles, and outputs follow sales and distribution management practice rather than general chat.

---

## Appendix A — Planned later file layout (not created in this phase)

When implementation starts, a simple layout is enough:

```text
AI_Business_Expert/
  PROJECT_ARCHITECTURE.md    ← this document
  app.py                     ← Streamlit UI (later)
  analytics/
    validation.py
    metrics.py               ← functions in Section 7
  agents/
    crew.py                  ← CrewAI agents, tasks, sequential process
    prompts.py
  sample_data/
    sample_sales_distribution.csv
  requirements.txt
```

Do **not** add extra services, databases, or frontend frameworks.

---

## Appendix B — Viva diagram (draw this)

```text
Question + File
      → Validate (Python)
      → Calculate metrics (Python)
      → Sales Analyst (AI)
      → Distribution Analyst (AI)
      → Strategy Analyst (AI)
      → Management Advisor (AI)
      → 11-section management report
```

**Memory aid:** *Validate → Calculate → Specialize → Synthesize → Advise.*

---

*End of architecture document. Next implementation step (only when requested): Python validation + metric functions, then CrewAI agents, then Streamlit UI.*
