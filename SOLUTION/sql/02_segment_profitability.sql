-- Question 2: customer-segment scale and profitability.
-- Uses historical customer class stored on each transaction and the same
-- complete-year reporting window as Question 1.

WITH segment_performance AS (
    SELECT
        transaction_customer_class AS customer_class,
        COALESCE(transaction_class_description, 'Unmapped') AS customer_class_description,
        COUNT(*) AS transaction_rows,
        COUNT(DISTINCT customer_number) AS customer_count,
        SUM(sales) AS total_revenue,
        SUM(cost) AS total_cost,
        SUM(gross_profit) AS gross_profit
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY 1, 2
),
portfolio_totals AS (
    SELECT
        SUM(total_revenue) AS portfolio_revenue,
        SUM(gross_profit) AS portfolio_gross_profit
    FROM segment_performance
),
ranked AS (
    SELECT
        s.*,
        p.portfolio_revenue,
        p.portfolio_gross_profit,
        ROW_NUMBER() OVER (ORDER BY s.total_revenue DESC, s.customer_class) AS revenue_rank,
        ROW_NUMBER() OVER (ORDER BY s.gross_profit DESC, s.customer_class) AS gross_profit_rank,
        ROW_NUMBER() OVER (
            ORDER BY s.gross_profit / NULLIF(s.total_revenue, 0) DESC, s.customer_class
        ) AS margin_rank
    FROM segment_performance s
    CROSS JOIN portfolio_totals p
)
SELECT
    customer_class,
    customer_class_description,
    transaction_rows,
    customer_count,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(total_cost, 2) AS total_cost,
    ROUND(gross_profit, 2) AS gross_profit,
    ROUND(100.0 * gross_profit / NULLIF(total_revenue, 0), 4) AS gross_margin_pct,
    ROUND(100.0 * total_revenue / portfolio_revenue, 4) AS revenue_share_pct,
    ROUND(100.0 * gross_profit / portfolio_gross_profit, 4) AS gross_profit_share_pct,
    revenue_rank,
    gross_profit_rank,
    margin_rank
FROM ranked
ORDER BY revenue_rank;
