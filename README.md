# Revenue Quality & Customer Profitability Case Study

## Project Overview

This case study explores revenue performance, customer profitability, and growth sustainability within a structured wholesale distribution environment. The project is built using a production-style transactional dataset modeled to reflect real-world enterprise sales operations.

At its core, this analysis focuses on a centralized invoice-level sales fact table supported by customer master data and structured segmentation dimensions. The dataset captures revenue, cost, sales ownership, geographic attributes, and financial reporting periods — enabling a comprehensive evaluation of revenue quality rather than simple top-line growth.

A key component of this environment is the company’s revenue recognition standard. While transaction activity is recorded by invoice date, official financial reporting is governed by an accounting period field (`Period`, formatted as YYMM). All executive reporting, sales performance evaluation, and profitability analysis are aligned to recognized revenue periods rather than transaction timestamps. This distinction mirrors real-world accounting controls and ensures analytical accuracy.

Let's get started !! 
---

## Business Context

Despite steady revenue growth over multiple years, leadership seeks clarity on several strategic questions:

- Is revenue growth translating into sustainable profit growth?
- Are margins stable across customer segments?
- Is the business overly dependent on a small concentration of accounts?
- Where does customer retention risk exist?
- How should strategic focus shift to improve revenue quality?

This project approaches these questions from a financial and operational perspective, combining dimensional modeling principles with period-based revenue logic to deliver executive-ready insight.
---

## Analytical Direction

This Case Study aims to focus on:

- Period-based revenue and gross margin trends  
- Customer-level profitability segmentation  
- Revenue concentration risk assessment  
- Lifecycle and retention analysis  
- Segmentation-level performance benchmarking  
- Sales representative performance evaluation  

All queries and supporting analysis will be developed using Google BigQuery and Visualizations will be captured using Google Looker Studio.

---

## 🏗 Data Architecture

The dataset follows a dimensional modeling structure commonly used in warehouse environments, consisting of one centralized fact table supported by customer dimension tables.

---

### 📌 Fact Table: `TotalSales`

**Grain:** One row per invoice line item  

This table contains all transactional sales activity and serves as the primary analytical source.
**Columns:**
- `ItemID` (INTEGER)
- `Brand` (STRING)
- `PackSize` (STRING)
- `CustomerNumber` (INTEGER)
- `Cases` (INTEGER)
- `Pieces` (INTEGER)
- `Sales` (FLOAT)
- `Cost` (FLOAT)
- `InvoiceID` (STRING)
- `SalesPerson` (STRING)
- `Warehouse` (INTEGER)
- `Price` (FLOAT)
- `Weight` (FLOAT)
- `InvoiceDate` (DATE)
- `AccountingID` (STRING)
- `Period` (INTEGER, YYMM format – revenue recognition period)
- `BillingType` (INTEGER)
- `CustomerClass` (INTEGER)
- `OrderID` (STRING)
- `PerMonth` (INTEGER)
- `PerYear` (INTEGER)
- `PerQuarter` (STRING)

The combination of (`InvoiceID`, `ItemID`) represents a unique transaction line in this table.
`CustomerNumber` is a foreign key referencing `CustomerData(CustomerNumber)`.
`CustomerClass` is a foreign key referencing `CustomerSegmentationData(CustomerClass)`

---

### 📌 Dimension Table: `CustomerData`
**Grain:** One row per customer  
This table provides geographic, lifecycle, and classification context for each account.

**Columns:**

- `CustomerNumber` (INTEGER)
- `City` (STRING)
- `State` (STRING)
- `ZipCode` (STRING)
- `SalesPerson` (STRING)
- `DATE STARTED` (DATE)
- `CustomerClass` (INTEGER)
- `CustomerClassDescription` (STRING)

`CustomerNumber` is the primary key of this table.
`CustomerClass` is a foreign key referencing `CustomerSegmentationData(CustomerClass)`.

---

### 📌 Dimension Table: `CustomerSegmentationData`

**Grain:** One row per customer class  

This table defines structured segmentation categories used for channel and profitability analysis.

**Columns:**

- `CustomerClass` (INTEGER)
- `CustomerClassDescription` (STRING)
- `string_field_2` (STRING)
- `string_field_3` (STRING)
- `string_field_4` (STRING)
- `string_field_5` (STRING)

`CustomerClass` is the primary key of this table.

## Important to Note for Revenue Recognition Logic

While `InvoiceDate` captures transaction timing, the company recognizes revenue using the `Period` field.
- `Period` follows a **YYMM format**
- Example:
  - `2201` = January 2022
  - `2112` = December 2021

All financial reporting and erformance evaluation are based on `Period`, not invoice date.  
This mirrors real-world accounting standards and ensures reporting consistency across the organization.

---

## 🎯 Business Objectives

The analysis addresses the following executive questions:

1. How has recognized revenue trended over time?
2. Is revenue growth translating into profit growth?
3. Are we overly dependent on a small subset of customers?
4. Which customer segments generate the strongest margins?
5. Where are we experiencing customer churn or revenue risk?
