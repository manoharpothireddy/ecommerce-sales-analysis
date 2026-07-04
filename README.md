# 🛒 E-Commerce Sales & Customer Behavior Analysis

<div align="center">

![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.1.4-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-1.26.2-013243?style=for-the-badge&logo=numpy&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/Scikit--learn-1.3.2-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8.2-11557C?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen?style=for-the-badge)

**End-to-end data analytics pipeline on a synthetic Indian e-commerce dataset.**  
Data generation → Cleaning → SQL analysis → EDA → RFM segmentation → Dashboard exports.

[📊 Key Findings](#-key-findings) · [🚀 Quick Start](#-quick-start) · [📁 Project Structure](#-project-structure) · [📈 Analysis Scripts](#-analysis-scripts) · [📸 Dashboard Screenshots](#-dashboard-screenshots)](#-sample-plots)

</div>

---

## 📌 Project Overview

A complete, production-style analytics project built on a **synthetic Indian e-commerce dataset** containing:

| Dataset | Size |
|---------|------|
| Customers | 1,000 rows |
| Products | 100 rows (6 categories) |
| Orders | 5,000 rows |
| Order Items | 8,000 rows |
| Date Range | 2022-01-01 → 2024-01-01 |

The project covers the **full analytics lifecycle**:

1. 🏭 **Data Generation** — synthetic realistic data using Faker (Indian locale)
2. 🧹 **Data Cleaning** — null checks, deduplication, feature engineering
3. 🗄️ **SQL Analysis** — 8 queries via SQLAlchemy on a SQLite database
4. 📊 **EDA** — 8 publication-quality Matplotlib/Seaborn charts
5. 👥 **RFM Segmentation** — Recency, Frequency, Monetary scoring with quartile binning
6. 📤 **Dashboard Exports** — 6 Tableau/Power BI-ready CSV files

---

## 🔍 Key Findings

| KPI | Value |
|-----|-------|
| 💰 Total Revenue | ₹4.88 Cr (delivered orders only) |
| 📦 Total Orders | 5,000 |
| ✅ Delivered Orders | 3,470 (69.4%) |
| 🔄 Return Rate | ~10.1% overall |
| 🛒 Avg Order Value | ₹14,067 |
| 👤 Total Customers | 1,000 |

### 🏆 Category Performance

| Category | Revenue | Share |
|----------|---------|-------|
| Electronics | ₹1.49 Cr | 21.0% |
| Sports | ₹1.11 Cr | 15.7% |
| Home & Kitchen | ₹1.10 Cr | 15.5% |
| Clothing | ₹0.61 Cr | 8.7% |
| Beauty | ₹0.41 Cr | 5.7% |
| Books | ₹0.16 Cr | 2.3% |

### 💳 Payment Methods

| Method | Orders | Share |
|--------|--------|-------|
| UPI | 1,766 | 35.3% |
| Credit Card | 1,240 | 24.8% |
| Debit Card | 980 | 19.6% |
| Net Banking | 510 | 10.2% |
| COD | 504 | 10.1% |

### 👥 RFM Customer Segments

| Segment | Count | % | Avg Spend | Avg Orders |
|---------|-------|---|-----------|------------|
| Loyal Customers | 426 | 44.4% | ₹65,997 | 4.7 |
| Others | 246 | 25.6% | ₹31,845 | 2.3 |
| At Risk | 118 | 12.3% | ₹39,141 | 2.9 |
| Lost | 116 | 12.1% | ₹19,766 | 1.5 |
| Champions | 54 | 5.6% | ₹1,10,257 | 6.8 |

### 🌟 Notable Insights

- 📅 **Peak AOV Month:** November 2022 — ₹21,608 average order value
- 🥇 **Top Customer:** Shanaya Sood (Premium, Pune) — ₹2,26,615 across 11 orders
- 🏅 **Top Product:** Wireless Earbuds — ₹23,34,075 total revenue
- 🏆 **Champions (5.6% of customers)** drive disproportionately high spend at ₹1.1 Lakh each
- 📉 **Lost segment** (12.1%) hasn't ordered in 447 days on average — prime re-engagement targets

---

## 🛠 Tech Stack

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12 | Core language |
| Pandas | 2.1.4 | Data manipulation & preprocessing |
| NumPy | 1.26.2 | Numerical computations |
| Matplotlib | 3.8.2 | Static chart generation |
| Seaborn | 0.13.0 | Statistical visualizations |
| Scikit-learn | 1.3.2 | KMeans clustering, preprocessing |
| SQLAlchemy | 2.0.23 | ORM & SQL query execution |
| SQLite | built-in | Lightweight relational database |
| Faker | 20.1.0 | Synthetic data generation (Indian locale) |
| openpyxl | 3.1.2 | Excel export support |
| Jupyter | 1.0.0 | Interactive notebook analysis |
| Tableau / Power BI | — | Interactive business dashboards |

---

## 📁 Project Structure

```
ecommerce-sales-analysis/
│
├── data/
│   ├── raw/                          # Generated source data
│   │   ├── customers.csv             # 1,000 customers
│   │   ├── products.csv              # 100 products across 6 categories
│   │   ├── orders.csv                # 5,000 orders (2022–2024)
│   │   ├── order_items.csv           # 8,000 line items
│   │   └── ecommerce.db              # SQLite database (all 4 tables)
│   │
│   └── processed/                    # Cleaned & engineered data
│       ├── customers_clean.csv       # + tenure_days
│       ├── products_clean.csv        # + profit_margin
│       ├── orders_clean.csv          # + order_year/month/quarter/weekday
│       ├── order_items_clean.csv     # + recalculated total_price
│       ├── rfm_scores.csv            # RFM scores + segment labels
│       └── dashboard_exports/        # Tableau / Power BI ready files
│           ├── kpi_summary.csv
│           ├── monthly_revenue.csv
│           ├── category_performance.csv
│           ├── customer_segments.csv
│           ├── product_performance.csv
│           └── daily_orders.csv
│
├── scripts/                          # Standalone Python pipeline scripts
│   ├── generate_data.py              # Synthetic data generation (Faker + NumPy)
│   ├── data_cleaning.py              # Cleaning, validation, RFM analysis
│   ├── eda_analysis.py               # 8 EDA plots + SQL query results
│   └── dashboard_export.py           # 6 CSV exports for BI tools
│
├── sql/
│   └── queries.sql                   # 8 SQL analysis queries (SQLite compatible)
│
├── notebooks/                        # Jupyter notebooks (step-by-step)
│   ├── 01_data_generation.ipynb
│   ├── 02_exploratory_data_analysis.ipynb
│   ├── 03_revenue_trend_analysis.ipynb
│   ├── 04_customer_segmentation.ipynb
│   ├── 05_cohort_analysis.ipynb
│   └── 06_purchasing_pattern_analysis.ipynb
│
├── dashboards/
│   └── DASHBOARD_GUIDE.md            # Tableau & Power BI visual mapping guide
│
├── outputs/
│   └── plots/                        # 8 saved PNG charts (DPI 150)
│       ├── top_products_revenue.png
│       ├── monthly_revenue_trend.png
│       ├── revenue_by_category.png
│       ├── orders_by_payment_method.png
│       ├── customer_segment_distribution.png
│       ├── rfm_segment_distribution.png
│       ├── weekly_order_trend.png
│       └── category_return_rate.png
│
├── .gitignore
├── requirements.txt
├── setup.sh                          # Mac/Linux environment setup
├── setup.bat                         # Windows environment setup
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites
- Python **3.11+** — [python.org](https://www.python.org/downloads/)
- Git — [git-scm.com](https://git-scm.com/)

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/ecommerce-sales-analysis.git
cd ecommerce-sales-analysis
```

### 2. Run Setup

**Windows:**
```bat
setup.bat
```

**macOS / Linux:**
```bash
chmod +x setup.sh && ./setup.sh
```

The setup script automatically:
- Creates a Python virtual environment (`venv/`)
- Installs all dependencies from `requirements.txt`
- Registers the Jupyter kernel as `Python (ecommerce-analysis)`

### 3. Run the Full Pipeline

Activate the environment first:

```bat
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

Then run each script in order:

```bash
# Step 1 — Generate 14,100 rows of synthetic data + SQLite DB
python scripts/generate_data.py

# Step 2 — Clean all tables, add feature columns, compute RFM scores
python scripts/data_cleaning.py

# Step 3 — Generate 8 EDA plots + run 4 SQL queries
python scripts/eda_analysis.py

# Step 4 — Export 6 dashboard-ready CSVs for Tableau / Power BI
python scripts/dashboard_export.py
```

### 4. Launch Jupyter Notebook (Optional)

```bash
jupyter notebook
# or
jupyter lab
```

Open notebooks in the `notebooks/` folder and select the `Python (ecommerce-analysis)` kernel.

---

## 📈 Analysis Scripts

### `generate_data.py`
Generates the entire synthetic dataset using **Faker** (Indian locale) and **NumPy** with `seed=42` for full reproducibility.

| Output | Details |
|--------|---------|
| customers.csv | 1,000 rows — names, cities, states, segments |
| products.csv | 100 rows — 6 categories, realistic pricing |
| orders.csv | 5,000 rows — status weighted 70/10/10/10 |
| order_items.csv | 8,000 rows — quantity 1–5, discount 0–20% |
| ecommerce.db | SQLite DB with all 4 tables loaded |
| queries.sql | 8 SQL analysis queries |

---

### `data_cleaning.py`

Runs a **9-step cleaning pipeline**:

| Step | Action |
|------|--------|
| Quality Report | Shape, dtypes, null values, duplicate count per table |
| Customers | Parse dates, strip whitespace, lowercase emails, add `tenure_days` |
| Products | Coerce numerics, strip text, add `profit_margin` |
| Orders | Parse dates, add `order_year/month/quarter/weekday/week_number` |
| Order Items | Recalculate `total_price`, drop invalid rows |
| RFM Analysis | Score R/F/M 1–4 via quartile binning, assign segment labels |
| Save | Write 5 cleaned CSVs to `data/processed/` |

**RFM Segment Rules:**

| Segment | Rule |
|---------|------|
| Champions | R=4, F=4, M=4 |
| Loyal Customers | F ≥ 3 |
| At Risk | R ≤ 2, F ≥ 2 |
| Lost | R=1, F=1 |
| Others | Everything else |

---

### `eda_analysis.py`

Generates **8 publication-quality plots** (DPI 150, saved as PNG) and runs **4 SQL queries** against the SQLite database.

| Plot | File |
|------|------|
| Top 10 Products by Revenue (teal gradient H-bar) | `top_products_revenue.png` |
| Monthly Revenue Trend 2022 vs 2023 (dual line) | `monthly_revenue_trend.png` |
| Revenue by Product Category (bar) | `revenue_by_category.png` |
| Orders by Payment Method (pie) | `orders_by_payment_method.png` |
| Customer Segment Distribution (donut) | `customer_segment_distribution.png` |
| RFM Segments (color-coded H-bar) | `rfm_segment_distribution.png` |
| Weekly Order Volume + 4-week rolling avg | `weekly_order_trend.png` |
| Return Rate by Category (red H-bar) | `category_return_rate.png` |

---

### `dashboard_export.py`

Produces **6 ready-to-connect CSV files** for Tableau and Power BI:

| Export | Rows | Purpose |
|--------|------|---------|
| `kpi_summary.csv` | 1 | Single-row KPI snapshot for card visuals |
| `monthly_revenue.csv` | 25 | Year-month revenue for trend charts |
| `category_performance.csv` | 6 | Category metrics incl. return rate |
| `customer_segments.csv` | 1,000 | Customers merged with RFM scores |
| `product_performance.csv` | 100 | Per-product revenue, margin, discount |
| `daily_orders.csv` | 731 | Full date-range daily orders (gap-filled) |

See [`dashboards/DASHBOARD_GUIDE.md`](dashboards/DASHBOARD_GUIDE.md) for the complete Tableau and Power BI visual mapping guide.

---

## 📸 Dashboard Screenshots

> All plots saved to `outputs/plots/` at 150 DPI.

| Top 10 Products by Revenue | Monthly Revenue Trend |
|---|---|
| Teal gradient horizontal bar, ₹ labels | 2022 vs 2023 dual-line with fill |

| RFM Customer Segments | Return Rate by Category |
|---|---|
| Color-coded by segment (green/blue/orange/red/gray) | Red horizontal bars with % labels |

---

## 🗄️ SQL Queries (`sql/queries.sql`)

8 production-ready SQLite queries included:

| # | Query |
|---|-------|
| 1 | Top 10 best-selling products by revenue |
| 2 | Monthly revenue trend for 2022 and 2023 |
| 3 | Revenue by product category with share % |
| 4 | Customer count by segment |
| 5 | Top 10 customers by total spend |
| 6 | Orders by payment method with status breakdown |
| 7 | Return rate by product category |
| 8 | Average order value by month |

Run any query directly against the database:

```python
from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine("sqlite:///data/raw/ecommerce.db")
with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM customers LIMIT 5"), conn)
print(df)
```

---

## 📊 Dashboard Integration

### Tableau
1. Open Tableau Desktop → **Connect to a File → Text File**
2. Navigate to `data/processed/dashboard_exports/`
3. Load `kpi_summary.csv` for KPI cards
4. Load `monthly_revenue.csv` for trend charts
5. Create **relationships** between files using `customer_id`, `product_id`, `order_id`
6. Follow the visual plan in [`dashboards/DASHBOARD_GUIDE.md`](dashboards/DASHBOARD_GUIDE.md)

### Power BI
1. Open Power BI Desktop → **Get Data → Text/CSV**
2. Load all 6 CSV files from `data/processed/dashboard_exports/`
3. In Power Query, set correct data types for date and numeric columns
4. Create **relationships** in the Model view
5. Follow the page-by-page plan in [`dashboards/DASHBOARD_GUIDE.md`](dashboards/DASHBOARD_GUIDE.md)

---

## 📦 Requirements

```
pandas==2.1.4
numpy==1.26.2
matplotlib==3.8.2
seaborn==0.13.0
scikit-learn==1.3.2
faker==20.1.0
sqlalchemy==2.0.23
ipykernel==6.27.1
jupyter==1.0.0
openpyxl==3.1.2
```

Install manually:

```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-analysis`
3. Commit your changes: `git commit -m "Add: cohort retention analysis"`
4. Push to GitHub: `git push origin feature/your-analysis`
5. Open a Pull Request

Please follow [PEP 8](https://peps.python.org/pep-0008/) and add docstrings to all functions.

---

## 📄 License

This project is licensed under the **MIT License**.

---

## 👤 Author

**P Manohar Reddy**
- GitHub: [@manoharpothireddy](https://github.com/manoharpothireddy)
- LinkedIn: [Manohar Reddy Pothireddy](https://www.linkedin.com/in/manohar-reddy-pothireddy-3ab1a7319/)
- Email: p.manoharreddy789809@gmail.com

---

<div align="center">

⭐ **Star this repo** if you found it useful!

Built with ❤️, Python, and a lot of ₹ signs.

</div>
