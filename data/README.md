# Data Directory

This directory keeps source inputs, generated data, and validation evidence in separate locations.

```text
data/
├── raw/
│   ├── reference/        # Small public reference files
│   └── transactions/     # Seven externally hosted annual transaction files
├── processed/            # Reproducible local SQLite database
└── metadata/             # Checksums, ingestion logs, and validation evidence
```

## Reference Data

`data/raw/reference/` contains:

- `CustomerSegmentationData.csv`: the 67-row historical customer-class mapping.
- `schema.xlsx`: the original source-field dictionary.

`CustomerData.csv` is an optional local supplement and is intentionally absent from the public repository because the source version contains customer numbers, locations, and salesperson names. The canonical transaction analysis does not require it.

## Annual Transaction Data

The seven `itmsls20xx.csv` files contain the authoritative transaction history. They will be distributed through an external dataset host rather than committed directly to GitHub.

After downloading, place the files in `data/raw/transactions/` or set `DISTRO_TRANSACTIONS_DIR` to another location. Then verify them against `data/metadata/source_manifest.json`:

```bash
python scripts/verify_source_files.py
```

## Generated Data and Local-Only Material

- `data/processed/distributor_case_study.sqlite` is reproducible and ignored by Git.
- `data/metadata/` contains small, publishable validation artifacts.
- Private customer exports, scrub workbooks, quarterly duplicates, and legacy analysis files are intentionally kept outside the portfolio project.

Non-technical readers can review the finished analysis without downloading the raw transaction data.

## Public-Release Boundary

The transaction fact analysis does not depend on customer names. Published customer-level outputs replace source customer numbers with labels such as `CUSTOMER_0001`, and the supplemental customer reference remains local-only unless a documented privacy review approves an anonymized replacement.
