# Public Data

This repository includes the complete scrubbed dataset required to reproduce the case study.

## What Is Included

```text
data/
|-- raw/
|   |-- transactions/     # Seven annual UTF-8 transaction CSVs, 2018-2024
|   `-- reference/        # Scrubbed customer, customer-class, and schema references
|-- processed/            # Locally generated SQLite database; not committed
`-- metadata/             # Checksums, ingestion logs, and validation evidence
```

The public files contain anonymized identifiers and scaled financial values. They preserve the analytical structure, trends, relationships, edge cases, and multi-year behavior of the source data without publishing the source company's actual identifying or financial information.

## Transaction Data

[`raw/transactions/`](raw/transactions/) contains:

```text
itmsls2018.csv
itmsls2019.csv
itmsls2020.csv
itmsls2021.csv
itmsls2022.csv
itmsls2023.csv
itmsls2024.csv
```

These seven files contain 3,714,624 rows and are the authoritative transaction inputs. Verify their sizes, UTF-8 encoding, and SHA-256 checksums with:

```bash
python scripts/verify_source_files.py
```

Do not add the quarterly extracts. They are derived partitions of the same annual rows and would double-count transactions if loaded with the annual files.

## Reference Data

[`raw/reference/`](raw/reference/) contains:

- `CustomerSegmentationData.csv`: the 67-row historical customer-class mapping, including `37 = Legacy Customer`.
- `CustomerData.csv`: a scrubbed supplemental customer reference used for current-state attributes such as geography and customer class.
- `schema.xlsx`: the original source-field dictionary.

Historical analysis always uses the customer class stored on each transaction. The current customer reference is supplemental and never rewrites historical financial classifications.

## Generated Data

`processed/distributor_case_study.sqlite` is built locally and intentionally excluded from Git because it can be recreated from the included public CSV files:

```bash
python scripts/prepare_reference_data.py
python scripts/build_final_database.py
python scripts/validate_final_database.py
```

See [`../docs/DATA_PIPELINE.md`](../docs/DATA_PIPELINE.md) for the complete reproduction workflow and [`metadata/source_manifest.json`](metadata/source_manifest.json) for file-level verification evidence.
