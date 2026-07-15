"""Validate the final SQLite database against audited source invariants."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "processed" / "distributor_case_study.sqlite"
REPORT_PATH = PROJECT_ROOT / "data" / "metadata" / "final_validation_report.json"

EXPECTED_FILE_ROWS = {
    "itmsls2018.csv": 406_856,
    "itmsls2019.csv": 436_872,
    "itmsls2020.csv": 494_162,
    "itmsls2021.csv": 541_492,
    "itmsls2022.csv": 574_256,
    "itmsls2023.csv": 612_189,
    "itmsls2024.csv": 648_797,
}
EXPECTED = {
    "row_count": 3_714_624,
    "sales": 724_422_941.42901,
    "cost": 570_505_668.775113,
    "gross_profit": 153_917_272.653897,
    "return_rows": 22_766,
    "zero_sales_nonzero_cost_rows": 34_780,
    "nonzero_sales_zero_cost_rows": 6_179,
    "zero_sales_and_cost_rows": 1_259,
    "invoice_period_mismatch_rows": 274_193,
    "rows_in_duplicate_groups": 273,
    "duplicate_groups": 127,
    "duplicate_rows_beyond_first": 146,
}


def scalar(connection: sqlite3.Connection, sql: str, parameters: tuple = ()):
    return connection.execute(sql, parameters).fetchone()[0]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    args = parser.parse_args()
    database = args.database.resolve()
    connection = sqlite3.connect(f"file:{database.as_posix()}?mode=ro", uri=True)

    checks: list[dict] = []

    def check(name: str, actual, expected, tolerance: float = 0.0) -> None:
        if isinstance(expected, float):
            passed = abs(float(actual) - expected) <= tolerance
        else:
            passed = actual == expected
        checks.append(
            {
                "check": name,
                "passed": passed,
                "actual": actual,
                "expected": expected,
                "tolerance": tolerance,
            }
        )

    check("sqlite_integrity", scalar(connection, "PRAGMA integrity_check"), "ok")
    check("total_sales_rows", scalar(connection, "SELECT COUNT(*) FROM total_sales"), EXPECTED["row_count"])
    check("sales_total", scalar(connection, "SELECT SUM(sales) FROM total_sales"), EXPECTED["sales"], 0.01)
    check("cost_total", scalar(connection, "SELECT SUM(cost) FROM total_sales"), EXPECTED["cost"], 0.01)
    check(
        "gross_profit_total",
        scalar(connection, "SELECT SUM(gross_profit) FROM total_sales"),
        EXPECTED["gross_profit"],
        0.01,
    )

    for source_file, expected_rows in EXPECTED_FILE_ROWS.items():
        check(
            f"rows_{source_file}",
            scalar(
                connection,
                "SELECT COUNT(*) FROM total_sales WHERE source_file = ?",
                (source_file,),
            ),
            expected_rows,
        )

    check(
        "quarterly_files_excluded",
        scalar(connection, "SELECT COUNT(*) FROM total_sales WHERE source_file LIKE '%-Q%.csv'"),
        0,
    )
    check(
        "customer_class_reference_rows",
        scalar(connection, "SELECT COUNT(*) FROM customer_class_reference"),
        67,
    )
    check(
        "legacy_class_mapping",
        scalar(
            connection,
            "SELECT customer_class_description FROM customer_class_reference WHERE customer_class = '37'",
        ),
        "Legacy Customer",
    )
    customer_reference_rows = scalar(
        connection, "SELECT COUNT(*) FROM customer_reference"
    )
    check(
        "supplemental_unmapped_reference",
        scalar(
            connection,
            "SELECT COUNT(*) FROM customer_reference WHERE city = 'Unmapped'",
        ),
        1 if customer_reference_rows else 0,
    )
    check(
        "unmapped_customer_rows",
        scalar(connection, "SELECT SUM(is_unmapped_customer) FROM total_sales"),
        0 if customer_reference_rows else EXPECTED["row_count"],
    )
    check(
        "unmapped_customer_class_rows",
        scalar(connection, "SELECT SUM(is_unmapped_customer_class) FROM total_sales"),
        0,
    )
    check(
        "transaction_class_37_description",
        scalar(
            connection,
            """
            SELECT COUNT(*)
            FROM total_sales
            WHERE transaction_customer_class = '37'
              AND transaction_class_description = 'Legacy Customer'
            """,
        ),
        2_232,
    )
    check(
        "historical_class_movement_preserved",
        scalar(
            connection,
            """
            SELECT COUNT(*)
            FROM total_sales_enriched
            WHERE current_customer_class IS NOT NULL
              AND transaction_customer_class <> current_customer_class
            """,
        ),
        90_233 if customer_reference_rows else 0,
    )

    check(
        "pack_size_storage_type",
        scalar(
            connection,
            "SELECT typeof(pack_size) FROM total_sales WHERE pack_size = '1-Jan' LIMIT 1",
        ),
        "text",
    )
    check(
        "pack_size_date_like_values_preserved",
        scalar(connection, "SELECT COUNT(*) FROM total_sales WHERE pack_size = '1-Jan'") > 0,
        True,
    )
    check(
        "period_is_four_digit_text",
        scalar(
            connection,
            """
            SELECT COUNT(*) FROM total_sales
            WHERE typeof(period) <> 'text'
               OR length(period) <> 4
               OR period GLOB '*[^0-9]*'
            """,
        ),
        0,
    )
    check(
        "period_components_reconcile",
        scalar(
            connection,
            """
            SELECT COUNT(*) FROM total_sales
            WHERE per_year <> 2000 + CAST(substr(period, 1, 2) AS INTEGER)
               OR per_month <> CAST(substr(period, 3, 2) AS INTEGER)
               OR per_quarter <> 'Q' || CAST(((per_month - 1) / 3) + 1 AS INTEGER)
            """,
        ),
        0,
    )
    check(
        "period_date_reconciles",
        scalar(
            connection,
            """
            SELECT COUNT(*) FROM total_sales
            WHERE period_date <> printf('%04d-%02d-01', per_year, per_month)
            """,
        ),
        0,
    )

    flag_queries = {
        "return_rows": "SELECT SUM(is_return_or_credit) FROM total_sales",
        "zero_sales_nonzero_cost_rows": "SELECT SUM(is_zero_sales_nonzero_cost) FROM total_sales",
        "nonzero_sales_zero_cost_rows": "SELECT SUM(is_nonzero_sales_zero_cost) FROM total_sales",
        "zero_sales_and_cost_rows": "SELECT SUM(is_zero_sales_and_cost) FROM total_sales",
        "invoice_period_mismatch_rows": "SELECT SUM(is_invoice_period_mismatch) FROM total_sales",
        "rows_in_duplicate_groups": "SELECT SUM(is_exact_duplicate_candidate) FROM total_sales",
        "duplicate_groups": "SELECT COUNT(DISTINCT source_row_hash) FROM total_sales WHERE is_exact_duplicate_candidate = 1",
        "duplicate_rows_beyond_first": "SELECT CAST(ROUND(SUM(CASE WHEN is_exact_duplicate_candidate = 1 THEN 1.0 - (1.0 / duplicate_group_size) ELSE 0 END)) AS INTEGER) FROM total_sales",
    }
    for name, sql in flag_queries.items():
        check(name, scalar(connection, sql), EXPECTED[name])

    connection.close()
    passed = all(item["passed"] for item in checks)
    report = {
        "database": database.relative_to(PROJECT_ROOT).as_posix(),
        "passed": passed,
        "check_count": len(checks),
        "failed_check_count": sum(not item["passed"] for item in checks),
        "checks": checks,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    for item in checks:
        print(f"{'PASS' if item['passed'] else 'FAIL'}: {item['check']}")
    print(REPORT_PATH)
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
