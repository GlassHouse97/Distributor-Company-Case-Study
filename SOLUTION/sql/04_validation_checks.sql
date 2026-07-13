-- Question 4 validation checks.

WITH parameters AS (
    SELECT MAX(per_year * 12 + per_month) AS latest_period_index, MAX(period) AS latest_period
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
),
last_active AS (
    SELECT
        customer_number,
        MAX(CASE WHEN sales > 0 THEN per_year * 12 + per_month END) AS last_active_index
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
),
checks AS (
    SELECT 'latest_recognized_period' AS check_name,
           latest_period AS actual_value,
           '2412' AS expected_value,
           CASE WHEN latest_period = '2412' THEN 'PASS' ELSE 'FAIL' END AS status
    FROM parameters

    UNION ALL

    SELECT 'lifecycle_customer_count',
           CAST(COUNT(*) AS TEXT),
           '3230',
           CASE WHEN COUNT(*) = 3230 THEN 'PASS' ELSE 'FAIL' END
    FROM classified

    UNION ALL

    SELECT 'bucket_customer_reconciliation',
           CAST(SUM(CASE WHEN churn_risk_bucket IS NOT NULL THEN 1 ELSE 0 END) AS TEXT),
           '3230',
           CASE WHEN SUM(CASE WHEN churn_risk_bucket IS NOT NULL THEN 1 ELSE 0 END) = 3230 THEN 'PASS' ELSE 'FAIL' END
    FROM classified

    UNION ALL

    SELECT 'active_revenue_at_risk',
           printf('%.2f', SUM(CASE WHEN churn_risk_bucket = 'Active' THEN revenue_at_risk ELSE 0 END)),
           '0.00',
           CASE WHEN ABS(SUM(CASE WHEN churn_risk_bucket = 'Active' THEN revenue_at_risk ELSE 0 END)) < 0.01 THEN 'PASS' ELSE 'FAIL' END
    FROM classified

    UNION ALL

    SELECT 'nonnegative_revenue_at_risk',
           CAST(SUM(revenue_at_risk < 0) AS TEXT),
           '0',
           CASE WHEN SUM(revenue_at_risk < 0) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM classified

    UNION ALL

    SELECT 'no_positive_sales_customer_count',
           CAST(SUM(churn_risk_bucket = 'No Positive Sales') AS TEXT),
           '21',
           CASE WHEN SUM(churn_risk_bucket = 'No Positive Sales') = 21 THEN 'PASS' ELSE 'FAIL' END
    FROM classified
)
SELECT check_name, actual_value, expected_value, status
FROM checks
ORDER BY check_name;
