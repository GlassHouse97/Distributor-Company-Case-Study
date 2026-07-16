"""Create stable public customer labels without exposing source customer numbers."""

from __future__ import annotations

import csv
import os
import re
import sqlite3
from pathlib import Path
from typing import Iterable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "SOLUTION" / "outputs"
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "processed" / "distributor_case_study.sqlite"
CUSTOMER_OUTPUTS = [
    "02_customer_concentration.csv",
    "03_customer_lifecycle.csv",
    "03_priority_outreach.csv",
]
PUBLIC_ID_PATTERN = re.compile(r"^CUSTOMER_\d+$")


def build_public_id_map(connection: sqlite3.Connection) -> dict[str, str]:
    """Map the complete customer universe to stable sequential public labels."""
    customer_numbers = [
        str(row[0])
        for row in connection.execute(
            """
            SELECT DISTINCT customer_number
            FROM total_sales
            WHERE customer_number IS NOT NULL
            ORDER BY customer_number
            """
        )
    ]
    width = max(4, len(str(len(customer_numbers))))
    return {
        customer_number: f"CUSTOMER_{index:0{width}d}"
        for index, customer_number in enumerate(customer_numbers, start=1)
    }


def apply_public_labels(values: Iterable[object], mapping: dict[str, str]) -> list[str]:
    """Return public labels for a customer-number series and reject missing mappings."""
    labels: list[str] = []
    missing: list[str] = []
    for value in values:
        key = str(value)
        label = mapping.get(key)
        if label is None:
            missing.append(key)
        else:
            labels.append(label)
    if missing:
        sample = ", ".join(missing[:5])
        raise ValueError(f"Missing public labels for {len(missing)} customer IDs: {sample}")
    return labels


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", errors="strict", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    temp_path = path.with_name(path.name + ".public.tmp")
    try:
        with temp_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def sanitize_outputs(
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    database_path: Path = DEFAULT_DATABASE,
) -> int:
    """Apply the database-backed label map to customer outputs that currently exist."""
    with sqlite3.connect(database_path) as connection:
        mapping = build_public_id_map(connection)

    updated_rows = 0
    existing_files = 0
    for file_name in CUSTOMER_OUTPUTS:
        path = output_dir / file_name
        if not path.exists():
            continue
        existing_files += 1
        fieldnames, rows = read_csv(path)
        if "customer_number" not in fieldnames:
            raise ValueError(f"Missing customer_number in {path}")
        source_values = [row["customer_number"] for row in rows]
        if all(PUBLIC_ID_PATTERN.fullmatch(value) for value in source_values):
            continue
        if any(PUBLIC_ID_PATTERN.fullmatch(value) for value in source_values):
            raise ValueError(f"Mixed source and public customer IDs in {path}")
        labels = apply_public_labels(source_values, mapping)
        for row, label in zip(rows, labels):
            row["customer_number"] = label
        write_csv(path, fieldnames, rows)
        updated_rows += len(rows)

    if existing_files == 0:
        raise FileNotFoundError("No customer-level analysis outputs were found")
    return updated_rows


if __name__ == "__main__":
    count = sanitize_outputs()
    print(f"Applied public labels to {count:,} customer rows")
