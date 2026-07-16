# Script Guide

The scripts are grouped below by purpose. A clean-clone reproduction uses only the **core pipeline**. The other scripts support maintenance, analyst exploration, or packaging.

## Core Pipeline

Run these from the repository root in this order:

| Script | Why it exists | Required? |
| --- | --- | --- |
| `verify_source_files.py` | Confirms the included CSV files match the published row counts, SHA-256 checksums, and UTF-8 encoding. | Yes |
| `prepare_reference_data.py` | Enforces the two-column, 67-row customer-class map and validates the supplemental customer reference. | Yes |
| `build_final_database.py` | Loads the seven annual transaction files into the local SQLite transaction table, derives period fields, and adds quality flags. | Yes |
| `validate_final_database.py` | Runs database integrity, reconciliation, mapping, period, text-field, and edge-case checks. | Yes |
| `analyze_q1.py` | Runs the Question 1 SQL and writes its result tables, validation output, summary metrics, and chart. | Yes |
| `analyze_q2_q4.py` | Runs the Question 2-4 SQL and writes result tables, validation outputs, summary metrics, and charts. | Yes |

## Optional Analyst and Publication Tools

| Script | Why it exists | When to use it |
| --- | --- | --- |
| `query_database.py` | Runs an ad hoc read-only SQL query against the generated SQLite database and can export a compact CSV. | When exploring the data beyond the supplied questions |
| `build_business_report.py` | Rebuilds the polished Word report from the published result tables and charts. | When refreshing the business-facing report |
| `sanitize_public_outputs.py` | Replaces customer numbers in three public result files with stable labels. It is imported automatically by `analyze_q2_q4.py`. | Normally do not run it separately |

## Data-Maintenance Tools

These document the preparation and release process. They are not needed for a normal clean-clone analysis unless source files change.

| Script | Why it exists | When to use it |
| --- | --- | --- |
| `convert_csv_to_utf8.py` | Checks project CSV encoding and atomically converts a non-UTF-8 CSV while preserving row counts. | Before publishing newly added or replaced CSV files |
| `generate_source_manifest.py` | Recalculates public file sizes, row counts, UTF-8 declarations, and SHA-256 checksums. | Only after intentionally changing public source files |
