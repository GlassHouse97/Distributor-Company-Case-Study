-- Question 4: customer count and revenue at risk by lifecycle bucket.

WITH parameters AS (
    SELECT MAX(per_year * 12 + per_month) AS latest_period_index
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
),
last_active AS (
    SELECT
        customer_number,
        MAX(CASE WHEN sales > 0 THEN per_year * 12 + per_month END) AS last_active_index,
        MAX(CASE WHEN sales > 0 THEN period END) AS last_active_period
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY customer_number
),
customer_baseline AS (
    SELECT
        l.customer_number,
        l.last_active_index,
        SUM(
            CASE
                WHEN (t.per_year * 12 + t.per_month)
                     BETWEEN l.last_active_index - 11 AND l.last_active_index
                THEN t.sales
                ELSE 0
            END
        ) AS trailing_12_month_revenue
    FROM last_active l
    JOIN total_sales t
      ON t.customer_number = l.customer_number
     AND t.period BETWEEN '1801' AND '2412'
    GROUP BY 1, 2
),
classified AS (
    SELECT
        b.customer_number,
        p.latest_period_index - b.last_active_index AS months_since_last_active,
        CASE
            WHEN b.last_active_index IS NULL THEN 'No Positive Sales'
            WHEN p.latest_period_index - b.last_active_index <= 3 THEN 'Active (0-3 months)'
            WHEN p.latest_period_index - b.last_active_index <= 6 THEN 'Watch (4-6 months)'
            WHEN p.latest_period_index - b.last_active_index <= 12 THEN 'At Risk (7-12 months)'
            ELSE 'Dormant (13+ months)'
        END AS churn_risk_bucket,
        MAX(b.trailing_12_month_revenue, 0) AS baseline_revenue,
        CASE
            WHEN b.last_active_index IS NULL
              OR p.latest_period_index - b.last_active_index <= 3
            THEN 0
            ELSE MAX(b.trailing_12_month_revenue, 0)
        END AS revenue_at_risk
    FROM customer_baseline b
    CROSS JOIN parameters p
),
bucket_summary AS (
    SELECT
        churn_risk_bucket,
        COUNT(*) AS customer_count,
        SUM(baseline_revenue) AS baseline_revenue,
        SUM(revenue_at_risk) AS revenue_at_risk,
        MIN(months_since_last_active) AS minimum_months_inactive,
        MAX(months_since_last_active) AS maximum_months_inactive
    FROM classified
    GROUP BY churn_risk_bucket
),
totals AS (
    SELECT
        SUM(customer_count) AS total_customers,
        SUM(revenue_at_risk) AS total_revenue_at_risk,
        (SELECT SUM(sales) FROM total_sales WHERE per_year = 2024) AS revenue_2024
    FROM bucket_summary
)
SELECT
    churn_risk_bucket,
    customer_count,
    ROUND(100.0 * customer_count / total_customers, 2) AS customer_pct,
    ROUND(baseline_revenue, 2) AS baseline_revenue,
    ROUND(revenue_at_risk, 2) AS revenue_at_risk,
    ROUND(100.0 * revenue_at_risk / NULLIF(total_revenue_at_risk, 0), 2) AS revenue_at_risk_share_pct,
    ROUND(100.0 * revenue_at_risk / revenue_2024, 2) AS revenue_at_risk_pct_of_2024_revenue,
    minimum_months_inactive,
    maximum_months_inactive
FROM bucket_summary
CROSS JOIN totals
ORDER BY
    CASE churn_risk_bucket
        WHEN 'Active (0-3 months)' THEN 1
        WHEN 'Watch (4-6 months)' THEN 2
        WHEN 'At Risk (7-12 months)' THEN 3
        WHEN 'Dormant (13+ months)' THEN 4
        ELSE 5
    END;
