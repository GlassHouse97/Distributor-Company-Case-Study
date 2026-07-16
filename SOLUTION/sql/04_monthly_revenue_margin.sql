-- Question 4 supporting output: monthly results and year-over-year comparisons.

WITH monthly_performance AS (
    SELECT
        period,
        period_date,
        per_year,
        per_month,
        per_quarter,
        COUNT(*) AS transaction_rows,
        SUM(sales) AS total_revenue,
        SUM(cost) AS total_cost,
        SUM(gross_profit) AS gross_profit,
        100.0 * SUM(gross_profit) / NULLIF(SUM(sales), 0) AS gross_margin_pct
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY period, period_date, per_year, per_month, per_quarter
),
monthly_comparison AS (
    SELECT
        *,
        LAG(total_revenue, 12) OVER (ORDER BY period) AS prior_year_revenue,
        LAG(gross_profit, 12) OVER (ORDER BY period) AS prior_year_gross_profit,
        LAG(gross_margin_pct, 12) OVER (ORDER BY period) AS prior_year_margin_pct
    FROM monthly_performance
)
SELECT
    period,
    period_date,
    per_year,
    per_month,
    per_quarter,
    transaction_rows,
    ROUND(total_revenue, 2) AS total_revenue,
    ROUND(total_cost, 2) AS total_cost,
    ROUND(gross_profit, 2) AS gross_profit,
    ROUND(gross_margin_pct, 4) AS gross_margin_pct,
    ROUND(
        100.0 * (total_revenue / NULLIF(prior_year_revenue, 0) - 1),
        2
    ) AS revenue_yoy_pct,
    ROUND(
        100.0 * (gross_profit / NULLIF(prior_year_gross_profit, 0) - 1),
        2
    ) AS gross_profit_yoy_pct,
    ROUND(gross_margin_pct - prior_year_margin_pct, 2) AS margin_change_pp
FROM monthly_comparison
ORDER BY period;
