# Sales Data Structure Notice

## Quarterly Data Breakdown

Due to GitHub file size limitations, the full `TotalSales` dataset could not be uploaded as a single file.

To ensure the dataset remains accessible and reproducible, the transactional sales data has been broken down into **quarterly segments**.

Each quarterly file represents a portion of the complete `TotalSales` fact table. When combined, these files reconstruct the full sales dataset used throughout the SQL analysis.

---

## Why This Was Necessary

GitHub enforces file size limits for repository uploads. The original `TotalSales` table exceeded those limits due to:

- Multi-year transactional history  
- Invoice-level granularity  
- Large row volume  

Segmenting the data into quarterly files allows:

- Easier download and replication  
- Cleaner repository structure  
- Compliance with GitHub storage constraints  

---

## How to Reconstruct the Full `TotalSales` Table

To recreate the full dataset:

1. Import all quarterly files into your SQL environment.
2. Use `UNION ALL` to combine them into a single table.

Example:

```sql
SELECT * FROM TotalSales_Q1_2018
UNION ALL
SELECT * FROM TotalSales_Q2_2018
UNION ALL
SELECT * FROM TotalSales_Q3_2018
UNION ALL
SELECT * FROM TotalSales_Q4_2018;
