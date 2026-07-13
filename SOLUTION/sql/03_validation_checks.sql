-- Question 3 validation checks.

WITH customer_performance AS (
    SELECT customer_number, SUM(sales) AS revenue
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY customer_number
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (ORDER BY revenue DESC, customer_number) AS revenue_rank,
        SUM(revenue) OVER () AS portfolio_revenue,
        SUM(revenue) OVER (
            ORDER BY revenue DESC, customer_number
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS cumulative_revenue
    FROM customer_performance
),
checks AS (
    SELECT 'customer_count' AS check_name,
           CAST(COUNT(*) AS TEXT) AS actual_value,
           '3230' AS expected_value,
           CASE WHEN COUNT(*) = 3230 THEN 'PASS' ELSE 'FAIL' END AS status
    FROM ranked

    UNION ALL

    SELECT 'customer_revenue_reconciliation',
           printf('%.2f', SUM(revenue) - MAX(portfolio_revenue)),
           '0.00',
           CASE WHEN ABS(SUM(revenue) - MAX(portfolio_revenue)) < 0.01 THEN 'PASS' ELSE 'FAIL' END
    FROM ranked

    UNION ALL

    SELECT 'final_cumulative_revenue_pct',
           printf('%.4f', 100.0 * MAX(CASE WHEN revenue_rank = 3230 THEN cumulative_revenue END) / MAX(portfolio_revenue)),
           '100.0000',
           CASE WHEN ABS(100.0 * MAX(CASE WHEN revenue_rank = 3230 THEN cumulative_revenue END) / MAX(portfolio_revenue) - 100.0) < 0.0001 THEN 'PASS' ELSE 'FAIL' END
    FROM ranked

    UNION ALL

    SELECT 'unique_customer_ranks',
           CAST(COUNT(DISTINCT revenue_rank) AS TEXT),
           '3230',
           CASE WHEN COUNT(DISTINCT revenue_rank) = 3230 THEN 'PASS' ELSE 'FAIL' END
    FROM ranked

    UNION ALL

    SELECT 'top_customer_below_two_pct',
           printf('%.4f', 100.0 * MAX(CASE WHEN revenue_rank = 1 THEN revenue END) / MAX(portfolio_revenue)),
           '<2.0000',
           CASE WHEN 100.0 * MAX(CASE WHEN revenue_rank = 1 THEN revenue END) / MAX(portfolio_revenue) < 2.0 THEN 'PASS' ELSE 'FAIL' END
    FROM ranked
)
SELECT check_name, actual_value, expected_value, status
FROM checks
ORDER BY check_name;
