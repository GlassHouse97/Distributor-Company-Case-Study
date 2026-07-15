# Annual Transaction Files

This folder contains the seven public, anonymized, and scaled annual transaction files used by the case study:

```text
itmsls2018.csv
itmsls2019.csv
itmsls2020.csv
itmsls2021.csv
itmsls2022.csv
itmsls2023.csv
itmsls2024.csv
```

Run `python scripts/verify_source_files.py` from the repository root to confirm every file against the published checksum manifest.

Do not add the quarterly extracts. They contain the same transactions partitioned by quarter and would double-count the dataset if loaded with the annual files.
