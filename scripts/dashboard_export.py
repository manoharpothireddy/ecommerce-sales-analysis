# -*- coding: utf-8 -*-
"""
dashboard_export.py
===================
Prepares all dashboard-ready CSV exports for Tableau and Power BI.

Exports created in data/processed/dashboard_exports/:
  1. kpi_summary.csv          — single-row KPI snapshot
  2. monthly_revenue.csv      — revenue by year-month
  3. category_performance.csv — per-category metrics
  4. customer_segments.csv    — customers + RFM scores merged
  5. product_performance.csv  — per-product revenue & discount stats
  6. daily_orders.csv         — daily order counts & revenue (gap-filled)

Usage:
    python scripts/dashboard_export.py

Dependencies:
    pandas, numpy, sqlalchemy
"""

import sys
import io
from pathlib import Path

import numpy  as np
import pandas as pd
from sqlalchemy import create_engine, text

# ── UTF-8 stdout for Windows ───────────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).resolve().parent.parent
PROC_DIR   = BASE_DIR / "data" / "processed"
RAW_DIR    = BASE_DIR / "data" / "raw"
EXPORT_DIR = PROC_DIR / "dashboard_exports"
DASH_DIR   = BASE_DIR / "dashboards"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)
DASH_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH    = RAW_DIR / "ecommerce.db"
MONTH_NAMES = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",
               7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}

SEP  = "=" * 65
SEP2 = "-" * 65

def _section(title: str) -> None:
    print(f"\n{SEP}\n  {title}\n{SEP}")


# ===========================================================================
# LOAD DATA
# ===========================================================================
def load_all():
    _section("Loading Data")
    customers   = pd.read_csv(PROC_DIR / "customers_clean.csv",
                               parse_dates=["registration_date"])
    products    = pd.read_csv(PROC_DIR / "products_clean.csv")
    orders      = pd.read_csv(PROC_DIR / "orders_clean.csv",
                               parse_dates=["order_date"])
    order_items = pd.read_csv(PROC_DIR / "order_items_clean.csv")
    rfm         = pd.read_csv(PROC_DIR / "rfm_scores.csv")

    print(f"  customers   : {len(customers):,} rows")
    print(f"  products    : {len(products):,} rows")
    print(f"  orders      : {len(orders):,} rows")
    print(f"  order_items : {len(order_items):,} rows")
    print(f"  rfm         : {len(rfm):,} rows")
    return customers, products, orders, order_items, rfm


# ===========================================================================
# EXPORT 1 — kpi_summary.csv
# ===========================================================================
def export_kpi_summary(orders, order_items, customers, products) -> pd.DataFrame:
    # Join order_items with orders to get status
    oi_ord = order_items.merge(
        orders[["order_id", "status", "payment_method", "customer_id"]],
        on="order_id", how="left"
    )
    oi_ord_prod = oi_ord.merge(
        products[["product_id", "category"]], on="product_id", how="left"
    )

    delivered = oi_ord[oi_ord["status"] == "Delivered"]

    total_revenue       = round(delivered["total_price"].sum(), 2)
    total_orders        = orders["order_id"].nunique()
    delivered_orders    = (orders["status"] == "Delivered").sum()
    cancelled_orders    = (orders["status"] == "Cancelled").sum()
    returned_orders     = (orders["status"] == "Returned").sum()
    total_customers     = customers["customer_id"].nunique()
    avg_order_value     = round(total_revenue / delivered_orders, 2) \
                          if delivered_orders else 0

    # Avg items per order (delivered)
    del_items = delivered.groupby("order_id")["quantity"].sum()
    avg_items_per_order = round(del_items.mean(), 2)

    # Top category by revenue
    cat_rev = (
        oi_ord_prod[oi_ord_prod["status"] == "Delivered"]
        .groupby("category")["total_price"].sum()
    )
    top_category = cat_rev.idxmax() if not cat_rev.empty else "N/A"

    # Top payment method
    top_payment = orders["payment_method"].value_counts().idxmax()

    kpi = pd.DataFrame([{
        "total_revenue":       total_revenue,
        "total_orders":        total_orders,
        "delivered_orders":    int(delivered_orders),
        "cancelled_orders":    int(cancelled_orders),
        "returned_orders":     int(returned_orders),
        "total_customers":     total_customers,
        "avg_order_value":     avg_order_value,
        "avg_items_per_order": avg_items_per_order,
        "top_category":        top_category,
        "top_payment_method":  top_payment,
    }])

    out = EXPORT_DIR / "kpi_summary.csv"
    kpi.to_csv(out, index=False)
    print(f"  [OK] kpi_summary.csv")
    print(f"       total_revenue        = Rs.{total_revenue:,.2f}")
    print(f"       delivered_orders     = {delivered_orders:,}")
    print(f"       avg_order_value      = Rs.{avg_order_value:,.2f}")
    print(f"       top_category         = {top_category}")
    print(f"       top_payment_method   = {top_payment}")
    return kpi


# ===========================================================================
# EXPORT 2 — monthly_revenue.csv
# ===========================================================================
def export_monthly_revenue(orders, order_items) -> pd.DataFrame:
    oi_ord = order_items.merge(
        orders[["order_id", "status", "order_date",
                "order_year", "order_month"]],
        on="order_id", how="left"
    )
    delivered = oi_ord[oi_ord["status"] == "Delivered"].copy()
    delivered["order_year"]  = pd.to_numeric(delivered["order_year"],  errors="coerce")
    delivered["order_month"] = pd.to_numeric(delivered["order_month"], errors="coerce")

    monthly = (
        delivered.groupby(["order_year", "order_month"])
        .agg(
            order_count   = ("order_id",    "nunique"),
            total_revenue = ("total_price", "sum"),
        )
        .reset_index()
    )
    monthly["avg_order_value"] = (
        monthly["total_revenue"] / monthly["order_count"]
    ).round(2)
    monthly["total_revenue"]   = monthly["total_revenue"].round(2)
    monthly["month_name"]      = monthly["order_month"].map(MONTH_NAMES)
    monthly = monthly.rename(columns={
        "order_year": "year", "order_month": "month"
    })
    monthly = monthly[
        ["year", "month", "month_name", "order_count",
         "total_revenue", "avg_order_value"]
    ].sort_values(["year", "month"]).reset_index(drop=True)

    out = EXPORT_DIR / "monthly_revenue.csv"
    monthly.to_csv(out, index=False)
    print(f"  [OK] monthly_revenue.csv        ({len(monthly)} rows)")
    return monthly


# ===========================================================================
# EXPORT 3 — category_performance.csv
# ===========================================================================
def export_category_performance(orders, order_items, products) -> pd.DataFrame:
    oi_full = (
        order_items
        .merge(orders[["order_id", "status"]], on="order_id", how="left")
        .merge(products[["product_id", "category", "price"]], on="product_id", how="left")
    )

    # Total per category (all statuses)
    total = oi_full.groupby("category").agg(
        total_orders    = ("order_id",    "nunique"),
        total_units_sold= ("quantity",    "sum"),
        avg_price       = ("unit_price",  "mean"),
    ).reset_index()

    # Delivered
    delivered = (
        oi_full[oi_full["status"] == "Delivered"]
        .groupby("category")
        .agg(
            delivered_orders = ("order_id",    "nunique"),
            total_revenue    = ("total_price", "sum"),
        )
        .reset_index()
    )

    # Returned
    returned = (
        oi_full[oi_full["status"] == "Returned"]
        .groupby("category")["order_id"]
        .nunique()
        .reset_index()
        .rename(columns={"order_id": "returned_orders"})
    )

    cat_perf = (
        total
        .merge(delivered, on="category", how="left")
        .merge(returned,  on="category", how="left")
    )
    cat_perf["returned_orders"] = cat_perf["returned_orders"].fillna(0).astype(int)
    cat_perf["return_rate_pct"] = (
        cat_perf["returned_orders"] / cat_perf["total_orders"] * 100
    ).round(2)
    cat_perf["total_revenue"] = cat_perf["total_revenue"].round(2)
    cat_perf["avg_price"]     = cat_perf["avg_price"].round(2)
    cat_perf = cat_perf[[
        "category", "total_orders", "delivered_orders", "returned_orders",
        "return_rate_pct", "total_revenue", "avg_price", "total_units_sold"
    ]].sort_values("total_revenue", ascending=False).reset_index(drop=True)

    out = EXPORT_DIR / "category_performance.csv"
    cat_perf.to_csv(out, index=False)
    print(f"  [OK] category_performance.csv   ({len(cat_perf)} rows)")
    return cat_perf


# ===========================================================================
# EXPORT 4 — customer_segments.csv
# ===========================================================================
def export_customer_segments(customers, rfm) -> pd.DataFrame:
    cust_rfm = customers[[
        "customer_id", "name", "city", "state",
        "customer_segment", "tenure_days"
    ]].merge(
        rfm[[
            "customer_id", "rfm_segment",
            "recency", "frequency", "monetary"
        ]],
        on="customer_id", how="left"
    )
    cust_rfm = cust_rfm.rename(columns={
        "recency":   "recency_days",
        "frequency": "frequency",
        "monetary":  "monetary",
    })
    cust_rfm["monetary"] = cust_rfm["monetary"].round(2)
    cust_rfm = cust_rfm[[
        "customer_id", "name", "city", "state",
        "customer_segment", "rfm_segment",
        "recency_days", "frequency", "monetary", "tenure_days"
    ]].sort_values("monetary", ascending=False).reset_index(drop=True)

    out = EXPORT_DIR / "customer_segments.csv"
    cust_rfm.to_csv(out, index=False)
    print(f"  [OK] customer_segments.csv      ({len(cust_rfm)} rows)")
    return cust_rfm


# ===========================================================================
# EXPORT 5 — product_performance.csv
# ===========================================================================
def export_product_performance(orders, order_items, products) -> pd.DataFrame:
    oi_del = (
        order_items
        .merge(orders[["order_id", "status"]], on="order_id", how="left")
    )
    delivered = oi_del[oi_del["status"] == "Delivered"]

    prod_perf = delivered.groupby("product_id").agg(
        total_units_sold = ("quantity",         "sum"),
        total_revenue    = ("total_price",      "sum"),
        order_count      = ("order_id",         "nunique"),
        avg_discount_pct = ("discount_percent", "mean"),
    ).reset_index()

    prod_perf = prod_perf.merge(
        products[[
            "product_id", "product_name", "category",
            "brand", "price", "profit_margin"
        ]],
        on="product_id", how="left"
    )
    prod_perf["total_revenue"]    = prod_perf["total_revenue"].round(2)
    prod_perf["avg_discount_pct"] = prod_perf["avg_discount_pct"].round(2)
    prod_perf = prod_perf[[
        "product_id", "product_name", "category", "brand",
        "price", "profit_margin",
        "total_units_sold", "total_revenue",
        "order_count", "avg_discount_pct"
    ]].sort_values("total_revenue", ascending=False).reset_index(drop=True)

    out = EXPORT_DIR / "product_performance.csv"
    prod_perf.to_csv(out, index=False)
    print(f"  [OK] product_performance.csv    ({len(prod_perf)} rows)")
    return prod_perf


# ===========================================================================
# EXPORT 6 — daily_orders.csv
# ===========================================================================
def export_daily_orders(orders, order_items) -> pd.DataFrame:
    oi_ord = order_items.merge(
        orders[["order_id", "order_date", "status"]],
        on="order_id", how="left"
    )
    delivered = oi_ord[oi_ord["status"] == "Delivered"].copy()
    delivered["order_date"] = pd.to_datetime(delivered["order_date"])

    daily = delivered.groupby("order_date").agg(
        order_count   = ("order_id",    "nunique"),
        total_revenue = ("total_price", "sum"),
    ).reset_index()

    # Fill every calendar day in the range with zeros if no orders
    full_range = pd.date_range(
        start=daily["order_date"].min(),
        end=daily["order_date"].max(),
        freq="D"
    )
    daily = (
        daily.set_index("order_date")
        .reindex(full_range, fill_value=0)
        .reset_index()
        .rename(columns={"index": "order_date"})
    )
    daily["order_date"]     = daily["order_date"].dt.strftime("%Y-%m-%d")
    daily["total_revenue"]  = daily["total_revenue"].round(2)
    daily["avg_order_value"] = np.where(
        daily["order_count"] > 0,
        (daily["total_revenue"] / daily["order_count"]).round(2),
        0.0
    )
    daily = daily[["order_date", "order_count",
                   "total_revenue", "avg_order_value"]]

    out = EXPORT_DIR / "daily_orders.csv"
    daily.to_csv(out, index=False)
    print(f"  [OK] daily_orders.csv           ({len(daily)} rows, "
          f"date range: {daily['order_date'].min()} to {daily['order_date'].max()})")
    return daily


# ===========================================================================
# DASHBOARD GUIDE
# ===========================================================================
DASHBOARD_GUIDE_MD = """\
# Dashboard Guide — E-Commerce Sales & Customer Behaviour

> Auto-generated by `scripts/dashboard_export.py`

All export files are located in `data/processed/dashboard_exports/`.

---

## Tableau Dashboard Plan

### Dashboard 1: Executive KPI Overview

| Visual | Source File | Fields |
|--------|-------------|--------|
| KPI Card — Total Revenue | `kpi_summary.csv` | `total_revenue` |
| KPI Card — Total Orders | `kpi_summary.csv` | `total_orders` |
| KPI Card — Avg Order Value | `kpi_summary.csv` | `avg_order_value` |
| KPI Card — Total Customers | `kpi_summary.csv` | `total_customers` |
| Monthly Revenue Trend (Line) | `monthly_revenue.csv` | `year_month`, `total_revenue` |
| Revenue by Category (Bar) | `category_performance.csv` | `category`, `total_revenue` |
| Orders by Payment Method (Pie) | orders data | `payment_method`, count |

**Filters**: Year, Quarter, Customer Segment

---

### Dashboard 2: Customer Intelligence

| Visual | Source File | Fields |
|--------|-------------|--------|
| RFM Segment Donut | `customer_segments.csv` | `rfm_segment`, count |
| Customer Segment Bar | `customer_segments.csv` | `customer_segment`, count |
| Top 10 Customers Table | `customer_segments.csv` | `name`, `monetary`, `frequency` |
| Recency vs Monetary Scatter | `customer_segments.csv` | `recency_days`, `monetary`, `rfm_segment` |
| State-wise Customer Map | `customer_segments.csv` | `state`, count |

**Filters**: RFM Segment, Customer Segment, State

---

### Dashboard 3: Product Performance

| Visual | Source File | Fields |
|--------|-------------|--------|
| Top 10 Products by Revenue (H-Bar) | `product_performance.csv` | `product_name`, `total_revenue` |
| Category Return Rate (Bar) | `category_performance.csv` | `category`, `return_rate_pct` |
| Price vs Profit Margin Scatter | `product_performance.csv` | `price`, `profit_margin`, `category` |
| Units Sold by Category (Bar) | `product_performance.csv` | `category`, `total_units_sold` |
| Full Product Table | `product_performance.csv` | all fields |

**Filters**: Category, Brand, Price Range

---

## Power BI Dashboard Plan

### Page 1: Sales Overview

| Visual Type | Source | Notes |
|-------------|--------|-------|
| Card — Total Revenue | `kpi_summary.csv` | Format as currency |
| Card — Total Orders | `kpi_summary.csv` | |
| Card — AOV | `kpi_summary.csv` | Avg Order Value |
| Card — Total Customers | `kpi_summary.csv` | |
| Line Chart — Monthly Revenue | `monthly_revenue.csv` | X = month_name, Y = total_revenue, Legend = year |
| Bar Chart — Revenue by Category | `category_performance.csv` | Sort descending |
| Slicer | `monthly_revenue.csv` | Fields: year, quarter, payment method |

---

### Page 2: Customer Analysis

| Visual Type | Source | Notes |
|-------------|--------|-------|
| Donut Chart — RFM Segments | `customer_segments.csv` | rfm_segment |
| Table — Top Customers | `customer_segments.csv` | Sort by monetary desc |
| Bar Chart — Segment Distribution | `customer_segments.csv` | customer_segment |
| Map Visual — Orders by State | `customer_segments.csv` | state field → India map |
| Scatter — Recency vs Spend | `customer_segments.csv` | Color by rfm_segment |

---

### Page 3: Product Analysis

| Visual Type | Source | Notes |
|-------------|--------|-------|
| Bar Chart — Top Products | `product_performance.csv` | Top 10, sort by total_revenue |
| Scatter — Price vs Margin | `product_performance.csv` | Color by category |
| Table — Product Detail | `product_performance.csv` | All columns |
| Bar Chart — Return Rate | `category_performance.csv` | return_rate_pct |
| Bar Chart — Units Sold | `category_performance.csv` | total_units_sold |

---

## Field Mapping Reference

| Export File | Primary Use | Key Fields |
|-------------|-------------|------------|
| `kpi_summary.csv` | KPI cards in both tools | All metric columns |
| `monthly_revenue.csv` | Trend charts, YoY comparison | year, month, total_revenue |
| `category_performance.csv` | Category drilldown | category, total_revenue, return_rate_pct |
| `customer_segments.csv` | RFM dashboards, maps | rfm_segment, monetary, state |
| `product_performance.csv` | Product leaderboards | product_name, total_revenue, profit_margin |
| `daily_orders.csv` | Time series, forecasting | order_date, order_count, total_revenue |

---

## Data Refresh Instructions

Re-run the full pipeline in this order:

```bash
# Step 1: Generate synthetic data
python scripts/generate_data.py

# Step 2: Clean all tables
python scripts/data_cleaning.py

# Step 3: EDA plots
python scripts/eda_analysis.py

# Step 4: Dashboard exports
python scripts/dashboard_export.py
```

> All files use `data/processed/dashboard_exports/` as the output directory.
> Connect Tableau / Power BI to this folder using a **Folder connector** for easy refresh.

---

*Generated by the E-Commerce Sales & Customer Behaviour Analysis project.*
"""


def write_dashboard_guide() -> None:
    path = DASH_DIR / "DASHBOARD_GUIDE.md"
    path.write_text(DASHBOARD_GUIDE_MD, encoding="utf-8")
    size = path.stat().st_size / 1024
    print(f"  [OK] DASHBOARD_GUIDE.md -> dashboards/  ({size:.1f} KB)")


# ===========================================================================
# SUMMARY TABLE
# ===========================================================================
def print_export_summary() -> None:
    _section("Export Summary")
    files = [
        "kpi_summary.csv",
        "monthly_revenue.csv",
        "category_performance.csv",
        "customer_segments.csv",
        "product_performance.csv",
        "daily_orders.csv",
    ]
    print(f"\n  {'#':<3} {'File':<35} {'Rows':>6} {'Cols':>6} {'Size':>8}")
    print(f"  {'-'*3}  {'-'*34}  {'-'*6}  {'-'*6}  {'-'*8}")
    for i, fname in enumerate(files, 1):
        fpath = EXPORT_DIR / fname
        if fpath.exists():
            df   = pd.read_csv(fpath)
            rows = len(df)
            cols = df.shape[1]
            size = fpath.stat().st_size / 1024
            print(f"  {i:<3}  {fname:<35} {rows:>6,} {cols:>6}  {size:>6.1f}KB")
        else:
            print(f"  {i:<3}  {fname:<35}  MISSING")


# ===========================================================================
# MAIN
# ===========================================================================
def main() -> None:
    print(f"\n{SEP}")
    print("  E-Commerce — Dashboard Export Pipeline")
    print(f"{SEP}")

    # Load
    customers, products, orders, order_items, rfm = load_all()

    # Exports
    _section("Creating Export Files")
    export_kpi_summary(orders, order_items, customers, products)
    export_monthly_revenue(orders, order_items)
    export_category_performance(orders, order_items, products)
    export_customer_segments(customers, rfm)
    export_product_performance(orders, order_items, products)
    export_daily_orders(orders, order_items)

    # Dashboard guide
    _section("Writing Dashboard Guide")
    write_dashboard_guide()

    # Summary
    print_export_summary()

    print(f"\n{SEP}")
    print("  Dashboard exports complete. "
          "Guide saved to dashboards/DASHBOARD_GUIDE.md")
    print(SEP)
    print(f"\n  All exports -> {EXPORT_DIR}\n")


if __name__ == "__main__":
    main()
