# 4. Revenue and Margin Trends

## Executive Question

Are revenue and gross profit growing over time, and is the company keeping more gross profit from each dollar of sales?

## Executive Answer

Yes. Revenue increased every year from 2018 through 2024, rising from **$79.4 million to $131.0 million**. Gross profit rose faster, from **$15.2 million to $28.8 million**, and gross margin improved from **19.15% to 22.01%**.

The simplest reading is that the company sold more and kept a slightly larger share of each sales dollar as gross profit. Growth slowed to about 6% in 2023 and 2024 after stronger years in 2021 and 2022, but gross profit continued to grow faster than revenue. Nothing in the historical trend suggests that recent growth came at the expense of gross margin.

## Key Findings

- Revenue grew **65.0%** from 2018 to 2024, equal to an **8.7% compound annual growth rate**.
- Gross profit grew **89.6%**, equal to an **11.3% compound annual growth rate**.
- Cost grew **59.2%**, slower than both revenue and gross profit.
- Gross margin improved by **2.86 percentage points**. It increased in five of the six year-over-year comparisons; the only decline was 0.05 percentage point in 2021.
- Revenue growth was strongest in **2021 at 16.65%**. In 2024, revenue grew **6.05%** and gross profit grew **7.28%**.
- The fourth quarter contributes an average **31.43% of annual revenue**. December contributes **11.70%**, while February is the lightest month at **6.40%**.
- Twelve of 72 monthly year-over-year comparisons were negative. The declines were scattered rather than part of one long downturn.

![Annual recognized revenue composition and gross margin trend](visualizations/04_revenue_margin_trends.svg)

## Annual Results

| Year | Revenue | Cost | Gross Profit | Gross Margin | Revenue YoY | Gross Profit YoY | Margin Change |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2018 | $79.4M | $64.2M | $15.2M | 19.15% | - | - | - |
| 2019 | $82.9M | $66.0M | $17.0M | 20.47% | 4.49% | 11.65% | +1.31 pp |
| 2020 | $88.3M | $69.4M | $18.9M | 21.43% | 6.44% | 11.47% | +0.97 pp |
| 2021 | $103.0M | $81.0M | $22.0M | 21.39% | 16.65% | 16.40% | -0.05 pp |
| 2022 | $116.4M | $91.3M | $25.1M | 21.56% | 12.99% | 13.88% | +0.17 pp |
| 2023 | $123.5M | $96.6M | $26.9M | 21.76% | 6.15% | 7.15% | +0.20 pp |
| 2024 | $131.0M | $102.1M | $28.8M | 22.01% | 6.05% | 7.28% | +0.25 pp |

## Business Interpretation

The company did more than increase sales. Gross profit grew faster than revenue, and gross margin ended almost three percentage points above where it started. In plain terms, the company kept more gross profit from each dollar of revenue in 2024 than it did in 2018.

The recent slowdown is worth watching, but it is not automatically a warning sign. Revenue grew about 6% in both 2023 and 2024, compared with double-digit growth in 2021 and 2022. At the same time, gross profit still grew faster than revenue and margin still improved. That looks more like growth settling into a slower pace than a loss of profitability.

The fourth quarter is consistently the busiest part of the year. Staffing, purchasing, inventory, and cash planning should account for that pattern instead of assuming every month will contribute the same amount.

Based on the data available, the historical growth pattern looks healthy through 2024. This is not a forecast. The dataset does not include market conditions, inflation, detailed pricing decisions, or operating expenses, so it cannot explain every cause or predict what happens next.

## Method and Assumptions

- `Period` is the financial-reporting authority and is interpreted as YYMM.
- The trend window is `1801` through `2412`, providing seven complete years and 84 consecutive months.
- Four adjustment rows recognized in `1712` remain in the database but are excluded because 2017 does not contain a complete year.
- Revenue is `SUM(Sales)`, cost is `SUM(Cost)`, gross profit is `SUM(Sales - Cost)`, and gross margin is total gross profit divided by total revenue.
- Returns, credits, zero-sales activity, zero-cost activity, and exact-duplicate candidates remain in the analysis.
- Year-over-year comparisons use recognized accounting periods rather than invoice dates or order-entry dates.

## Reproducible Queries and Outputs

| Purpose | SQL | Result table |
| --- | --- | --- |
| Annual trend and year-over-year growth | [`04_revenue_margin_trends.sql`](sql/04_revenue_margin_trends.sql) | [`04_annual_revenue_margin.csv`](outputs/04_annual_revenue_margin.csv) |
| Monthly trend and year-over-year comparisons | [`04_monthly_revenue_margin.sql`](sql/04_monthly_revenue_margin.sql) | [`04_monthly_revenue_margin.csv`](outputs/04_monthly_revenue_margin.csv) |
| Month-of-year seasonality | [`04_revenue_seasonality.sql`](sql/04_revenue_seasonality.sql) | [`04_revenue_seasonality.csv`](outputs/04_revenue_seasonality.csv) |
| Scope and formula reconciliation | [`04_validation_checks.sql`](sql/04_validation_checks.sql) | [`04_validation_checks.csv`](outputs/04_validation_checks.csv) |

Regenerate the outputs and chart with:

```bash
python scripts/analyze_q4.py
```

## Validation Notes

All Question 4 checks pass:

- 7 complete reporting years and 84 unique reporting months.
- 3,714,620 in-scope transaction rows.
- All seven years contain exactly 12 recognized periods.
- Stored gross profit reconciles to `Sales - Cost` within one cent.
- Annual, monthly, and seasonality tables use the same complete-year window.
- The four partial-period 2017 rows are identified and excluded only from this trend analysis.
