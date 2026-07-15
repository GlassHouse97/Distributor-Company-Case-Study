# Processed Data

This directory contains locally generated analytical data stores.

- `distributor_case_study.sqlite` is rebuilt from the seven annual `itmsls20xx.csv` files.
- Generated databases are intentionally ignored by Git because they are reproducible and may exceed repository hosting limits.
- Quarterly extracts are not ingestion inputs because they duplicate the annual transaction partitions.

Run `python scripts/build_final_database.py` from the project root to rebuild the database.
