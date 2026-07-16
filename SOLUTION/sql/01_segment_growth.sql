-- Question 1: segment contribution to growth from 2018 to 2024.
-- Growth can reflect both customer activity and historical reclassification.

WITH segment_year AS (
    SELECT
        transaction_customer_class AS customer_class,
        COALESCE(transaction_class_description, 'Unmapped') AS customer_class_description,
        per_year,
        COUNT(DISTINCT customer_number) AS customer_count,
        SUM(sales) AS total_revenue,
        SUM(gross_profit) AS gross_profit
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
      AND per_year IN (2018, 2024)
    GROUP BY 1, 2, 3
),
segment_comparison AS (
    SELECT
        customer_class,
        customer_class_description,
        SUM(CASE WHEN per_year = 2018 THEN customer_count ELSE 0 END) AS customers_2018,
        SUM(CASE WHEN per_year = 2024 THEN customer_count ELSE 0 END) AS customers_2024,
        SUM(CASE WHEN per_year = 2018 THEN total_revenue ELSE 0 END) AS revenue_2018,
        SUM(CASE WHEN per_year = 2024 THEN total_revenue ELSE 0 END) AS revenue_2024,
        SUM(CASE WHEN per_year = 2018 THEN gross_profit ELSE 0 END) AS gross_profit_2018,
        SUM(CASE WHEN per_year = 2024 THEN gross_profit ELSE 0 END) AS gross_profit_2024
    FROM segment_year
    GROUP BY 1, 2
),
portfolio_growth AS (
    SELECT SUM(revenue_2024 - revenue_2018) AS total_revenue_growth
    FROM segment_comparison
)
SELECT
    customer_class,
    customer_class_description,
    customers_2018,
    customers_2024,
    ROUND(revenue_2018, 2) AS revenue_2018,
    ROUND(revenue_2024, 2) AS revenue_2024,
    ROUND(revenue_2024 - revenue_2018, 2) AS revenue_growth,
    ROUND(100.0 * (revenue_2024 / NULLIF(revenue_2018, 0) - 1), 2) AS revenue_growth_pct,
    ROUND(gross_profit_2018, 2) AS gross_profit_2018,
    ROUND(gross_profit_2024, 2) AS gross_profit_2024,
    ROUND(gross_profit_2024 - gross_profit_2018, 2) AS gross_profit_growth,
    ROUND(100.0 * (gross_profit_2024 / NULLIF(gross_profit_2018, 0) - 1), 2) AS gross_profit_growth_pct,
    ROUND(100.0 * (revenue_2024 - revenue_2018) / total_revenue_growth, 2) AS growth_contribution_pct,
    ROUND(100.0 * gross_profit_2018 / NULLIF(revenue_2018, 0), 2) AS margin_2018_pct,
    ROUND(100.0 * gross_profit_2024 / NULLIF(revenue_2024, 0), 2) AS margin_2024_pct
FROM segment_comparison
CROSS JOIN portfolio_growth
ORDER BY revenue_growth DESC, customer_class;
