"""
Synthetic sales and distribution data generator for the MBA mini-project:
AI Sales & Distribution Management Expert.

Company: NovaTech Electronics (fictional)
All names, distributors, and salespeople are synthetic. No real personal data.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RANDOM_SEED = 42
N_RECORDS = 1000
OUTPUT_PATH = Path(__file__).resolve().parent / "data" / "sample_sales_data.csv"

REGIONS_STATES = {
    "North": ["Delhi", "Punjab", "Haryana", "Uttar Pradesh", "Rajasthan"],
    "South": ["Karnataka", "Tamil Nadu", "Kerala", "Telangana", "Andhra Pradesh"],
    "East": ["West Bengal", "Odisha", "Bihar", "Assam"],
    "West": ["Maharashtra", "Gujarat", "Goa"],
    "Central": ["Madhya Pradesh", "Chhattisgarh"],
}

PRODUCTS = [
    {"Product": "NovaPhone X", "Product_Category": "Smartphone", "Unit_Price": 18999},
    {"Product": "NovaPhone Pro", "Product_Category": "Smartphone", "Unit_Price": 34999},
    {"Product": "NovaTab 10", "Product_Category": "Tablet", "Unit_Price": 15999},
    {"Product": "NovaTab Pro", "Product_Category": "Tablet", "Unit_Price": 27999},
    {"Product": "NovaBook Air", "Product_Category": "Laptop", "Unit_Price": 54999},
    {"Product": "NovaBook Pro", "Product_Category": "Laptop", "Unit_Price": 89999},
    {"Product": "NovaBuds", "Product_Category": "Audio", "Unit_Price": 3999},
    {"Product": "NovaWatch", "Product_Category": "Wearable", "Unit_Price": 8999},
]

# Demand weight: NovaPhone Pro is the hero SKU; NovaTab 10 is the laggard.
PRODUCT_DEMAND_WEIGHT = {
    "NovaPhone X": 1.05,
    "NovaPhone Pro": 1.45,
    "NovaTab 10": 0.62,
    "NovaTab Pro": 0.95,
    "NovaBook Air": 0.90,
    "NovaBook Pro": 0.78,
    "NovaBuds": 1.20,
    "NovaWatch": 1.00,
}

# Target is set above expected demand for East so it consistently misses.
REGION_VOLUME_FACTOR = {
    "North": 1.05,
    "South": 1.18,
    "East": 0.78,
    "West": 1.22,
    "Central": 0.92,
}

REGION_TARGET_FACTOR = {
    "North": 1.00,
    "South": 1.02,
    "East": 1.08,  # ambitious target vs weaker actuals
    "West": 1.00,
    "Central": 1.00,
}

DISTRIBUTORS = [
    {"Distributor": "Delhi Digital Distributors", "Region": "North", "Strength": 1.15, "ReturnMult": 0.8, "Lead": 4},
    {"Distributor": "Punjab Pixel Partners", "Region": "North", "Strength": 1.00, "ReturnMult": 1.0, "Lead": 5},
    {"Distributor": "Noida Network Supplies", "Region": "North", "Strength": 0.95, "ReturnMult": 1.1, "Lead": 5},
    {"Distributor": "Jaipur Gadget Gateway", "Region": "North", "Strength": 0.90, "ReturnMult": 1.0, "Lead": 6},
    {"Distributor": "Bangalore Electronics Hub", "Region": "South", "Strength": 1.25, "ReturnMult": 0.7, "Lead": 3},
    {"Distributor": "Chennai Digital Supply", "Region": "South", "Strength": 1.10, "ReturnMult": 0.9, "Lead": 4},
    {"Distributor": "Hyderabad Circuit Circle", "Region": "South", "Strength": 1.05, "ReturnMult": 0.9, "Lead": 4},
    {"Distributor": "Kochi Coastal Gadgets", "Region": "South", "Strength": 0.92, "ReturnMult": 1.0, "Lead": 6},
    {"Distributor": "Kolkata Tech Network", "Region": "East", "Strength": 0.88, "ReturnMult": 1.2, "Lead": 7},
    {"Distributor": "Bhubaneswar Byte Bridge", "Region": "East", "Strength": 0.70, "ReturnMult": 1.1, "Lead": 8},
    {"Distributor": "Patna Channel Partners", "Region": "East", "Strength": 0.82, "ReturnMult": 2.4, "Lead": 9},
    {"Distributor": "Guwahati Connect Wholesale", "Region": "East", "Strength": 0.58, "ReturnMult": 1.6, "Lead": 11},
    {"Distributor": "Mumbai Tech Distribution", "Region": "West", "Strength": 1.28, "ReturnMult": 0.75, "Lead": 3},
    {"Distributor": "Pune Processor Pipeline", "Region": "West", "Strength": 1.08, "ReturnMult": 0.85, "Lead": 4},
    {"Distributor": "Ahmedabad Appliance Alliance", "Region": "West", "Strength": 1.02, "ReturnMult": 0.95, "Lead": 5},
    {"Distributor": "Surat Silicon Stores", "Region": "West", "Strength": 0.94, "ReturnMult": 1.0, "Lead": 5},
    {"Distributor": "Bhopal Bundle Distributors", "Region": "Central", "Strength": 0.90, "ReturnMult": 1.15, "Lead": 6},
    {"Distributor": "Indore Inventory Interlink", "Region": "Central", "Strength": 0.86, "ReturnMult": 1.1, "Lead": 7},
    {"Distributor": "Raipur Rapid Retail", "Region": "Central", "Strength": 0.60, "ReturnMult": 2.1, "Lead": 10},
    {"Distributor": "Jabalpur Junction Gadgets", "Region": "Central", "Strength": 0.84, "ReturnMult": 1.2, "Lead": 8},
]

SALESPEOPLE = [
    "Aarav Mehta", "Diya Kapoor", "Rohan Iyer", "Ananya Reddy", "Kabir Nair",
    "Ishita Bose", "Vihaan Joshi", "Myra Kulkarni", "Arjun Desai", "Saanvi Pillai",
    "Aditya Rao", "Kiara Bansal", "Dev Patel", "Nisha Sharma", "Kunal Verma",
    "Pooja Nanda", "Rahul Chatterjee", "Meera Krishnan", "Siddharth Jain", "Tanya Ghosh",
    "Nikhil Saxena", "Riya Malhotra", "Harsh Vardhan", "Aisha Qureshi", "Varun Menon",
    "Sneha Kaur", "Manish Gupta", "Leela Thomas", "Yash Agarwal", "Fatima Shaikh",
]

CHANNELS = ["General Trade", "Modern Trade", "Online", "Institutional"]
CUSTOMER_TYPES = ["Retailer", "Wholesaler", "Institutional Buyer", "Online Customer"]

CHANNEL_WEIGHTS = [0.42, 0.28, 0.20, 0.10]
CUSTOMER_WEIGHTS = [0.45, 0.30, 0.12, 0.13]

# Calendar year 2025: one full year of activity.
START_DATE = pd.Timestamp("2025-01-01")
END_DATE = pd.Timestamp("2025-12-31")

# Month demand index (1=Jan ... 12=Dec). Festive Oct-Nov peak; monsoon dip; laptop lift in Jun-Jul.
MONTH_DEMAND = {
    1: 0.88,
    2: 0.90,
    3: 1.02,
    4: 0.95,
    5: 0.92,
    6: 1.08,
    7: 1.06,
    8: 0.94,
    9: 1.00,
    10: 1.28,
    11: 1.32,
    12: 1.12,
}

# Extra seasonal lift by product category.
CATEGORY_MONTH_LIFT = {
    "Smartphone": {10: 1.20, 11: 1.25, 12: 1.10},
    "Audio": {10: 1.22, 11: 1.30, 12: 1.15},
    "Wearable": {10: 1.18, 11: 1.22, 2: 1.08},
    "Laptop": {6: 1.25, 7: 1.22, 1: 1.08},
    "Tablet": {6: 1.10, 10: 1.08},
}

COLUMNS = [
    "Date",
    "Month",
    "Region",
    "State",
    "Product",
    "Product_Category",
    "Distributor",
    "Salesperson",
    "Channel",
    "Customer_Type",
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


def _month_factor(month: int, category: str) -> float:
    base = MONTH_DEMAND[month]
    extra = CATEGORY_MONTH_LIFT.get(category, {}).get(month, 1.0)
    return base * extra


def _base_units(product_name: str, rng: np.random.Generator) -> int:
    if product_name in ("NovaBuds", "NovaWatch"):
        return int(rng.integers(8, 36))
    if product_name in ("NovaPhone X", "NovaPhone Pro"):
        return int(rng.integers(4, 22))
    if "Tab" in product_name:
        return int(rng.integers(3, 16))
    return int(rng.integers(2, 10))


def generate_dataset(n_records: int = N_RECORDS, seed: int = RANDOM_SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    product_by_name = {p["Product"]: p for p in PRODUCTS}
    dist_by_region: dict[str, list[dict]] = {}
    for d in DISTRIBUTORS:
        dist_by_region.setdefault(d["Region"], []).append(d)

    region_names = list(REGIONS_STATES.keys())
    region_probs = np.array([0.20, 0.24, 0.16, 0.24, 0.16], dtype=float)
    region_probs = region_probs / region_probs.sum()

    product_names = [p["Product"] for p in PRODUCTS]
    product_probs = np.array([PRODUCT_DEMAND_WEIGHT[name] for name in product_names], dtype=float)
    product_probs = product_probs / product_probs.sum()

    rows: list[dict] = []
    date_span = (END_DATE - START_DATE).days + 1

    for _ in range(n_records):
        region = str(rng.choice(region_names, p=region_probs))
        state = str(rng.choice(REGIONS_STATES[region]))
        distributor = dist_by_region[region][int(rng.integers(0, len(dist_by_region[region])))]
        product_name = str(rng.choice(product_names, p=product_probs))
        product = product_by_name[product_name]

        offset = int(rng.integers(0, date_span))
        date = START_DATE + pd.Timedelta(days=offset)
        month_num = int(date.month)
        month_label = date.strftime("%b-%Y")

        units_raw = _base_units(product_name, rng)
        volume = (
            units_raw
            * PRODUCT_DEMAND_WEIGHT[product_name]
            * REGION_VOLUME_FACTOR[region]
            * float(distributor["Strength"])
            * _month_factor(month_num, product["Product_Category"])
            * float(rng.uniform(0.85, 1.15))
        )
        units_sold = max(1, int(round(volume)))

        # Festive months: slightly deeper discounts.
        if month_num in (10, 11):
            discount = float(np.clip(rng.normal(11.5, 3.0), 4.0, 18.0))
        else:
            discount = float(np.clip(rng.normal(7.5, 2.8), 2.0, 15.0))
        discount = round(discount, 1)

        unit_price = int(product["Unit_Price"])
        revenue = round(units_sold * unit_price * (1 - discount / 100.0), 2)

        expected_units = max(
            1.0,
            units_raw
            * PRODUCT_DEMAND_WEIGHT[product_name]
            * ((REGION_VOLUME_FACTOR[region] + 1.0) / 2.0)
            * 1.05
            * _month_factor(month_num, product["Product_Category"]),
        )
        target_revenue = (
            expected_units
            * unit_price
            * (1 - 0.08)
            * REGION_TARGET_FACTOR[region]
        )
        if product_name == "NovaTab 10":
            target_revenue *= 1.18
        if product_name == "NovaPhone Pro":
            target_revenue *= 0.96
        target = round(max(target_revenue, revenue * 0.55), 2)

        orders = max(1, int(round(units_sold / float(rng.uniform(2.2, 5.5)))))
        orders = min(orders, units_sold)

        return_rate = float(np.clip(rng.normal(0.028, 0.012) * float(distributor["ReturnMult"]), 0.005, 0.18))
        returns = int(round(units_sold * return_rate))
        if returns >= units_sold:
            returns = max(0, units_sold - 1)

        lead_time = int(np.clip(round(rng.normal(distributor["Lead"], 1.1)), 2, 14))

        # Closing inventory. Weak East/Central coverage and laggard SKUs run tighter stock.
        cover_days = float(rng.uniform(12, 45))
        if region in ("East", "Central") and product_name in ("NovaWatch", "NovaTab 10", "NovaPhone X"):
            cover_days = float(rng.uniform(2, 14))
        if distributor["Distributor"] in ("Guwahati Connect Wholesale", "Raipur Rapid Retail"):
            cover_days = min(cover_days, float(rng.uniform(1, 9)))
        if product_name == "NovaPhone Pro" and region in ("West", "South"):
            cover_days = float(rng.uniform(18, 50))

        daily_run = max(units_sold / 7.0, 0.5)
        inventory = max(0, int(round(daily_run * cover_days)))
        if cover_days < 4 and units_sold >= 8:
            inventory = int(rng.integers(0, 4))

        salesperson = str(rng.choice(SALESPEOPLE))
        channel = str(rng.choice(CHANNELS, p=CHANNEL_WEIGHTS))
        if channel == "Online":
            customer_type = "Online Customer"
        elif channel == "Institutional":
            customer_type = "Institutional Buyer"
        else:
            customer_type = str(rng.choice(["Retailer", "Wholesaler"], p=[0.62, 0.38]))

        rows.append(
            {
                "Date": date.strftime("%Y-%m-%d"),
                "Month": month_label,
                "Region": region,
                "State": state,
                "Product": product_name,
                "Product_Category": product["Product_Category"],
                "Distributor": distributor["Distributor"],
                "Salesperson": salesperson,
                "Channel": channel,
                "Customer_Type": customer_type,
                "Units_Sold": units_sold,
                "Unit_Price": unit_price,
                "Revenue": revenue,
                "Target": target,
                "Discount_Percentage": discount,
                "Orders": orders,
                "Returns": returns,
                "Inventory": inventory,
                "Lead_Time_Days": lead_time,
            }
        )

    df = pd.DataFrame(rows, columns=COLUMNS)
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(["Date", "Region", "Distributor", "Product"]).reset_index(drop=True)
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    return df


def validate_dataset(df: pd.DataFrame) -> dict:
    """Run demo-quality checks and return a results dictionary."""
    expected_rev = df["Units_Sold"] * df["Unit_Price"] * (1 - df["Discount_Percentage"] / 100.0)
    revenue_gap = (df["Revenue"] - expected_rev).abs()

    checks = {
        "row_count_ok": 950 <= len(df) <= 1100,
        "column_count_ok": list(df.columns) == COLUMNS,
        "no_missing_values": int(df.isna().sum().sum()) == 0,
        "numeric_core_ok": all(
            pd.api.types.is_numeric_dtype(df[c])
            for c in [
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
        ),
        "valid_dates": pd.to_datetime(df["Date"], errors="coerce").notna().all(),
        "no_negative_sales": (df["Units_Sold"] >= 0).all() and (df["Revenue"] >= 0).all(),
        "no_negative_units_or_orders": (df["Units_Sold"] >= 1).all() and (df["Orders"] >= 1).all(),
        "discount_range_ok": df["Discount_Percentage"].between(0, 25).all(),
        "returns_not_above_units": (df["Returns"] <= df["Units_Sold"]).all(),
        "revenue_formula_ok": (revenue_gap < 0.02).all(),
        "multiple_regions": df["Region"].nunique() >= 5,
        "multiple_distributors": df["Distributor"].nunique() >= 15,
        "all_products_present": set(df["Product"].unique()) == {p["Product"] for p in PRODUCTS},
        "twelve_months": df["Date"].map(lambda x: str(x)[:7]).nunique() == 12,
    }

    summary = {
        "n_rows": int(len(df)),
        "n_columns": int(df.shape[1]),
        "columns": list(df.columns),
        "missing_values": {k: int(v) for k, v in df.isna().sum().to_dict().items() if v},
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "regions": sorted(df["Region"].unique().tolist()),
        "n_products": int(df["Product"].nunique()),
        "products": sorted(df["Product"].unique().tolist()),
        "n_distributors": int(df["Distributor"].nunique()),
        "date_min": str(df["Date"].min()),
        "date_max": str(df["Date"].max()),
        "max_revenue_formula_gap": float(revenue_gap.max()),
        "checks": {k: bool(v) for k, v in checks.items()},
        "all_passed": bool(all(checks.values())),
    }
    return summary


def print_validation(summary: dict) -> None:
    print("\n=== Dataset validation ===")
    print(f"Rows: {summary['n_rows']}")
    print(f"Columns: {summary['n_columns']}")
    print(f"Date range: {summary['date_min']} to {summary['date_max']}")
    print(f"Regions: {summary['regions']}")
    print(f"Products ({summary['n_products']}): {summary['products']}")
    print(f"Distributors: {summary['n_distributors']}")
    print(f"Missing-value columns: {summary['missing_values'] or 'none'}")
    print(f"Max revenue formula gap: {summary['max_revenue_formula_gap']:.6f}")
    print("Checks:")
    for name, ok in summary["checks"].items():
        flag = "PASS" if ok else "FAIL"
        print(f"  [{flag}] {name}")
    print(f"\nOverall: {'PASSED' if summary['all_passed'] else 'FAILED'}")


def main() -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = generate_dataset()
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"Wrote {OUTPUT_PATH}")

    loaded = pd.read_csv(OUTPUT_PATH)
    summary = validate_dataset(loaded)
    print_validation(summary)
    if not summary["all_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
