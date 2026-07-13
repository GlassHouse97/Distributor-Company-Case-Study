# Analysis Outputs

This folder contains small, reproducible result tables generated from the canonical SQLite database. They are suitable for spreadsheet review and portfolio publication; the 3.7-million-row transaction fact remains in SQLite.

| Prefix | Analysis | Contents |
| --- | --- | --- |
| `01_` | Revenue and margin trends | Annual, monthly, seasonality, validation, and summary outputs |
| `02_` | Segment profitability | Historical profitability, 2018–2024 growth, and validation |
| `03_` | Revenue concentration | Ranked customers, concentration summary, segment comparison, and validation |
| `04_` | Customer retention | Customer lifecycle, risk summary, segment risk, outreach priorities, and validation |

`02_04_analysis_summary.json` contains the compact derived metrics used by the portfolio deliverables. Every CSV can be regenerated from the SQL and canonical database with the analysis scripts in `scripts/`.

The three customer-level outputs use stable anonymized labels (`CUSTOMER_0001`, etc.) instead of source customer numbers. `scripts/analyze_q2_q4.py` applies this publication step automatically, and `scripts/sanitize_public_outputs.py` can apply it independently.
