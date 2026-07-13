"""Run Questions 2-4, validate outputs, and create portfolio charts."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont

from sanitize_public_outputs import sanitize_outputs


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "distributor_case_study.sqlite"
SQL_DIR = PROJECT_ROOT / "SOLUTION" / "sql"
OUTPUT_DIR = PROJECT_ROOT / "SOLUTION" / "outputs"
VISUAL_DIR = PROJECT_ROOT / "SOLUTION" / "visualizations"
SUMMARY_PATH = OUTPUT_DIR / "02_04_analysis_summary.json"

QUERY_OUTPUTS = {
    "02_segment_profitability.sql": "02_segment_profitability.csv",
    "02_segment_growth.sql": "02_segment_growth.csv",
    "02_validation_checks.sql": "02_validation_checks.csv",
    "03_customer_concentration.sql": "03_customer_concentration.csv",
    "03_concentration_summary.sql": "03_concentration_summary.csv",
    "03_segment_concentration.sql": "03_segment_concentration.csv",
    "03_validation_checks.sql": "03_validation_checks.csv",
    "04_customer_lifecycle.sql": "04_customer_lifecycle.csv",
    "04_retention_summary.sql": "04_retention_summary.csv",
    "04_retention_by_segment.sql": "04_retention_by_segment.csv",
    "04_priority_outreach.sql": "04_priority_outreach.csv",
    "04_validation_checks.sql": "04_validation_checks.csv",
}

NAVY = "#173B57"
BLUE = "#2F75B5"
LIGHT_BLUE = "#A9C8E5"
ORANGE = "#D97732"
GREEN = "#4E9F6D"
YELLOW = "#D7A928"
RED = "#C9574D"
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


def money_millions(value: float) -> str:
    return f"${value / 1_000_000:.1f}M"


def save_chart(image: Image.Image, filename: str) -> None:
    path = VISUAL_DIR / filename
    image.save(path, format="PNG", optimize=True)
    print(path)


def chart_segment_profitability(segment: pd.DataFrame) -> None:
    top = segment.nsmallest(10, "revenue_rank").copy().iloc[::-1]
    image = Image.new("RGB", (1600, 1020), WHITE)
    draw = ImageDraw.Draw(image)
    title_font = load_font(42, bold=True)
    subtitle_font = load_font(23)
    label_font = load_font(21, bold=True)
    small_font = load_font(18)
    value_font = load_font(18, bold=True)

    draw.text((70, 50), "Segment Scale and Profit Contribution", font=title_font, fill=NAVY)
    draw.text(
        (70, 108),
        "Top 10 historical customer segments | Complete reporting years 2018-2024",
        font=subtitle_font,
        fill=GRAY,
    )
    draw.rectangle((1040, 70, 1068, 90), fill=LIGHT_BLUE)
    draw.text((1080, 66), "Revenue share", font=small_font, fill=DARK)
    draw.rectangle((1270, 70, 1298, 90), fill=BLUE)
    draw.text((1310, 66), "Gross-profit share", font=small_font, fill=DARK)

    label_left = 70
    plot_left = 585
    plot_right = 1515
    plot_top = 190
    plot_bottom = 905
    max_share = 55.0
    row_height = (plot_bottom - plot_top) / len(top)

    for tick in range(0, 56, 10):
        x = plot_left + (plot_right - plot_left) * tick / max_share
        draw.line((x, plot_top - 18, x, plot_bottom + 5), fill=LIGHT_GRAY, width=2)
        draw.text((x - 12, plot_bottom + 18), f"{tick}%", font=small_font, fill=GRAY)

    for row_index, row in enumerate(top.itertuples(index=False)):
        y = plot_top + row_index * row_height
        description = str(row.customer_class_description).replace("–", "-").replace("—", "-")
        if len(description) > 39:
            description = description[:36] + "..."
        draw.text(
            (label_left, y + 13),
            f"{row.customer_class}  {description}",
            font=label_font,
            fill=DARK,
        )
        draw.text(
            (label_left, y + 42),
            f"Margin {row.gross_margin_pct:.1f}%",
            font=small_font,
            fill=GRAY,
        )

        revenue_width = (plot_right - plot_left) * row.revenue_share_pct / max_share
        profit_width = (plot_right - plot_left) * row.gross_profit_share_pct / max_share
        draw.rounded_rectangle(
            (plot_left, y + 10, plot_left + revenue_width, y + 30),
            radius=7,
            fill=LIGHT_BLUE,
        )
        draw.rounded_rectangle(
            (plot_left, y + 38, plot_left + profit_width, y + 58),
            radius=7,
            fill=BLUE,
        )
        draw.text(
            (min(plot_left + revenue_width + 9, 1535), y + 9),
            f"{row.revenue_share_pct:.1f}%",
            font=value_font,
            fill=DARK,
            anchor="lm",
        )
        draw.text(
            (min(plot_left + profit_width + 9, 1535), y + 37),
            f"{row.gross_profit_share_pct:.1f}%",
            font=value_font,
            fill=DARK,
            anchor="lm",
        )

    draw.text(
        (70, 970),
        "A segment creates favorable mix when its gross-profit share exceeds its revenue share.",
        font=small_font,
        fill=GRAY,
    )
    save_chart(image, "02_segment_profitability.png")


def chart_customer_concentration(customer: pd.DataFrame, summary: pd.Series) -> None:
    image = Image.new("RGB", (1600, 930), WHITE)
    draw = ImageDraw.Draw(image)
    title_font = load_font(42, bold=True)
    subtitle_font = load_font(23)
    label_font = load_font(19)
    callout_font = load_font(20, bold=True)

    draw.text((70, 48), "Customer Revenue Is Broadly Distributed", font=title_font, fill=NAVY)
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
    save_chart(image, "03_customer_concentration.png")


def chart_retention_risk(retention: pd.DataFrame, revenue_2024: float) -> None:
    image = Image.new("RGB", (1600, 820), WHITE)
    draw = ImageDraw.Draw(image)
    title_font = load_font(42, bold=True)
    subtitle_font = load_font(23)
    label_font = load_font(23, bold=True)
    segment_font = load_font(18, bold=True)
    note_font = load_font(19)

    draw.text((70, 52), "Customer Inactivity Is Concentrated in the Dormant Tail", font=title_font, fill=NAVY)
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
    customer_y = 300
    risk_y = 530
    bar_height = 86

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
        "Dormant revenue is a reactivation opportunity indicator, not a forecast of future loss.",
        font=note_font,
        fill=GRAY,
    )
    save_chart(image, "04_retention_risk.png")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, pd.DataFrame] = {}

    with sqlite3.connect(DATABASE_PATH) as connection:
        for sql_name, output_name in QUERY_OUTPUTS.items():
            query = (SQL_DIR / sql_name).read_text(encoding="utf-8")
            frame = pd.read_sql_query(query, connection)
            frame.to_csv(OUTPUT_DIR / output_name, index=False)
            results[sql_name] = frame
            print(OUTPUT_DIR / output_name)

    sanitized_customer_count = sanitize_outputs(OUTPUT_DIR)
    print(f"Anonymized {sanitized_customer_count:,} customer identifiers in public outputs")

    for sql_name in (
        "02_validation_checks.sql",
        "03_validation_checks.sql",
        "04_validation_checks.sql",
    ):
        validation = results[sql_name]
        if not validation["status"].eq("PASS").all():
            failures = validation.loc[validation["status"].ne("PASS"), "check_name"].tolist()
            raise ValueError(f"Validation failed for {sql_name}: {failures}")

    segment = results["02_segment_profitability.sql"]
    segment_growth = results["02_segment_growth.sql"]
    customer = results["03_customer_concentration.sql"]
    concentration = results["03_concentration_summary.sql"].iloc[0]
    lifecycle = results["04_customer_lifecycle.sql"]
    retention = results["04_retention_summary.sql"]
    retention_segment = results["04_retention_by_segment.sql"]
    priority = results["04_priority_outreach.sql"]

    if len(segment) != 64:
        raise ValueError(f"Expected 64 active segments; found {len(segment)}")
    if len(customer) != 3230 or len(lifecycle) != 3230:
        raise ValueError("Customer concentration and lifecycle outputs must each contain 3,230 customers")
    if len(retention) != 5 or len(priority) != 100:
        raise ValueError("Retention summary or priority output has an unexpected row count")

    top_segment = segment.iloc[0]
    material = segment[segment["revenue_share_pct"] >= 0.5]
    best_material_margin = material.loc[material["gross_margin_pct"].idxmax()]
    weakest_material_margin = material.loc[material["gross_margin_pct"].idxmin()]
    growth_top_three = float(segment_growth.nlargest(3, "revenue_growth")["growth_contribution_pct"].sum())
    total_risk = float(retention["revenue_at_risk"].sum())
    revenue_2024 = 130_976_372.66
    top_risk_segment = retention_segment.iloc[0]

    summary = {
        "reporting_window": {"first_period": "1801", "last_period": "2412", "months": 84},
        "question_2": {
            "active_segments": int(len(segment)),
            "top_segment": str(top_segment["customer_class_description"]),
            "top_segment_revenue_share_pct": float(top_segment["revenue_share_pct"]),
            "top_segment_gross_profit_share_pct": float(top_segment["gross_profit_share_pct"]),
            "top_segment_margin_pct": float(top_segment["gross_margin_pct"]),
            "top_three_growth_contribution_pct": growth_top_three,
            "best_material_margin_segment": str(best_material_margin["customer_class_description"]),
            "best_material_margin_pct": float(best_material_margin["gross_margin_pct"]),
            "weakest_material_margin_segment": str(weakest_material_margin["customer_class_description"]),
            "weakest_material_margin_pct": float(weakest_material_margin["gross_margin_pct"]),
        },
        "question_3": {
            key: (int(value) if key in {
                "total_customers", "positive_revenue_customers", "zero_revenue_customers",
                "negative_revenue_customers", "customers_to_50_pct", "customers_to_80_pct",
                "customers_to_90_pct", "active_segments", "segments_to_80_pct"
            } else float(value))
            for key, value in concentration.to_dict().items()
        },
        "question_4": {
            "total_revenue_at_risk": total_risk,
            "revenue_at_risk_pct_of_2024_revenue": 100.0 * total_risk / revenue_2024,
            "top_risk_segment": str(top_risk_segment["customer_class_description"]),
            "top_risk_segment_share_pct": float(top_risk_segment["revenue_at_risk_share_pct"]),
            "priority_customer_count": int(len(priority)),
            "buckets": json.loads(retention.to_json(orient="records")),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    print(SUMMARY_PATH)

    chart_segment_profitability(segment)
    chart_customer_concentration(customer, concentration)
    chart_retention_risk(retention, revenue_2024)


if __name__ == "__main__":
    main()
