# -*- coding: utf-8 -*-
"""
eda_analysis.py
===============
Exploratory Data Analysis for E-Commerce Sales & Customer Behaviour.

Produces 8 publication-quality plots saved to outputs/plots/ and runs
4 SQL queries against data/raw/ecommerce.db, printing results to the terminal.

Usage:
    python scripts/eda_analysis.py

Dependencies:
    pandas, numpy, matplotlib, seaborn, sqlalchemy
"""

import sys
import io
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                       # non-interactive backend (safe on all OSes)
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from sqlalchemy import create_engine, text

warnings.filterwarnings("ignore")

# ── Force UTF-8 output on Windows ─────────────────────────────────────────────
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8",
                                  errors="replace")

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
PROC_DIR  = BASE_DIR / "data" / "processed"
RAW_DIR   = BASE_DIR / "data" / "raw"
PLOTS_DIR = BASE_DIR / "outputs" / "plots"
PLOTS_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH   = RAW_DIR / "ecommerce.db"

# ── Global plot settings ───────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi":        150,
    "figure.facecolor":  "#FAFAFA",
    "axes.facecolor":    "#FAFAFA",
    "font.family":       "DejaVu Sans",
    "axes.titlesize":    14,
    "axes.titleweight":  "bold",
    "axes.labelsize":    11,
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "legend.fontsize":   9,
    "axes.spines.top":   False,
    "axes.spines.right": False,
})
try:
    plt.style.use("seaborn-v0_8-whitegrid")
except OSError:
    plt.style.use("seaborn-whitegrid")

RUPEE    = "\u20B9"          # ₹
SEP      = "=" * 65
SEP2     = "-" * 65

# ── Colour palettes ────────────────────────────────────────────────────────────
TEAL_GRAD  = sns.color_palette("YlGnBu", 10)[::-1]
CAT_COLORS = sns.color_palette("Set2", 8)
PIE_COLORS = sns.color_palette("pastel", 6)

SEGMENT_COLORS = {
    "Champions":       "#2ecc71",
    "Loyal Customers": "#3498db",
    "At Risk":         "#e67e22",
    "Lost":            "#e74c3c",
    "Others":          "#95a5a6",
}


# ===========================================================================
# HELPERS
# ===========================================================================
def _section(title: str) -> None:
    print(f"\n{SEP}\n  {title}\n{SEP}")


def _save(fig: plt.Figure, filename: str) -> None:
    path = PLOTS_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"  [OK] {filename}")


def _fmt_inr(val: float) -> str:
    """Format a number as Indian Rupees with commas."""
    return f"{RUPEE}{val:,.0f}"


# ===========================================================================
# 1. LOAD DATA
# ===========================================================================
def load_data():
    _section("Loading Cleaned Data")

    customers   = pd.read_csv(PROC_DIR / "customers_clean.csv",
                               parse_dates=["registration_date"])
    products    = pd.read_csv(PROC_DIR / "products_clean.csv")
    orders      = pd.read_csv(PROC_DIR / "orders_clean.csv",
                               parse_dates=["order_date"])
    order_items = pd.read_csv(PROC_DIR / "order_items_clean.csv")
    rfm         = pd.read_csv(PROC_DIR / "rfm_scores.csv")

    # Master dataframe: orders + order_items + products
    df_master = (
        order_items
        .merge(orders[["order_id", "customer_id", "order_date",
                        "status", "payment_method",
                        "order_year", "order_month", "order_quarter",
                        "order_weekday", "order_week_number",
                        "shipping_state"]],
               on="order_id", how="left")
        .merge(products[["product_id", "product_name", "category",
                          "sub_category", "brand", "profit_margin"]],
               on="product_id", how="left")
        .merge(customers[["customer_id", "customer_segment",
                           "gender", "state", "tenure_days"]],
               on="customer_id", how="left")
    )

    for col in ["order_year", "order_month", "order_week_number"]:
        df_master[col] = pd.to_numeric(df_master[col], errors="coerce")

    print(f"  customers   : {len(customers):,} rows")
    print(f"  products    : {len(products):,} rows")
    print(f"  orders      : {len(orders):,} rows")
    print(f"  order_items : {len(order_items):,} rows")
    print(f"  rfm         : {len(rfm):,} rows")
    print(f"  df_master   : {len(df_master):,} rows x {df_master.shape[1]} cols")

    return customers, products, orders, order_items, rfm, df_master


# ===========================================================================
# PLOT 1 — Top 10 Products by Revenue
# ===========================================================================
def plot_top_products(df_master: pd.DataFrame) -> None:
    delivered = df_master[df_master["status"] == "Delivered"]
    top10 = (
        delivered.groupby("product_name")["total_price"]
        .sum()
        .nlargest(10)
        .sort_values()          # ascending so longest bar is at top
    )

    fig, ax = plt.subplots(figsize=(11, 6))
    bars = ax.barh(
        top10.index, top10.values,
        color=TEAL_GRAD, edgecolor="white", height=0.65
    )

    # Value labels on bars
    for bar, val in zip(bars, top10.values):
        ax.text(
            bar.get_width() + top10.max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            _fmt_inr(val),
            va="center", ha="left", fontsize=8.5, color="#2c3e50"
        )

    ax.set_xlabel(f"Total Revenue ({RUPEE})")
    ax.set_title("Top 10 Products by Revenue", pad=14)
    ax.xaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{RUPEE}{x/1e6:.1f}M"))
    ax.set_xlim(0, top10.max() * 1.18)
    ax.tick_params(axis="y", labelsize=9)
    fig.tight_layout()
    _save(fig, "top_products_revenue.png")


# ===========================================================================
# PLOT 2 — Monthly Revenue Trend 2022 vs 2023
# ===========================================================================
def plot_monthly_revenue_trend(df_master: pd.DataFrame) -> None:
    delivered = df_master[
        (df_master["status"] == "Delivered") &
        (df_master["order_year"].isin([2022, 2023]))
    ].copy()

    monthly = (
        delivered.groupby(["order_year", "order_month"])["total_price"]
        .sum()
        .reset_index()
    )

    month_labels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    fig, ax = plt.subplots(figsize=(12, 5))

    palette = {"2022": "#3498db", "2023": "#e74c3c"}
    markers = {"2022": "o",       "2023": "s"}

    for yr in [2022, 2023]:
        grp = monthly[monthly["order_year"] == yr].sort_values("order_month")
        label = str(yr)
        ax.plot(
            grp["order_month"], grp["total_price"],
            color=palette[label], marker=markers[label],
            linewidth=2.2, markersize=7,
            label=label, zorder=3
        )
        ax.fill_between(
            grp["order_month"], grp["total_price"],
            alpha=0.08, color=palette[label]
        )

    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(month_labels)
    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{RUPEE}{x/1e6:.1f}M"))
    ax.set_xlabel("Month")
    ax.set_ylabel(f"Revenue ({RUPEE})")
    ax.set_title("Monthly Revenue Trend: 2022 vs 2023", pad=14)
    ax.legend(title="Year", framealpha=0.6)
    fig.tight_layout()
    _save(fig, "monthly_revenue_trend.png")


# ===========================================================================
# PLOT 3 — Revenue by Product Category
# ===========================================================================
def plot_revenue_by_category(df_master: pd.DataFrame) -> None:
    delivered = df_master[df_master["status"] == "Delivered"]
    cat_rev = (
        delivered.groupby("category")["total_price"]
        .sum()
        .sort_values(ascending=False)
    )

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(
        cat_rev.index, cat_rev.values,
        color=CAT_COLORS[:len(cat_rev)],
        edgecolor="white", width=0.6
    )

    for bar, val in zip(bars, cat_rev.values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + cat_rev.max() * 0.01,
            _fmt_inr(val),
            ha="center", va="bottom", fontsize=8.5, color="#2c3e50"
        )

    ax.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{RUPEE}{x/1e6:.1f}M"))
    ax.set_ylabel(f"Total Revenue ({RUPEE})")
    ax.set_title("Revenue by Product Category", pad=14)
    ax.set_ylim(0, cat_rev.max() * 1.15)
    fig.tight_layout()
    _save(fig, "revenue_by_category.png")


# ===========================================================================
# PLOT 4 — Orders by Payment Method (Pie)
# ===========================================================================
def plot_payment_method(orders: pd.DataFrame) -> None:
    pm = orders["payment_method"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 7))
    wedges, texts, autotexts = ax.pie(
        pm.values,
        labels=None,
        autopct=lambda p: f"{p:.1f}%\n({int(round(p * pm.sum() / 100)):,})",
        colors=PIE_COLORS[:len(pm)],
        startangle=140,
        pctdistance=0.72,
        wedgeprops=dict(linewidth=1.5, edgecolor="white"),
    )
    for at in autotexts:
        at.set_fontsize(8.5)
        at.set_color("#2c3e50")

    ax.legend(
        wedges, pm.index,
        title="Payment Method",
        loc="lower center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=3,
        framealpha=0.7,
        fontsize=9,
    )
    ax.set_title("Orders by Payment Method", pad=16, fontsize=14)
    fig.tight_layout()
    _save(fig, "orders_by_payment_method.png")


# ===========================================================================
# PLOT 5 — Customer Segment Distribution (Donut)
# ===========================================================================
def plot_customer_segment(customers: pd.DataFrame) -> None:
    seg = customers["customer_segment"].value_counts()

    fig, ax = plt.subplots(figsize=(8, 7))
    wedge_props = dict(linewidth=2, edgecolor="white")
    wedges, texts, autotexts = ax.pie(
        seg.values,
        labels=None,
        autopct=lambda p: f"{p:.1f}%",
        colors=sns.color_palette("Set3", len(seg)),
        startangle=90,
        pctdistance=0.75,
        wedgeprops=wedge_props,
    )
    # Donut hole
    centre_circle = plt.Circle((0, 0), 0.50, fc="#FAFAFA", linewidth=0)
    ax.add_artist(centre_circle)

    for at in autotexts:
        at.set_fontsize(10)
        at.set_fontweight("bold")
        at.set_color("#2c3e50")

    # Centre annotation
    total = seg.sum()
    ax.text(0, 0, f"{total:,}\nCustomers",
            ha="center", va="center",
            fontsize=12, fontweight="bold", color="#34495e")

    ax.legend(
        wedges,
        [f"{s}  ({c:,})" for s, c in zip(seg.index, seg.values)],
        title="Segment",
        loc="lower center",
        bbox_to_anchor=(0.5, -0.08),
        ncol=3,
        framealpha=0.7,
    )
    ax.set_title("Customer Segment Distribution", pad=16)
    fig.tight_layout()
    _save(fig, "customer_segment_distribution.png")


# ===========================================================================
# PLOT 6 — RFM Segment Distribution
# ===========================================================================
def plot_rfm_segments(rfm: pd.DataFrame) -> None:
    seg = rfm["rfm_segment"].value_counts().sort_values()
    colors = [SEGMENT_COLORS.get(s, "#95a5a6") for s in seg.index]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(seg.index, seg.values, color=colors,
                   edgecolor="white", height=0.55)

    for bar, val in zip(bars, seg.values):
        ax.text(
            bar.get_width() + seg.max() * 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{val:,} customers",
            va="center", ha="left", fontsize=9, color="#2c3e50"
        )

    ax.set_xlabel("Number of Customers")
    ax.set_title("RFM Customer Segments", pad=14)
    ax.set_xlim(0, seg.max() * 1.22)
    fig.tight_layout()
    _save(fig, "rfm_segment_distribution.png")


# ===========================================================================
# PLOT 7 — Weekly Order Volume Trend
# ===========================================================================
def plot_weekly_order_trend(orders: pd.DataFrame) -> None:
    ord_ts = orders.copy()
    ord_ts = ord_ts.set_index("order_date").sort_index()

    # Resample to weekly order counts
    weekly = ord_ts["order_id"].resample("W").count()
    rolling = weekly.rolling(window=4, min_periods=1).mean()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(weekly.index, weekly.values,
            color="#3498db", linewidth=1.2,
            alpha=0.55, label="Weekly Orders")
    ax.fill_between(weekly.index, weekly.values,
                    alpha=0.08, color="#3498db")
    ax.plot(rolling.index, rolling.values,
            color="#e74c3c", linewidth=2.2,
            label="4-Week Rolling Avg", zorder=5)

    ax.set_xlabel("Date")
    ax.set_ylabel("Number of Orders")
    ax.set_title("Weekly Order Volume Trend", pad=14)
    ax.legend(framealpha=0.6)
    fig.autofmt_xdate()
    fig.tight_layout()
    _save(fig, "weekly_order_trend.png")


# ===========================================================================
# PLOT 8 — Return Rate by Product Category
# ===========================================================================
def plot_category_return_rate(df_master: pd.DataFrame) -> None:
    cat_total    = df_master.groupby("category")["order_id"].nunique()
    cat_returned = (
        df_master[df_master["status"] == "Returned"]
        .groupby("category")["order_id"]
        .nunique()
    )
    return_rate = (cat_returned / cat_total * 100).fillna(0).sort_values()

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(
        return_rate.index, return_rate.values,
        color="#e74c3c", edgecolor="white", height=0.55, alpha=0.85
    )

    for bar, val in zip(bars, return_rate.values):
        ax.text(
            bar.get_width() + 0.15,
            bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%",
            va="center", ha="left", fontsize=9.5, color="#2c3e50"
        )

    ax.set_xlabel("Return Rate (%)")
    ax.set_title("Return Rate by Product Category", pad=14)
    ax.set_xlim(0, return_rate.max() * 1.2)
    fig.tight_layout()
    _save(fig, "category_return_rate.png")


# ===========================================================================
# SQL QUERIES via SQLAlchemy
# ===========================================================================
def run_sql_queries() -> None:
    _section("SQL Query Results")
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

    queries = {
        "Top 10 Customers by Total Spend": """
            SELECT
                c.customer_id,
                c.name,
                c.customer_segment,
                c.city,
                COUNT(DISTINCT o.order_id)    AS orders,
                ROUND(SUM(oi.total_price), 2) AS total_spend
            FROM customers c
            JOIN orders      o  ON c.customer_id = o.customer_id
            JOIN order_items oi ON o.order_id    = oi.order_id
            WHERE o.status = 'Delivered'
            GROUP BY c.customer_id, c.name, c.customer_segment, c.city
            ORDER BY total_spend DESC
            LIMIT 10
        """,
        "Revenue by Product Category": """
            SELECT
                p.category,
                COUNT(DISTINCT oi.order_id)      AS total_orders,
                SUM(oi.quantity)                  AS units_sold,
                ROUND(SUM(oi.total_price), 2)     AS total_revenue,
                ROUND(SUM(oi.total_price)*100.0/
                      (SELECT SUM(total_price) FROM order_items), 2) AS share_pct
            FROM order_items oi
            JOIN products p ON oi.product_id = p.product_id
            JOIN orders   o ON oi.order_id   = o.order_id
            WHERE o.status = 'Delivered'
            GROUP BY p.category
            ORDER BY total_revenue DESC
        """,
        "Average Order Value by Month": """
            SELECT
                strftime('%Y-%m', o.order_date)  AS year_month,
                COUNT(DISTINCT o.order_id)        AS total_orders,
                ROUND(SUM(oi.total_price)/
                      COUNT(DISTINCT o.order_id), 2) AS avg_order_value
            FROM orders o
            JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status = 'Delivered'
              AND strftime('%Y', o.order_date) IN ('2022','2023')
            GROUP BY year_month
            ORDER BY year_month
        """,
        "Orders by Payment Method": """
            SELECT
                payment_method,
                COUNT(*)                    AS total_orders,
                SUM(CASE WHEN status='Delivered' THEN 1 ELSE 0 END)  AS delivered,
                SUM(CASE WHEN status='Returned'  THEN 1 ELSE 0 END)  AS returned,
                SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END)  AS cancelled,
                ROUND(COUNT(*)*100.0/(SELECT COUNT(*) FROM orders),2) AS pct
            FROM orders
            GROUP BY payment_method
            ORDER BY total_orders DESC
        """,
    }

    with engine.connect() as conn:
        for title, sql in queries.items():
            print(f"\n  {'─'*60}")
            print(f"  {title}")
            print(f"  {'─'*60}")
            df = pd.read_sql(text(sql), conn)
            # Format monetary column if present
            if "total_spend" in df.columns:
                df["total_spend"] = df["total_spend"].apply(
                    lambda x: f"{RUPEE}{x:,.2f}")
            if "total_revenue" in df.columns:
                df["total_revenue"] = df["total_revenue"].apply(
                    lambda x: f"{RUPEE}{x:,.2f}")
            if "avg_order_value" in df.columns:
                df["avg_order_value"] = df["avg_order_value"].apply(
                    lambda x: f"{RUPEE}{x:,.2f}")
            print(df.to_string(index=False))


# ===========================================================================
# FINAL SUMMARY
# ===========================================================================
def print_summary() -> None:
    _section("EDA Complete")
    print("  8 plots saved to outputs/plots/\n")
    plots = [
        "top_products_revenue.png",
        "monthly_revenue_trend.png",
        "revenue_by_category.png",
        "orders_by_payment_method.png",
        "customer_segment_distribution.png",
        "rfm_segment_distribution.png",
        "weekly_order_trend.png",
        "category_return_rate.png",
    ]
    for i, name in enumerate(plots, 1):
        fpath = PLOTS_DIR / name
        size  = fpath.stat().st_size / 1024 if fpath.exists() else 0
        print(f"  [{i}] {name:<42}  ({size:.0f} KB)")
    print()


# ===========================================================================
# MAIN
# ===========================================================================
def main() -> None:
    print(f"\n{SEP}")
    print("  E-Commerce — Exploratory Data Analysis")
    print(f"{SEP}")

    # Load data
    customers, products, orders, order_items, rfm, df_master = load_data()

    # ── Generate all 8 plots ───────────────────────────────────────────────
    _section("Generating Plots")

    print("  Plot 1/8 : Top 10 Products by Revenue")
    plot_top_products(df_master)

    print("  Plot 2/8 : Monthly Revenue Trend 2022 vs 2023")
    plot_monthly_revenue_trend(df_master)

    print("  Plot 3/8 : Revenue by Product Category")
    plot_revenue_by_category(df_master)

    print("  Plot 4/8 : Orders by Payment Method")
    plot_payment_method(orders)

    print("  Plot 5/8 : Customer Segment Distribution (Donut)")
    plot_customer_segment(customers)

    print("  Plot 6/8 : RFM Segment Distribution")
    plot_rfm_segments(rfm)

    print("  Plot 7/8 : Weekly Order Volume Trend")
    plot_weekly_order_trend(orders)

    print("  Plot 8/8 : Return Rate by Product Category")
    plot_category_return_rate(df_master)

    # ── SQL query results ──────────────────────────────────────────────────
    run_sql_queries()

    # ── Summary ───────────────────────────────────────────────────────────
    print_summary()


if __name__ == "__main__":
    main()
