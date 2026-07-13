-- Question 3: customer-level recognized-revenue concentration.
-- Customer numbers are identifiers only; no customer names are exposed.

WITH customer_performance AS (
    SELECT
        customer_number,
        COUNT(*) AS transaction_rows,
        SUM(sales) AS total_revenue,
        SUM(gross_profit) AS gross_profit
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY customer_number
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY total_revenue DESC, customer_number) AS revenue_rank,
        SUM(total_revenue) OVER () AS portfolio_revenue,
        SUM(total_revenue) OVER (
            ORDER BY total_revenue DESC, customer_number
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue,
        COUNT(*) OVER () AS portfolio_customer_count
    FROM customer_performance
)
SELECT
    customer_number,
    transaction_rows,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(gross_profit, 2) AS gross_profit,
    ROUND(100.0 * gross_profit / NULLIF(total_revenue, 0), 4) AS gross_margin_pct,
    ROUND(100.0 * total_revenue / portfolio_revenue, 6) AS revenue_share_pct,
    ROUND(100.0 * cumulative_revenue / portfolio_revenue, 6) AS cumulative_revenue_pct,
    ROUND(100.0 * revenue_rank / portfolio_customer_count, 6) AS cumulative_customer_pct,
    revenue_rank
FROM ranked
ORDER BY revenue_rank;
