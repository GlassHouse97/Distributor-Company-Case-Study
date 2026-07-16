# Script Guide

Every Python file in this folder has a specific job. A normal clean-clone reproduction uses the eight core scripts. The remaining five support exploration, publication, or data maintenance.

## Core Pipeline

Run these from the repository root in this order:

| Script | What it does |
| --- | --- |
| `verify_source_files.py` | Checks the included transaction CSVs against the published filenames, sizes, SHA-256 hashes, and UTF-8 encoding. |
| `prepare_reference_data.py` | Enforces the 67-row customer-class map and validates the supplemental customer reference. |
| `build_final_database.py` | Loads the seven annual transaction files into SQLite and adds dates, descriptions, provenance, and quality flags. |
| `validate_final_database.py` | Runs database integrity, reconciliation, mapping, period, text-field, and edge-case checks. |
| `analyze_q1.py` | Produces the segment profitability outputs, summary file, validation results, and chart. |
| `analyze_q2.py` | Produces the customer and segment concentration outputs, summary file, validation results, and chart. |
| `analyze_q3.py` | Produces the lifecycle and retention outputs, summary file, validation results, outreach list, and chart. |
| `analyze_q4.py` | Produces the annual and monthly financial trend outputs, seasonality analysis, summary file, validation results, and chart. |

## Optional Analyst and Publication Tools

| Script | What it does | When to use it |
| --- | --- | --- |
| `query_database.py` | Runs a read-only SQL query against the generated SQLite database and can export a compact CSV. | When exploring questions beyond the supplied case study |
| `build_business_report.py` | Rebuilds the Word report from the final result tables and charts. | After refreshing the four analyses |
| `sanitize_public_outputs.py` | Creates stable public customer labels from the database-backed customer map. It is imported by Questions 2 and 3. | Normally do not run it separately |

## Data-Maintenance Tools

These two files document how the public data package is maintained. They are not needed for normal analysis unless source files change.

| Script | What it does | When to use it |
| --- | --- | --- |
| `convert_csv_to_utf8.py` | Checks CSV encoding and can convert a non-UTF-8 file without changing its row count. | Before publishing a new or replaced CSV |
| `generate_source_manifest.py` | Recalculates public file sizes, row counts, UTF-8 declarations, and SHA-256 hashes. | Only after intentionally changing public source files |
