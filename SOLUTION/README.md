# Solution

This folder contains the author's analysis for the four canonical case-study questions and the final strategic synthesis defined in [`CASE_STUDY_QUESTIONS.md`](../CASE_STUDY_QUESTIONS.md).

## Solution Structure

| File | Purpose | Status |
| --- | --- | --- |
| `EXECUTIVE_SUMMARY.md` | Concise hiring-manager narrative and recommendations | Complete |
| `01_revenue_margin_trends.md` | Recognized revenue, gross profit, and margin trends | Complete |
| `02_segment_profitability.md` | Customer-segment scale and profitability | Complete |
| `03_revenue_concentration.md` | Customer- and segment-level concentration risk | Complete |
| `04_customer_retention.md` | Inactivity, churn-risk categories, and revenue at risk | Complete |
| `05_strategic_synthesis.md` | Integrated findings and recommendations | Complete |
| `sql/` | Reproducible SQL queries | Questions 1–4 validated |
| `visualizations/` | Final analytical charts | Questions 1–4 complete |

The executive summary is the primary non-technical entry point. The question-level files provide supporting detail, while `sql/` provides the reproducible analyst path.

## Standard for Each Analysis

Each solution should contain:

1. The executive question.
2. The analytical method and key assumptions.
3. A link to the corresponding SQL query.
4. The principal results and validation checks.
5. A business interpretation written in plain language.
6. A final visualization when it materially improves understanding.

The analysis documents should report findings without exposing confidential or identifying source data.

## Regenerate the Analysis

After building the canonical SQLite database from the project root:

```bash
python scripts/analyze_q1.py
python scripts/analyze_q2_q4.py
```

The commands recreate the public result tables, validation evidence, summary metadata, and visualizations used in the written answers.
