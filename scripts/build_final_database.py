"""Build a queryable final SQLite database from the annual transaction CSVs."""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATABASE = PROJECT_ROOT / "data" / "processed" / "distributor_case_study.sqlite"
REFERENCE_DIR = PROJECT_ROOT / "data" / "reference"
REPORT_PATH = PROJECT_ROOT / "data" / "metadata" / "final_ingestion_report.json"
CHUNK_SIZE = 100_000

SOURCE_COLUMNS = [
    "ItemID",
    "Brand",
    "PackSize",
    "CustomerNumber",
    "Cases",
    "Pieces",
    "Sales",
    "Cost",
    "InvoiceID",
    "SalesPerson",
    "Warehouse",
    "Price",
    "Weight",
    "InvoiceDate",
    "AccountingID",
    "Period",
    "BillingType",
    "CustomerClass",
    "OrderID",
    "PerMonth",
    "PerYear",
    "PerQuarter",
]

STRING_COLUMNS = {
    "ItemID",
    "Brand",
    "PackSize",
    "CustomerNumber",
    "InvoiceID",
    "SalesPerson",
    "Warehouse",
    "AccountingID",
    "Period",
    "BillingType",
    "CustomerClass",
    "OrderID",
    "PerQuarter",
}

CUSTOMER_REFERENCE_COLUMNS = [
    "customer_number",
    "city",
    "state",
    "zip_code",
    "current_sales_person",
    "date_started",
    "current_customer_class",
    "current_customer_class_description",
]

INSERT_COLUMNS = [
    "source_file",
    "source_row_number",
    "transaction_row_id",
    "source_row_hash",
    "item_id",
    "brand",
    "pack_size",
    "customer_number",
    "cases",
    "pieces",
    "sales",
    "cost",
    "gross_profit",
    "invoice_id",
    "sales_person",
    "warehouse",
    "price",
    "weight",
    "invoice_date",
    "accounting_id",
    "period",
    "period_date",
    "billing_type",
    "transaction_customer_class",
    "transaction_class_description",
    "order_id",
    "per_month",
    "per_year",
    "per_quarter",
    "is_return_or_credit",
    "is_zero_sales_nonzero_cost",
    "is_nonzero_sales_zero_cost",
    "is_zero_sales_and_cost",
    "is_financial_edge_case",
    "is_invoice_period_mismatch",
    "is_unmapped_customer",
    "is_unmapped_customer_class",
]


def clean_string(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip()


def default_transactions_dir() -> Path:
    configured = os.environ.get("DISTRO_TRANSACTIONS_DIR")
    if configured:
        return Path(configured).expanduser()
    return PROJECT_ROOT / "data" / "transactions"


def load_reference_data() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str], set[str]]:
    class_reference = pd.read_csv(
        REFERENCE_DIR / "CustomerSegmentationData.csv",
        dtype="string",
        encoding="utf-8",
    )
    class_reference = class_reference[
        ["CustomerClass", "CustomerClassDescription"]
    ].rename(
        columns={
            "CustomerClass": "customer_class",
            "CustomerClassDescription": "customer_class_description",
        }
    )
    class_reference["customer_class"] = clean_string(class_reference["customer_class"])
    class_reference["customer_class_description"] = clean_string(
        class_reference["customer_class_description"]
    )
    if class_reference["customer_class"].duplicated().any():
        raise ValueError("Customer class reference contains duplicate keys")
    class_map = dict(
        zip(
            class_reference["customer_class"],
            class_reference["customer_class_description"],
        )
    )

    customer_path = REFERENCE_DIR / "CustomerData.csv"
    if customer_path.exists():
        customer_reference = pd.read_csv(
            customer_path, dtype="string", encoding="utf-8"
        ).rename(
            columns={
                "CustomerNumber": "customer_number",
                "City": "city",
                "State": "state",
                "ZipCode": "zip_code",
                "SalesPerson": "current_sales_person",
                "DATE STARTED": "date_started",
                "CustomerClass": "current_customer_class",
                "CustomerClassDescription": "current_customer_class_description",
            }
        )
        if list(customer_reference.columns) != CUSTOMER_REFERENCE_COLUMNS:
            raise ValueError(
                f"Unexpected CustomerData columns: {list(customer_reference.columns)}"
            )
    else:
        customer_reference = pd.DataFrame(
            {column: pd.Series(dtype="string") for column in CUSTOMER_REFERENCE_COLUMNS}
        )
    for column in customer_reference.columns:
        customer_reference[column] = clean_string(customer_reference[column])
    if not customer_reference.empty:
        parsed_start = pd.to_datetime(customer_reference["date_started"], errors="coerce")
        customer_reference["date_started"] = parsed_start.dt.strftime("%Y-%m-%d")
    if customer_reference["customer_number"].duplicated().any():
        raise ValueError("Customer reference contains duplicate keys")
    customer_keys = set(customer_reference["customer_number"].dropna())
    return class_reference, customer_reference, class_map, customer_keys


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE total_sales (
            source_file TEXT NOT NULL,
            source_row_number INTEGER NOT NULL,
            transaction_row_id TEXT PRIMARY KEY,
            source_row_hash INTEGER NOT NULL,
            item_id TEXT NOT NULL,
            brand TEXT,
            pack_size TEXT,
            customer_number TEXT NOT NULL,
            cases REAL NOT NULL,
            pieces REAL NOT NULL,
            sales REAL NOT NULL,
            cost REAL NOT NULL,
            gross_profit REAL NOT NULL,
            invoice_id TEXT NOT NULL,
            sales_person TEXT,
            warehouse TEXT,
            price REAL,
            weight REAL,
            invoice_date TEXT NOT NULL,
            accounting_id TEXT,
            period TEXT NOT NULL,
            period_date TEXT NOT NULL,
            billing_type TEXT,
            transaction_customer_class TEXT NOT NULL,
            transaction_class_description TEXT,
            order_id TEXT,
            per_month INTEGER NOT NULL,
            per_year INTEGER NOT NULL,
            per_quarter TEXT NOT NULL,
            is_return_or_credit INTEGER NOT NULL CHECK (is_return_or_credit IN (0, 1)),
            is_zero_sales_nonzero_cost INTEGER NOT NULL CHECK (is_zero_sales_nonzero_cost IN (0, 1)),
            is_nonzero_sales_zero_cost INTEGER NOT NULL CHECK (is_nonzero_sales_zero_cost IN (0, 1)),
            is_zero_sales_and_cost INTEGER NOT NULL CHECK (is_zero_sales_and_cost IN (0, 1)),
            is_financial_edge_case INTEGER NOT NULL CHECK (is_financial_edge_case IN (0, 1)),
            is_invoice_period_mismatch INTEGER NOT NULL CHECK (is_invoice_period_mismatch IN (0, 1)),
            is_unmapped_customer INTEGER NOT NULL CHECK (is_unmapped_customer IN (0, 1)),
            is_unmapped_customer_class INTEGER NOT NULL CHECK (is_unmapped_customer_class IN (0, 1)),
            duplicate_group_size INTEGER NOT NULL DEFAULT 1,
            is_exact_duplicate_candidate INTEGER NOT NULL DEFAULT 0
                CHECK (is_exact_duplicate_candidate IN (0, 1))
        );

        CREATE TABLE ingestion_metadata (
            metric TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )


def transform_chunk(
    chunk: pd.DataFrame,
    path: Path,
    row_offset: int,
    class_map: dict[str, str],
    customer_keys: set[str],
) -> pd.DataFrame:
    if list(chunk.columns) != SOURCE_COLUMNS:
        raise ValueError(f"Unexpected schema in {path.name}: {list(chunk.columns)}")

    raw_for_hash = chunk.fillna("<NA>").astype("string")
    row_hash_unsigned = pd.util.hash_pandas_object(raw_for_hash, index=False).to_numpy(
        dtype=np.uint64
    )
    row_hash_signed = row_hash_unsigned.view(np.int64)

    for column in STRING_COLUMNS:
        chunk[column] = clean_string(chunk[column])
    numeric = {
        column: pd.to_numeric(chunk[column], errors="raise")
        for column in ["Cases", "Pieces", "Sales", "Cost", "Price", "Weight", "PerMonth", "PerYear"]
    }
    invoice_date = pd.to_datetime(chunk["InvoiceDate"], errors="raise")
    period_number = pd.to_numeric(chunk["Period"], errors="raise").astype("int64")
    period_month = period_number % 100
    period_year = 2000 + (period_number // 100)
    if not period_month.between(1, 12).all():
        raise ValueError(f"Invalid YYMM accounting period in {path.name}")
    if not (numeric["PerMonth"].astype("int64") == period_month).all():
        raise ValueError(f"PerMonth does not reconcile to Period in {path.name}")
    if not (numeric["PerYear"].astype("int64") == period_year).all():
        raise ValueError(f"PerYear does not reconcile to Period in {path.name}")

    period_date = pd.to_datetime(
        {
            "year": period_year,
            "month": period_month,
            "day": pd.Series(1, index=chunk.index),
        }
    )
    expected_quarter = "Q" + (((period_month - 1) // 3) + 1).astype("string")
    if not (chunk["PerQuarter"] == expected_quarter).all():
        raise ValueError(f"PerQuarter does not reconcile to Period in {path.name}")

    sales = numeric["Sales"].astype("float64")
    cost = numeric["Cost"].astype("float64")
    cases = numeric["Cases"].astype("float64")
    pieces = numeric["Pieces"].astype("float64")
    is_return = (sales < 0) | (cost < 0) | (cases < 0) | (pieces < 0)
    is_zero_sales_cost = (sales == 0) & (cost != 0)
    is_sales_zero_cost = (sales != 0) & (cost == 0)
    is_zero_both = (sales == 0) & (cost == 0)

    row_numbers = np.arange(row_offset + 1, row_offset + len(chunk) + 1, dtype=np.int64)
    row_number_text = pd.Series(row_numbers, index=chunk.index).astype("string").str.zfill(7)
    result = pd.DataFrame(index=chunk.index)
    result["source_file"] = path.name
    result["source_row_number"] = row_numbers
    result["transaction_row_id"] = path.stem + ":" + row_number_text
    result["source_row_hash"] = row_hash_signed
    result["item_id"] = chunk["ItemID"]
    result["brand"] = chunk["Brand"]
    # Deliberately textual: values such as 1-Jan must not be parsed as dates.
    result["pack_size"] = chunk["PackSize"]
    result["customer_number"] = chunk["CustomerNumber"]
    result["cases"] = cases
    result["pieces"] = pieces
    result["sales"] = sales
    result["cost"] = cost
    result["gross_profit"] = sales - cost
    result["invoice_id"] = chunk["InvoiceID"]
    result["sales_person"] = chunk["SalesPerson"]
    result["warehouse"] = chunk["Warehouse"]
    result["price"] = numeric["Price"].astype("float64")
    result["weight"] = numeric["Weight"].astype("float64")
    result["invoice_date"] = invoice_date.dt.strftime("%Y-%m-%d")
    result["accounting_id"] = chunk["AccountingID"]
    result["period"] = chunk["Period"].str.zfill(4)
    result["period_date"] = period_date.dt.strftime("%Y-%m-%d")
    result["billing_type"] = chunk["BillingType"]
    result["transaction_customer_class"] = chunk["CustomerClass"]
    result["transaction_class_description"] = chunk["CustomerClass"].map(class_map)
    result["order_id"] = chunk["OrderID"]
    result["per_month"] = numeric["PerMonth"].astype("int64")
    result["per_year"] = numeric["PerYear"].astype("int64")
    result["per_quarter"] = chunk["PerQuarter"]
    result["is_return_or_credit"] = is_return.astype("int8")
    result["is_zero_sales_nonzero_cost"] = is_zero_sales_cost.astype("int8")
    result["is_nonzero_sales_zero_cost"] = is_sales_zero_cost.astype("int8")
    result["is_zero_sales_and_cost"] = is_zero_both.astype("int8")
    result["is_financial_edge_case"] = (
        is_return | is_zero_sales_cost | is_sales_zero_cost | is_zero_both
    ).astype("int8")
    result["is_invoice_period_mismatch"] = (
        invoice_date.dt.to_period("M") != period_date.dt.to_period("M")
    ).astype("int8")
    result["is_unmapped_customer"] = (~chunk["CustomerNumber"].isin(customer_keys)).astype("int8")
    result["is_unmapped_customer_class"] = (~chunk["CustomerClass"].isin(class_map)).astype(
        "int8"
    )
    return result[INSERT_COLUMNS]


def add_references_and_views(
    connection: sqlite3.Connection,
    class_reference: pd.DataFrame,
    customer_reference: pd.DataFrame,
) -> None:
    class_reference.to_sql(
        "customer_class_reference", connection, if_exists="replace", index=False
    )
    customer_reference.to_sql(
        "customer_reference", connection, if_exists="replace", index=False
    )
    connection.executescript(
        """
        CREATE UNIQUE INDEX idx_customer_reference_number
            ON customer_reference(customer_number);
        CREATE UNIQUE INDEX idx_customer_class_reference_code
            ON customer_class_reference(customer_class);

        CREATE VIEW total_sales_enriched AS
        SELECT
            fact.*,
            COALESCE(customer.city, 'Unmapped') AS customer_city,
            COALESCE(customer.state, 'Unmapped') AS customer_state,
            COALESCE(customer.zip_code, 'Unmapped') AS customer_zip_code,
            COALESCE(customer.current_sales_person, 'Unmapped') AS current_sales_person,
            customer.date_started AS customer_date_started,
            customer.current_customer_class,
            COALESCE(
                customer.current_customer_class_description,
                'Unmapped'
            ) AS current_customer_class_description
        FROM total_sales AS fact
        LEFT JOIN customer_reference AS customer
            ON fact.customer_number = customer.customer_number;
        """
    )


def finalize_database(connection: sqlite3.Connection) -> dict:
    connection.executescript(
        """
        CREATE INDEX idx_total_sales_period ON total_sales(period);
        CREATE INDEX idx_total_sales_period_date ON total_sales(period_date);
        CREATE INDEX idx_total_sales_customer ON total_sales(customer_number);
        CREATE INDEX idx_total_sales_transaction_class
            ON total_sales(transaction_customer_class);
        CREATE INDEX idx_total_sales_invoice ON total_sales(invoice_id);
        CREATE INDEX idx_total_sales_source_hash ON total_sales(source_row_hash);

        CREATE TEMP TABLE duplicate_hash_counts AS
        SELECT source_row_hash, COUNT(*) AS group_size
        FROM total_sales
        GROUP BY source_row_hash
        HAVING COUNT(*) > 1;

        UPDATE total_sales
        SET
            duplicate_group_size = (
                SELECT group_size
                FROM duplicate_hash_counts
                WHERE duplicate_hash_counts.source_row_hash = total_sales.source_row_hash
            ),
            is_exact_duplicate_candidate = 1
        WHERE source_row_hash IN (SELECT source_row_hash FROM duplicate_hash_counts);

        ANALYZE;
        """
    )
    row = connection.execute(
        """
        SELECT
            COUNT(*) AS row_count,
            SUM(sales) AS sales,
            SUM(cost) AS cost,
            SUM(gross_profit) AS gross_profit,
            SUM(is_return_or_credit) AS return_rows,
            SUM(is_zero_sales_nonzero_cost) AS zero_sales_nonzero_cost_rows,
            SUM(is_nonzero_sales_zero_cost) AS nonzero_sales_zero_cost_rows,
            SUM(is_zero_sales_and_cost) AS zero_sales_and_cost_rows,
            SUM(is_invoice_period_mismatch) AS invoice_period_mismatch_rows,
            SUM(is_unmapped_customer) AS unmapped_customer_rows,
            SUM(is_unmapped_customer_class) AS unmapped_class_rows,
            SUM(CASE WHEN is_exact_duplicate_candidate = 1 THEN 1 ELSE 0 END)
                AS rows_in_duplicate_groups,
            SUM(CASE WHEN is_exact_duplicate_candidate = 1
                THEN 1.0 / duplicate_group_size ELSE 0 END) AS duplicate_groups
        FROM total_sales
        """
    ).fetchone()
    result_keys = [
        "row_count",
        "sales",
        "cost",
        "gross_profit",
        "return_rows",
        "zero_sales_nonzero_cost_rows",
        "nonzero_sales_zero_cost_rows",
        "zero_sales_and_cost_rows",
        "invoice_period_mismatch_rows",
        "unmapped_customer_rows",
        "unmapped_class_rows",
        "rows_in_duplicate_groups",
        "duplicate_groups",
    ]
    return dict(zip(result_keys, row))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, default=DEFAULT_DATABASE)
    parser.add_argument(
        "--transactions-dir",
        type=Path,
        default=default_transactions_dir(),
        help="Directory containing only the seven annual itmsls20xx.csv files.",
    )
    args = parser.parse_args()

    transaction_dir = args.transactions_dir.resolve()
    annual_files = sorted(transaction_dir.glob("itmsls20??.csv"))
    if len(annual_files) != 7:
        raise ValueError(f"Expected seven annual transaction files; found {len(annual_files)}")
    if any("-Q" in path.stem for path in annual_files):
        raise ValueError("Quarterly extracts must not be ingested")

    class_reference, customer_reference, class_map, customer_keys = load_reference_data()
    output_path = args.database.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_name(output_path.name + ".building")
    for candidate in [temp_path, Path(str(temp_path) + "-wal"), Path(str(temp_path) + "-shm")]:
        if candidate.exists():
            candidate.unlink()

    connection = sqlite3.connect(temp_path)
    connection.execute("PRAGMA journal_mode = OFF")
    connection.execute("PRAGMA synchronous = OFF")
    connection.execute("PRAGMA temp_store = MEMORY")
    connection.execute("PRAGMA cache_size = -200000")
    create_schema(connection)

    file_metrics = []
    try:
        for path in annual_files:
            row_offset = 0
            file_sales = 0.0
            file_cost = 0.0
            dtype = {column: "string" for column in STRING_COLUMNS}
            for chunk in pd.read_csv(
                path,
                dtype=dtype,
                chunksize=CHUNK_SIZE,
                encoding="utf-8",
                low_memory=False,
            ):
                transformed = transform_chunk(
                    chunk, path, row_offset, class_map, customer_keys
                )
                transformed.to_sql(
                    "total_sales",
                    connection,
                    if_exists="append",
                    index=False,
                    chunksize=5_000,
                )
                row_offset += len(transformed)
                file_sales += float(transformed["sales"].sum())
                file_cost += float(transformed["cost"].sum())
                print(f"{path.name}: {row_offset:,} rows", flush=True)
            file_metrics.append(
                {
                    "source_file": path.name,
                    "rows": row_offset,
                    "sales": file_sales,
                    "cost": file_cost,
                    "gross_profit": file_sales - file_cost,
                }
            )

        add_references_and_views(connection, class_reference, customer_reference)
        totals = finalize_database(connection)
        metadata = {
            "schema_version": "1.0",
            "authoritative_financial_period": "period (YYMM)",
            "authoritative_customer_class": "transaction_customer_class",
            "quarterly_extracts_ingested": False,
            "transaction_input_layout": "seven annual itmsls20xx.csv files",
            "annual_source_files": [path.name for path in annual_files],
            "file_metrics": file_metrics,
            "totals": totals,
        }
        for metric, value in {
            "schema_version": metadata["schema_version"],
            "authoritative_financial_period": metadata[
                "authoritative_financial_period"
            ],
            "authoritative_customer_class": metadata[
                "authoritative_customer_class"
            ],
            "quarterly_extracts_ingested": json.dumps(False),
            "annual_source_files": json.dumps(metadata["annual_source_files"]),
        }.items():
            connection.execute(
                "INSERT INTO ingestion_metadata(metric, value) VALUES (?, ?)",
                (metric, str(value)),
            )
        connection.commit()
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"SQLite integrity check failed: {integrity}")
    finally:
        connection.close()

    os.replace(temp_path, output_path)
    metadata["database_path"] = output_path.relative_to(PROJECT_ROOT).as_posix()
    metadata["database_bytes"] = output_path.stat().st_size
    metadata["sqlite_integrity_check"] = integrity
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(output_path)
    print(REPORT_PATH)


if __name__ == "__main__":
    main()
