# Revenue Quality & Customer Profitability Case Study

This portfolio project examines whether multi-year revenue growth is profitable, durable, appropriately diversified, and supported by a healthy customer base.

> **Current status:** The data foundation, all four canonical analyses, strategic synthesis, validation suite, charts, analyst workbook, and polished business report are complete. This repository is the privacy-safe portfolio release; full source-data reproduction still depends on an approved external dataset link and redistribution license.

## Choose Your Path

| Audience | Start Here | What You Will Find |
| --- | --- | --- |
| Hiring managers and business readers | [`SOLUTION/EXECUTIVE_SUMMARY.md`](SOLUTION/EXECUTIVE_SUMMARY.md) | A concise business narrative, final visuals, findings, and recommendations. |
| Analysts and technical reviewers | [`docs/DATA_PIPELINE.md`](docs/DATA_PIPELINE.md) | Reproducible setup, modeling rules, validation checks, and query instructions. |
| Case-study reviewers | [`CASE_STUDY_QUESTIONS.md`](CASE_STUDY_QUESTIONS.md) | The four executive questions and final strategic synthesis. |
| Downloadable portfolio deliverables | [`deliverables/`](deliverables/) | A polished Word business report and filterable Excel analysis workbook. |

## Results at a Glance

- Recognized revenue grew **65.0%** from 2018 to 2024; gross profit grew **89.6%**, and gross margin expanded from **19.15% to 22.01%**.
- Independent Retail Accounts generated **48.75% of revenue** and **51.37% of gross profit**, making it both the core economic engine and the main segment-level exposure.
- The largest customer generated only **1.13% of revenue**; it takes **599 customers** to reach 80% of revenue, but only seven customer segments.
- Non-active customers carry a **$23.0 million trailing revenue baseline**, equal to **17.60% of 2024 revenue**. This is a reactivation-opportunity measure, not a forecast.

The complete evidence and recommendations are in [`SOLUTION/EXECUTIVE_SUMMARY.md`](SOLUTION/EXECUTIVE_SUMMARY.md).

## Business Context

The company has produced steady top-line revenue growth across multiple years. Leadership is not only concerned with how much revenue is growing, but whether that growth is profitable, durable, and appropriately diversified.

The case study addresses four questions:

1. Is recognized revenue growth translating into sustainable gross-profit growth?
2. Which customer segments drive profitable growth rather than revenue alone?
3. Is the business overly dependent on a small number of customers or segments?
4. Which customers appear inactive or at risk, and how much revenue is associated with that risk?

The final synthesis asks how strategic focus should shift to improve the overall quality of revenue.

## Data Foundation

The seven annual transaction files contain:

- **3,714,624 transaction rows**
- **3,230 transacting customers**
- **$724.4 million in recognized sales**
- **$153.9 million in gross profit**
- **2018–2024 annual source files**, with accounting-period boundary activity preserved

The project uses a local SQLite database rather than Excel for the canonical transaction table. Excel remains useful for small result tables and polished summaries, but its 1,048,576-row worksheet limit cannot accommodate the transaction grain.

## Modeling Rules

- `Period` is the financial-reporting authority. It is stored as YYMM; for example, `2604` represents April 2026.
- The transaction row's `CustomerClass` is the historical authority. Current customer classifications never overwrite financial history.
- A local `data/raw/reference/CustomerData.csv` may supply optional current customer attributes, but it is excluded from the public repository and is never authoritative for historical analysis.
- `PackSize` is always loaded as text, including date-like values such as `1-Jan`.
- Returns, zero-sales cost activity, zero-cost activity, and exact-duplicate candidates are retained and flagged rather than silently removed.
- Only the seven annual transaction files are ingested. Quarterly files are derived duplicates and are excluded.

## Reproducible Pipeline

```mermaid
flowchart LR
    A["Annual transaction CSVs"] --> B["UTF-8 validation"]
    B --> C["Reference cleanup"]
    C --> D["SQLite total_sales"]
    D --> E["Validation checks"]
    E --> F["SQL analyses"]
    F --> G["Executive report and visuals"]
```

From the project root:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python scripts/convert_csv_to_utf8.py
python scripts/prepare_reference_data.py
python scripts/build_canonical_database.py
python scripts/validate_canonical_database.py
```

The generated database is `data/processed/distributor_case_study.sqlite`. It is reproducible and intentionally excluded from Git.

## Data Access and Privacy

The public repository contains code, SQL, documentation, validation metadata, approved non-identifying reference files, visuals, and finished business deliverables. Customer-level result tables and the analyst workbook use stable anonymized labels such as `CUSTOMER_0001`; the supplemental customer reference is excluded.

The seven large annual transaction files will be published only after de-identification and redistribution approval, through an external dataset host with a stable download link and checksum manifest. Raw identifying customer files and internal scrub workbooks will never be published. See [`data/README.md`](data/README.md) and [`docs/PUBLICATION_CHECKLIST.md`](docs/PUBLICATION_CHECKLIST.md).

## Repository Structure

```text
.
├── README.md                         # Portfolio landing page
├── CASE_STUDY_QUESTIONS.md           # Canonical scope
├── data/
│   ├── raw/
│   │   ├── reference/                # Public reference files and source schema
│   │   └── transactions/             # Seven annual CSVs; hosted externally
│   ├── processed/                    # Reproducible local SQLite database
│   └── metadata/                     # Checksums and validation evidence
├── docs/                              # Technical documentation
├── deliverables/                      # Business report and analyst workbook
├── scripts/                           # Portable ingestion and validation tools
└── SOLUTION/                          # Executive and question-level analysis
    ├── EXECUTIVE_SUMMARY.md
    ├── 01_revenue_margin_trends.md
    ├── 02_segment_profitability.md
    ├── 03_revenue_concentration.md
    ├── 04_customer_retention.md
    ├── 05_strategic_synthesis.md
    ├── outputs/
    ├── sql/
    └── visualizations/
```

## Tooling

- Python and pandas for ingestion and validation
- SQLite and SQL for the canonical analytical layer
- Excel-compatible exports for small review tables
- Portfolio-ready charts and a concise executive document for final presentation

## Regenerate the Analysis and Deliverables

After building and validating the canonical database:

```bash
python scripts/analyze_q1.py
python scripts/analyze_q2_q4.py
python scripts/build_business_report.py
node scripts/build_analysis_workbook.mjs
```

The first two commands recreate the SQL outputs and charts; Question 2-4 processing also replaces source customer numbers with stable public labels. The last two commands rebuild the portfolio-facing Word report and Excel workbook. The workbook builder uses the Codex bundled artifact runtime in this working environment; the finished workbook itself is standard `.xlsx` and does not require Codex to open.

Before a public release, complete [`docs/PUBLICATION_CHECKLIST.md`](docs/PUBLICATION_CHECKLIST.md).
