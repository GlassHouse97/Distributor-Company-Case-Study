-- Question 4: annual recognized-revenue and gross-margin trends.
-- Period is the reporting authority. The four adjustment rows in Period 1712
-- are retained in total_sales but excluded here because 2017 is not a complete
-- reporting year. The analytical window contains all 84 months from 2018-2024.

WITH annual_performance AS (
    SELECT
        per_year,
        COUNT(DISTINCT period) AS reported_months,
        COUNT(*) AS transaction_rows,
        SUM(sales) AS total_revenue,
        SUM(cost) AS total_cost,
        SUM(gross_profit) AS gross_profit,
        100.0 * SUM(gross_profit) / NULLIF(SUM(sales), 0) AS gross_margin_pct
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY per_year
),
annual_comparison AS (
    SELECT
        *,
        LAG(total_revenue) OVER (ORDER BY per_year) AS prior_year_revenue,
        LAG(gross_profit) OVER (ORDER BY per_year) AS prior_year_gross_profit,
        LAG(gross_margin_pct) OVER (ORDER BY per_year) AS prior_year_margin_pct
    FROM annual_performance
)
SELECT
    per_year,
    reported_months,
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
FROM annual_comparison
ORDER BY per_year;
