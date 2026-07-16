"""Convert public project CSVs to UTF-8 without changing decoded content."""

from __future__ import annotations

import argparse
import codecs
import hashlib
import json
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
METADATA_DIR = PROJECT_ROOT / "data" / "metadata"
REPORT_PATH = METADATA_DIR / "utf8_conversion_manifest.json"
VALIDATION_REPORT_PATH = METADATA_DIR / "utf8_validation_manifest.json"
READ_SIZE = 1024 * 1024
EXCLUDED_DIRECTORY_NAMES = {
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(READ_SIZE), b""):
            digest.update(block)
    return digest.hexdigest()


def detects_as_utf8(path: Path) -> tuple[bool, bool]:
    """Return (is_utf8, has_utf8_bom)."""
    with path.open("rb") as handle:
        prefix = handle.read(3)
        has_bom = prefix == b"\xef\xbb\xbf"
        handle.seek(0)
        encoding = "utf-8-sig" if has_bom else "utf-8"
        decoder = codecs.getincrementaldecoder(encoding)(errors="strict")
        try:
            for block in iter(lambda: handle.read(READ_SIZE), b""):
                decoder.decode(block, final=False)
            decoder.decode(b"", final=True)
        except UnicodeDecodeError:
            return False, has_bom
    return True, has_bom


def count_newlines(path: Path) -> int:
    count = 0
    last_byte = b""
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(READ_SIZE), b""):
            count += block.count(b"\n")
            if block:
                last_byte = block[-1:]
    return count + (1 if path.stat().st_size and last_byte != b"\n" else 0)


def transcode(path: Path, source_encoding: str) -> None:
    temp_path = path.with_name(path.name + ".utf8.tmp")
    try:
        with path.open("r", encoding=source_encoding, errors="strict", newline="") as source:
            with temp_path.open("w", encoding="utf-8", newline="") as target:
                for block in iter(lambda: source.read(READ_SIZE), ""):
                    target.write(block)
        # Prove the replacement decodes strictly before replacing the source.
        with temp_path.open("r", encoding="utf-8", errors="strict", newline="") as check:
            for _ in iter(lambda: check.read(READ_SIZE), ""):
                pass
        if count_newlines(path) != count_newlines(temp_path):
            raise ValueError(f"Line count changed while transcoding {path}")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def project_csv_paths() -> list[Path]:
    """Return repository CSVs while pruning virtual environments and generated data."""
    csv_paths: list[Path] = []
    for root, directory_names, file_names in os.walk(PROJECT_ROOT):
        directory_names[:] = [
            name
            for name in directory_names
            if name.lower() not in EXCLUDED_DIRECTORY_NAMES
        ]
        root_path = Path(root)
        relative_root = root_path.relative_to(PROJECT_ROOT)
        relative_parts = tuple(part.lower() for part in relative_root.parts)
        if relative_parts[:2] == ("data", "processed"):
            directory_names.clear()
            continue
        csv_paths.extend(
            root_path / file_name
            for file_name in file_names
            if file_name.lower().endswith(".csv")
        )
    return sorted(csv_paths)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Verify strict UTF-8 without modifying files.",
    )
    args = parser.parse_args()

    csv_paths = project_csv_paths()
    results = []

    for path in csv_paths:
        relative_path = path.relative_to(PROJECT_ROOT).as_posix()
        original_hash = sha256_file(path)
        original_size = path.stat().st_size
        original_lines = count_newlines(path)
        is_utf8, has_bom = detects_as_utf8(path)

        if is_utf8 and not has_bom:
            source_encoding = "utf-8"
            converted = False
        elif args.check_only:
            source_encoding = "utf-8-sig" if is_utf8 else "cp1252"
            converted = False
        else:
            source_encoding = "utf-8-sig" if is_utf8 else "cp1252"
            transcode(path, source_encoding)
            converted = True

        final_utf8, final_bom = detects_as_utf8(path)
        results.append(
            {
                "path": relative_path,
                "detected_source_encoding": source_encoding,
                "converted": converted,
                "strict_utf8_after_run": final_utf8,
                "utf8_bom_after_run": final_bom,
                "line_count_before": original_lines,
                "line_count_after": count_newlines(path),
                "size_before": original_size,
                "size_after": path.stat().st_size,
                "sha256_before": original_hash,
                "sha256_after": sha256_file(path),
            }
        )
        print(f"{relative_path}: {source_encoding} -> {'converted' if converted else 'unchanged'}")

    invalid = [item["path"] for item in results if not item["strict_utf8_after_run"]]
    changed_lines = [
        item["path"]
        for item in results
        if item["line_count_before"] != item["line_count_after"]
    ]
    report_path = VALIDATION_REPORT_PATH if args.check_only else REPORT_PATH
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(
        json.dumps(
            {
                "project_csv_count": len(results),
                "converted_count": sum(item["converted"] for item in results),
                "invalid_utf8_files": invalid,
                "line_count_mismatches": changed_lines,
                "files": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    if invalid or changed_lines:
        raise SystemExit(1)
    print(report_path)


if __name__ == "__main__":
    main()
