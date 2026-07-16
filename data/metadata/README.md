# Data Metadata

This folder contains small audit receipts, not additional source data.

| File | What it proves |
| --- | --- |
| `source_manifest.json` | Lists every public input file with its row count, byte size, UTF-8 declaration, and SHA-256 checksum. |
| `utf8_validation_manifest.json` | Records the strict UTF-8 and line-count check for every published CSV. |
| `reference_data_change_log.json` | Records the final customer-class mapping and the supplemental role of `CustomerData.csv`. |
| `final_ingestion_report.json` | Reconciles the files and rows loaded into the generated SQLite database. |
| `final_validation_report.json` | Records the 33 database checks and whether each one passed. |

These JSON files are evidence for technical reviewers. A reader who only wants the data or final analysis does not need to open them.
