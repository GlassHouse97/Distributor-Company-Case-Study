"""Clean public references and, when supplied locally, optional customer data."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = PROJECT_ROOT / "data" / "raw" / "reference"
SEGMENT_PATH = REFERENCE_DIR / "CustomerSegmentationData.csv"
CUSTOMER_PATH = REFERENCE_DIR / "CustomerData.csv"
REPORT_PATH = PROJECT_ROOT / "data" / "metadata" / "reference_data_change_log.json"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_dicts(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", errors="strict", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def atomic_write(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    temp_path = path.with_name(path.name + ".reference.tmp")
    try:
        with temp_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=fieldnames,
                extrasaction="ignore",
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
        with temp_path.open("r", encoding="utf-8", errors="strict") as check:
            check.read()
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def clean_segmentation() -> dict:
    before_hash = sha256_file(SEGMENT_PATH)
    fieldnames, rows = read_dicts(SEGMENT_PATH)
    required = ["CustomerClass", "CustomerClassDescription"]
    if not set(required).issubset(fieldnames):
        raise ValueError(f"Missing required segmentation columns: {required}")

    mapping: dict[str, str] = {}
    for row in rows:
        class_code = (row.get("CustomerClass") or "").strip()
        description = (row.get("CustomerClassDescription") or "").strip()
        if not class_code:
            continue
        prior = mapping.get(class_code)
        if prior and prior != description:
            raise ValueError(
                f"Conflicting descriptions for class {class_code}: {prior!r} and {description!r}"
            )
        mapping[class_code] = description

    valid_before = len(mapping)
    if valid_before != 66 and "37" not in mapping:
        raise ValueError(f"Expected 66 valid source mappings before adding class 37; found {valid_before}")
    mapping["37"] = "Legacy Customer"
    cleaned_rows = [
        {
            "CustomerClass": class_code,
            "CustomerClassDescription": mapping[class_code],
        }
        for class_code in sorted(mapping, key=int)
    ]
    atomic_write(SEGMENT_PATH, required, cleaned_rows)
    return {
        "path": SEGMENT_PATH.name,
        "sha256_before": before_hash,
        "sha256_after": sha256_file(SEGMENT_PATH),
        "source_rows": len(rows),
        "valid_mappings_before": valid_before,
        "mappings_after": len(cleaned_rows),
        "added_mapping": {"CustomerClass": "37", "CustomerClassDescription": "Legacy Customer"},
    }


def clean_optional_customer_reference() -> dict:
    if not CUSTOMER_PATH.exists():
        return {
            "path": CUSTOMER_PATH.name,
            "included": False,
            "status": "Not included in the public repository; supplemental only.",
        }

    before_hash = sha256_file(CUSTOMER_PATH)
    fieldnames, rows = read_dicts(CUSTOMER_PATH)
    required = [
        "CustomerNumber",
        "City",
        "State",
        "ZipCode",
        "SalesPerson",
        "DATE STARTED",
        "CustomerClass",
        "CustomerClassDescription",
    ]
    if fieldnames != required:
        raise ValueError(f"Unexpected CustomerData columns: {fieldnames}")

    customer_numbers = [(row.get("CustomerNumber") or "").strip() for row in rows]
    if len(customer_numbers) != len(set(customer_numbers)):
        raise ValueError("CustomerData contains duplicate customer numbers")
    rows.sort(key=lambda row: int((row.get("CustomerNumber") or "0").strip()))
    atomic_write(CUSTOMER_PATH, required, rows)
    return {
        "path": CUSTOMER_PATH.name,
        "sha256_before": before_hash,
        "sha256_after": sha256_file(CUSTOMER_PATH),
        "rows_after": len(rows),
        "included": True,
        "modeling_role": "Supplemental only; transaction class remains authoritative.",
    }


def main() -> None:
    segment_result = clean_segmentation()
    customer_result = clean_optional_customer_reference()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps(
            {
                "modeling_rule": (
                    "Historical transaction CustomerClass is authoritative; CustomerData is supplemental."
                ),
                "segmentation": segment_result,
                "customer": customer_result,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"segmentation": segment_result, "customer": customer_result}, indent=2))
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
