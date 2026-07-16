-- Question 1 validation checks.

WITH scoped AS (
    SELECT *
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
),
segments AS (
    SELECT
        transaction_customer_class AS customer_class,
        SUM(sales) AS revenue,
        SUM(gross_profit) AS gross_profit
    FROM scoped
    GROUP BY 1
),
checks AS (
    SELECT 'active_segment_count' AS check_name,
           CAST(COUNT(*) AS TEXT) AS actual_value,
           '64' AS expected_value,
           CASE WHEN COUNT(*) = 64 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM segments

    UNION ALL

    SELECT 'segment_revenue_reconciliation',
           printf('%.2f', SUM(revenue) - (SELECT SUM(sales) FROM scoped)),
           '0.00',
           CASE WHEN ABS(SUM(revenue) - (SELECT SUM(sales) FROM scoped)) < 0.01 THEN 'PASS' ELSE 'FAIL' END
    FROM segments

    UNION ALL

    SELECT 'segment_gross_profit_reconciliation',
           printf('%.2f', SUM(gross_profit) - (SELECT SUM(gross_profit) FROM scoped)),
           '0.00',
           CASE WHEN ABS(SUM(gross_profit) - (SELECT SUM(gross_profit) FROM scoped)) < 0.01 THEN 'PASS' ELSE 'FAIL' END
    FROM segments

    UNION ALL

    SELECT 'unmapped_transaction_class_rows',
           CAST(SUM(is_unmapped_customer_class) AS TEXT),
           '0',
           CASE WHEN SUM(is_unmapped_customer_class) = 0 THEN 'PASS' ELSE 'FAIL' END
    FROM scoped

    UNION ALL

    SELECT 'complete_reporting_months',
           CAST(COUNT(DISTINCT period) AS TEXT),
           '84',
           CASE WHEN COUNT(DISTINCT period) = 84 THEN 'PASS' ELSE 'FAIL' END
    FROM scoped
)
SELECT check_name, actual_value, expected_value, status
FROM checks
ORDER BY check_name;
