-- Question 3: retention risk by the customer's last active historical class.

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
        COALESCE(c.customer_class, 'Unmapped') AS customer_class,
        COALESCE(c.customer_class_description, 'Unmapped') AS customer_class_description,
        CASE
            WHEN b.last_active_index IS NULL THEN 'No Positive Sales'
            WHEN p.latest_period_index - b.last_active_index <= 3 THEN 'Active'
            WHEN p.latest_period_index - b.last_active_index <= 6 THEN 'Watch'
            WHEN p.latest_period_index - b.last_active_index <= 12 THEN 'At Risk'
            ELSE 'Dormant'
        END AS churn_risk_bucket,
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
),
segment_summary AS (
    SELECT
        customer_class,
        customer_class_description,
        COUNT(*) AS total_customers,
        SUM(churn_risk_bucket = 'Active') AS active_customers,
        SUM(churn_risk_bucket = 'Watch') AS watch_customers,
        SUM(churn_risk_bucket = 'At Risk') AS at_risk_customers,
        SUM(churn_risk_bucket = 'Dormant') AS dormant_customers,
        SUM(churn_risk_bucket = 'No Positive Sales') AS no_positive_sales_customers,
        SUM(CASE WHEN churn_risk_bucket IN ('Watch', 'At Risk', 'Dormant') THEN 1 ELSE 0 END) AS risky_customers,
        SUM(revenue_at_risk) AS revenue_at_risk
    FROM classified
    GROUP BY 1, 2
),
totals AS (
    SELECT SUM(revenue_at_risk) AS total_revenue_at_risk
    FROM segment_summary
)
SELECT
    customer_class,
    customer_class_description,
    total_customers,
    active_customers,
    watch_customers,
    at_risk_customers,
    dormant_customers,
    no_positive_sales_customers,
    risky_customers,
    ROUND(100.0 * risky_customers / total_customers, 2) AS risky_customer_pct,
    ROUND(revenue_at_risk, 2) AS revenue_at_risk,
    ROUND(100.0 * revenue_at_risk / total_revenue_at_risk, 2) AS revenue_at_risk_share_pct
FROM segment_summary
CROSS JOIN totals
ORDER BY revenue_at_risk DESC, customer_class;
