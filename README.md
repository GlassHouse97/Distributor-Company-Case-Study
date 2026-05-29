# Revenue Quality & Customer Profitability Case Study

## Project Overview

This case study explores revenue performance, customer profitability, and growth sustainability within a structured wholesale distribution environment. The project is built using a production-style transactional dataset modeled to reflect real-world enterprise sales operations.

At its core, this analysis focuses on a centralized invoice-level sales fact table supported by customer master data and structured segmentation dimensions. The dataset captures revenue, cost, sales ownership, geographic attributes, and financial reporting periods — enabling a comprehensive evaluation of **revenue quality** rather than simple top-line growth.

A key component of this environment is the company's revenue recognition standard. While transaction activity is recorded by invoice date, official financial reporting is governed by an accounting period field (`Period`, formatted as YYMM). All executive reporting, sales performance evaluation, and profitability analysis are aligned to recognized revenue periods rather than transaction timestamps. This distinction mirrors real-world accounting controls and ensures analytical accuracy.

Let's get started!

## Business Context

The company has posted steady top-line revenue growth over multiple years. The strategic concern is not *how much* revenue is growing, but **how durable and profitable that growth actually is.** Leadership wants clarity on four questions, plus a synthesis:

1. Is revenue growth translating into sustainable **profit** growth, or is margin quietly eroding?
2. Which customer **segments** generate the strongest margins — and are the high-revenue segments also the high-margin ones?
3. Is the business overly dependent on a small **concentration** of accounts, and does that risk look different at the segment level versus the individual-customer level?
4. Where does **customer retention risk** exist, and how much revenue is genuinely exposed to it?

Taken together: **how should strategic focus shift to improve the quality of revenue?**

This project approaches these questions from a financial and operational perspective, combining dimensional modeling principles with period-based revenue logic to deliver executive-ready insight.

## Analytical Direction

The analysis is organized around four questions, each pairing a SQL solution with a business interpretation:

1. **Revenue & Margin Trend Analysis** — period-based revenue and gross margin trends over time.
2. **Customer & Segment Profitability** — revenue and margin performance by customer segment, separating volume from profitability.
3. **Revenue Concentration Risk (Pareto Analysis)** — how broadly revenue is distributed across customers, and how customer-level concentration compares to segment-level concentration.
4. **Customer Lifecycle & Churn Analysis** — recognized-period activity used to classify churn risk and quantify the revenue actually exposed to it.

All queries and supporting analysis are developed in **Google BigQuery**, and visualizations are captured in **Google Looker Studio**.

## Data Architecture

The dataset follows a dimensional modeling structure commonly used in warehouse environments, consisting of one centralized fact table supported by customer dimension tables.

### Fact Table: `TotalSales`

**Grain:** One row per invoice line item

This table contains all transactional sales activity and serves as the primary analytical source.

**Columns:**

| Column Name | Data Type |
| --- | --- |
| ItemID | INTEGER |
| Brand | STRING |
| PackSize | STRING |
| CustomerNumber | INTEGER |
| Cases | INTEGER |
| Pieces | INTEGER |
| Sales | FLOAT |
| Cost | FLOAT |
| InvoiceID | STRING |
| SalesPerson | STRING |
| Warehouse | INTEGER |
| Price | FLOAT |
| Weight | FLOAT |
| InvoiceDate | DATE |
| AccountingID | STRING |
| Period | INTEGER (YYMM format – revenue recognition period) |
| BillingType | INTEGER |
| CustomerClass | INTEGER |
| OrderID | STRING |
| PerMonth | INTEGER |
| PerYear | INTEGER |
| PerQuarter | STRING |

The combination of `(InvoiceID, ItemID)` represents a unique transaction line in this table.

- `CustomerNumber` is a foreign key referencing `CustomerData(CustomerNumber)`.
- `CustomerClass` is a foreign key referencing `CustomerSegmentationData(CustomerClass)`.

### Dimension Table: `CustomerData`

**Grain:** One row per customer

This table provides geographic, lifecycle, and classification context for each account.

**Columns:**

| Column Name | Data Type |
| --- | --- |
| CustomerNumber | INTEGER |
| City | STRING |
| State | STRING |
| ZipCode | STRING |
| SalesPerson | STRING |
| DATE STARTED | DATE |
| CustomerClass | INTEGER |
| CustomerClassDescription | STRING |

`CustomerNumber` is the primary key of this table.

`CustomerClass` is a foreign key referencing `CustomerSegmentationData(CustomerClass)`.

### Dimension Table: `CustomerSegmentationData`

**Grain:** One row per customer class

This table defines structured segmentation categories used for channel and profitability analysis.

**Columns:**

| Column Name | Data Type |
| --- | --- |
| CustomerClass | INTEGER |
| CustomerClassDescription | STRING |
| string_field_2 | STRING |
| string_field_3 | STRING |
| string_field_4 | STRING |
| string_field_5 | STRING |

`CustomerClass` is the primary key of this table.

## Revenue Recognition Logic

While `InvoiceDate` captures transaction timing, the company recognizes revenue using the `Period` field.

- `Period` follows a YYMM format
- Example:
  - `2201` = January 2022
  - `2112` = December 2021

All financial reporting and performance evaluation are based on `Period`, not invoice date. This mirrors real-world accounting standards and ensures reporting consistency across the organization.

## Business Objectives

The analysis addresses the following executive questions, in order:

1. How has recognized revenue and gross margin trended over time, and is revenue growth translating into profit growth?
2. Which customer segments drive profitable growth — not just revenue?
3. Is the business overly dependent on a small group of customers, and how does concentration differ at the segment versus customer level?
4. Which customers appear inactive, and how much revenue is actually exposed to churn?
