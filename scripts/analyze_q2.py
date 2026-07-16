"""Run Question 2 customer and segment concentration analysis."""

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
SUMMARY_PATH = OUTPUT_DIR / "02_analysis_summary.json"

QUERY_OUTPUTS = {
    "02_customer_concentration.sql": "02_customer_concentration.csv",
    "02_concentration_summary.sql": "02_concentration_summary.csv",
    "02_segment_concentration.sql": "02_segment_concentration.csv",
    "02_validation_checks.sql": "02_validation_checks.csv",
}

NAVY = "#173B57"
BLUE = "#2F75B5"
ORANGE = "#D97732"
GRAY = "#718096"
LIGHT_GRAY = "#DCE3E8"
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


def create_chart(customer: pd.DataFrame, summary: pd.Series) -> None:
    image = Image.new("RGB", (1600, 930), WHITE)
    draw = ImageDraw.Draw(image)
    title_font = load_font(42, bold=True)
    subtitle_font = load_font(23)
    label_font = load_font(19)
    callout_font = load_font(20, bold=True)

    draw.text((70, 48), "Revenue Is Spread Across Many Customers", font=title_font, fill=NAVY)
    draw.text(
        (70, 106),
        "Cumulative recognized revenue by share of customer portfolio | 2018-2024",
        font=subtitle_font,
        fill=GRAY,
    )
    left, top, right, bottom = 120, 185, 1510, 790
    for tick in range(0, 101, 20):
        x = left + (right - left) * tick / 100
        y = bottom - (bottom - top) * tick / 100
        draw.line((x, top, x, bottom), fill=LIGHT_GRAY, width=2)
        draw.line((left, y, right, y), fill=LIGHT_GRAY, width=2)
        draw.text((x, bottom + 18), f"{tick}%", font=label_font, fill=GRAY, anchor="ma")
        draw.text((left - 18, y), f"{tick}%", font=label_font, fill=GRAY, anchor="rm")

    draw.line((left, bottom, right, top), fill="#B8C2CC", width=2)
    points = []
    for row in customer.itertuples(index=False):
        x = left + (right - left) * float(row.cumulative_customer_pct) / 100
        y_value = min(max(float(row.cumulative_revenue_pct), 0), 102)
        y = bottom - (bottom - top) * y_value / 100
        points.append((x, y))
    draw.line(points, fill=BLUE, width=5, joint="curve")

    thresholds = [
        (50, int(summary.customers_to_50_pct), float(summary.customer_pct_to_50_revenue)),
        (80, int(summary.customers_to_80_pct), float(summary.customer_pct_to_80_revenue)),
        (90, int(summary.customers_to_90_pct), float(summary.customer_pct_to_90_revenue)),
    ]
    for revenue_pct, count, customer_pct in thresholds:
        x = left + (right - left) * customer_pct / 100
        y = bottom - (bottom - top) * revenue_pct / 100
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=ORANGE)
        draw.text(
            (x + 15, y - 30),
            f"{revenue_pct}% revenue\n{count:,} customers ({customer_pct:.1f}%)",
            font=callout_font,
            fill=DARK,
            spacing=3,
        )

    draw.text((left, 825), "Cumulative share of customers", font=label_font, fill=DARK)
    draw.text((70, 500), "Cumulative\nrevenue", font=label_font, fill=DARK, anchor="mm")
    draw.text(
        (940, 840),
        f"Top customer: {summary.top_1_customer_share_pct:.1f}%  |  "
        f"Top 10: {summary.top_10_customer_share_pct:.1f}%  |  "
        f"Top 100: {summary.top_100_customer_share_pct:.1f}%",
        font=callout_font,
        fill=NAVY,
    )
    path = VISUAL_DIR / "02_customer_concentration.png"
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

    validation = results["02_validation_checks.sql"]
    if not validation["status"].eq("PASS").all():
        failures = validation.loc[validation["status"].ne("PASS"), "check_name"].tolist()
        raise ValueError(f"Question 2 validation failed: {failures}")

    customer = results["02_customer_concentration.sql"]
    concentration = results["02_concentration_summary.sql"].iloc[0]
    if len(customer) != 3230:
        raise ValueError(f"Expected 3,230 customers; found {len(customer):,}")

    customer["customer_number"] = apply_public_labels(customer["customer_number"], public_id_map)
    for sql_name, output_name in QUERY_OUTPUTS.items():
        results[sql_name].to_csv(OUTPUT_DIR / output_name, index=False)
        print(OUTPUT_DIR / output_name)

    integer_fields = {
        "total_customers",
        "positive_revenue_customers",
        "zero_revenue_customers",
        "negative_revenue_customers",
        "customers_to_50_pct",
        "customers_to_80_pct",
        "customers_to_90_pct",
        "active_segments",
        "segments_to_80_pct",
    }
    summary = {
        key: int(value) if key in integer_fields else float(value)
        for key, value in concentration.to_dict().items()
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    print(SUMMARY_PATH)
    create_chart(customer, concentration)


if __name__ == "__main__":
    main()
