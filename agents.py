"""
Four specialist agents plus three run modes:

1. demo     - no API key; narrative built from Python metrics (labelled DEMO).
2. crewai   - sequential CrewAI crew (preferred when the library and key work).
3. openai   - same four roles via sequential OpenAI chat calls (fallback).
"""

from __future__ import annotations

import os
import re
from typing import Any

import prompts
import tasks
from tools import build_metrics_pack, metrics_to_prompt_text

DEFAULT_MODEL = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")


def get_api_key() -> str | None:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    return key or None


def crewai_importable() -> bool:
    try:
        import crewai  # noqa: F401
        return True
    except Exception:
        return False


def _pct(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"{value}%"


def _money(value: Any) -> str:
    if value is None:
        return "n/a"
    return f"INR {value:,.0f}"


def _status_ok(block: dict[str, Any] | None) -> bool:
    return bool(block) and block.get("status") == "ok"


def _names(rows: list[dict[str, Any]], key: str, limit: int = 3) -> str:
    return ", ".join(str(r.get(key)) for r in rows[:limit] if r.get(key) is not None) or "n/a"


def build_demo_report(metrics: dict[str, Any], question: str) -> dict[str, Any]:
    """
    Demonstration narrative derived from CALCULATED metrics.
    This is not a live LLM. The UI must label it as Demo Mode.
    """
    calc = metrics.get("calculated", {})
    reported = metrics.get("reported", {})
    rev = calc.get("total_revenue", {})
    units = calc.get("total_units", {})
    ach = calc.get("target_achievement", {})
    growth = calc.get("revenue_growth", {})
    regions = calc.get("regional_sales", {})
    products = calc.get("product_sales", {})
    dist = calc.get("distributor_sales", {})
    returns = calc.get("return_rate", {})
    inv = calc.get("inventory_analysis", {})
    channels = calc.get("channel_performance", {})
    monthly = calc.get("monthly_sales", {})

    total_rev = rev.get("total_revenue") if _status_ok(rev) else None
    total_units = units.get("total_units") if _status_ok(units) else None
    ach_pct = ach.get("achievement_pct") if _status_ok(ach) else None
    gap = ach.get("gap") if _status_ok(ach) else None

    below_regions = regions.get("below_target", []) if _status_ok(regions) else []
    region_rows = regions.get("rows", []) if _status_ok(regions) else []
    product_rows = products.get("rows", []) if _status_ok(products) else []
    dist_rows = dist.get("rows", []) if _status_ok(dist) else []
    weak_dist = list(reversed(dist_rows))[:2] if dist_rows else []
    strong_prod = product_rows[0] if product_rows else {}
    weak_prod = product_rows[-1] if product_rows else {}
    high_returns = (returns.get("by_distributor") or [None])[0] if _status_ok(returns) else None
    stockout_n = inv.get("stockout_risk_count") if _status_ok(inv) else None
    mom = growth.get("month_on_month_growth_pct") if _status_ok(growth) else None

    sales_findings = f"""
### Sales Analyst (Demo)

- [CALCULATED] Total revenue is {_money(total_rev)}; total units are {total_units if total_units is not None else "n/a"}.
- [CALCULATED] Overall target achievement is {_pct(ach_pct)}; gap versus target is {_money(gap)}.
- [CALCULATED] Regions below target: {", ".join(below_regions) if below_regions else "none identified"}.
- [CALCULATED] Strongest product by revenue: {strong_prod.get("Product", "n/a")}.
- [CALCULATED] Weakest product by revenue: {weak_prod.get("Product", "n/a")}.
- [CALCULATED] Latest month-on-month revenue change: {_pct(mom)}.
- [REPORTED] Dataset rows: {reported.get("n_rows")}; date range {reported.get("date_min")} to {reported.get("date_max")}.
- Manager question considered: {question}
""".strip()

    dist_findings = f"""
### Distribution Analyst (Demo)

- [CALCULATED] Distributor count: {reported.get("n_distributors")}.
- [CALCULATED] Weaker distributors by revenue: {_names(weak_dist, "Distributor")}.
- [CALCULATED] Overall return rate: {_pct(returns.get("return_rate_pct") if _status_ok(returns) else None)}.
- [CALCULATED] Highest listed return-rate distributor: {high_returns.get("Distributor") if high_returns else "n/a"} ({_pct(high_returns.get("Return_Rate_Pct") if high_returns else None)}).
- [CALCULATED] Potential stockout-risk groups: {stockout_n if stockout_n is not None else "n/a"}.
- [CALCULATED] Channel mix (top): {_names(channels.get("rows", []) if _status_ok(channels) else [], "Channel")}.
- [HYPOTHESIS] Weak revenue and tight inventory in the same partner *may* indicate a coverage or replenishment issue; the file does not prove the operational cause.
""".strip()

    p1 = f"Target miss concentrated in: {', '.join(below_regions)}" if below_regions else "Check overall target achievement"
    p2 = f"Weak distributors: {_names(weak_dist, 'Distributor')}"
    p3 = f"Product underperformance: {weak_prod.get('Product', 'n/a')}"

    strategy = f"""
### Strategy Analyst (Demo)

**Priority problems**
- P1 [CALCULATED]: {p1} (achievement {_pct(ach_pct)}).
- P2 [CALCULATED]: {p2}.
- P3 [CALCULATED]: {p3}.
- P4 [CALCULATED]: Inventory stockout-risk groups = {stockout_n if stockout_n is not None else "n/a"}; elevated returns at {high_returns.get("Distributor") if high_returns else "n/a"}.

**Opportunities**
- Scale what already works: {strong_prod.get("Product", "n/a")} and stronger regions {[r.get("Region") for r in region_rows[:2]]}.

**Confirmed vs hypothesis**
- Confirmed: the ranking and percentages above come from Pandas.
- [HYPOTHESIS] Root causes such as brand weakness, competitor activity, or field-force gaps are not in the file.
""".strip()

    executive = (
        f"Overall achievement is {_pct(ach_pct)} on {_money(total_rev)} of revenue. "
        f"Management should first address below-target regions ({', '.join(below_regions) or 'none flagged'}) "
        f"and the weakest distributors ({_names(weak_dist, 'Distributor')}), while protecting the strong product "
        f"{strong_prod.get('Product', 'n/a')}. Inventory risk groups: {stockout_n if stockout_n is not None else 'n/a'}."
    )

    management = f"""
## Executive Summary
{executive}

## Key Findings
- Achievement {_pct(ach_pct)}; revenue {_money(total_rev)}; units {total_units}.
- Below-target regions: {", ".join(below_regions) or "none flagged"}.
- Hero SKU: {strong_prod.get("Product", "n/a")}; lagging SKU: {weak_prod.get("Product", "n/a")}.
- Weak distributors: {_names(weak_dist, "Distributor")}.
- Return rate {_pct(returns.get("return_rate_pct") if _status_ok(returns) else None)}; stockout-risk groups {stockout_n}.

## Data-Supported Findings
- [REPORTED] {reported.get("n_rows")} rows, {reported.get("n_regions")} regions, {reported.get("n_products")} products, {reported.get("n_distributors")} distributors.
- [CALCULATED] Figures in the metrics pack (achievement, rankings, return rate, inventory flags).

## Calculated Metrics
- Total revenue: {_money(total_rev)}
- Target achievement: {_pct(ach_pct)}
- Return rate: {_pct(returns.get("return_rate_pct") if _status_ok(returns) else None)}
- MoM growth: {_pct(mom)}

## Potential Root Causes
- Combined below-target sales and weaker distributors in the same geography is a plausible distribution constraint.
- High returns at a named distributor may reflect product mix, handling, or overselling — not proven.

## Hypotheses
- [HYPOTHESIS] East or other weak regions may have thinner brand presence; no awareness field exists.
- [HYPOTHESIS] Low inventory may already be causing lost sales; the file only shows stock levels, not lost orders.

## Priority Problems
- P1: Close the target gap in {", ".join(below_regions) or "the company overall"}.
- P2: Review weak distributors.
- P3: Lift or rationalise {weak_prod.get("Product", "the lagging product")}.
- P4: Replenish stockout-risk items.

## Recommended Actions
- High / short-term: Focus sales reviews on below-target regions and the two weakest distributors.
- High / short-term: Replenish SKUs with zero or very low inventory.
- Medium: Investigate high-return distributors with a returns audit.
- Medium: Protect supply and visibility for {strong_prod.get("Product", "the hero SKU")}.
- Low: Revisit target setting where achievement is structurally far from 100%.

## Implementation Plan
- 0-30 days: dashboard review with regional managers; stock reallocation; distributor joint business plan for weak partners.
- 30-90 days: channel mix review; inventory policy; product plan for the lagging SKU.

## KPIs to Monitor
- Target achievement % (overall and by region)
- Revenue and units by product
- Distributor share and return rate
- Stockout-risk count / inventory cover
- Monthly revenue change

## Risks and Limitations
- Demo Mode did not call a live LLM. Numbers are calculated; the narrative is a template over those numbers.
- No cost, profit, competitor, or customer-satisfaction fields unless present in the file.
- Hypotheses are unproven. A manager must validate before acting.
- Significant monthly moves: {monthly.get("significant_changes", []) if _status_ok(monthly) else "n/a"}.
""".strip()

    parsed = parse_management_report(management)
    parsed.update(
        {
            "mode": "demo",
            "mode_label": "DEMO MODE — generated from Python metrics, not a live LLM",
            "sales_findings": sales_findings,
            "distribution_findings": dist_findings,
            "strategy_findings": strategy,
            "management_report": management,
            "question": question,
        }
    )
    return parsed


def parse_management_report(text: str) -> dict[str, str]:
    """Split the 11-section markdown into UI-friendly chunks."""
    headings = [
        "Executive Summary",
        "Key Findings",
        "Data-Supported Findings",
        "Calculated Metrics",
        "Potential Root Causes",
        "Hypotheses",
        "Priority Problems",
        "Recommended Actions",
        "Implementation Plan",
        "KPIs to Monitor",
        "Risks and Limitations",
    ]
    sections = {h: "" for h in headings}
    current = None
    collected: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^#{1,3}\s+(.*)$", line.strip())
        if match:
            title = match.group(1).strip()
            if current is not None:
                sections[current] = "\n".join(collected).strip()
            current = title if title in sections else current
            collected = []
            continue
        if current is not None:
            collected.append(line)
    if current is not None:
        sections[current] = "\n".join(collected).strip()
    return {
        "executive_summary": sections["Executive Summary"],
        "key_findings": sections["Key Findings"],
        "data_supported": sections["Data-Supported Findings"],
        "calculated_metrics_text": sections["Calculated Metrics"],
        "root_causes": sections["Potential Root Causes"],
        "hypotheses": sections["Hypotheses"],
        "priority_problems": sections["Priority Problems"],
        "recommended_actions": sections["Recommended Actions"],
        "implementation_plan": sections["Implementation Plan"],
        "kpis": sections["KPIs to Monitor"],
        "risks": sections["Risks and Limitations"],
    }


def create_agents(llm: Any) -> dict[str, Any]:
    from crewai import Agent

    common = dict(llm=llm, verbose=False, allow_delegation=False)
    return {
        "sales": Agent(
            role=prompts.SALES_ANALYST_ROLE,
            goal=prompts.SALES_ANALYST_GOAL,
            backstory=prompts.SALES_ANALYST_BACKSTORY,
            **common,
        ),
        "distribution": Agent(
            role=prompts.DISTRIBUTION_ANALYST_ROLE,
            goal=prompts.DISTRIBUTION_ANALYST_GOAL,
            backstory=prompts.DISTRIBUTION_ANALYST_BACKSTORY,
            **common,
        ),
        "strategy": Agent(
            role=prompts.STRATEGY_ANALYST_ROLE,
            goal=prompts.STRATEGY_ANALYST_GOAL,
            backstory=prompts.STRATEGY_ANALYST_BACKSTORY,
            **common,
        ),
        "management": Agent(
            role=prompts.MANAGEMENT_ADVISOR_ROLE,
            goal=prompts.MANAGEMENT_ADVISOR_GOAL,
            backstory=prompts.MANAGEMENT_ADVISOR_BACKSTORY,
            **common,
        ),
    }


def _task_output_text(task: Any) -> str:
    output = getattr(task, "output", None)
    if output is None:
        return ""
    for attr in ("raw", "description"):
        value = getattr(output, attr, None)
        if value:
            return str(value)
    return str(output)


def run_crewai(question: str, analysis_type: str, metrics_text: str) -> dict[str, Any]:
    from crewai import Crew, Process

    llm = os.getenv("OPENAI_MODEL_NAME", DEFAULT_MODEL)
    if not llm.startswith("openai/") and "/" not in llm:
        llm = f"openai/{llm}"

    agents = create_agents(llm)
    crew_tasks = tasks.create_crewai_tasks(agents, question, analysis_type, metrics_text)
    crew = Crew(
        agents=list(agents.values()),
        tasks=crew_tasks,
        process=Process.sequential,
        verbose=False,
    )
    result = crew.kickoff()
    sales_text = _task_output_text(crew_tasks[0])
    dist_text = _task_output_text(crew_tasks[1])
    strategy_text = _task_output_text(crew_tasks[2])
    management_text = _task_output_text(crew_tasks[3]) or str(result)
    parsed = parse_management_report(management_text)
    parsed.update(
        {
            "mode": "crewai",
            "mode_label": "Live CrewAI sequential crew (OpenAI)",
            "sales_findings": sales_text,
            "distribution_findings": dist_text,
            "strategy_findings": strategy_text,
            "management_report": management_text,
            "question": question,
        }
    )
    return parsed


def _chat(client: Any, model: str, system: str, user: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


def run_openai_sequence(question: str, analysis_type: str, metrics_text: str) -> dict[str, Any]:
    """Same four roles without CrewAI, used if the library cannot import on this Python."""
    from openai import OpenAI

    client = OpenAI(api_key=get_api_key())
    model = DEFAULT_MODEL.replace("openai/", "")
    specs = tasks.build_task_specs(question, analysis_type, metrics_text)
    notes: dict[str, str] = {}

    systems = {
        "sales": prompts.SALES_ANALYST_BACKSTORY,
        "distribution": prompts.DISTRIBUTION_ANALYST_BACKSTORY,
        "strategy": prompts.STRATEGY_ANALYST_BACKSTORY,
        "management": prompts.MANAGEMENT_ADVISOR_BACKSTORY,
    }

    for spec in specs:
        extra = ""
        for dep in spec["context"]:
            extra += f"\n\nPRIOR NOTE ({dep}):\n{notes.get(dep, '')}"
        notes[spec["name"]] = _chat(
            client,
            model,
            systems[spec["agent"]],
            spec["description"] + extra,
        )

    parsed = parse_management_report(notes["management"])
    parsed.update(
        {
            "mode": "openai",
            "mode_label": "Live sequential OpenAI agents (CrewAI fallback)",
            "sales_findings": notes["sales"],
            "distribution_findings": notes["distribution"],
            "strategy_findings": notes["strategy"],
            "management_report": notes["management"],
            "question": question,
        }
    )
    return parsed


def run_analysis(
    df,
    question: str,
    analysis_type: str = "Full analysis",
    demo_mode: bool = False,
) -> dict[str, Any]:
    """Public entry used by Streamlit and tests."""
    metrics = build_metrics_pack(df)
    metrics_text = metrics_to_prompt_text(metrics)
    question = (question or "").strip() or "Give a full sales and distribution management review."

    if demo_mode or not get_api_key():
        report = build_demo_report(metrics, question)
        report["metrics"] = metrics
        if not get_api_key() and not demo_mode:
            report["mode_label"] = "DEMO MODE — no OPENAI_API_KEY found; using Python metrics narrative"
        return report

    try:
        if crewai_importable():
            report = run_crewai(question, analysis_type, metrics_text)
        else:
            report = run_openai_sequence(question, analysis_type, metrics_text)
        report["metrics"] = metrics
        return report
    except Exception as exc:  # noqa: BLE001
        report = build_demo_report(metrics, question)
        report["metrics"] = metrics
        report["mode"] = "demo"
        report["mode_label"] = f"DEMO MODE fallback after live-agent error: {exc}"
        report["error"] = str(exc)
        return report
