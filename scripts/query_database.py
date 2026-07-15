"""Run an ad hoc read-only query against the final SQLite database."""

from __future__ import annotations

import argparse
import csv
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "processed" / "distributor_case_study.sqlite"


def main() -> None:
    parser = argparse.ArgumentParser()
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--query", help="SQL SELECT statement to execute.")
    source.add_argument("--sql-file", type=Path, help="File containing one SQL SELECT statement.")
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path, help="Optional CSV output path.")
    parser.add_argument("--preview-rows", type=int, default=25)
    args = parser.parse_args()

    sql = args.query or args.sql_file.read_text(encoding="utf-8")
    database = args.database.resolve()
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)
    cursor = connection.execute(sql)
    columns = [description[0] for description in cursor.description]

    if args.output:
        output = args.output.resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(columns)
            while rows := cursor.fetchmany(10_000):
                writer.writerows(rows)
        print(output)
    else:
        rows = cursor.fetchmany(args.preview_rows)
        print(" | ".join(columns))
        for row in rows:
            print(" | ".join("" if value is None else str(value) for value in row))

    connection.close()


if __name__ == "__main__":
    main()
