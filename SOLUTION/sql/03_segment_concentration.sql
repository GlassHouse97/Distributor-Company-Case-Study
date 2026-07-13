-- Question 3: segment-level revenue concentration.

WITH segment_performance AS (
    SELECT
        transaction_customer_class AS customer_class,
        COALESCE(transaction_class_description, 'Unmapped') AS customer_class_description,
        COUNT(DISTINCT customer_number) AS customer_count,
        SUM(sales) AS total_revenue
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY 1, 2
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC, customer_class) AS revenue_rank,
        SUM(total_revenue) OVER () AS portfolio_revenue,
        SUM(total_revenue) OVER (
            ORDER BY total_revenue DESC, customer_class
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue
    FROM segment_performance
)
SELECT
    customer_class,
    customer_class_description,
    customer_count,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(100.0 * total_revenue / portfolio_revenue, 4) AS revenue_share_pct,
    ROUND(100.0 * cumulative_revenue / portfolio_revenue, 4) AS cumulative_revenue_pct,
    revenue_rank
FROM ranked
ORDER BY revenue_rank;
