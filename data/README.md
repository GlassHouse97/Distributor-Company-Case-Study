# Public Data

## Download the Transaction CSVs

The complete transaction dataset is in **[`transactions/`](transactions/)**. That folder contains the seven annual CSV files used by every analysis in this case study.

| Year | File | Rows | Approximate Size |
| --- | --- | ---: | ---: |
| 2018 | [`itmsls2018.csv`](transactions/itmsls2018.csv) | 406,856 | 50 MB |
| 2019 | [`itmsls2019.csv`](transactions/itmsls2019.csv) | 436,872 | 54 MB |
| 2020 | [`itmsls2020.csv`](transactions/itmsls2020.csv) | 494,162 | 61 MB |
| 2021 | [`itmsls2021.csv`](transactions/itmsls2021.csv) | 541,492 | 67 MB |
| 2022 | [`itmsls2022.csv`](transactions/itmsls2022.csv) | 574,256 | 71 MB |
| 2023 | [`itmsls2023.csv`](transactions/itmsls2023.csv) | 612,189 | 76 MB |
| 2024 | [`itmsls2024.csv`](transactions/itmsls2024.csv) | 648,797 | 79 MB |

On GitHub, select a CSV and use **Download raw file**. Analysts who want the complete project should clone the repository instead of downloading the files individually.

## What the Data Represents

The public data is a scrubbed analytical model of a real distributor dataset. Identifiers were anonymized and financial values were scaled to protect the source company while preserving the structure, relationships, trends, edge cases, and analytical usefulness of the data. The figures do not represent the source company's actual financial results.

## Data Folder Guide

```text
data/
|-- transactions/    # Seven public annual transaction CSVs
|-- reference/       # Customer, customer-class, and field references
|-- metadata/        # Checksums, ingestion records, and validation evidence
|-- processed/       # Locally generated SQLite database; ignored by Git
`-- README.md         # This download and analyst guide
```

### Transaction data

[`transactions/`](transactions/) is the authoritative transaction source. Only the seven annual files are loaded. Quarterly extracts are excluded because they contain the same transactions and would double-count activity.

### Reference data

[`reference/`](reference/) contains:

- `CustomerData.csv`: scrubbed supplemental customer attributes.
- `CustomerSegmentationData.csv`: the 67-row historical customer-class mapping.
- `schema.xlsx`: source-field definitions.

The transaction row's customer class remains the historical reporting authority. The customer reference never rewrites prior financial classifications.

### Metadata

[`metadata/`](metadata/) contains the published file checksums and the ingestion and validation evidence produced by the pipeline.

## Reproduce the Dataset

From the repository root:

```bash
python -m venv .venv
python -m pip install -r requirements.txt
python scripts/verify_source_files.py
python scripts/prepare_reference_data.py
python scripts/build_final_database.py
python scripts/validate_final_database.py
```

The build creates `data/processed/distributor_case_study.sqlite`. Run your own SQL against its `total_sales` table or continue with the supplied analyses:

```bash
python scripts/analyze_q1.py
python scripts/analyze_q2_q4.py
```

See the [complete data pipeline](../docs/DATA_PIPELINE.md) and [data dictionary](../docs/DATA_DICTIONARY.md) for field definitions and modeling rules.
