"""
CrewAI task definitions.

Tasks run in a fixed order that is easy to draw in a viva:
Sales Analyst -> Distribution Analyst -> Strategy Analyst -> Management Advisor.
"""

from __future__ import annotations

from typing import Any

import prompts


def build_task_specs(question: str, analysis_type: str, metrics_text: str) -> list[dict[str, Any]]:
    """Plain dictionaries so the same specs work with CrewAI or the OpenAI fallback."""
    return [
        {
            "name": "sales",
            "description": prompts.sales_task_description(question, analysis_type, metrics_text),
            "expected_output": prompts.SALES_EXPECTED,
            "agent": "sales",
            "context": [],
        },
        {
            "name": "distribution",
            "description": prompts.distribution_task_description(question, analysis_type, metrics_text),
            "expected_output": prompts.DISTRIBUTION_EXPECTED,
            "agent": "distribution",
            "context": [],
        },
        {
            "name": "strategy",
            "description": prompts.strategy_task_description(question, analysis_type, metrics_text),
            "expected_output": prompts.STRATEGY_EXPECTED,
            "agent": "strategy",
            "context": ["sales", "distribution"],
        },
        {
            "name": "management",
            "description": prompts.management_task_description(question, analysis_type, metrics_text),
            "expected_output": prompts.MANAGEMENT_EXPECTED,
            "agent": "management",
            "context": ["strategy"],
        },
    ]


def create_crewai_tasks(agents: dict[str, Any], question: str, analysis_type: str, metrics_text: str):
    """Build CrewAI Task objects when the library is installed."""
    from crewai import Task

    specs = build_task_specs(question, analysis_type, metrics_text)
    created: dict[str, Any] = {}
    for spec in specs:
        kwargs = {
            "description": spec["description"],
            "expected_output": spec["expected_output"],
            "agent": agents[spec["agent"]],
        }
        created[spec["name"]] = Task(**kwargs)

    # Attach prior notes so Strategy and Management can read earlier work.
    created["strategy"].context = [created["sales"], created["distribution"]]
    created["management"].context = [created["strategy"]]
    return [
        created["sales"],
        created["distribution"],
        created["strategy"],
        created["management"],
    ]
