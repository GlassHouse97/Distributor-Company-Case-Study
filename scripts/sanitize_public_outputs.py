"""Replace source customer numbers with stable public labels in compact outputs."""

from __future__ import annotations

import csv
import os
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "SOLUTION" / "outputs"
CUSTOMER_OUTPUTS = [
    "03_customer_concentration.csv",
    "04_customer_lifecycle.csv",
    "04_priority_outreach.csv",
]
PUBLIC_ID_PATTERN = re.compile(r"^CUSTOMER_\d+$")


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


def sanitize_outputs(output_dir: Path = DEFAULT_OUTPUT_DIR) -> int:
    datasets: list[tuple[Path, list[str], list[dict[str, str]]]] = []
    identifiers: list[str] = []
    for file_name in CUSTOMER_OUTPUTS:
        path = output_dir / file_name
        fieldnames, rows = read_csv(path)
        if "customer_number" not in fieldnames:
            raise ValueError(f"Missing customer_number in {path}")
        datasets.append((path, fieldnames, rows))
        identifiers.extend(row["customer_number"] for row in rows)

    unique_identifiers = list(dict.fromkeys(identifiers))
    if all(PUBLIC_ID_PATTERN.fullmatch(value) for value in unique_identifiers):
        return len(unique_identifiers)
    if any(PUBLIC_ID_PATTERN.fullmatch(value) for value in unique_identifiers):
        raise ValueError("Public outputs contain a mix of source and anonymized customer IDs")

    width = max(4, len(str(len(unique_identifiers))))
    mapping = {
        value: f"CUSTOMER_{index:0{width}d}"
        for index, value in enumerate(unique_identifiers, start=1)
    }
    for path, fieldnames, rows in datasets:
        for row in rows:
            row["customer_number"] = mapping[row["customer_number"]]
        write_csv(path, fieldnames, rows)
    return len(mapping)


if __name__ == "__main__":
    count = sanitize_outputs()
    print(f"Anonymized {count:,} customer identifiers")
