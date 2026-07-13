-- Question 3: customer- and segment-level concentration summary.

WITH customers AS (
    SELECT customer_number, SUM(sales) AS revenue
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY customer_number
),
customer_ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY revenue DESC, customer_number) AS revenue_rank,
        SUM(revenue) OVER () AS portfolio_revenue,
        SUM(revenue) OVER (
            ORDER BY revenue DESC, customer_number
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue,
        COUNT(*) OVER () AS customer_count
    FROM customers
),
segments AS (
    SELECT
        transaction_customer_class AS customer_class,
        SUM(sales) AS revenue
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY 1
),
segment_ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY revenue DESC, customer_class) AS segment_rank,
        SUM(revenue) OVER () AS portfolio_revenue,
        SUM(revenue) OVER (
            ORDER BY revenue DESC, customer_class
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue
    FROM segments
),
customer_metrics AS (
    SELECT
        MAX(customer_count) AS total_customers,
        SUM(CASE WHEN revenue > 0 THEN 1 ELSE 0 END) AS positive_revenue_customers,
        SUM(CASE WHEN revenue = 0 THEN 1 ELSE 0 END) AS zero_revenue_customers,
        SUM(CASE WHEN revenue < 0 THEN 1 ELSE 0 END) AS negative_revenue_customers,
        100.0 * SUM(CASE WHEN revenue_rank <= 1 THEN revenue ELSE 0 END) / MAX(portfolio_revenue) AS top_1_share_pct,
        100.0 * SUM(CASE WHEN revenue_rank <= 10 THEN revenue ELSE 0 END) / MAX(portfolio_revenue) AS top_10_share_pct,
        100.0 * SUM(CASE WHEN revenue_rank <= 100 THEN revenue ELSE 0 END) / MAX(portfolio_revenue) AS top_100_share_pct,
        MIN(CASE WHEN cumulative_revenue / portfolio_revenue >= 0.50 THEN revenue_rank END) AS customers_to_50_pct,
        MIN(CASE WHEN cumulative_revenue / portfolio_revenue >= 0.80 THEN revenue_rank END) AS customers_to_80_pct,
        MIN(CASE WHEN cumulative_revenue / portfolio_revenue >= 0.90 THEN revenue_rank END) AS customers_to_90_pct,
        SUM(POWER(100.0 * revenue / portfolio_revenue, 2)) AS customer_hhi
    FROM customer_ranked
),
segment_metrics AS (
    SELECT
        COUNT(*) AS active_segments,
        100.0 * SUM(CASE WHEN segment_rank <= 1 THEN revenue ELSE 0 END) / MAX(portfolio_revenue) AS top_1_segment_share_pct,
        100.0 * SUM(CASE WHEN segment_rank <= 3 THEN revenue ELSE 0 END) / MAX(portfolio_revenue) AS top_3_segment_share_pct,
        100.0 * SUM(CASE WHEN segment_rank <= 5 THEN revenue ELSE 0 END) / MAX(portfolio_revenue) AS top_5_segment_share_pct,
        MIN(CASE WHEN cumulative_revenue / portfolio_revenue >= 0.80 THEN segment_rank END) AS segments_to_80_pct,
        SUM(POWER(100.0 * revenue / portfolio_revenue, 2)) AS segment_hhi
    FROM segment_ranked
)
SELECT
    total_customers,
    positive_revenue_customers,
    zero_revenue_customers,
    negative_revenue_customers,
    ROUND(top_1_share_pct, 4) AS top_1_customer_share_pct,
    ROUND(top_10_share_pct, 4) AS top_10_customer_share_pct,
    ROUND(top_100_share_pct, 4) AS top_100_customer_share_pct,
    customers_to_50_pct,
    ROUND(100.0 * customers_to_50_pct / total_customers, 2) AS customer_pct_to_50_revenue,
    customers_to_80_pct,
    ROUND(100.0 * customers_to_80_pct / total_customers, 2) AS customer_pct_to_80_revenue,
    customers_to_90_pct,
    ROUND(100.0 * customers_to_90_pct / total_customers, 2) AS customer_pct_to_90_revenue,
    ROUND(customer_hhi, 2) AS customer_hhi,
    active_segments,
    ROUND(top_1_segment_share_pct, 2) AS top_1_segment_share_pct,
    ROUND(top_3_segment_share_pct, 2) AS top_3_segment_share_pct,
    ROUND(top_5_segment_share_pct, 2) AS top_5_segment_share_pct,
    segments_to_80_pct,
    ROUND(segment_hhi, 2) AS segment_hhi
FROM customer_metrics
CROSS JOIN segment_metrics;
