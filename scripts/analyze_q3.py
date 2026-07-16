"""Run Question 3 customer lifecycle and retention-risk analysis."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from sanitize_public_outputs import apply_public_labels, build_public_id_map


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "distributor_case_study.sqlite"
SQL_DIR = PROJECT_ROOT / "SOLUTION" / "sql"
OUTPUT_DIR = PROJECT_ROOT / "SOLUTION" / "outputs"
VISUAL_DIR = PROJECT_ROOT / "SOLUTION" / "visualizations"
SUMMARY_PATH = OUTPUT_DIR / "03_analysis_summary.json"

QUERY_OUTPUTS = {
    "03_customer_lifecycle.sql": "03_customer_lifecycle.csv",
    "03_retention_summary.sql": "03_retention_summary.csv",
    "03_retention_by_segment.sql": "03_retention_by_segment.csv",
    "03_priority_outreach.sql": "03_priority_outreach.csv",
    "03_validation_checks.sql": "03_validation_checks.csv",
}

NAVY = "#173B57"
GREEN = "#4E9F6D"
YELLOW = "#D7A928"
ORANGE = "#D97732"
RED = "#C9574D"
GRAY = "#718096"
DARK = "#1F2D3D"
WHITE = "#FFFFFF"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "Arial Bold.ttf" if bold else "Arial.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def money_millions(value: float) -> str:
    return f"${value / 1_000_000:.1f}M"


def create_chart(retention: pd.DataFrame, revenue_2024: float) -> None:
    image = Image.new("RGB", (1600, 820), WHITE)
    draw = ImageDraw.Draw(image)
    title_font = load_font(42, bold=True)
    subtitle_font = load_font(23)
    label_font = load_font(23, bold=True)
    segment_font = load_font(18, bold=True)
    note_font = load_font(19)

    draw.text((70, 52), "Most Inactive Revenue Sits With Dormant Customers", font=title_font, fill=NAVY)
    draw.text(
        (70, 111),
        "Lifecycle status at December 2024 and trailing-12-month revenue baseline",
        font=subtitle_font,
        fill=GRAY,
    )
    colors = {
        "Active (0-3 months)": GREEN,
        "Watch (4-6 months)": YELLOW,
        "At Risk (7-12 months)": ORANGE,
        "Dormant (13+ months)": RED,
        "No Positive Sales": GRAY,
    }
    short = {
        "Active (0-3 months)": "Active",
        "Watch (4-6 months)": "Watch",
        "At Risk (7-12 months)": "At Risk",
        "Dormant (13+ months)": "Dormant",
        "No Positive Sales": "No Positive Sales",
    }
    legend_x = 75
    for bucket in retention["churn_risk_bucket"]:
        draw.rectangle((legend_x, 165, legend_x + 24, 189), fill=colors[bucket])
        draw.text((legend_x + 34, 163), short[bucket], font=note_font, fill=DARK)
        legend_x += 250 if bucket != "No Positive Sales" else 300

    bar_left, bar_right = 240, 1510
    bar_width = bar_right - bar_left
    customer_y, risk_y, bar_height = 300, 530, 86
    draw.text((70, customer_y + 27), "Customers", font=label_font, fill=DARK)
    cursor = bar_left
    for row in retention.itertuples(index=False):
        width = bar_width * row.customer_pct / 100
        draw.rectangle((cursor, customer_y, cursor + width, customer_y + bar_height), fill=colors[row.churn_risk_bucket])
        if row.customer_pct >= 4:
            draw.text(
                (cursor + width / 2, customer_y + bar_height / 2),
                f"{row.customer_count:,}\n{row.customer_pct:.1f}%",
                font=segment_font,
                fill=WHITE,
                anchor="mm",
                align="center",
            )
        cursor += width

    draw.text((70, risk_y + 15), "Revenue\nat risk", font=label_font, fill=DARK, spacing=3)
    risky = retention[retention["revenue_at_risk"] > 0].copy()
    total_risk = float(risky["revenue_at_risk"].sum())
    cursor = bar_left
    for row in risky.itertuples(index=False):
        share = row.revenue_at_risk / total_risk * 100
        width = bar_width * share / 100
        draw.rectangle((cursor, risk_y, cursor + width, risk_y + bar_height), fill=colors[row.churn_risk_bucket])
        if share >= 5:
            draw.text(
                (cursor + width / 2, risk_y + bar_height / 2),
                f"{money_millions(row.revenue_at_risk)}\n{share:.1f}%",
                font=segment_font,
                fill=WHITE,
                anchor="mm",
                align="center",
            )
        cursor += width

    draw.text(
        (240, 690),
        f"Total trailing revenue baseline at risk: {money_millions(total_risk)} "
        f"({100 * total_risk / revenue_2024:.1f}% of 2024 revenue)",
        font=label_font,
        fill=NAVY,
    )
    draw.text(
        (240, 736),
        "This is a historical reactivation measure, not a forecast of future loss.",
        font=note_font,
        fill=GRAY,
    )
    path = VISUAL_DIR / "03_retention_risk.png"
    image.save(path, format="PNG", optimize=True)
    print(path)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, pd.DataFrame] = {}
    with sqlite3.connect(DATABASE_PATH) as connection:
        for sql_name in QUERY_OUTPUTS:
            results[sql_name] = pd.read_sql_query(
                (SQL_DIR / sql_name).read_text(encoding="utf-8"), connection
            )
        public_id_map = build_public_id_map(connection)
        revenue_2024 = float(
            connection.execute(
                "SELECT SUM(sales) FROM total_sales WHERE period BETWEEN '2401' AND '2412'"
            ).fetchone()[0]
        )

    validation = results["03_validation_checks.sql"]
    if not validation["status"].eq("PASS").all():
        failures = validation.loc[validation["status"].ne("PASS"), "check_name"].tolist()
        raise ValueError(f"Question 3 validation failed: {failures}")

    lifecycle = results["03_customer_lifecycle.sql"]
    retention = results["03_retention_summary.sql"]
    retention_segment = results["03_retention_by_segment.sql"]
    priority = results["03_priority_outreach.sql"]
    if len(lifecycle) != 3230:
        raise ValueError(f"Expected 3,230 lifecycle rows; found {len(lifecycle):,}")
    if len(retention) != 5 or len(priority) != 100:
        raise ValueError("Retention summary or priority output has an unexpected row count")

    lifecycle["customer_number"] = apply_public_labels(lifecycle["customer_number"], public_id_map)
    priority["customer_number"] = apply_public_labels(priority["customer_number"], public_id_map)
    for sql_name, output_name in QUERY_OUTPUTS.items():
        results[sql_name].to_csv(OUTPUT_DIR / output_name, index=False)
        print(OUTPUT_DIR / output_name)

    total_risk = float(retention["revenue_at_risk"].sum())
    top_risk_segment = retention_segment.iloc[0]
    summary = {
        "reporting_window": {"first_period": "1801", "last_period": "2412", "months": 84},
        "total_revenue_at_risk": total_risk,
        "revenue_at_risk_pct_of_2024_revenue": 100.0 * total_risk / revenue_2024,
        "top_risk_segment": str(top_risk_segment["customer_class_description"]),
        "top_risk_segment_share_pct": float(top_risk_segment["revenue_at_risk_share_pct"]),
        "priority_customer_count": int(len(priority)),
        "buckets": json.loads(retention.to_json(orient="records")),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    print(SUMMARY_PATH)
    create_chart(retention, revenue_2024)


if __name__ == "__main__":
    main()
