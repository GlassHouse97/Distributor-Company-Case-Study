# Analysis Outputs

This folder contains compact result tables created from the final SQLite database. The 3.7-million-row transaction table stays in SQLite; these files contain only the results needed to review the case study.

| Prefix | Question | Contents |
| --- | --- | --- |
| `01_` | Customer segment profitability | Segment revenue, gross profit, margin, growth, validation, and summary metrics |
| `02_` | Revenue concentration | Ranked customers, concentration thresholds, segment comparison, validation, and summary metrics |
| `03_` | Customer lifecycle and retention | Lifecycle results, retention summary, segment risk, outreach priorities, validation, and summary metrics |
| `04_` | Revenue and margin trends | Annual results, monthly results, seasonality, validation, and summary metrics |

Each question has its own `0X_analysis_summary.json` file. Every CSV and JSON file can be regenerated from the SQL and final database with the matching `scripts/analyze_qX.py` script.

The customer-level files for Questions 2 and 3 use stable labels such as `CUSTOMER_0001` instead of source customer numbers. The question scripts apply those labels automatically through `scripts/sanitize_public_outputs.py`.
