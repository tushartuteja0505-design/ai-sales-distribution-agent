"""
Pandas analytics for the AI Sales & Distribution Management Expert.

All important numbers are calculated here. Agents interpret these results;
they must not invent totals, percentages, or rankings.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

# Common CSV header aliases so a slightly different upload still works.
COLUMN_ALIASES: dict[str, list[str]] = {
    "Date": ["date", "order_date", "transaction_date"],
    "Month": ["month", "period"],
    "Region": ["region", "zone"],
    "State": ["state"],
    "Product": ["product", "sku", "item"],
    "Product_Category": ["product_category", "category"],
    "Distributor": ["distributor", "dealer", "partner"],
    "Salesperson": ["salesperson", "sales_person", "rep"],
    "Channel": ["channel", "route_to_market"],
    "Customer_Type": ["customer_type", "customer"],
    "Units_Sold": ["units_sold", "units", "quantity", "qty"],
    "Unit_Price": ["unit_price", "price"],
    "Revenue": ["revenue", "sales", "amount", "sales_value"],
    "Target": ["target", "sales_target"],
    "Discount_Percentage": ["discount_percentage", "discount", "discount_pct"],
    "Orders": ["orders", "order_count"],
    "Returns": ["returns", "returned_units"],
    "Inventory": ["inventory", "stock", "closing_stock"],
    "Lead_Time_Days": ["lead_time_days", "lead_time"],
}

NUMERIC_COLUMNS = [
    "Units_Sold",
    "Unit_Price",
    "Revenue",
    "Target",
    "Discount_Percentage",
    "Orders",
    "Returns",
    "Inventory",
    "Lead_Time_Days",
]


def _not_available(reason: str) -> dict[str, Any]:
    return {"status": "not_available", "reason": reason}


def _ok(payload: dict[str, Any]) -> dict[str, Any]:
    out = {"status": "ok"}
    out.update(payload)
    return out


def _json_safe(value: Any) -> Any:
    """Convert pandas/numpy values into plain Python types for JSON and prompts."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except (ValueError, AttributeError):
            pass
    if isinstance(value, pd.Timestamp):
        return value.strftime("%Y-%m-%d")
    return value


def _round_num(value: Any, digits: int = 2) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    return round(float(value), digits)


def normalize_columns(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Rename known aliases to the project's standard column names."""
    working = df.copy()
    working.columns = [str(c).strip() for c in working.columns]
    notes: list[str] = []
    lower_map = {c.lower().replace(" ", "_"): c for c in working.columns}

    for standard, aliases in COLUMN_ALIASES.items():
        if standard in working.columns:
            continue
        for alias in aliases:
            key = alias.lower().replace(" ", "_")
            if key in lower_map:
                original = lower_map[key]
                working = working.rename(columns={original: standard})
                notes.append(f"Mapped column '{original}' to '{standard}'.")
                break
    return working, notes


def coerce_types(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """Make numeric and date columns usable; collect warnings instead of crashing."""
    working = df.copy()
    warnings: list[str] = []

    if "Date" in working.columns:
        working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
        bad_dates = int(working["Date"].isna().sum())
        if bad_dates:
            warnings.append(f"{bad_dates} row(s) have invalid dates and were ignored in time analysis.")

    for col in NUMERIC_COLUMNS:
        if col not in working.columns:
            continue
        working[col] = pd.to_numeric(working[col], errors="coerce")
        missing = int(working[col].isna().sum())
        if missing:
            warnings.append(f"{missing} row(s) have non-numeric values in '{col}'.")

    if "Revenue" not in working.columns and {"Units_Sold", "Unit_Price"} <= set(working.columns):
        discount = working["Discount_Percentage"] if "Discount_Percentage" in working.columns else 0
        working["Revenue"] = working["Units_Sold"] * working["Unit_Price"] * (1 - pd.to_numeric(discount, errors="coerce").fillna(0) / 100.0)
        warnings.append("Revenue was calculated from Units_Sold, Unit_Price, and Discount_Percentage.")

    return working, warnings


def validate_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Check that a uploaded/sample table can be analysed."""
    if df is None or df.empty:
        return {
            "ok": False,
            "error": "The dataset is empty. Upload a CSV with at least one data row.",
            "warnings": [],
            "columns": [],
            "n_rows": 0,
        }

    normalised, map_notes = normalize_columns(df)
    typed, type_notes = coerce_types(normalised)
    warnings = map_notes + type_notes

    if "Revenue" not in typed.columns:
        return {
            "ok": False,
            "error": "The file needs a Revenue column, or Units_Sold plus Unit_Price so revenue can be calculated.",
            "warnings": warnings,
            "columns": list(typed.columns),
            "n_rows": int(len(typed)),
        }

    usable = typed.dropna(subset=["Revenue"])
    if usable.empty:
        return {
            "ok": False,
            "error": "Revenue values are missing or not numeric.",
            "warnings": warnings,
            "columns": list(typed.columns),
            "n_rows": int(len(typed)),
        }

    return {
        "ok": True,
        "error": None,
        "warnings": warnings,
        "columns": list(typed.columns),
        "n_rows": int(len(usable)),
        "dataframe": usable.reset_index(drop=True),
        "reported_columns": list(typed.columns),
        "missing_standard_columns": [c for c in COLUMN_ALIASES if c not in typed.columns],
    }


def load_csv_file(source: Any) -> dict[str, Any]:
    """Load a CSV path or Streamlit UploadedFile. Never raises to the UI."""
    try:
        df = pd.read_csv(source)
    except Exception as exc:  # noqa: BLE001 - show a friendly message in the app
        return {
            "ok": False,
            "error": f"Could not read the CSV file. {exc}",
            "warnings": [],
            "columns": [],
            "n_rows": 0,
        }
    return validate_dataframe(df)


def _has(df: pd.DataFrame, *cols: str) -> bool:
    return all(col in df.columns for col in cols)


def total_revenue(df: pd.DataFrame) -> dict[str, Any]:
    if not _has(df, "Revenue"):
        return _not_available("Revenue column is missing.")
    return _ok({"total_revenue": _round_num(df["Revenue"].sum())})


def total_units(df: pd.DataFrame) -> dict[str, Any]:
    if not _has(df, "Units_Sold"):
        return _not_available("Units_Sold column is missing.")
    return _ok({"total_units": _round_num(df["Units_Sold"].sum(), 0)})


def revenue_growth(df: pd.DataFrame) -> dict[str, Any]:
    """Month-on-month growth using the last two months, plus first-vs-last month."""
    if not _has(df, "Revenue"):
        return _not_available("Revenue column is missing.")

    monthly = _monthly_frame(df)
    if monthly is None or len(monthly) < 2:
        return _not_available("At least two months of dated revenue are required for growth.")

    last = monthly.iloc[-1]
    prev = monthly.iloc[-2]
    mom = None
    if prev["Revenue"] not in (0, None):
        mom = (last["Revenue"] - prev["Revenue"]) / prev["Revenue"] * 100

    first = monthly.iloc[0]
    overall = None
    if first["Revenue"] not in (0, None):
        overall = (last["Revenue"] - first["Revenue"]) / first["Revenue"] * 100

    return _ok(
        {
            "latest_month": last["Month"],
            "previous_month": prev["Month"],
            "latest_revenue": _round_num(last["Revenue"]),
            "previous_revenue": _round_num(prev["Revenue"]),
            "month_on_month_growth_pct": _round_num(mom, 1),
            "first_month": first["Month"],
            "first_month_revenue": _round_num(first["Revenue"]),
            "first_to_last_growth_pct": _round_num(overall, 1),
        }
    )


def target_achievement(df: pd.DataFrame) -> dict[str, Any]:
    if not _has(df, "Revenue", "Target"):
        return _not_available("Revenue and Target columns are required.")
    actual = float(df["Revenue"].sum())
    target = float(df["Target"].sum())
    pct = (actual / target * 100) if target > 0 else None
    return _ok(
        {
            "actual_revenue": _round_num(actual),
            "target_revenue": _round_num(target),
            "gap": _round_num(actual - target),
            "achievement_pct": _round_num(pct, 1),
        }
    )


def _group_sales(df: pd.DataFrame, dimension: str) -> dict[str, Any]:
    if not _has(df, "Revenue", dimension):
        return _not_available(f"Revenue and {dimension} columns are required.")

    grouped = df.groupby(dimension, dropna=False)
    table = grouped["Revenue"].sum().reset_index()
    if _has(df, "Units_Sold"):
        table["Units_Sold"] = grouped["Units_Sold"].sum().values
    if _has(df, "Target"):
        table["Target"] = grouped["Target"].sum().values
        table["Achievement_Pct"] = table.apply(
            lambda r: round(r["Revenue"] / r["Target"] * 100, 1) if r["Target"] else None,
            axis=1,
        )
    total = float(table["Revenue"].sum()) or 1.0
    table["Share_Pct"] = (table["Revenue"] / total * 100).round(1)
    table = table.sort_values("Revenue", ascending=False)
    records = [
        {k: _json_safe(v) if not isinstance(v, float) else _round_num(v) for k, v in row.items()}
        for row in table.to_dict(orient="records")
    ]
    below_target = []
    if "Achievement_Pct" in table.columns:
        below_target = [
            rec[dimension]
            for rec in records
            if rec.get("Achievement_Pct") is not None and rec["Achievement_Pct"] < 100
        ]
    return _ok({"rows": records, "below_target": below_target})


def regional_sales(df: pd.DataFrame) -> dict[str, Any]:
    return _group_sales(df, "Region")


def product_sales(df: pd.DataFrame) -> dict[str, Any]:
    return _group_sales(df, "Product")


def distributor_sales(df: pd.DataFrame) -> dict[str, Any]:
    result = _group_sales(df, "Distributor")
    if result.get("status") != "ok":
        return result
    if _has(df, "Returns", "Units_Sold"):
        extra = (
            df.groupby("Distributor", dropna=False)[["Returns", "Units_Sold"]]
            .sum()
            .reset_index()
        )
        extra["Return_Rate_Pct"] = extra.apply(
            lambda r: round(r["Returns"] / r["Units_Sold"] * 100, 2) if r["Units_Sold"] else None,
            axis=1,
        )
        rates = {row["Distributor"]: row["Return_Rate_Pct"] for _, row in extra.iterrows()}
        for rec in result["rows"]:
            rec["Return_Rate_Pct"] = rates.get(rec["Distributor"])
    if _has(df, "Inventory"):
        inv = df.groupby("Distributor", dropna=False)["Inventory"].mean().round(1)
        for rec in result["rows"]:
            rec["Avg_Inventory"] = _json_safe(inv.get(rec["Distributor"]))
    if _has(df, "Lead_Time_Days"):
        lead = df.groupby("Distributor", dropna=False)["Lead_Time_Days"].mean().round(1)
        for rec in result["rows"]:
            rec["Avg_Lead_Time_Days"] = _json_safe(lead.get(rec["Distributor"]))
    return result


def channel_performance(df: pd.DataFrame) -> dict[str, Any]:
    return _group_sales(df, "Channel")


def _monthly_frame(df: pd.DataFrame) -> pd.DataFrame | None:
    working = df.copy()
    if "Date" in working.columns:
        dates = pd.to_datetime(working["Date"], errors="coerce")
        working = working.loc[dates.notna()].copy()
        working["MonthKey"] = dates.loc[dates.notna()].dt.to_period("M").astype(str)
    elif "Month" in working.columns:
        working["MonthKey"] = working["Month"].astype(str)
    else:
        return None
    monthly = working.groupby("MonthKey", dropna=False)["Revenue"].sum().reset_index()
    monthly = monthly.sort_values("MonthKey")
    monthly = monthly.rename(columns={"MonthKey": "Month"})
    if _has(working, "Target"):
        monthly["Target"] = working.groupby("MonthKey")["Target"].sum().values
    if _has(working, "Units_Sold"):
        monthly["Units_Sold"] = working.groupby("MonthKey")["Units_Sold"].sum().values
    monthly["Change_Pct"] = monthly["Revenue"].pct_change() * 100
    monthly["Change_Pct"] = monthly["Change_Pct"].round(1)
    return monthly


def monthly_sales(df: pd.DataFrame) -> dict[str, Any]:
    monthly = _monthly_frame(df)
    if monthly is None or monthly.empty:
        return _not_available("Date or Month column is required for trend analysis.")
    rows = []
    for rec in monthly.to_dict(orient="records"):
        rows.append(
            {
                "Month": rec["Month"],
                "Revenue": _round_num(rec["Revenue"]),
                "Target": _round_num(rec.get("Target")),
                "Units_Sold": _round_num(rec.get("Units_Sold"), 0),
                "Change_Pct": _json_safe(rec.get("Change_Pct")),
            }
        )
    significant = [r for r in rows if r.get("Change_Pct") is not None and abs(float(r["Change_Pct"])) >= 15]
    return _ok({"rows": rows, "significant_changes": significant})


def inventory_analysis(df: pd.DataFrame) -> dict[str, Any]:
    if not _has(df, "Inventory"):
        return _not_available("Inventory column is missing.")

    grain_cols = [c for c in ["Region", "Product", "Distributor"] if c in df.columns]
    if not grain_cols:
        return _ok(
            {
                "row_count": int(len(df)),
                "stockout_risk_count": int((df["Inventory"] <= 0).sum()),
                "zero_inventory_rows": int((df["Inventory"] <= 0).sum()),
                "risks": [],
                "lowest_inventory": [],
            }
        )

    agg_kwargs: dict[str, tuple[str, str]] = {
        "Avg_Inventory": ("Inventory", "mean"),
        "Min_Inventory": ("Inventory", "min"),
    }
    if "Units_Sold" in df.columns:
        agg_kwargs["Units_Sold"] = ("Units_Sold", "sum")

    grouped = df.groupby(grain_cols, dropna=False).agg(**agg_kwargs).reset_index()
    if "Units_Sold" not in grouped.columns:
        grouped["Units_Sold"] = None

    grouped["Avg_Inventory"] = grouped["Avg_Inventory"].round(1)
    grouped["Stockout_Risk"] = grouped.apply(
        lambda r: bool(
            r["Min_Inventory"] <= 0
            or (
                pd.notna(r.get("Units_Sold"))
                and r["Units_Sold"]
                and r["Avg_Inventory"] < 0.15 * r["Units_Sold"]
            )
        ),
        axis=1,
    )
    rows = [
        {k: _json_safe(v) if not isinstance(v, float) else _round_num(v) for k, v in rec.items()}
        for rec in grouped.to_dict(orient="records")
    ]
    risks = [r for r in rows if r.get("Stockout_Risk")]
    return _ok(
        {
            "row_count": len(rows),
            "stockout_risk_count": len(risks),
            "zero_inventory_rows": int((df["Inventory"] <= 0).sum()),
            "risks": risks[:15],
            "lowest_inventory": sorted(rows, key=lambda r: r.get("Min_Inventory") or 0)[:8],
        }
    )


def return_rate(df: pd.DataFrame) -> dict[str, Any]:
    if not _has(df, "Returns", "Units_Sold"):
        return _not_available("Returns and Units_Sold columns are required.")
    units = float(df["Units_Sold"].sum())
    returns = float(df["Returns"].sum())
    pct = (returns / units * 100) if units else None
    by_dist: list[dict[str, Any]] = []
    if "Distributor" in df.columns:
        g = df.groupby("Distributor")[["Returns", "Units_Sold"]].sum().reset_index()
        g["Return_Rate_Pct"] = g.apply(
            lambda r: round(r["Returns"] / r["Units_Sold"] * 100, 2) if r["Units_Sold"] else None,
            axis=1,
        )
        by_dist = [
            {
                "Distributor": rec["Distributor"],
                "Return_Rate_Pct": rec["Return_Rate_Pct"],
                "Returns": _round_num(rec["Returns"], 0),
            }
            for rec in g.sort_values("Return_Rate_Pct", ascending=False).to_dict(orient="records")
        ]
    return _ok(
        {
            "total_returns": _round_num(returns, 0),
            "total_units": _round_num(units, 0),
            "return_rate_pct": _round_num(pct, 2),
            "by_distributor": by_dist[:10],
        }
    )


def discount_analysis(df: pd.DataFrame) -> dict[str, Any]:
    if not _has(df, "Discount_Percentage"):
        return _not_available("Discount_Percentage column is missing.")
    payload: dict[str, Any] = {
        "average_discount_pct": _round_num(df["Discount_Percentage"].mean(), 1),
        "max_discount_pct": _round_num(df["Discount_Percentage"].max(), 1),
        "min_discount_pct": _round_num(df["Discount_Percentage"].min(), 1),
    }
    if "Region" in df.columns:
        payload["by_region"] = [
            {"Region": idx, "Average_Discount_Pct": _round_num(val, 1)}
            for idx, val in df.groupby("Region")["Discount_Percentage"].mean().items()
        ]
    return _ok(payload)


def top_performers(df: pd.DataFrame, dimension: str, n: int = 5) -> dict[str, Any]:
    grouped = _group_sales(df, dimension)
    if grouped.get("status") != "ok":
        return grouped
    return _ok({"dimension": dimension, "rows": grouped["rows"][:n]})


def bottom_performers(df: pd.DataFrame, dimension: str, n: int = 5) -> dict[str, Any]:
    grouped = _group_sales(df, dimension)
    if grouped.get("status") != "ok":
        return grouped
    rows = list(reversed(grouped["rows"]))[:n]
    return _ok({"dimension": dimension, "rows": rows})


def build_metrics_pack(df: pd.DataFrame) -> dict[str, Any]:
    """Single source of numerical truth passed into the agents."""
    date_min = date_max = None
    if "Date" in df.columns:
        dates = pd.to_datetime(df["Date"], errors="coerce")
        if dates.notna().any():
            date_min = dates.min().strftime("%Y-%m-%d")
            date_max = dates.max().strftime("%Y-%m-%d")

    pack = {
        "reported": {
            "n_rows": int(len(df)),
            "columns": list(df.columns),
            "date_min": date_min,
            "date_max": date_max,
            "n_regions": int(df["Region"].nunique()) if "Region" in df.columns else None,
            "n_products": int(df["Product"].nunique()) if "Product" in df.columns else None,
            "n_distributors": int(df["Distributor"].nunique()) if "Distributor" in df.columns else None,
            "n_channels": int(df["Channel"].nunique()) if "Channel" in df.columns else None,
        },
        "calculated": {
            "total_revenue": total_revenue(df),
            "total_units": total_units(df),
            "revenue_growth": revenue_growth(df),
            "target_achievement": target_achievement(df),
            "regional_sales": regional_sales(df),
            "product_sales": product_sales(df),
            "distributor_sales": distributor_sales(df),
            "monthly_sales": monthly_sales(df),
            "inventory_analysis": inventory_analysis(df),
            "return_rate": return_rate(df),
            "discount_analysis": discount_analysis(df),
            "channel_performance": channel_performance(df),
            "top_products": top_performers(df, "Product", 5),
            "bottom_products": bottom_performers(df, "Product", 5),
            "top_distributors": top_performers(df, "Distributor", 5),
            "bottom_distributors": bottom_performers(df, "Distributor", 5),
            "top_regions": top_performers(df, "Region", 5),
        },
    }
    return pack


def metrics_to_prompt_text(pack: dict[str, Any], max_chars: int = 12000) -> str:
    """Compact, readable metrics block for agent prompts."""
    import json

    text = json.dumps(pack, indent=2, default=str)
    if len(text) > max_chars:
        return text[:max_chars] + "\n... [truncated for prompt length]"
    return text


def overview_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Numbers shown in the Streamlit Business Overview strip."""
    rev = total_revenue(df)
    units = total_units(df)
    ach = target_achievement(df)
    ret = return_rate(df)
    n_dist = int(df["Distributor"].nunique()) if "Distributor" in df.columns else None
    return {
        "total_revenue": rev.get("total_revenue"),
        "total_units": units.get("total_units"),
        "achievement_pct": ach.get("achievement_pct"),
        "n_distributors": n_dist,
        "return_rate_pct": ret.get("return_rate_pct"),
        "target_status": ach.get("status"),
        "return_status": ret.get("status"),
    }
