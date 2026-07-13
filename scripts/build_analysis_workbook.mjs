import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const PROJECT_ROOT = path.resolve(SCRIPT_DIR, "..");
const OUTPUTS = path.join(PROJECT_ROOT, "SOLUTION", "outputs");
const DELIVERABLES = path.join(PROJECT_ROOT, "deliverables");
const PREVIEW_DIR = process.argv[2] || path.join(os.tmpdir(), "distro-workbook-previews");
const OUTPUT_PATH = path.join(DELIVERABLES, "Distributor_Case_Study_Analysis.xlsx");
const BUNDLED_MODULES = process.env.CODEX_NODE_MODULES ||
  path.join(os.homedir(), ".cache", "codex-runtimes", "codex-primary-runtime", "dependencies", "node", "node_modules");

const bundleRequire = createRequire(pathToFileURL(path.join(BUNDLED_MODULES, "_anchor.js")));
const artifactEntry = bundleRequire.resolve("@oai/artifact-tool");
const { SpreadsheetFile, Workbook } = await import(pathToFileURL(artifactEntry).href);

const NAVY = "#17365D";
const BLUE = "#2F75B5";
const LIGHT_BLUE = "#D9EAF7";
const PALE = "#F4F7FA";
const GRID = "#D6DEE8";
const INK = "#1F2937";
const MUTED = "#64748B";
const GREEN = "#2E8B57";
const GOLD = "#D9A520";
const ORANGE = "#D9772A";
const RED = "#C7524A";

function parseCsv(text) {
  const rows = [];
  let row = [];
  let value = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') {
        value += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        value += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(value);
      value = "";
    } else if (char === "\n") {
      row.push(value.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      value = "";
    } else {
      value += char;
    }
  }
  if (value.length || row.length) {
    row.push(value.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows;
}

function prettyHeader(value) {
  return value
    .replace(/_/g, " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase())
    .replace(/Pct\b/g, "%")
    .replace(/Pp\b/g, "pp")
    .replace(/Gp\b/g, "GP")
    .replace(/Hhi\b/g, "HHI");
}

function isThresholdCount(header) {
  return ["customers_to_50_pct", "customers_to_80_pct", "customers_to_90_pct"].includes(header);
}

function isPercentHeader(header) {
  return header.includes("_pct") && !isThresholdCount(header);
}

function convertValue(header, value) {
  if (value === "" || value === "NaN") return null;
  value = value.replace(/–|—/g, "-");
  const textColumns = new Set([
    "customer_number", "customer_class", "last_active_period", "latest_period",
    "period", "check_name", "status", "expected_value", "customer_class_description",
    "churn_risk_bucket"
  ]);
  if (textColumns.has(header)) return value;
  if (/^-?\d+(?:\.\d+)?$/.test(value)) {
    const number = Number(value);
    return isPercentHeader(header) ? number / 100 : number;
  }
  return value;
}

async function loadCsv(name) {
  const rows = parseCsv(await fs.readFile(path.join(OUTPUTS, name), "utf8"));
  const headers = rows[0];
  return {
    headers,
    values: rows.slice(1).filter((row) => row.some((cell) => cell !== "")).map(
      (row) => headers.map((header, index) => convertValue(header, row[index] ?? ""))
    ),
  };
}

function styleTitle(sheet, title, subtitle, lastColumn) {
  sheet.mergeCells(`A1:${lastColumn}1`);
  sheet.getRange("A1").values = [[title]];
  sheet.getRange("A1").format = {
    fill: NAVY,
    font: { bold: true, color: "#FFFFFF", size: 18 },
    rowHeight: 32,
    verticalAlignment: "center",
  };
  sheet.mergeCells(`A2:${lastColumn}2`);
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange("A2").format = {
    fill: LIGHT_BLUE,
    font: { italic: true, color: MUTED, size: 10 },
    rowHeight: 24,
    verticalAlignment: "center",
  };
  sheet.showGridLines = false;
}

function styleTable(sheet, range, headerRow, tableName) {
  const table = sheet.tables.add(range, true, tableName);
  table.style = "TableStyleMedium2";
  table.showBandedRows = true;
  table.showFilterButton = true;
  sheet.getRange(headerRow).format = {
    fill: BLUE,
    font: { bold: true, color: "#FFFFFF" },
    wrapText: true,
    verticalAlignment: "center",
    borders: { preset: "all", style: "thin", color: GRID },
  };
  return table;
}

function colName(index) {
  let value = index + 1;
  let result = "";
  while (value > 0) {
    const rem = (value - 1) % 26;
    result = String.fromCharCode(65 + rem) + result;
    value = Math.floor((value - 1) / 26);
  }
  return result;
}

function applyFormats(sheet, headers, startRow, rowCount) {
  headers.forEach((header, index) => {
    const column = colName(index);
    const range = sheet.getRange(`${column}${startRow}:${column}${startRow + rowCount - 1}`);
    if (isPercentHeader(header)) range.format.numberFormat = "0.00%";
    else if (header.endsWith("_pp")) range.format.numberFormat = '0.00 "pp"';
    else if (/rank|customer_count|customers_|transaction_rows|reported_months|months_/.test(header)) {
      range.format.numberFormat = "#,##0";
    } else if (/revenue|cost|gross_profit/.test(header) && !header.includes("share")) {
      range.format.numberFormat = "$#,##0.00;[Red]-$#,##0.00";
    }
  });
}

function addDataSheet(workbook, name, title, subtitle, data, tableName, options = {}) {
  const sheet = workbook.worksheets.getOrAdd(name);
  const columns = data.headers.length;
  const lastColumn = colName(columns - 1);
  styleTitle(sheet, title, subtitle, lastColumn);
  const matrix = [data.headers.map(prettyHeader), ...data.values];
  sheet.getRange(`A4:${lastColumn}${3 + matrix.length}`).values = matrix;
  styleTable(sheet, `A4:${lastColumn}${3 + matrix.length}`, `A4:${lastColumn}4`, tableName);
  applyFormats(sheet, data.headers, 5, data.values.length);
  sheet.freezePanes.freezeRows(4);
  sheet.getRange(`A4:${lastColumn}${3 + matrix.length}`).format.wrapText = false;
  sheet.getRange(`A4:${lastColumn}${3 + matrix.length}`).format.autofitColumns();
  sheet.getRange(`A4:${lastColumn}${3 + matrix.length}`).format.autofitRows();
  if (options.descriptionColumn) sheet.getRange(`${options.descriptionColumn}:${options.descriptionColumn}`).format.columnWidth = 34;
  if (options.maxColumnWidths) {
    Object.entries(options.maxColumnWidths).forEach(([column, width]) => {
      sheet.getRange(`${column}:${column}`).format.columnWidth = width;
    });
  }
  return sheet;
}

const [annual, segment, segmentGrowth, concentration, customerConcentration, segmentConcentration,
  retention, retentionSegment, outreach, q1Checks, q2Checks, q3Checks, q4Checks] = await Promise.all([
  loadCsv("01_annual_revenue_margin.csv"),
  loadCsv("02_segment_profitability.csv"),
  loadCsv("02_segment_growth.csv"),
  loadCsv("03_concentration_summary.csv"),
  loadCsv("03_customer_concentration.csv"),
  loadCsv("03_segment_concentration.csv"),
  loadCsv("04_retention_summary.csv"),
  loadCsv("04_retention_by_segment.csv"),
  loadCsv("04_priority_outreach.csv"),
  loadCsv("01_validation_checks.csv"),
  loadCsv("02_validation_checks.csv"),
  loadCsv("03_validation_checks.csv"),
  loadCsv("04_validation_checks.csv"),
]);

const workbook = Workbook.create();

// Formula targets must exist before cross-sheet formulas are assigned.
["Annual Trend", "Segment Profitability", "Concentration", "Retention Summary"].forEach(
  (name) => workbook.worksheets.add(name)
);

const executive = workbook.worksheets.add("Executive Summary");
styleTitle(
  executive,
  "Revenue Quality & Customer Profitability",
  "Executive summary | Recognized-period analysis, 2018–2024",
  "L"
);
executive.getRange("A4:B4").values = [["Portfolio KPI", "Validated result"]];
executive.getRange("A5:A12").values = [
  ["2018–2024 revenue growth"],
  ["2018–2024 gross-profit growth"],
  ["2024 gross margin"],
  ["Largest segment revenue share"],
  ["Largest customer revenue share"],
  ["Customers needed for 80% of revenue"],
  ["Trailing revenue baseline at risk"],
  ["Risk baseline as % of 2024 revenue"],
];
executive.getRange("B5:B12").formulas = [
  ["='Annual Trend'!D11/'Annual Trend'!D5-1"],
  ["='Annual Trend'!F11/'Annual Trend'!F5-1"],
  ["='Annual Trend'!G11"],
  ["='Segment Profitability'!I5"],
  ["='Concentration'!M5"],
  ["='Concentration'!M9"],
  ["=SUM('Retention Summary'!E6:E8)"],
  ["=B11/'Annual Trend'!D11"],
];
executive.getRange("B5:B9").format.numberFormat = "0.00%";
executive.getRange("B10").format.numberFormat = "#,##0";
executive.getRange("B11").format.numberFormat = "$#,##0.00";
executive.getRange("B12").format.numberFormat = "0.00%";
executive.getRange("A4:B12").format.borders = { preset: "all", style: "thin", color: GRID };
executive.getRange("A4:B4").format = { fill: BLUE, font: { bold: true, color: "#FFFFFF" } };
executive.getRange("A5:A12").format = { fill: PALE, font: { bold: true, color: INK } };
executive.getRange("A:A").format.columnWidth = 36;
executive.getRange("B:B").format.columnWidth = 20;
executive.getRange("D4:L4").merge();
executive.getRange("D4").values = [["Executive conclusion"]];
executive.getRange("D4").format = { fill: NAVY, font: { bold: true, color: "#FFFFFF", size: 12 } };
executive.getRange("D5:L7").merge();
executive.getRange("D5").values = [[
  "Growth is profitable and individual-customer dependency is low. The highest-value next moves are to protect the Independent Retail core, improve economics in large margin-light segments, and operationalize value-based retention outreach."
]];
executive.getRange("D5:L7").format = { fill: PALE, wrapText: true, verticalAlignment: "top", font: { color: INK, size: 11 } };
executive.getRange("D9:L9").merge();
executive.getRange("D9").values = [["Prioritized actions"]];
executive.getRange("D9").format = { fill: BLUE, font: { bold: true, color: "#FFFFFF", size: 12 } };
executive.mergeCells("E10:H10"); executive.mergeCells("I10:L10");
executive.mergeCells("E11:H11"); executive.mergeCells("I11:L11");
executive.mergeCells("E12:H12"); executive.mergeCells("I12:L12");
executive.getRange("D10:D12").values = [["1"], ["2"], ["3"]];
executive.getRange("E10:E12").values = [
  ["Protect Independent Retail while expanding high-margin segments"],
  ["Launch a monthly value-based retention queue"],
  ["Review pricing and cost-to-serve in margin-light segments"],
];
executive.getRange("I10:I12").values = [
  ["Defend the main profit pool and improve diversification"],
  ["Prioritize recent, high-value risk and measure reactivation"],
  ["Convert existing scale into incremental gross profit"],
];
executive.getRange("D10:D12").format = { fill: LIGHT_BLUE, font: { bold: true, color: NAVY }, horizontalAlignment: "center" };
executive.getRange("E10:L12").format = { wrapText: true, verticalAlignment: "top", borders: { preset: "all", style: "thin", color: GRID } };
executive.getRange("D10:L12").format.rowHeight = 36;
executive.getRange("D:D").format.columnWidth = 5;
executive.getRange("E:H").format.columnWidth = 15;
executive.getRange("I:L").format.columnWidth = 14;
executive.showGridLines = false;
executive.freezePanes.freezeRows(2);

const annualSheet = addDataSheet(
  workbook, "Annual Trend", "Annual Revenue and Margin Trend",
  "Seven complete recognized-reporting years; returns and adjustments retained",
  annual, "AnnualTrendTable", { maxColumnWidths: { A: 11 } }
);
annualSheet.getRange("L4:N11").values = [
  ["Year", "Revenue ($M)", "Gross Profit ($M)"],
  ...annual.values.map((row) => [row[0], row[3] / 1_000_000, row[5] / 1_000_000]),
];
annualSheet.getRange("M5:N11").format.numberFormat = "$0.0";
const annualChart = annualSheet.charts.add("line", annualSheet.getRange("L4:N11"));
annualChart.title = "Revenue and Gross Profit Growth ($M)";
annualChart.hasLegend = true;
annualChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
annualChart.yAxis = { numberFormatCode: "$0.0", min: 0 };
annualChart.setPosition("L13", "T31");

addDataSheet(
  workbook, "Segment Profitability", "Customer Segment Profitability",
  "Historical transaction class is the reporting authority | 2018–2024",
  segment, "SegmentProfitabilityTable", { descriptionColumn: "B", maxColumnWidths: { A: 15 } }
);
addDataSheet(
  workbook, "Segment Growth", "Segment Growth Contribution",
  "Full-year 2018 compared with full-year 2024; blank rates indicate a zero base",
  segmentGrowth, "SegmentGrowthTable", { descriptionColumn: "B", maxColumnWidths: { A: 15 } }
);

const concentrationRows = customerConcentration.values.slice(0, 100);
const concentrationData = {
  headers: customerConcentration.headers,
  values: concentrationRows,
};
const concentrationSheet = addDataSheet(
  workbook, "Concentration", "Revenue Concentration",
  "Summary metrics and top 100 anonymized customers by net recognized revenue",
  concentrationData, "TopCustomerConcentrationTable", { maxColumnWidths: { A: 15 } }
);
concentrationSheet.getRange("L4:M4").values = [["Concentration Metric", "Value"]];
const metricLabels = [
  "Top 1 customer", "Top 10 customers", "Top 100 customers", "Customers to 50%",
  "Customers to 80%", "Customers to 90%", "Top segment", "Top 3 segments", "Segment HHI"
];
concentrationSheet.getRange("L5:L13").values = metricLabels.map((label) => [label]);
const c = concentration.values[0];
concentrationSheet.getRange("M5:M13").values = [[c[4]], [c[5]], [c[6]], [c[7]], [c[9]], [c[11]], [c[15]], [c[16]], [c[19]]];
concentrationSheet.getRange("M5:M7").format.numberFormat = "0.00%";
concentrationSheet.getRange("M11:M12").format.numberFormat = "0.00%";
concentrationSheet.getRange("L4:M13").format.borders = { preset: "all", style: "thin", color: GRID };
concentrationSheet.getRange("L4:M4").format = { fill: NAVY, font: { bold: true, color: "#FFFFFF" } };
concentrationSheet.getRange("L5:L13").format = { fill: PALE, font: { bold: true } };
concentrationSheet.getRange("L:L").format.columnWidth = 23;
concentrationSheet.getRange("M:M").format.columnWidth = 15;

addDataSheet(
  workbook, "Segment Concentration", "Segment Revenue Concentration",
  "Historical customer segments ranked by recognized revenue",
  segmentConcentration, "SegmentConcentrationTable", { descriptionColumn: "B", maxColumnWidths: { A: 15 } }
);
addDataSheet(
  workbook, "Retention Summary", "Customer Lifecycle and Revenue at Risk",
  "Status measured at December 2024; risk is a trailing historical baseline, not a forecast",
  retention, "RetentionSummaryTable", { descriptionColumn: "A" }
);
addDataSheet(
  workbook, "Retention by Segment", "Retention Risk by Customer Segment",
  "Risky customers include Watch, At Risk, and Dormant lifecycle groups",
  retentionSegment, "RetentionBySegmentTable", { descriptionColumn: "B", maxColumnWidths: { A: 15 } }
);
const outreachSheet = addDataSheet(
  workbook, "Outreach Priorities", "At-Risk Customer Outreach Priorities",
  "Top 100 anonymized customers inactive 7–12 months, ranked by trailing revenue baseline",
  outreach, "OutreachPriorityTable", { descriptionColumn: "C", maxColumnWidths: { A: 15, B: 15 } }
);

for (const [sheet, range] of [
  [concentrationSheet, "A5:A104"],
  [outreachSheet, "A5:A104"],
]) {
  const labels = sheet.getRange(range).values.flat().filter((value) => value !== null);
  if (!labels.every((value) => /^CUSTOMER_\d+$/.test(String(value)))) {
    throw new Error(`Non-anonymized customer identifier found in ${sheet.name}!${range}`);
  }
}

const validation = workbook.worksheets.add("Validation");
styleTitle(validation, "Analysis Validation", "Automated checks for Questions 1–4", "E");
const validationRows = [];
[
  ["Q1", q1Checks], ["Q2", q2Checks], ["Q3", q3Checks], ["Q4", q4Checks]
].forEach(([question, dataset]) => {
  dataset.values.forEach((row) => validationRows.push([question, ...row]));
});
validation.getRange(`A4:E${4 + validationRows.length}`).values = [
  ["Question", "Check", "Actual", "Expected", "Status"],
  ...validationRows,
];
styleTable(validation, `A4:E${4 + validationRows.length}`, "A4:E4", "AnalysisValidationTable");
validation.getRange("A:E").format.autofitColumns();
validation.getRange("B:B").format.columnWidth = 38;
validation.getRange("E5:E100").format.font = { bold: true, color: GREEN };
validation.freezePanes.freezeRows(4);

await fs.mkdir(DELIVERABLES, { recursive: true });
await fs.mkdir(PREVIEW_DIR, { recursive: true });

const previewSheets = [
  "Executive Summary", "Annual Trend", "Segment Profitability", "Segment Growth",
  "Concentration", "Segment Concentration", "Retention Summary", "Retention by Segment",
  "Outreach Priorities", "Validation"
];
for (const sheetName of previewSheets) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 0.9, format: "png" });
  const safeName = sheetName.toLowerCase().replace(/[^a-z0-9]+/g, "-");
  await fs.writeFile(path.join(PREVIEW_DIR, `${safeName}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const inspected = await workbook.inspect({
  kind: "table",
  range: "Executive Summary!A1:L12",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 14,
});
await fs.writeFile(path.join(PREVIEW_DIR, "executive-inspect.json"), JSON.stringify(inspected, null, 2));

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
await fs.writeFile(path.join(PREVIEW_DIR, "formula-errors.json"), JSON.stringify(errors, null, 2));

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(OUTPUT_PATH);
await fs.rm(`${OUTPUT_PATH}.inspect.ndjson`, { force: true });

console.log(OUTPUT_PATH);
console.log(PREVIEW_DIR);
