"""Generate checksums for the externally hosted annual transaction files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_DIR = PROJECT_ROOT / "data" / "raw" / "reference"
MANIFEST_PATH = PROJECT_ROOT / "data" / "metadata" / "source_manifest.json"


def default_transactions_dir() -> Path:
    configured = os.environ.get("DISTRO_TRANSACTIONS_DIR")
    if configured:
        return Path(configured).expanduser()
    return PROJECT_ROOT / "data" / "raw" / "transactions"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def data_row_count(path: Path) -> int:
    newlines = 0
    last = b""
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            newlines += block.count(b"\n")
            if block:
                last = block[-1:]
    physical_lines = newlines + (1 if path.stat().st_size and last != b"\n" else 0)
    return max(physical_lines - 1, 0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transactions-dir", type=Path, default=default_transactions_dir())
    args = parser.parse_args()
    transaction_dir = args.transactions_dir.resolve()
    annual_files = sorted(transaction_dir.glob("itmsls20??.csv"))
    if len(annual_files) != 7:
        raise ValueError(f"Expected seven annual files; found {len(annual_files)}")

    files = [
        {
            "file_name": path.name,
            "bytes": path.stat().st_size,
            "data_rows": data_row_count(path),
            "sha256": sha256_file(path),
            "encoding": "UTF-8",
        }
        for path in annual_files
    ]
    references = []
    for file_name in ["CustomerSegmentationData.csv"]:
        path = REFERENCE_DIR / file_name
        references.append(
            {
                "file_name": file_name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
                "encoding": "UTF-8",
            }
        )

    manifest = {
        "schema_version": "1.0",
        "dataset_host_url": None,
        "dataset_license": "To be selected before publication",
        "expected_download_directory": "data/raw/transactions",
        "annual_transaction_files": files,
        "public_reference_files": references,
        "total_transaction_rows": sum(item["data_rows"] for item in files),
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(MANIFEST_PATH)


if __name__ == "__main__":
    main()
