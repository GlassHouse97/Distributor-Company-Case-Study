# Revenue Quality & Customer Profitability Case Study

## Final Case Study Questions

This file defines the official scope of the project. The questions move from focused customer analysis to the broader financial trend, then close with one combined recommendation.

## Business Context

The company has grown over several years. Leadership wants to know where that growth is coming from, whether the customer base is overly concentrated, which inactive customers may be worth contacting, and whether sales growth is producing more gross profit.

## Reporting Rules

- Use `Period` as the official month for financial reporting.
- Read `Period` as `YYMM`; for example, `2201` means January 2022.
- Use `InvoiceDate` only when transaction timing is specifically relevant.
- Calculate gross profit as `SUM(Sales) - SUM(Cost)`.
- Calculate gross margin as total gross profit divided by total revenue.
- Keep returns, credits, and other documented edge cases in the analysis unless a question states otherwise.
- Explain all filters, thresholds, exclusions, and assumptions in the answer.

## What Each Answer Must Include

1. The SQL used to answer the question.
2. A compact result table with the main measures.
3. A chart when it makes the result easier to understand.
4. A direct written answer in plain language.
5. A short validation note covering important assumptions and reconciliation checks.

## Question 1: Customer Segment Profitability

### Main Question

Which customer segments bring in the most revenue and gross profit, and which segments earn stronger or weaker margins?

### Analysis

Summarize revenue, cost, gross profit, and gross margin by customer segment. Compare each segment's share of revenue with its share of gross profit so that large segments are not automatically treated as the best-performing segments.

### Minimum Output

- `CustomerClass`
- `CustomerClassDescription`
- `total_revenue`
- `gross_profit`
- `gross_margin_pct`
- `revenue_share_pct`
- `gross_profit_share_pct`

### Questions to Answer

- Which segments generate the most revenue and gross profit?
- Which large segments earn relatively strong or weak margins?
- Which segments contribute more profit than their revenue share would suggest?
- Which segments should the company protect, improve, expand, or monitor?

## Question 2: Revenue Concentration

### Main Question

Does the company depend too heavily on a small number of customers or customer segments?

### Analysis

Rank customers by recognized revenue and calculate revenue share and cumulative revenue share. Measure how many customers account for 50%, 80%, and 90% of revenue, then compare customer concentration with segment concentration.

### Customer-Level Output

- `CustomerNumber`
- `total_revenue`
- `revenue_share_pct`
- `cumulative_revenue_pct`
- `revenue_rank`

### Concentration Summary

- Revenue share from the top 1, 10, and 100 customers
- Customers needed to reach 50%, 80%, and 90% of revenue
- Revenue share by customer segment

### Questions to Answer

- How much revenue would be affected by losing one of the largest customers?
- Is concentration more significant at the customer or segment level?
- Does the long tail of smaller customers add useful diversification, extra operating work, or both?
- Which concentration measures should leadership continue to watch?

## Question 3: Customer Lifecycle and Retention Risk

### Main Question

Which customers appear inactive, and how much recent historical revenue is connected to those customers?

### Analysis

Use recognized `Period` activity to find each customer's latest positive-sale month. Define clear inactivity ranges relative to the latest period in the data. Count customers in each group and calculate a clearly defined historical revenue baseline for non-active customers.

### Customer-Level Output

- `CustomerNumber`
- `CustomerClassDescription`
- `last_active_period`
- `months_since_last_active`
- `churn_risk_bucket`
- `revenue_at_risk`

### Retention Summary

- Customer count and percentage by lifecycle group
- Historical revenue baseline by lifecycle group
- Lifecycle results by customer segment
- A prioritized outreach list

### Questions to Answer

- Which customers and segments show the most inactivity?
- Is the inactive population mostly high-value or low-value customers?
- Which customers are recent enough to justify immediate outreach?
- What prevents inactivity from being treated as confirmed churn?

## Question 4: Revenue and Margin Trends

### Main Question

Are revenue and gross profit growing over time, and is the company keeping more gross profit from each dollar of sales?

### Analysis

Summarize performance by recognized `Period`, then roll it up by year. Compare revenue, cost, gross profit, and gross margin over time. Review year-over-year growth, monthly changes, and seasonality before deciding whether the overall pattern looks healthy.

### Minimum Output

- `Period`
- `total_revenue`
- `total_cost`
- `gross_profit`
- `gross_margin_pct`

### Questions to Answer

- Is revenue growing, declining, or staying flat?
- Is gross profit growing faster or slower than revenue?
- Is gross margin improving or weakening?
- Are there seasonal peaks or unusual reporting periods?
- Does the historical pattern look healthy, and what can the data not tell us about the future?

## Final Strategic Synthesis

### Main Question

What should leadership focus on next based on all four analyses?

### Required Synthesis

Connect the segment, concentration, retention, and financial-trend findings into one practical recommendation. Do not present the four answers as unrelated observations.

### Final Output

- Three to five evidence-backed findings
- Three prioritized recommendations
- The expected benefit of each recommendation
- Important limitations and measures to keep watching
- A short conclusion suitable for a hiring manager or business reader

## Outside the Current Scope

The following topics are possible future extensions, but they are not required for this version of the case study:

- Product assortment optimization
- Sales-representative scoring
- Geographic territory design
- Demand forecasting
- Customer lifetime value modeling
- Predictive churn modeling
