"""
Streamlit dashboard for the AI Sales & Distribution Management Expert.

Python/Pandas calculates the numbers. Four agents interpret them.
Demo Mode works without an API key.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv

import agents
from tools import (
    build_metrics_pack,
    channel_performance,
    distributor_sales,
    inventory_analysis,
    load_csv_file,
    monthly_sales,
    overview_kpis,
    product_sales,
    regional_sales,
    target_achievement,
)

load_dotenv()

SAMPLE_PATH = Path(__file__).resolve().parent / "data" / "sample_sales_data.csv"

SAMPLE_QUESTIONS = [
    "Which regions are below sales target, and what should management do first?",
    "Which products are high performers and which are dragging down revenue?",
    "How is overall target achievement, and where is the largest gap?",
    "Which distributors are weak, and is the issue sales, returns, or inventory?",
    "Are there products or regions with potential stockout risk?",
    "Is the main problem a sales problem, a distribution problem, or both?",
]


def format_inr(value) -> str:
    if value is None:
        return "n/a"
    try:
        return f"₹{float(value):,.0f}"
    except (TypeError, ValueError):
        return "n/a"


def format_num(value, digits: int = 0, suffix: str = "") -> str:
    if value is None:
        return "n/a"
    try:
        return f"{float(value):,.{digits}f}{suffix}"
    except (TypeError, ValueError):
        return "n/a"


def _chart_frame(block: dict, index_col: str) -> pd.DataFrame | None:
    if not block or block.get("status") != "ok":
        return None
    rows = block.get("rows") or []
    if not rows:
        return None
    return pd.DataFrame(rows)


st.set_page_config(
    page_title="AI Sales & Distribution Management Expert",
    page_icon="📊",
    layout="wide",
)

st.title("AI Sales & Distribution Management Expert")
st.caption(
    "MBA academic demonstration · Python calculates · Agents interpret · "
    "Hypotheses are never treated as facts"
)

with st.sidebar:
    st.header("Controls")
    st.write("Upload a sales CSV or load the fictional NovaTech sample.")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    load_sample = st.button("Load sample dataset", use_container_width=True)

    analysis_type = st.selectbox(
        "Analysis type",
        [
            "Full analysis",
            "Sales focus",
            "Distribution focus",
            "Strategy and recommendations",
        ],
    )

    preset = st.selectbox("Sample business questions", ["Type my own question"] + SAMPLE_QUESTIONS)
    if preset == "Type my own question":
        question = st.text_area(
            "Business question",
            value="Give a full sales and distribution review with management recommendations.",
            height=90,
        )
    else:
        question = preset
        st.text_area("Business question", value=question, height=90, disabled=True)

    api_present = bool(agents.get_api_key())
    demo_default = not api_present
    demo_mode = st.checkbox(
        "Demo Mode (no live LLM required)",
        value=demo_default,
        help="Uses Python metrics and a labelled demonstration narrative. Turn off to call CrewAI/OpenAI.",
    )
    if not api_present:
        st.info("No OPENAI_API_KEY found. Demo Mode will be used unless you add a key to `.env`.")
    elif demo_mode:
        st.warning("Demo Mode is on. Results will be labelled as demonstration output.")

    run_clicked = st.button("Run analysis", type="primary", use_container_width=True)

    st.divider()
    st.caption("Reported = in the file. Calculated = Pandas. Hypothesis = unproven.")


if "dataframe" not in st.session_state:
    st.session_state.dataframe = None
    st.session_state.load_message = None
    st.session_state.load_warnings = []
    st.session_state.report = None

if load_sample:
    if not SAMPLE_PATH.exists():
        st.sidebar.error("Sample file is missing. Run `python data_generator.py` first.")
    else:
        result = load_csv_file(SAMPLE_PATH)
        if result["ok"]:
            st.session_state.dataframe = result["dataframe"]
            st.session_state.load_message = "Loaded synthetic NovaTech sample (fictional company)."
            st.session_state.load_warnings = result.get("warnings", [])
            st.session_state.report = None
            st.session_state.file_id = "sample"
        else:
            st.sidebar.error(result["error"])

if uploaded is not None:
    file_id = f"{uploaded.name}-{uploaded.size}"
    if st.session_state.get("file_id") != file_id:
        result = load_csv_file(uploaded)
        if result["ok"]:
            st.session_state.dataframe = result["dataframe"]
            st.session_state.load_message = f"Loaded upload: {uploaded.name}"
            st.session_state.load_warnings = result.get("warnings", [])
            st.session_state.report = None
            st.session_state.file_id = file_id
        else:
            st.sidebar.error(result["error"])

df = st.session_state.dataframe

if df is None:
    st.info("Upload a CSV or click **Load sample dataset** in the sidebar to begin.")
    st.markdown(
        """
**What this app does**

1. Validates the file and calculates sales/distribution metrics with Pandas.
2. Shows an overview, sales charts, and distribution charts.
3. Runs four agents: Sales Analyst → Distribution Analyst → Strategy Analyst → Management Advisor.

The sample file is **synthetic**. It does not contain real customers or employees.
"""
    )
    st.stop()

if st.session_state.load_message:
    st.success(st.session_state.load_message)
for warning in st.session_state.load_warnings:
    st.warning(warning)

# --- Section 1: Business Overview -------------------------------------------------
st.header("1. Business Overview")
kpis = overview_kpis(df)
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Revenue", format_inr(kpis["total_revenue"]))
c2.metric("Total Units", format_num(kpis["total_units"]))
c3.metric("Target Achievement", format_num(kpis["achievement_pct"], 1, "%"))
c4.metric("Distributors", format_num(kpis["n_distributors"]))
c5.metric("Return Rate", format_num(kpis["return_rate_pct"], 2, "%"))

with st.expander("Data snapshot", expanded=False):
    st.write(f"Rows: **{len(df)}** · Columns: **{len(df.columns)}**")
    st.write("Columns: " + ", ".join(df.columns.astype(str)))
    st.dataframe(df.head(20), use_container_width=True)

# --- Section 2: Sales Dashboard ---------------------------------------------------
st.header("2. Sales Dashboard")
col_a, col_b = st.columns(2)

region_df = _chart_frame(regional_sales(df), "Region")
if region_df is not None and "Region" in region_df.columns:
    fig = px.bar(region_df, x="Region", y="Revenue", title="Revenue by region", text_auto=".2s")
    fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    col_a.plotly_chart(fig, use_container_width=True)
else:
    col_a.info("Regional revenue chart needs a Region column.")

product_df = _chart_frame(product_sales(df), "Product")
if product_df is not None and "Product" in product_df.columns:
    fig = px.bar(product_df, x="Product", y="Revenue", title="Revenue by product", text_auto=".2s")
    fig.update_layout(margin=dict(t=50, b=20, l=20, r=20), xaxis_tickangle=-25)
    col_b.plotly_chart(fig, use_container_width=True)
else:
    col_b.info("Product revenue chart needs a Product column.")

col_c, col_d = st.columns(2)
ach = target_achievement(df)
if ach.get("status") == "ok":
    cmp = pd.DataFrame(
        {
            "Measure": ["Actual", "Target"],
            "INR": [ach["actual_revenue"], ach["target_revenue"]],
        }
    )
    fig = px.bar(cmp, x="Measure", y="INR", title="Target vs actual revenue", text_auto=".2s")
    fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    col_c.plotly_chart(fig, use_container_width=True)
else:
    col_c.info("Target vs actual needs a Target column.")

month_block = monthly_sales(df)
month_df = _chart_frame(month_block, "Month")
if month_df is not None:
    fig = px.line(month_df, x="Month", y="Revenue", markers=True, title="Monthly revenue trend")
    fig.update_layout(margin=dict(t=50, b=20, l=20, r=20))
    col_d.plotly_chart(fig, use_container_width=True)
else:
    col_d.info("Monthly trend needs Date or Month.")

# --- Section 3: Distribution Dashboard --------------------------------------------
st.header("3. Distribution Dashboard")
col_e, col_f = st.columns(2)

dist_df = _chart_frame(distributor_sales(df), "Distributor")
if dist_df is not None:
    top_dist = dist_df.head(10)
    fig = px.bar(
        top_dist,
        x="Revenue",
        y="Distributor",
        orientation="h",
        title="Distributor performance (top 10 by revenue)",
        text_auto=".2s",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, margin=dict(t=50, b=20, l=20, r=20))
    col_e.plotly_chart(fig, use_container_width=True)
else:
    col_e.info("Distributor chart needs a Distributor column.")

channel_df = _chart_frame(channel_performance(df), "Channel")
if channel_df is not None:
    fig = px.pie(channel_df, names="Channel", values="Revenue", title="Channel performance")
    col_f.plotly_chart(fig, use_container_width=True)
else:
    col_f.info("Channel chart needs a Channel column.")

inv_block = inventory_analysis(df)
col_g, col_h = st.columns(2)
if inv_block.get("status") == "ok":
    col_g.metric("Potential stockout-risk groups", inv_block.get("stockout_risk_count"))
    col_g.metric("Zero / empty inventory rows", inv_block.get("zero_inventory_rows"))
    risk_rows = inv_block.get("risks") or []
    if risk_rows:
        col_h.write("Stockout-risk sample (calculated flags)")
        col_h.dataframe(pd.DataFrame(risk_rows).head(10), use_container_width=True)
    else:
        col_h.info("No stockout-risk groups flagged with the simple inventory rule.")
else:
    st.info(inv_block.get("reason", "Inventory analysis is not available."))

if dist_df is not None and "Return_Rate_Pct" in dist_df.columns:
    st.subheader("Distributor return rates")
    st.dataframe(
        dist_df[["Distributor", "Revenue", "Return_Rate_Pct", "Avg_Inventory", "Avg_Lead_Time_Days"]]
        .sort_values("Return_Rate_Pct", ascending=False)
        .head(10),
        use_container_width=True,
    )

# --- Run agents -------------------------------------------------------------------
if run_clicked:
    with st.spinner("Calculating metrics and running agents..."):
        st.session_state.report = agents.run_analysis(
            df,
            question=question,
            analysis_type=analysis_type,
            demo_mode=demo_mode,
        )

report = st.session_state.report
if report is None:
    st.header("4. AI Analysis")
    st.info("Choose a question in the sidebar and click **Run analysis**.")
    st.header("5. Management Summary")
    st.info("The executive summary appears after analysis.")
    st.stop()

if report.get("mode") == "demo":
    st.warning(report.get("mode_label", "DEMO MODE — demonstration output"))
else:
    st.success(report.get("mode_label", "Live agent run complete"))

if report.get("error"):
    st.error("Live agents failed; showing Demo Mode output instead. " + str(report["error"]))

# --- Section 4: AI Analysis -------------------------------------------------------
st.header("4. AI Analysis")
tabs = st.tabs(
    [
        "Key findings",
        "Root causes",
        "Recommendations",
        "Priority actions",
        "KPIs",
        "Sales agent",
        "Distribution agent",
        "Strategy agent",
    ]
)

with tabs[0]:
    st.markdown(report.get("key_findings") or report.get("sales_findings") or "_No findings parsed._")
with tabs[1]:
    st.markdown("**Potential root causes**")
    st.markdown(report.get("root_causes") or "_None parsed._")
    st.markdown("**Hypotheses (not proven)**")
    st.markdown(report.get("hypotheses") or "_None parsed._")
with tabs[2]:
    st.markdown(report.get("recommended_actions") or "_None parsed._")
with tabs[3]:
    st.markdown(report.get("priority_problems") or "_None parsed._")
    st.markdown(report.get("implementation_plan") or "")
with tabs[4]:
    st.markdown(report.get("kpis") or "_None parsed._")
with tabs[5]:
    st.markdown(report.get("sales_findings") or "")
with tabs[6]:
    st.markdown(report.get("distribution_findings") or "")
with tabs[7]:
    st.markdown(report.get("strategy_findings") or "")

# --- Section 5: Management Summary ------------------------------------------------
st.header("5. Management Summary")
st.subheader("Executive summary")
st.markdown(report.get("executive_summary") or "_Summary not parsed. Full report is below._")

with st.expander("Full management report", expanded=False):
    st.markdown(report.get("management_report") or "")

with st.expander("Risks and limitations", expanded=True):
    st.markdown(report.get("risks") or "")

with st.expander("Python metrics pack (source of numbers)", expanded=False):
    st.json(report.get("metrics") or build_metrics_pack(df))
