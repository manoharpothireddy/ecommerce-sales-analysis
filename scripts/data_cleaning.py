# -*- coding: utf-8 -*-
"""
data_cleaning.py
================
Data Cleaning & Feature Engineering Pipeline for E-Commerce Dataset.

Steps:
  1. Load raw CSVs from data/raw/
  2. Data quality report for each table
  3. Clean customers  -> add tenure_days
  4. Clean products   -> add profit_margin
  5. Clean orders     -> add time-based features
  6. Clean order_items -> recalculate / validate total_price
  7. RFM analysis     -> data/processed/rfm_scores.csv
  8. Save cleaned tables to data/processed/
  9. Print final summary

Usage:
    python scripts/data_cleaning.py

Dependencies:
    pandas, numpy
"""

import sys
import io
from pathlib import Path

import numpy  as np
import pandas as pd

# ---------------------------------------------------------------------------
# Force UTF-8 output on Windows consoles
# ---------------------------------------------------------------------------
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR   = Path(__file__).resolve().parent.parent
RAW_DIR    = BASE_DIR / "data" / "raw"
PROC_DIR   = BASE_DIR / "data" / "processed"
PROC_DIR.mkdir(parents=True, exist_ok=True)

REFERENCE_DATE = pd.Timestamp("2024-01-01")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
SEP  = "=" * 62
SEP2 = "-" * 62

def _section(title: str) -> None:
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)


def _subsection(title: str) -> None:
    print(f"\n  {SEP2}")
    print(f"  {title}")
    print(f"  {SEP2}")


def quality_report(df: pd.DataFrame, name: str) -> None:
    """Print a concise data-quality report for a DataFrame."""
    _subsection(f"Quality Report: {name}")

    # Shape
    print(f"\n  Shape          : {df.shape[0]:,} rows x {df.shape[1]} columns")

    # Dtypes
    print("\n  Column dtypes:")
    for col, dtype in df.dtypes.items():
        print(f"    {col:<25} {str(dtype)}")

    # Missing values
    missing = df.isnull().sum()
    missing = missing[missing > 0]
    if missing.empty:
        print("\n  Missing values : none")
    else:
        print("\n  Missing values:")
        for col, cnt in missing.items():
            pct = cnt / len(df) * 100
            print(f"    {col:<25} {cnt:>6,}  ({pct:.1f}%)")

    # Duplicates
    dups = df.duplicated().sum()
    print(f"\n  Duplicate rows : {dups:,}")


# ===========================================================================
# 1. LOAD RAW DATA
# ===========================================================================
def load_raw() -> tuple[pd.DataFrame, pd.DataFrame,
                         pd.DataFrame, pd.DataFrame]:
    _section("STEP 1 / 9 : Loading Raw Data")
    customers   = pd.read_csv(RAW_DIR / "customers.csv")
    products    = pd.read_csv(RAW_DIR / "products.csv")
    orders      = pd.read_csv(RAW_DIR / "orders.csv")
    order_items = pd.read_csv(RAW_DIR / "order_items.csv")
    print(f"  [OK] customers.csv   -> {len(customers):,} rows")
    print(f"  [OK] products.csv    -> {len(products):,} rows")
    print(f"  [OK] orders.csv      -> {len(orders):,} rows")
    print(f"  [OK] order_items.csv -> {len(order_items):,} rows")
    return customers, products, orders, order_items


# ===========================================================================
# 2. DATA QUALITY REPORTS
# ===========================================================================
def run_quality_checks(customers, products, orders, order_items) -> None:
    _section("STEP 2 / 9 : Data Quality Checks")
    quality_report(customers,   "customers")
    quality_report(products,    "products")
    quality_report(orders,      "orders")
    quality_report(order_items, "order_items")


# ===========================================================================
# 3. CLEAN CUSTOMERS
# ===========================================================================
def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    _section("STEP 3 / 9 : Cleaning Customers")
    before = len(df)

    # Strip whitespace from string columns
    str_cols = ["name", "email", "city", "state", "country",
                "customer_segment", "gender"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Lowercase emails
    df["email"] = df["email"].str.lower()

    # Parse registration_date
    df["registration_date"] = pd.to_datetime(
        df["registration_date"], errors="coerce"
    )
    bad_dates = df["registration_date"].isna().sum()
    if bad_dates:
        print(f"  [WARN] {bad_dates} unparseable registration_date rows dropped")
        df = df.dropna(subset=["registration_date"])

    # Tenure in days
    df["tenure_days"] = (REFERENCE_DATE - df["registration_date"]).dt.days

    # Remove duplicate customer_ids (keep first)
    dups = df.duplicated(subset=["customer_id"]).sum()
    df   = df.drop_duplicates(subset=["customer_id"], keep="first")

    after = len(df)
    print(f"  Rows before   : {before:,}")
    print(f"  Duplicate IDs removed : {dups}")
    print(f"  Rows after    : {after:,}")
    print(f"  New columns   : tenure_days")
    print(f"  tenure_days   -> min={df['tenure_days'].min()}, "
          f"max={df['tenure_days'].max()}, "
          f"mean={df['tenure_days'].mean():.0f}")
    return df


# ===========================================================================
# 4. CLEAN PRODUCTS
# ===========================================================================
def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    _section("STEP 4 / 9 : Cleaning Products")
    before = len(df)

    # Coerce numeric columns
    df["price"]      = pd.to_numeric(df["price"],      errors="coerce")
    df["cost_price"] = pd.to_numeric(df["cost_price"], errors="coerce")

    # Strip whitespace from string columns
    for col in ["product_name", "category", "sub_category", "brand"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()

    # Profit margin
    df["profit_margin"] = (
        (df["price"] - df["cost_price"]) / df["price"] * 100
    ).round(2)

    # Remove duplicate product_ids
    dups = df.duplicated(subset=["product_id"]).sum()
    df   = df.drop_duplicates(subset=["product_id"], keep="first")

    after = len(df)
    print(f"  Rows before   : {before:,}")
    print(f"  Duplicate IDs removed : {dups}")
    print(f"  Rows after    : {after:,}")
    print(f"  New columns   : profit_margin")
    print(f"  profit_margin -> min={df['profit_margin'].min():.1f}%, "
          f"max={df['profit_margin'].max():.1f}%, "
          f"mean={df['profit_margin'].mean():.1f}%")
    return df


# ===========================================================================
# 5. CLEAN ORDERS
# ===========================================================================
def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    _section("STEP 5 / 9 : Cleaning Orders")
    before = len(df)

    # Parse order_date
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    bad_dates = df["order_date"].isna().sum()
    if bad_dates:
        print(f"  [WARN] {bad_dates} unparseable order_date rows dropped")
        df = df.dropna(subset=["order_date"])

    # Time-based feature engineering
    df["order_year"]        = df["order_date"].dt.year
    df["order_month"]       = df["order_date"].dt.month
    df["order_quarter"]     = "Q" + df["order_date"].dt.quarter.astype(str)
    df["order_weekday"]     = df["order_date"].dt.day_name()
    df["order_week_number"] = df["order_date"].dt.isocalendar().week.astype(int)

    # Remove duplicate order_ids
    dups = df.duplicated(subset=["order_id"]).sum()
    df   = df.drop_duplicates(subset=["order_id"], keep="first")

    after = len(df)
    new_cols = ["order_year", "order_month", "order_quarter",
                "order_weekday", "order_week_number"]
    print(f"  Rows before   : {before:,}")
    print(f"  Duplicate IDs removed : {dups}")
    print(f"  Rows after    : {after:,}")
    print(f"  New columns   : {', '.join(new_cols)}")

    # Quick distribution
    print("\n  Order status distribution:")
    for status, cnt in df["status"].value_counts().items():
        print(f"    {status:<12} : {cnt:,} ({cnt/len(df)*100:.1f}%)")

    print("\n  Orders by year:")
    for yr, cnt in df["order_year"].value_counts().sort_index().items():
        print(f"    {yr} : {cnt:,}")

    return df


# ===========================================================================
# 6. CLEAN ORDER ITEMS
# ===========================================================================
def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    _section("STEP 6 / 9 : Cleaning Order Items")
    before = len(df)

    # Coerce numerics
    for col in ["quantity", "unit_price", "discount_percent", "total_price"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # Drop rows with invalid quantity or price
    invalid_mask = (df["quantity"] <= 0) | (df["unit_price"] <= 0)
    invalid_cnt  = invalid_mask.sum()
    if invalid_cnt:
        print(f"  [INFO] Dropping {invalid_cnt} rows with qty<=0 or price<=0")
        df = df[~invalid_mask].copy()

    # Recalculate total_price for accuracy
    df["total_price"] = (
        df["quantity"] * df["unit_price"] * (1 - df["discount_percent"] / 100)
    ).round(2)

    # Drop any NaN total_price after recalc
    null_total = df["total_price"].isna().sum()
    if null_total:
        print(f"  [WARN] Dropping {null_total} rows with NaN total_price")
        df = df.dropna(subset=["total_price"])

    after = len(df)
    print(f"  Rows before   : {before:,}")
    print(f"  Rows removed  : {before - after}")
    print(f"  Rows after    : {after:,}")
    print(f"  total_price   -> min=Rs.{df['total_price'].min():,.2f}, "
          f"max=Rs.{df['total_price'].max():,.2f}, "
          f"mean=Rs.{df['total_price'].mean():,.2f}")
    print(f"  Total revenue : Rs.{df['total_price'].sum():,.2f}")
    return df


# ===========================================================================
# 7. RFM ANALYSIS
# ===========================================================================
def compute_rfm(orders: pd.DataFrame,
                order_items: pd.DataFrame) -> pd.DataFrame:
    _section("STEP 7 / 9 : RFM Analysis")

    # Only Delivered orders count toward spend
    delivered_orders = orders[orders["status"] == "Delivered"][
        ["order_id", "customer_id", "order_date"]
    ].copy()

    # Merge order_items onto delivered orders
    merged = delivered_orders.merge(
        order_items[["order_id", "total_price"]],
        on="order_id",
        how="left"
    )

    # Aggregate RFM per customer
    rfm = merged.groupby("customer_id").agg(
        last_order_date=("order_date", "max"),
        frequency=("order_id",       "nunique"),
        monetary=("total_price",      "sum"),
    ).reset_index()

    rfm["recency"] = (
        REFERENCE_DATE - rfm["last_order_date"]
    ).dt.days

    # ── Score 1-4 using quartile-based binning ──────────────────────────
    # Recency: lower is better -> reverse rank (4 = most recent)
    rfm["r_score"] = pd.qcut(
        rfm["recency"],
        q=4,
        labels=[4, 3, 2, 1],   # reversed
        duplicates="drop"
    ).astype(int)

    rfm["f_score"] = pd.qcut(
        rfm["frequency"].rank(method="first"),
        q=4,
        labels=[1, 2, 3, 4],
        duplicates="drop"
    ).astype(int)

    rfm["m_score"] = pd.qcut(
        rfm["monetary"].rank(method="first"),
        q=4,
        labels=[1, 2, 3, 4],
        duplicates="drop"
    ).astype(int)

    rfm["rfm_score"] = (
        rfm["r_score"].astype(str)
        + rfm["f_score"].astype(str)
        + rfm["m_score"].astype(str)
    )

    # ── Segment assignment ──────────────────────────────────────────────
    def assign_segment(row: pd.Series) -> str:
        r, f, m = row["r_score"], row["f_score"], row["m_score"]
        if r == 4 and f == 4 and m == 4:
            return "Champions"
        elif f >= 3:
            return "Loyal Customers"
        elif r <= 2 and f >= 2:
            return "At Risk"
        elif r == 1 and f == 1:
            return "Lost"
        else:
            return "Others"

    rfm["rfm_segment"] = rfm.apply(assign_segment, axis=1)

    # Round monetary for readability
    rfm["monetary"] = rfm["monetary"].round(2)

    # Save
    out_cols = [
        "customer_id", "last_order_date", "recency",
        "frequency", "monetary",
        "r_score", "f_score", "m_score",
        "rfm_score", "rfm_segment"
    ]
    rfm[out_cols].to_csv(PROC_DIR / "rfm_scores.csv", index=False)
    print(f"  RFM table     : {len(rfm):,} customers scored")

    print("\n  RFM Segment Distribution:")
    seg_counts = rfm["rfm_segment"].value_counts()
    for seg, cnt in seg_counts.items():
        bar = "#" * int(cnt / len(rfm) * 40)
        print(f"    {seg:<20} : {cnt:>5,}  {bar}")

    print("\n  RFM Averages per Segment:")
    seg_stats = rfm.groupby("rfm_segment")[
        ["recency", "frequency", "monetary"]
    ].mean().round(1)
    print(seg_stats.to_string(
        formatters={"monetary": "Rs.{:,.1f}".format}
    ))

    print(f"\n  [OK] rfm_scores.csv saved -> data/processed/")
    return rfm


# ===========================================================================
# 8. SAVE CLEANED TABLES
# ===========================================================================
def save_cleaned(customers, products, orders, order_items) -> None:
    _section("STEP 8 / 9 : Saving Cleaned Tables")
    customers.to_csv(  PROC_DIR / "customers_clean.csv",   index=False)
    products.to_csv(   PROC_DIR / "products_clean.csv",    index=False)
    orders.to_csv(     PROC_DIR / "orders_clean.csv",      index=False)
    order_items.to_csv(PROC_DIR / "order_items_clean.csv", index=False)
    print("  [OK] customers_clean.csv")
    print("  [OK] products_clean.csv")
    print("  [OK] orders_clean.csv")
    print("  [OK] order_items_clean.csv")


# ===========================================================================
# 9. FINAL SUMMARY
# ===========================================================================
def print_summary(
    raw_counts:    dict,
    clean_dfs:     dict,
    new_features:  dict,
    rfm:           pd.DataFrame,
) -> None:
    _section("STEP 9 / 9 : Final Summary")

    print("\n  Row counts before vs. after cleaning:")
    print(f"  {'Table':<20} {'Before':>8}  {'After':>8}  {'Dropped':>8}")
    print(f"  {'-'*20}  {'-'*8}  {'-'*8}  {'-'*8}")
    for name, after_df in clean_dfs.items():
        before = raw_counts[name]
        after  = len(after_df)
        dropped = before - after
        print(f"  {name:<20} {before:>8,}  {after:>8,}  {dropped:>8,}")

    print("\n  New feature columns added:")
    for table, cols in new_features.items():
        print(f"    {table:<20}: {', '.join(cols)}")

    print("\n  RFM Segment Distribution:")
    seg_counts = rfm["rfm_segment"].value_counts()
    for seg, cnt in seg_counts.items():
        pct = cnt / len(rfm) * 100
        print(f"    {seg:<20} : {cnt:>5,}  ({pct:.1f}%)")

    print(f"\n{SEP}")
    print("  Cleaning complete. Files saved to data/processed/")
    print(SEP)
    print(f"\n  Output files:")
    for fname in [
        "customers_clean.csv", "products_clean.csv",
        "orders_clean.csv",    "order_items_clean.csv",
        "rfm_scores.csv",
    ]:
        fpath = PROC_DIR / fname
        size  = fpath.stat().st_size / 1024
        print(f"    {fname:<30}  ({size:.1f} KB)")
    print()


# ===========================================================================
# MAIN
# ===========================================================================
def main() -> None:
    print(f"\n{SEP}")
    print("  E-Commerce Data Cleaning & Feature Engineering")
    print(f"{SEP}")

    # 1. Load
    customers_raw, products_raw, orders_raw, order_items_raw = load_raw()

    # Record original row counts
    raw_counts = {
        "customers":   len(customers_raw),
        "products":    len(products_raw),
        "orders":      len(orders_raw),
        "order_items": len(order_items_raw),
    }

    # 2. Quality reports
    run_quality_checks(
        customers_raw.copy(), products_raw.copy(),
        orders_raw.copy(),    order_items_raw.copy()
    )

    # 3-6. Clean
    customers_clean   = clean_customers(customers_raw.copy())
    products_clean    = clean_products(products_raw.copy())
    orders_clean      = clean_orders(orders_raw.copy())
    order_items_clean = clean_order_items(order_items_raw.copy())

    # 7. RFM
    rfm = compute_rfm(orders_clean, order_items_clean)

    # 8. Save
    save_cleaned(
        customers_clean, products_clean,
        orders_clean,    order_items_clean
    )

    # 9. Summary
    clean_dfs = {
        "customers":   customers_clean,
        "products":    products_clean,
        "orders":      orders_clean,
        "order_items": order_items_clean,
    }
    new_features = {
        "customers":   ["tenure_days"],
        "products":    ["profit_margin"],
        "orders":      ["order_year", "order_month", "order_quarter",
                        "order_weekday", "order_week_number"],
        "order_items": ["total_price (recalculated)"],
    }
    print_summary(raw_counts, clean_dfs, new_features, rfm)


if __name__ == "__main__":
    main()
