# -*- coding: utf-8 -*-
"""
generate_data.py
================
Synthetic E-Commerce Data Generator
Generates Customers, Products, Orders, and Order Items tables,
saves them as CSVs, loads them into an SQLite database, and writes SQL queries.

Usage:
    python scripts/generate_data.py

Dependencies:
    pandas, numpy, faker, sqlalchemy
"""

import io
import os
import sys
import random
from pathlib import Path
from datetime import date, timedelta

import numpy as np
import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text

# ── Reproducibility ────────────────────────────────────────────────────────────
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
fake = Faker("en_IN")          # Indian locale for realistic names / cities
Faker.seed(SEED)

# ── Paths ──────────────────────────────────────────────────────────────────────
BASE_DIR  = Path(__file__).resolve().parent.parent
RAW_DIR   = BASE_DIR / "data" / "raw"
SQL_DIR   = BASE_DIR / "sql"
RAW_DIR.mkdir(parents=True, exist_ok=True)
SQL_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH   = RAW_DIR / "ecommerce.db"

# ── Indian cities & states ─────────────────────────────────────────────────────
INDIA_CITIES = {
    "Maharashtra":    ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Karnataka":      ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi"],
    "Tamil Nadu":     ["Chennai", "Coimbatore", "Madurai", "Salem", "Tiruchirappalli"],
    "Delhi":          ["New Delhi", "Dwarka", "Rohini", "Janakpuri", "Saket"],
    "Uttar Pradesh":  ["Lucknow", "Kanpur", "Agra", "Varanasi", "Noida"],
    "West Bengal":    ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],
    "Rajasthan":      ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer"],
    "Gujarat":        ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Gandhinagar"],
    "Telangana":      ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain"],
}
STATE_LIST  = list(INDIA_CITIES.keys())

def random_city_state():
    state = random.choice(STATE_LIST)
    city  = random.choice(INDIA_CITIES[state])
    return city, state


def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))


# ══════════════════════════════════════════════════════════════════════════════
# 1. CUSTOMERS  (1 000 rows)
# ══════════════════════════════════════════════════════════════════════════════
def generate_customers(n: int = 1000) -> pd.DataFrame:
    print(f"  Generating {n} customers...")

    reg_start = date(2021, 1, 1)
    reg_end   = date(2023, 1, 1)
    segments  = ["New", "Regular", "Premium"]
    seg_weights = [0.40, 0.40, 0.20]

    rows = []
    for i in range(1, n + 1):
        gender  = random.choice(["Male", "Female"])
        if gender == "Male":
            name = fake.name_male()
        else:
            name = fake.name_female()

        city, state = random_city_state()
        rows.append({
            "customer_id":       f"C{i:04d}",
            "name":              name,
            "email":             fake.email(),
            "phone":             fake.phone_number(),
            "gender":            gender,
            "city":              city,
            "state":             state,
            "country":           "India",
            "registration_date": random_date(reg_start, reg_end).isoformat(),
            "customer_segment":  random.choices(segments, weights=seg_weights, k=1)[0],
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# 2. PRODUCTS  (100 rows)
# ══════════════════════════════════════════════════════════════════════════════
CATEGORY_MAP = {
    "Electronics": {
        "sub_categories": ["Mobile Phones", "Laptops", "Tablets", "Accessories", "Cameras"],
        "brands":         ["Samsung", "Apple", "OnePlus", "Xiaomi", "Sony", "Dell", "HP", "Lenovo"],
        "price_range":    (2999, 9999),
    },
    "Clothing": {
        "sub_categories": ["Men's Wear", "Women's Wear", "Kids' Wear", "Ethnic Wear", "Sportswear"],
        "brands":         ["H&M", "Zara", "FabIndia", "Biba", "Manyavar", "Puma", "Nike"],
        "price_range":    (399, 3999),
    },
    "Home & Kitchen": {
        "sub_categories": ["Cookware", "Furniture", "Decor", "Cleaning", "Storage"],
        "brands":         ["Prestige", "Philips", "Bosch", "IKEA", "Amazon Basics", "Milton"],
        "price_range":    (299, 7999),
    },
    "Books": {
        "sub_categories": ["Fiction", "Non-Fiction", "Academic", "Children", "Self-Help"],
        "brands":         ["Penguin", "Harper Collins", "Oxford", "Scholastic", "Rupa", "S. Chand"],
        "price_range":    (199, 999),
    },
    "Sports": {
        "sub_categories": ["Fitness", "Cricket", "Football", "Cycling", "Yoga"],
        "brands":         ["Nike", "Adidas", "Cosco", "SG", "Nivia", "Decathlon", "Vector X"],
        "price_range":    (499, 6999),
    },
    "Beauty": {
        "sub_categories": ["Skincare", "Haircare", "Makeup", "Fragrances", "Personal Care"],
        "brands":         ["Lakme", "Himalaya", "Mamaearth", "L'Oreal", "Nivea", "Biotique"],
        "price_range":    (199, 2999),
    },
}

PRODUCT_NAMES = {
    "Electronics":    ["Smartphone", "Laptop", "Tablet", "Wireless Earbuds", "Smart Watch",
                       "DSLR Camera", "Power Bank", "Bluetooth Speaker", "USB Hub", "Web Cam"],
    "Clothing":       ["Formal Shirt", "Casual T-Shirt", "Denim Jeans", "Salwar Kameez",
                       "Kurti", "Track Pants", "Saree", "Blazer", "Shorts", "Jacket"],
    "Home & Kitchen": ["Non-Stick Cookware Set", "Pressure Cooker", "Mixer Grinder",
                       "Air Fryer", "Storage Box Set", "Cushion Cover Set", "Wall Clock",
                       "Dinner Set", "Knife Set", "Toaster"],
    "Books":          ["The Alchemist", "Atomic Habits", "Rich Dad Poor Dad",
                       "Wings of Fire", "Data Structures & Algorithms", "The Lean Startup",
                       "Sapiens", "Deep Work", "Think and Grow Rich", "Harry Potter Box Set"],
    "Sports":         ["Yoga Mat", "Resistance Bands Set", "Cricket Bat", "Football",
                       "Cycling Gloves", "Dumbbell Set", "Skipping Rope", "Badminton Racquet",
                       "Running Shoes", "Sports Water Bottle"],
    "Beauty":         ["Moisturiser SPF 50", "Vitamin C Serum", "Shampoo & Conditioner Combo",
                       "Lipstick Set", "Face Wash", "Perfume", "Sunscreen Gel",
                       "Hair Oil", "Eyeshadow Palette", "BB Cream"],
}

def generate_products(n: int = 100) -> pd.DataFrame:
    print(f"  Generating {n} products...")

    categories = list(CATEGORY_MAP.keys())
    # Distribute 100 products across 6 categories (roughly 16–17 each)
    cat_assignments = []
    for cat in categories:
        cat_assignments.extend([cat] * 16)
    cat_assignments += random.choices(categories, k=n - len(cat_assignments))
    random.shuffle(cat_assignments)

    rows = []
    name_counters = {c: 0 for c in categories}

    for i in range(1, n + 1):
        cat   = cat_assignments[i - 1]
        cfg   = CATEGORY_MAP[cat]
        idx   = name_counters[cat] % len(PRODUCT_NAMES[cat])
        pname = PRODUCT_NAMES[cat][idx]
        name_counters[cat] += 1

        lo, hi   = cfg["price_range"]
        price    = round(random.uniform(lo, hi) / 10) * 10   # round to nearest 10
        cost_pct = random.uniform(0.60, 0.80)
        cost     = round(price * cost_pct, 2)

        rows.append({
            "product_id":      f"P{i:03d}",
            "product_name":    pname,
            "category":        cat,
            "sub_category":    random.choice(cfg["sub_categories"]),
            "brand":           random.choice(cfg["brands"]),
            "price":           price,
            "cost_price":      cost,
            "stock_quantity":  random.randint(10, 500),
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# 3. ORDERS  (5 000 rows)
# ══════════════════════════════════════════════════════════════════════════════
def generate_orders(customers: pd.DataFrame, n: int = 5000) -> pd.DataFrame:
    print(f"  Generating {n} orders...")

    ord_start = date(2022, 1, 1)
    ord_end   = date(2024, 1, 1)

    statuses = ["Delivered", "Returned", "Cancelled", "Pending"]
    status_w = [0.70, 0.10, 0.10, 0.10]

    payments = ["UPI", "Credit Card", "Debit Card", "Net Banking", "COD"]
    pay_w    = [0.35, 0.25, 0.20, 0.10, 0.10]

    customer_ids = customers["customer_id"].tolist()

    rows = []
    for i in range(1, n + 1):
        city, state = random_city_state()
        rows.append({
            "order_id":        f"ORD{i:05d}",
            "customer_id":     random.choice(customer_ids),
            "order_date":      random_date(ord_start, ord_end).isoformat(),
            "status":          random.choices(statuses, weights=status_w, k=1)[0],
            "payment_method":  random.choices(payments, weights=pay_w, k=1)[0],
            "shipping_city":   city,
            "shipping_state":  state,
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# 4. ORDER ITEMS  (8 000 rows)
# ══════════════════════════════════════════════════════════════════════════════
def generate_order_items(orders: pd.DataFrame, products: pd.DataFrame,
                         n: int = 8000) -> pd.DataFrame:
    print(f"  Generating {n} order items...")

    order_ids   = orders["order_id"].tolist()
    product_ids = products["product_id"].tolist()
    price_map   = products.set_index("product_id")["price"].to_dict()

    discounts   = [0, 5, 10, 15, 20]
    disc_w      = [0.45, 0.25, 0.15, 0.10, 0.05]   # skewed toward 0

    rows = []
    for i in range(1, n + 1):
        oid      = random.choice(order_ids)
        pid      = random.choice(product_ids)
        qty      = random.randint(1, 5)
        u_price  = price_map[pid]
        disc_pct = random.choices(discounts, weights=disc_w, k=1)[0]
        total    = round(qty * u_price * (1 - disc_pct / 100), 2)

        rows.append({
            "item_id":          i,
            "order_id":         oid,
            "product_id":       pid,
            "quantity":         qty,
            "unit_price":       u_price,
            "discount_percent": disc_pct,
            "total_price":      total,
        })

    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════════
# 5. SQL QUERIES
# ══════════════════════════════════════════════════════════════════════════════
SQL_QUERIES = """\
-- ============================================================
-- E-Commerce Sales & Customer Behavior Analysis
-- SQL Queries
-- Database: data/raw/ecommerce.db
-- ============================================================

-- ── 1. Top 10 best-selling products by revenue ────────────────────────────
SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.brand,
    SUM(oi.quantity)    AS total_units_sold,
    ROUND(SUM(oi.total_price), 2) AS total_revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders   o ON oi.order_id   = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.category, p.brand
ORDER BY total_revenue DESC
LIMIT 10;


-- ── 2. Monthly revenue trend for 2022 and 2023 ───────────────────────────
SELECT
    strftime('%Y', o.order_date)     AS year,
    strftime('%m', o.order_date)     AS month,
    strftime('%Y-%m', o.order_date)  AS year_month,
    COUNT(DISTINCT o.order_id)       AS total_orders,
    ROUND(SUM(oi.total_price), 2)    AS monthly_revenue,
    ROUND(AVG(oi.total_price), 2)    AS avg_item_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
  AND strftime('%Y', o.order_date) IN ('2022', '2023')
GROUP BY year_month
ORDER BY year_month;


-- ── 3. Revenue by product category ───────────────────────────────────────
SELECT
    p.category,
    COUNT(DISTINCT oi.order_id)      AS total_orders,
    SUM(oi.quantity)                 AS total_units_sold,
    ROUND(SUM(oi.total_price), 2)    AS total_revenue,
    ROUND(AVG(oi.total_price), 2)    AS avg_item_revenue,
    ROUND(SUM(oi.total_price) * 100.0 /
          (SELECT SUM(total_price) FROM order_items), 2) AS revenue_share_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders   o ON oi.order_id   = o.order_id
WHERE o.status = 'Delivered'
GROUP BY p.category
ORDER BY total_revenue DESC;


-- ── 4. Customer count by segment ─────────────────────────────────────────
SELECT
    customer_segment,
    COUNT(*)                                        AS customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customers), 2) AS pct_of_total
FROM customers
GROUP BY customer_segment
ORDER BY customer_count DESC;


-- ── 5. Top 10 customers by total spend ───────────────────────────────────
SELECT
    c.customer_id,
    c.name,
    c.city,
    c.state,
    c.customer_segment,
    COUNT(DISTINCT o.order_id)       AS total_orders,
    ROUND(SUM(oi.total_price), 2)    AS total_spend,
    ROUND(AVG(oi.total_price), 2)    AS avg_order_item_value
FROM customers c
JOIN orders      o  ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id    = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY c.customer_id, c.name, c.city, c.state, c.customer_segment
ORDER BY total_spend DESC
LIMIT 10;


-- ── 6. Orders by payment method ──────────────────────────────────────────
SELECT
    payment_method,
    COUNT(*)                                         AS total_orders,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) AS pct_of_orders,
    SUM(CASE WHEN status = 'Delivered'  THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN status = 'Returned'   THEN 1 ELSE 0 END) AS returned,
    SUM(CASE WHEN status = 'Cancelled'  THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN status = 'Pending'    THEN 1 ELSE 0 END) AS pending
FROM orders
GROUP BY payment_method
ORDER BY total_orders DESC;


-- ── 7. Return rate by product category ───────────────────────────────────
SELECT
    p.category,
    COUNT(DISTINCT o.order_id)  AS total_orders,
    SUM(CASE WHEN o.status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
    ROUND(
        SUM(CASE WHEN o.status = 'Returned' THEN 1 ELSE 0 END) * 100.0
        / COUNT(DISTINCT o.order_id), 2
    )                           AS return_rate_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders   o ON oi.order_id   = o.order_id
GROUP BY p.category
ORDER BY return_rate_pct DESC;


-- ── 8. Average order value by month ──────────────────────────────────────
SELECT
    strftime('%Y-%m', o.order_date) AS year_month,
    COUNT(DISTINCT o.order_id)      AS total_orders,
    ROUND(SUM(oi.total_price), 2)   AS total_revenue,
    ROUND(
        SUM(oi.total_price) / COUNT(DISTINCT o.order_id), 2
    )                               AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status = 'Delivered'
GROUP BY year_month
ORDER BY year_month;
"""


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    # Force UTF-8 output on Windows so Unicode symbols print correctly
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    print("\n" + "=" * 60)
    print("  E-Commerce Data Generator")
    print("=" * 60)

    # ── Generate DataFrames ────────────────────────────────────────────────
    print("\n[1/4] Generating tables...")
    customers   = generate_customers(1000)
    products    = generate_products(100)
    orders      = generate_orders(customers, 5000)
    order_items = generate_order_items(orders, products, 8000)

    # ── Save CSVs ──────────────────────────────────────────────────────────
    print("\n[2/4] Saving CSV files to data/raw/...")
    customers.to_csv(RAW_DIR / "customers.csv",   index=False)
    products.to_csv(RAW_DIR  / "products.csv",    index=False)
    orders.to_csv(RAW_DIR    / "orders.csv",       index=False)
    order_items.to_csv(RAW_DIR / "order_items.csv", index=False)
    print("  [OK] customers.csv")
    print("  [OK] products.csv")
    print("  [OK] orders.csv")
    print("  [OK] order_items.csv")

    # ── Load into SQLite ───────────────────────────────────────────────────
    print(f"\n[3/4] Loading tables into SQLite ... {DB_PATH}")
    engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

    with engine.begin() as conn:
        customers.to_sql("customers",   conn, if_exists="replace", index=False)
        products.to_sql("products",     conn, if_exists="replace", index=False)
        orders.to_sql("orders",         conn, if_exists="replace", index=False)
        order_items.to_sql("order_items", conn, if_exists="replace", index=False)

    # Verify row counts from DB
    print("\n  Database row counts:")
    with engine.connect() as conn:
        for table in ["customers", "products", "orders", "order_items"]:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
            print(f"    {table:<15} ... {count:,} rows")

    # ── Write SQL file ─────────────────────────────────────────────────────
    print("\n[4/4] Writing SQL queries to sql/queries.sql ...")
    sql_path = SQL_DIR / "queries.sql"
    sql_path.write_text(SQL_QUERIES, encoding="utf-8")
    print(f"  [OK] queries.sql  ({len(SQL_QUERIES.splitlines())} lines, 8 queries)")

    # ── Summary ────────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  Data generation complete. Files saved to data/raw/")
    print("=" * 60)
    print(f"  customers   : {len(customers):>6,} rows  ->  customers.csv")
    print(f"  products    : {len(products):>6,} rows  ->  products.csv")
    print(f"  orders      : {len(orders):>6,} rows  ->  orders.csv")
    print(f"  order_items : {len(order_items):>6,} rows  ->  order_items.csv")
    print(f"  database    : ecommerce.db")
    print(f"  sql         : queries.sql  (8 analysis queries)")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
