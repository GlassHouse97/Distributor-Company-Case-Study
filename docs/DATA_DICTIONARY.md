# Canonical Data Dictionary

## `total_sales`

### Provenance

| Column | SQLite Type | Definition |
| --- | --- | --- |
| `source_file` | TEXT | Annual CSV from which the row originated. |
| `source_row_number` | INTEGER | One-based data-row number within the source file. |
| `transaction_row_id` | TEXT | Stable pipeline identifier formed from source file and row number. |
| `source_row_hash` | INTEGER | Reproducible row-content hash used to identify exact-duplicate candidates. |

### Transaction fields

| Column | SQLite Type | Definition |
| --- | --- | --- |
| `item_id` | TEXT | Item identifier. Treated as an identifier, not a measure. |
| `brand` | TEXT | Scrubbed brand label. |
| `pack_size` | TEXT | Pack-size label. Always text, including values such as `1-Jan`. |
| `customer_number` | TEXT | Customer identifier. |
| `cases` | REAL | Case quantity; negative values can indicate returns. |
| `pieces` | REAL | Piece quantity; negative values can indicate returns. |
| `sales` | REAL | Recognized sales amount at the transaction-line level. |
| `cost` | REAL | Transaction-line cost. |
| `gross_profit` | REAL | `sales - cost`. |
| `invoice_id` | TEXT | Invoice identifier. |
| `sales_person` | TEXT | Salesperson recorded on the historical transaction. |
| `warehouse` | TEXT | Warehouse code. Stored as a code rather than a measure. |
| `price` | REAL | Source transaction price. |
| `weight` | REAL | Source transaction weight. |
| `invoice_date` | TEXT | ISO date representing transaction timing. |
| `accounting_id` | TEXT | Accounting identifier. |
| `period` | TEXT | Recognized-revenue month in YYMM format. Financial reporting authority. |
| `period_date` | TEXT | First day of the recognized-revenue month in ISO format. |
| `billing_type` | TEXT | Billing-type code. |
| `transaction_customer_class` | TEXT | Historical class recorded on the transaction; authoritative for segment analysis. |
| `transaction_class_description` | TEXT | Description mapped from the historical transaction class. |
| `order_id` | TEXT | Order identifier. |
| `per_month` | INTEGER | Month extracted from `period`. |
| `per_year` | INTEGER | Four-digit year represented by `period`. |
| `per_quarter` | TEXT | Quarter represented by `period`. |

### Quality flags

| Column | SQLite Type | Definition |
| --- | --- | --- |
| `is_return_or_credit` | INTEGER | 1 when sales, cost, cases, or pieces is negative. |
| `is_zero_sales_nonzero_cost` | INTEGER | 1 when sales is zero and cost is nonzero. |
| `is_nonzero_sales_zero_cost` | INTEGER | 1 when sales is nonzero and cost is zero. |
| `is_zero_sales_and_cost` | INTEGER | 1 when both sales and cost are zero. |
| `is_financial_edge_case` | INTEGER | 1 when any principal financial exception flag is set. |
| `is_invoice_period_mismatch` | INTEGER | 1 when invoice month differs from recognized-revenue month. |
| `is_unmapped_customer` | INTEGER | 1 when no supplemental customer record is available. |
| `is_unmapped_customer_class` | INTEGER | 1 when the transaction class has no description mapping. |
| `duplicate_group_size` | INTEGER | Number of rows sharing the same row-content hash. |
| `is_exact_duplicate_candidate` | INTEGER | 1 when the row belongs to a repeated full-row hash group. Rows are retained. |

## `customer_class_reference`

| Column | SQLite Type | Definition |
| --- | --- | --- |
| `customer_class` | TEXT | Historical customer-class code. |
| `customer_class_description` | TEXT | Portfolio-safe segment description. Class 37 is `Legacy Customer`. |

## `customer_reference`

This table represents supplemental current-state attributes. It must not overwrite historical transaction fields.

| Column | SQLite Type | Definition |
| --- | --- | --- |
| `customer_number` | TEXT | Customer identifier and primary key. |
| `city` | TEXT | Current or supplemental city. |
| `state` | TEXT | Current or supplemental state. |
| `zip_code` | TEXT | Postal code stored as text. |
| `current_sales_person` | TEXT | Current customer-master salesperson. |
| `date_started` | TEXT | Supplemental start date when available. Not authoritative for churn. |
| `current_customer_class` | TEXT | Current customer-master classification. |
| `current_customer_class_description` | TEXT | Current customer-master class description. |
