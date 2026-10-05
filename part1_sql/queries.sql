-- @output: monthly_category_revenue.csv
-- Query 1: Monthly revenue by category
SELECT
    month,
    category,
    ROUND(SUM(quantity * unit_price), 2) AS revenue,
    COUNT(*) AS n_orders
FROM orders
GROUP BY month, category
ORDER BY
    CASE month WHEN 'April' THEN 1 WHEN 'May' THEN 2 ELSE 3 END,
    CASE category
        WHEN 'Ethnic Wear' THEN 1
        WHEN 'Western Wear' THEN 2
        WHEN 'Kids Wear' THEN 3
        WHEN 'Home & Kitchen' THEN 4
        ELSE 5
    END;

    
-- @output: region_revenue.csv
-- Query 2: Region-wise total revenue and order count
SELECT
    r.region,
    ROUND(SUM(o.quantity * o.unit_price), 2) AS revenue,
    COUNT(*) AS n_orders
FROM orders AS o
JOIN resellers AS r ON o.reseller_id = r.reseller_id
GROUP BY r.region
ORDER BY revenue DESC;


-- @output: grand_total_revenue.csv
-- Check: Grand total revenue across all 900 orders, all months
SELECT
    ROUND(SUM(quantity * unit_price), 2) AS grand_total_revenue
FROM orders;


-- @output: top_resellers.csv
-- Query 3: Top resellers by total spend (total_spend > 50000)
SELECT
    r.reseller_id,
    r.reseller_name,
    r.region,
    ROUND(SUM(o.quantity * o.unit_price), 2) AS total_spend
FROM orders AS o
JOIN resellers AS r ON o.reseller_id = r.reseller_id
GROUP BY r.reseller_id
HAVING total_spend > 50000
ORDER BY total_spend DESC
LIMIT 5;


-- @output: never_ordered_resellers.csv
-- Query 4a: Resellers who have never placed an order
-- LEFT JOIN keeps every reseller, even if no order matches.
-- For a reseller with no orders, all the order columns come back NULL,
-- so "o.order_id IS NULL" picks out exactly those resellers.
SELECT
    r.reseller_id,
    r.reseller_name,
    r.region
FROM resellers AS r
LEFT JOIN orders AS o ON r.reseller_id = o.reseller_id
WHERE o.order_id IS NULL;

-- @output: count_star_vs_count_order_id.csv
-- Query 4b: Why COUNT(*) cannot be used to detect a zero-match LEFT JOIN row
-- For RS024 the LEFT JOIN returns ONE row where every order column is NULL.
-- COUNT(*) counts rows, so it counts that single all-NULL unmatched row and returns 1.
-- COUNT(order_id) counts only non-NULL order_id values, so it returns 0.
-- Therefore COUNT(*) is the wrong way to test for a zero-match LEFT JOIN row.
-- COUNT(order_id) = 0 is the correct test.
SELECT
    r.reseller_id,
    COUNT(*) AS count_star,
    COUNT(o.order_id) AS count_order_id
FROM resellers AS r
LEFT JOIN orders AS o ON r.reseller_id = o.reseller_id
WHERE r.reseller_id = 'RS024'
GROUP BY r.reseller_id;


-- @output: june_delivered_aov.csv
-- Query 5: Average Order Value (AOV) for June, Delivered orders only
SELECT
    ROUND(SUM(quantity * unit_price) / COUNT(*), 2) AS aov_june_delivered
FROM orders
WHERE month = 'June' AND status = 'Delivered';