-- Question 1 supporting output: average month-of-year performance.

WITH monthly_performance AS (
    SELECT
        per_year,
        per_month,
        SUM(sales) AS total_revenue,
        SUM(gross_profit) AS gross_profit
    FROM total_sales
    WHERE period BETWEEN '1801' AND '2412'
    GROUP BY per_year, per_month
),
annual_performance AS (
    SELECT
        per_year,
        SUM(total_revenue) AS annual_revenue,
        SUM(gross_profit) AS annual_gross_profit
    FROM monthly_performance
    GROUP BY per_year
),
monthly_shares AS (
    SELECT
        monthly.per_month,
        monthly.total_revenue,
        monthly.gross_profit,
        100.0 * monthly.total_revenue / annual.annual_revenue AS revenue_share_pct,
        100.0 * monthly.gross_profit / annual.annual_gross_profit AS gross_profit_share_pct
    FROM monthly_performance AS monthly
    INNER JOIN annual_performance AS annual
        ON monthly.per_year = annual.per_year
)
SELECT
    per_month,
    CASE per_month
        WHEN 1 THEN 'January'
        WHEN 2 THEN 'February'
        WHEN 3 THEN 'March'
        WHEN 4 THEN 'April'
        WHEN 5 THEN 'May'
        WHEN 6 THEN 'June'
        WHEN 7 THEN 'July'
        WHEN 8 THEN 'August'
        WHEN 9 THEN 'September'
        WHEN 10 THEN 'October'
        WHEN 11 THEN 'November'
        WHEN 12 THEN 'December'
    END AS month_name,
    ROUND(AVG(total_revenue), 2) AS average_monthly_revenue,
    ROUND(AVG(gross_profit), 2) AS average_monthly_gross_profit,
    ROUND(AVG(revenue_share_pct), 2) AS average_annual_revenue_share_pct,
    ROUND(AVG(gross_profit_share_pct), 2) AS average_annual_gross_profit_share_pct
FROM monthly_shares
GROUP BY per_month
ORDER BY per_month;
