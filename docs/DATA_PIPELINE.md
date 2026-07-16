# Data Pipeline and Reproducibility

## Purpose

The project supports two audiences:

1. Business readers can review the final executive summary without downloading or querying the source data.
2. Analysts can reproduce the final dataset, inspect the quality rules, and run their own SQL analysis.

The pipeline uses relative paths, portable Python scripts, and SQLite. It does not depend on a particular cloud account, workstation path, or proprietary database.

## Source Files

### Authoritative transaction inputs

Only these annual files are ingested:

```text
itmsls2018.csv
itmsls2019.csv
itmsls2020.csv
itmsls2021.csv
itmsls2022.csv
itmsls2023.csv
itmsls2024.csv
```

The pipeline reads `data/transactions/` by default. A different location can be supplied with `--transactions-dir` or `DISTRO_TRANSACTIONS_DIR`.

Only the seven annual files are loaded. Quarterly versions contain the same transactions and would double-count sales if they were loaded with the annual files.

The files are included in the repository. After cloning, verify their SHA-256 checksums:

```bash
python scripts/verify_source_files.py
```

### Reference inputs

- `data/reference/CustomerSegmentationData.csv` maps historical transaction class codes to descriptions.
- `data/reference/CustomerData.csv` contains scrubbed supplemental current customer attributes.

Historical transaction values remain authoritative. The customer reference is never used to rewrite a transaction's class.

## Pipeline Stages

### 1. Encoding normalization

```bash
python scripts/convert_csv_to_utf8.py --check-only
```

The script checks every project CSV with strict UTF-8 decoding and confirms that line counts are unchanged. The published result is stored in `data/metadata/utf8_validation_manifest.json`. Maintainers can run the script without `--check-only` when a newly added CSV actually needs conversion.

### 2. Reference preparation

```bash
python scripts/prepare_reference_data.py
```

This stage:

- reduces the segmentation file to its two useful columns;
- retains the original 66 valid class mappings;
- adds `37 = Legacy Customer`;
- validates and cleans the included scrubbed `CustomerData.csv`;
- preserves every transaction even when no supplemental customer record exists, flagging the missing reference and exposing `Unmapped` supplemental text in the enriched view.

### 3. Final database build

```bash
python scripts/build_final_database.py
```

Optional explicit paths:

```bash
python scripts/build_final_database.py \
  --transactions-dir data/transactions \
  --database data/processed/distributor_case_study.sqlite
```

The build is atomic. A temporary database is created first and replaces the final database only after ingestion and integrity checks succeed.

### 4. Validation

```bash
python scripts/validate_final_database.py
```

The validation suite checks:

- SQLite file integrity;
- total and annual row counts;
- sales, cost, and gross-profit reconciliation;
- absence of quarterly inputs;
- customer-reference flag consistency and complete class mapping coverage;
- preservation of historical class movement;
- text storage for `PackSize`;
- YYMM period structure and derived dates;
- financial exception flags;
- exact-duplicate candidate counts.

Results are stored in `data/metadata/final_validation_report.json`.

## Final Database Objects

| Object | Type | Purpose |
| --- | --- | --- |
| `total_sales` | Table | Final transaction fact table with provenance, derived dates, descriptions, and quality flags. |
| `customer_class_reference` | Table | The 67 historical customer-class mappings. |
| `customer_reference` | Table | Scrubbed supplemental current customer attributes. |
| `total_sales_enriched` | View | Optional join from the final fact to current customer attributes. |
| `ingestion_metadata` | Table | Modeling rules and source-file metadata. |

## Accounting Period Rule

The source column is named `Period` and is loaded as the text field `period`.

```text
YYMM = period
2604 = April 2026
```

The final table also contains:

- `period_date`: first calendar day of the recognized-revenue month;
- `per_month`: month number;
- `per_year`: four-digit year;
- `per_quarter`: calendar quarter.

Analytical financial grouping must use `period` or `period_date`, not the source filename or invoice month.

## Historical Customer Classification

`transaction_customer_class` comes directly from each financial transaction and is the classification used for historical segment analysis.

The enriched view exposes `current_customer_class` separately. This permits current-state reporting without rewriting prior financial classifications.

## Quality Flags

No transaction is removed by the ingestion process. The following flags make edge cases visible:

- `is_return_or_credit`
- `is_zero_sales_nonzero_cost`
- `is_nonzero_sales_zero_cost`
- `is_zero_sales_and_cost`
- `is_financial_edge_case`
- `is_invoice_period_mismatch`
- `is_unmapped_customer`
- `is_unmapped_customer_class`
- `is_exact_duplicate_candidate`

`source_file`, `source_row_number`, and `transaction_row_id` preserve the provenance of every row.

## Querying Without Excel

Preview a query:

```bash
python scripts/query_database.py --query "SELECT per_year, ROUND(SUM(sales), 2) AS revenue FROM total_sales GROUP BY per_year ORDER BY per_year"
```

Export an aggregated result:

```bash
python scripts/query_database.py \
  --query "SELECT period, SUM(sales) AS revenue FROM total_sales GROUP BY period ORDER BY period" \
  --output SOLUTION/outputs/monthly_revenue.csv
```

Excel should be used for these compact outputs, not for the four-million-row fact table.

## Publication Model

The public GitHub repository contains the complete reproducible package: annual transaction CSVs, scrubbed reference data, code, SQL, documentation, validation reports, visuals, and final deliverables. The generated SQLite database remains excluded from version control because every user can rebuild it from the included CSV files.

## Analysis and Report Build

After the final database passes validation:

```bash
python scripts/analyze_q1.py
python scripts/analyze_q2.py
python scripts/analyze_q3.py
python scripts/analyze_q4.py
python scripts/build_business_report.py
```

Each question script runs its own SQL, exports compact result tables, checks its expected scope, writes a summary file, and regenerates its chart. The final command packages the same final outputs into the Word report. The published Excel workbook is a convenience download built from those result tables and is not required to reproduce the analysis.

Questions 2 and 3 automatically replace source customer numbers with stable labels such as `CUSTOMER_0001`. Both scripts use the same database-backed label map, so they can run independently without producing inconsistent public IDs.

See `docs/PUBLICATION_CHECKLIST.md` for final release and signed-out accessibility checks.
