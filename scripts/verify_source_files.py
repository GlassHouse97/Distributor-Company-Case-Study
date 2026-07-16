"""Verify the included annual transaction files against the published manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "data" / "metadata" / "source_manifest.json"


def default_transactions_dir() -> Path:
    configured = os.environ.get("DISTRO_TRANSACTIONS_DIR")
    if configured:
        return Path(configured).expanduser()
    return PROJECT_ROOT / "data" / "transactions"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def is_strict_utf8(path: Path) -> bool:
    try:
        with path.open("r", encoding="utf-8", errors="strict") as handle:
            for _ in iter(lambda: handle.read(1024 * 1024), ""):
                pass
    except UnicodeDecodeError:
        return False
    return True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--transactions-dir", type=Path, default=default_transactions_dir())
    args = parser.parse_args()
    transaction_dir = args.transactions_dir.resolve()
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    failures = []

    for expected in manifest["annual_transaction_files"]:
        path = transaction_dir / expected["file_name"]
        if not path.exists():
            failures.append(f"Missing: {expected['file_name']}")
            continue
        if path.stat().st_size != expected["bytes"]:
            failures.append(f"Size mismatch: {expected['file_name']}")
        if sha256_file(path) != expected["sha256"]:
            failures.append(f"Checksum mismatch: {expected['file_name']}")
        if not is_strict_utf8(path):
            failures.append(f"Not strict UTF-8: {expected['file_name']}")
        print(f"Checked {expected['file_name']}")

    if failures:
        print("\n".join(failures))
        raise SystemExit(1)
    print("All annual transaction files match the published manifest.")


if __name__ == "__main__":
    main()
