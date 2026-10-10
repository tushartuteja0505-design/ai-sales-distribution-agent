# AI Sales & Distribution Management Expert

MBA academic mini-project. **Not a production system.**

The app helps a sales and distribution manager upload a CSV, see Python-calculated metrics and charts, and receive recommendations from four specialist AI agents.

**Viva line:** *Python calculates. Agents interpret. Management Advisor recommends. Hypotheses are never treated as facts.*

## 1. Project objective

Demonstrate a **domain-specific multi-agent AI system** for Sales and Distribution Management:

1. Upload sales/distribution data (or use the synthetic NovaTech sample).
2. Validate the file and compute metrics with **Pandas**.
3. Display an overview, sales dashboard, and distribution dashboard.
4. Run four agents in a fixed order.
5. Show findings, root causes, actions, KPIs, and an executive summary.

The sample company **NovaTech Electronics** is fictional. The CSV contains **no real customers or employees**.

## 2. Architecture

```text
User question + CSV
        ↓
Python validation (tools.py)
        ↓
Python business metrics (Pandas)
        ↓
Sales Analyst  +  Distribution Analyst
        ↓
Strategy Analyst
        ↓
Management Advisor
        ↓
Streamlit dashboards + management report
```

| File | Role |
|---|---|
| `app.py` | Streamlit interface |
| `tools.py` | Pandas metrics (the numerical source of truth) |
| `prompts.py` | Agent instructions and information-discipline rules |
| `tasks.py` | Sequential task definitions |
| `agents.py` | CrewAI crew, OpenAI fallback, Demo Mode |
| `data_generator.py` | Builds the synthetic CSV |
| `data/sample_sales_data.csv` | ~1,000 fictional rows for 2025 |
| `PROJECT_ARCHITECTURE.md` | Full design note for the viva |

**Stack:** Python, Pandas, Plotly, Streamlit, CrewAI, OpenAI API, python-dotenv.

**Run modes**

| Mode | When |
|---|---|
| **Demo Mode** | No API key, or the checkbox is on. Narrative is built from Pandas metrics and labelled as demo output. |
| **CrewAI** | `OPENAI_API_KEY` is set and CrewAI imports successfully. |
| **OpenAI fallback** | Key is set but CrewAI cannot import (for example some Python 3.14 environments). Same four roles, sequential chat calls. |

If a live run fails, the app falls back to Demo Mode and shows the error.

## 3. Agent responsibilities

1. **Sales Analyst** — revenue, units, growth, target achievement, regions, products, trends. Uses calculated metrics only.
2. **Distribution Analyst** — distributors, inventory / stockout flags, channels, returns, gaps.
3. **Strategy Analyst** — combines the two notes, ranks problems, separates facts from hypotheses.
4. **Management Advisor** — actions (High/Medium/Low), short- and medium-term plan, KPIs, impact, risks, executive summary.

**Information types**

- **Reported** — already in the file.
- **Calculated** — produced by Pandas.
- **Hypothesis** — possible explanation, never presented as a fact.

## 4. Installation

You need Python 3.10+ (the project was developed in a local virtual environment).

```bash
cd AI_Business_Expert
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS / Linux:

```bash
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Optional: regenerate the sample file.

```bash
python data_generator.py
```

## 5. Virtual environment setup

Always activate `venv` before running the app or tests so packages do not install into the system Python.

If CrewAI does not install on your Python version, you can still:

- run **Demo Mode** (no extra packages beyond Streamlit/Pandas/Plotly/dotenv), or
- install `openai` and use the sequential fallback when a key is present.

## 6. API key configuration

Copy the example file and add your key. **Never put the key in source code or in Git.**

```bash
copy .env.example .env
```

On macOS/Linux: `cp .env.example .env`

Edit `.env`:

```text
OPENAI_API_KEY=your_key_here
OPENAI_MODEL_NAME=gpt-4o-mini
```

The app loads `.env` via `python-dotenv`. Streamlit Community Cloud should use **Secrets**, not a committed `.env` file.

Without a key, leave Demo Mode checked and the project still runs for a viva.

## 7. How to run Streamlit

```bash
streamlit run app.py
```

Typical local URL: `http://localhost:8501`

Suggested demo path:

1. Click **Load sample dataset**.
2. Keep **Demo Mode** on if you have no key.
3. Pick a sample question (for example regions below target).
4. Click **Run analysis**.
5. Walk through sections 1–5. Show the metrics pack expander to prove numbers come from Python.

## 8. How to run tests

```bash
pytest -q
```

Tests cover totals, growth, achievement, regional/product/distributor sales, inventory flags, return rate, discounts, missing columns, empty files, and the sample CSV.

## 9. How to deploy to Streamlit Community Cloud

1. Push this folder to a GitHub repository (**do not commit `.env`**).
2. Go to [https://share.streamlit.io](https://share.streamlit.io) and deploy from that repo.
3. Set the main file to `app.py`.
4. In **App settings → Secrets** add:

```text
OPENAI_API_KEY = "your_key_here"
OPENAI_MODEL_NAME = "gpt-4o-mini"
```

5. Confirm `data/sample_sales_data.csv` and `requirements.txt` are in the repo.
6. If Cloud build fails on CrewAI (heavy / Python pin), the app still works in Demo Mode and with the OpenAI fallback as long as `openai` installs.

Students can also demonstrate locally with `streamlit run app.py` if Cloud is not required by the course.

## 10. Limitations

- Academic demonstration only; a manager must check numbers before acting.
- Quality depends on the uploaded columns. Missing Target, Inventory, or Distributor reduces the story.
- Revenue is not profit. No competitor or customer-satisfaction engine unless those fields exist.
- Stockout flags are a simple inventory rule, not a full forecast.
- Live LLMs can still over-claim; prompts and the three-way information rule are the control, not a guarantee.
- Demo Mode is a metrics-based template, not a live model. It is labelled as such.
- No vector database, RAG, fine-tuning, Docker, or Kubernetes — by design, so an MBA student can explain the system.

## Example business questions

- Which regions are below sales target, and what should management do first?
- Which distributors are weak, and is the issue sales, returns, or inventory?
- Are there products or regions with potential stockout risk?
- Is the main problem a sales problem, a distribution problem, or both?
