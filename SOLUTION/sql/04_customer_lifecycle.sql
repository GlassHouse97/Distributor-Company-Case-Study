-- Question 4: customer inactivity and revenue at risk.
-- Positive sales define purchase activity. Revenue at risk is net recognized
-- revenue in the 12 months ending with the customer's last positive-sale
-- period, floored at zero and assigned only to non-active customers.

WITH parameters AS (
    SELECT
        MAX(per_year * 12 + per_month) AS latest_period_index,
        MAX(period) AS latest_period
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
class_candidates AS (
    SELECT
        l.customer_number,
        t.transaction_customer_class AS customer_class,
        COALESCE(t.transaction_class_description, 'Unmapped') AS customer_class_description,
        SUM(t.sales) AS class_revenue
    FROM last_active l
    JOIN total_sales t
      ON t.customer_number = l.customer_number
     AND t.period = l.last_active_period
    WHERE t.sales > 0
    GROUP BY 1, 2, 3
),
last_active_class AS (
    SELECT customer_number, customer_class, customer_class_description
    FROM (
        SELECT
            *,
            ROW_NUMBER() OVER (
                PARTITION BY customer_number
                ORDER BY class_revenue DESC, customer_class
            ) AS class_rank
        FROM class_candidates
    )
    WHERE class_rank = 1
),
customer_baseline AS (
    SELECT
        l.customer_number,
        l.last_active_index,
        l.last_active_period,
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
    GROUP BY 1, 2, 3
),
classified AS (
    SELECT
        b.customer_number,
        COALESCE(c.customer_class, 'Unmapped') AS customer_class,
        COALESCE(c.customer_class_description, 'Unmapped') AS customer_class_description,
        b.last_active_period,
        p.latest_period,
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
    LEFT JOIN last_active_class c
      ON c.customer_number = b.customer_number
)
SELECT
    customer_number,
    customer_class,
    customer_class_description,
    last_active_period,
    latest_period,
    months_since_last_active,
    churn_risk_bucket,
    ROUND(baseline_revenue, 2) AS baseline_revenue,
    ROUND(revenue_at_risk, 2) AS revenue_at_risk
FROM classified
ORDER BY
    CASE churn_risk_bucket
        WHEN 'At Risk (7-12 months)' THEN 1
        WHEN 'Watch (4-6 months)' THEN 2
        WHEN 'Dormant (13+ months)' THEN 3
        WHEN 'Active (0-3 months)' THEN 4
        ELSE 5
    END,
    revenue_at_risk DESC,
    customer_number;
