# Visualizations

This folder contains the final charts referenced by the solution documents. They avoid customer names and are safe for the intended public portfolio package.

| File | Analysis | Status |
| --- | --- | --- |
| `01_revenue_margin_trends.svg` | Annual recognized revenue composition and gross-margin trend | Complete |
| `01_revenue_margin_trends.png` | Word-report rendering of the annual revenue and margin trend | Complete |
| `02_segment_profitability.png` | Segment revenue share compared with gross-profit share | Complete |
| `03_customer_concentration.png` | Customer cumulative revenue concentration | Complete |
| `04_retention_risk.png` | Lifecycle mix and trailing revenue baseline at risk | Complete |

The GitHub-native Q1 SVG is regenerated with `scripts/analyze_q1.py`; its Word-report PNG is generated with `scripts/build_business_report.py`. The remaining charts are regenerated with `scripts/analyze_q2_q4.py`.
