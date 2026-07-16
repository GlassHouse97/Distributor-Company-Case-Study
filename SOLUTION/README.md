# Complete Case Study Solution

Everything produced for the finished case study is collected in this folder: the executive summary, detailed question answers, downloadable report and workbook, SQL, result tables, and visuals.

## Start Here

- **Read:** [`EXECUTIVE_SUMMARY.md`](EXECUTIVE_SUMMARY.md) presents the business story, findings, visuals, and recommendations in the browser.
- **Download:** [`Distributor_Case_Study_Report.docx`](Distributor_Case_Study_Report.docx) is the polished business report.
- **Explore:** [`Distributor_Case_Study_Analysis.xlsx`](Distributor_Case_Study_Analysis.xlsx) contains the filterable analyst workbook.

## Detailed Answers

| Question | Analysis |
| --- | --- |
| 1. Revenue and margin trends | [`01_revenue_margin_trends.md`](01_revenue_margin_trends.md) |
| 2. Segment profitability | [`02_segment_profitability.md`](02_segment_profitability.md) |
| 3. Revenue concentration | [`03_revenue_concentration.md`](03_revenue_concentration.md) |
| 4. Customer retention | [`04_customer_retention.md`](04_customer_retention.md) |
| Final strategic synthesis | [`05_strategic_synthesis.md`](05_strategic_synthesis.md) |

The approved project scope is in [`../CASE_STUDY_QUESTIONS.md`](../CASE_STUDY_QUESTIONS.md).

## Supporting Evidence

- [`sql/`](sql/) contains every reproducible SQLite query.
- [`outputs/`](outputs/) contains compact CSV result tables and validation checks.
- [`visualizations/`](visualizations/) contains the final charts used by the written analysis.

## Regenerate the Solution

After building the final SQLite database from the repository root:

```bash
python scripts/analyze_q1.py
python scripts/analyze_q2_q4.py
python scripts/build_business_report.py
```

These commands regenerate the analysis outputs, visuals, and Word report. The included Excel workbook is a finished portfolio download assembled from the same published CSV outputs; it is not part of the required analytical pipeline.
