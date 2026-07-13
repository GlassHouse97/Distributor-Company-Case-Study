-- Question 1 validation checks.
-- These checks reconcile the 2018-2024 complete-year reporting window back to
-- the canonical transaction table without removing returns or adjustments.

WITH scoped_transactions AS (
    SELECT *
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
),
annual_totals AS (
    SELECT
        per_year,
        COUNT(DISTINCT period) AS month_count,
        SUM(sales) AS revenue,
        SUM(cost) AS cost,
        SUM(gross_profit) AS gross_profit
    FROM scoped_transactions
    GROUP BY per_year
),
checks AS (
    SELECT
        'complete_year_count' AS check_name,
        CAST(COUNT(*) AS TEXT) AS actual_value,
        '7' AS expected_value,
        CASE WHEN COUNT(*) = 7 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM annual_totals

    UNION ALL

    SELECT
        'complete_month_count',
        CAST(COUNT(DISTINCT period) AS TEXT),
        '84',
        CASE WHEN COUNT(DISTINCT period) = 84 THEN 'PASS' ELSE 'FAIL' END
    FROM scoped_transactions

    UNION ALL

    SELECT
        'transaction_row_count',
        CAST(COUNT(*) AS TEXT),
        '3714620',
        CASE WHEN COUNT(*) = 3714620 THEN 'PASS' ELSE 'FAIL' END
    FROM scoped_transactions

    UNION ALL

    SELECT
        'gross_profit_formula_difference',
        printf('%.6f', SUM(sales - cost) - SUM(gross_profit)),
        '0.000000',
        CASE
            WHEN ABS(SUM(sales - cost) - SUM(gross_profit)) < 0.01
            THEN 'PASS'
            ELSE 'FAIL'
        END
    FROM scoped_transactions

    UNION ALL

    SELECT
        'years_with_12_months',
        CAST(SUM(CASE WHEN month_count = 12 THEN 1 ELSE 0 END) AS TEXT),
        '7',
        CASE
            WHEN SUM(CASE WHEN month_count = 12 THEN 1 ELSE 0 END) = 7
            THEN 'PASS'
            ELSE 'FAIL'
        END
    FROM annual_totals

    UNION ALL

    SELECT
        'partial_2017_rows_excluded',
        CAST(COUNT(*) AS TEXT),
        '4',
        CASE WHEN COUNT(*) = 4 THEN 'PASS' ELSE 'FAIL' END
    FROM total_sales
    WHERE period < '1801'
)
SELECT check_name, actual_value, expected_value, status
FROM checks
ORDER BY check_name;
