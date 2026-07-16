# Revenue Quality & Customer Profitability Case Study

An end-to-end portfolio project built from 3.7 million anonymized, scaled transaction records. It shows how raw annual CSV files can be prepared, modeled in SQLite, analyzed with SQL and Python, validated, and translated into an executive-ready business story.

> **Fully reproducible with public data.** The repository includes the complete 2018-2024 anonymized transaction dataset, all source code, SQL, checks, analysis outputs, visuals, and finished deliverables.

## Start Here

### 1. Read the case study

Start with the browser-friendly [Executive Summary](SOLUTION/EXECUTIVE_SUMMARY.md). It explains the business problem, key findings, visuals, and recommendations without requiring any setup.

- [Read the executive summary](SOLUTION/EXECUTIVE_SUMMARY.md)
- [Review the final case-study questions](CASE_STUDY_QUESTIONS.md)
- [Explore the detailed answers](SOLUTION/README.md)

### 2. Download the finished portfolio

Use the report for a polished business-facing presentation and the workbook for filterable supporting analysis.

- [Download the editable Word report](SOLUTION/Distributor_Case_Study_Report.docx)
- [Download the Excel analysis workbook](SOLUTION/Distributor_Case_Study_Analysis.xlsx)

### 3. Reproduce the analysis

The complete public dataset is already included in the clearly labeled [`data/transactions/`](data/transactions/) folder. Start with the [data download and analyst guide](data/README.md), or clone the repository and run:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python scripts/verify_source_files.py
python scripts/prepare_reference_data.py
python scripts/build_final_database.py
python scripts/validate_final_database.py
python scripts/analyze_q1.py
python scripts/analyze_q2_q4.py
```

This creates the final SQLite analysis database at `data/processed/distributor_case_study.sqlite` and regenerates the question-level outputs and visuals. See the [complete reproduction guide](docs/DATA_PIPELINE.md) for modeling rules, database objects, and query examples.

The [script guide](scripts/README.md) explains which scripts are required, optional, or only used when maintaining the published data.

## Results at a Glance

- Recognized revenue grew **65.0%** from 2018 to 2024; gross profit grew **89.6%**, and gross margin expanded from **19.15% to 22.01%**.
- Independent Retail Accounts generated **48.75% of revenue** and **51.37% of gross profit**, making the segment both the core economic engine and the main segment-level exposure.
- The largest customer generated only **1.13% of revenue**; it takes **599 customers** to reach 80% of revenue, but only seven customer segments.
- Non-active customers carry a **$23.0 million trailing revenue baseline**, equal to **17.60% of 2024 revenue**. This is a reactivation-opportunity measure, not a forecast.

## Business Questions

1. Is recognized revenue growth translating into sustainable gross-profit growth?
2. Which customer segments drive profitable growth rather than revenue alone?
3. Is the business overly dependent on a small number of customers or segments?
4. Which customers appear inactive or at risk, and how much revenue is associated with that risk?
5. How should strategic focus shift to improve the overall quality of revenue?

## Public Dataset

The seven annual transaction files contain:

- **3,714,624 transaction rows**
- **3,230 transacting customers**
- **2018-2024 annual source files**, with accounting-period boundary activity preserved
- Approximately **456 MB** of UTF-8 CSV data

The public data is a scrubbed analytical model of a real distributor dataset. Identifiers were anonymized and financial values were scaled to protect the source company while preserving the dataset's structure, relationships, trends, and analytical usefulness. The figures in this case study are therefore modeled portfolio values and do not represent the source company's actual financial results.

The scrub workbook, original identifying exports, quarterly duplicates, and legacy analysis files are not part of the public repository. See the [data guide](data/README.md), [data dictionary](docs/DATA_DICTIONARY.md), and [checksum manifest](data/metadata/source_manifest.json).

## Modeling Rules

- `Period` is the financial-reporting authority. It is stored as YYMM; for example, `2604` represents April 2026.
- The transaction row's `CustomerClass` is the historical authority. Current classifications never overwrite financial history.
- `PackSize` is loaded as text, including date-like values such as `1-Jan`.
- Returns, zero-sales cost activity, zero-cost activity, and exact-duplicate candidates are retained and flagged instead of silently removed.
- Only the seven annual transaction files are ingested. Quarterly files are derived duplicates and would double-count activity.
- SQLite stores the final transaction table because Excel's worksheet row limit cannot hold the 3.7-million-row fact table.

## Pipeline

```mermaid
flowchart LR
    A["Public annual CSVs"] --> B["UTF-8 and checksum checks"]
    B --> C["Reference preparation"]
    C --> D["Final SQLite database"]
    D --> E["Data-quality validation"]
    E --> F["SQL and Python analysis"]
    F --> G["Executive report, workbook, and visuals"]
```

## Repository Map

```text
.
|-- README.md                         # Start here
|-- CASE_STUDY_QUESTIONS.md           # Final project scope
|-- data/
|   |-- transactions/                 # Seven downloadable annual CSV files
|   |-- reference/                    # Scrubbed customer and class references
|   `-- metadata/                     # Checksums and validation evidence
|-- docs/                              # Pipeline, dictionary, and release notes
|-- scripts/                           # Ingestion, validation, and analysis code
`-- SOLUTION/                          # Executive and question-level analysis
    |-- EXECUTIVE_SUMMARY.md
    |-- Distributor_Case_Study_Report.docx
    |-- Distributor_Case_Study_Analysis.xlsx
    |-- 01_revenue_margin_trends.md
    |-- 02_segment_profitability.md
    |-- 03_revenue_concentration.md
    |-- 04_customer_retention.md
    |-- 05_strategic_synthesis.md
    |-- outputs/
    |-- sql/
    `-- visualizations/
```

The pipeline creates `data/processed/` locally for the generated SQLite database. That generated folder is intentionally absent from GitHub because the database can be rebuilt from the included CSV files.

## Regenerate the Analysis and Word Report

After the final database passes validation:

```bash
python scripts/build_business_report.py
```

The analysis scripts regenerate the result tables and visuals, and the final command rebuilds the Word report. The included Excel workbook is a finished portfolio download assembled from the same published result tables; it is not required to reproduce or inspect the analysis.
