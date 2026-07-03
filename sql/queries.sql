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
