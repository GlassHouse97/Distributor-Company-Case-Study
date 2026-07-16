"""Run Question 1 customer-segment profitability analysis."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "distributor_case_study.sqlite"
SQL_DIR = PROJECT_ROOT / "SOLUTION" / "sql"
OUTPUT_DIR = PROJECT_ROOT / "SOLUTION" / "outputs"
VISUAL_DIR = PROJECT_ROOT / "SOLUTION" / "visualizations"
SUMMARY_PATH = OUTPUT_DIR / "01_analysis_summary.json"

QUERY_OUTPUTS = {
    "01_segment_profitability.sql": "01_segment_profitability.csv",
    "01_segment_growth.sql": "01_segment_growth.csv",
    "01_validation_checks.sql": "01_validation_checks.csv",
}

NAVY = "#173B57"
BLUE = "#2F75B5"
LIGHT_BLUE = "#A9C8E5"
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


def create_chart(segment: pd.DataFrame) -> None:
    top = segment.nsmallest(10, "revenue_rank").copy().iloc[::-1]
    image = Image.new("RGB", (1600, 1020), WHITE)
    draw = ImageDraw.Draw(image)
    title_font = load_font(42, bold=True)
    subtitle_font = load_font(23)
    label_font = load_font(21, bold=True)
    small_font = load_font(18)
    value_font = load_font(18, bold=True)

    draw.text((70, 50), "Which Segments Drive Revenue and Profit?", font=title_font, fill=NAVY)
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

    label_left, plot_left, plot_right = 70, 585, 1515
    plot_top, plot_bottom, max_share = 190, 905, 55.0
    row_height = (plot_bottom - plot_top) / len(top)
    for tick in range(0, 56, 10):
        x = plot_left + (plot_right - plot_left) * tick / max_share
        draw.line((x, plot_top - 18, x, plot_bottom + 5), fill=LIGHT_GRAY, width=2)
        draw.text((x - 12, plot_bottom + 18), f"{tick}%", font=small_font, fill=GRAY)

    for row_index, row in enumerate(top.itertuples(index=False)):
        y = plot_top + row_index * row_height
        description = str(row.customer_class_description)
        if len(description) > 39:
            description = description[:36] + "..."
        draw.text(
            (label_left, y + 13),
            f"{row.customer_class}  {description}",
            font=label_font,
            fill=DARK,
        )
        draw.text((label_left, y + 42), f"Margin {row.gross_margin_pct:.1f}%", font=small_font, fill=GRAY)
        revenue_width = (plot_right - plot_left) * row.revenue_share_pct / max_share
        profit_width = (plot_right - plot_left) * row.gross_profit_share_pct / max_share
        draw.rounded_rectangle(
            (plot_left, y + 10, plot_left + revenue_width, y + 30), radius=7, fill=LIGHT_BLUE
        )
        draw.rounded_rectangle(
            (plot_left, y + 38, plot_left + profit_width, y + 58), radius=7, fill=BLUE
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
        "A segment contributes more profit than revenue when its dark-blue bar is longer.",
        font=small_font,
        fill=GRAY,
    )
    path = VISUAL_DIR / "01_segment_profitability.png"
    image.save(path, format="PNG", optimize=True)
    print(path)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    results: dict[str, pd.DataFrame] = {}
    with sqlite3.connect(DATABASE_PATH) as connection:
        for sql_name, output_name in QUERY_OUTPUTS.items():
            frame = pd.read_sql_query((SQL_DIR / sql_name).read_text(encoding="utf-8"), connection)
            frame.to_csv(OUTPUT_DIR / output_name, index=False)
            results[sql_name] = frame
            print(OUTPUT_DIR / output_name)

    validation = results["01_validation_checks.sql"]
    if not validation["status"].eq("PASS").all():
        failures = validation.loc[validation["status"].ne("PASS"), "check_name"].tolist()
        raise ValueError(f"Question 1 validation failed: {failures}")

    segment = results["01_segment_profitability.sql"]
    growth = results["01_segment_growth.sql"]
    if len(segment) != 64:
        raise ValueError(f"Expected 64 active segments; found {len(segment)}")

    top_segment = segment.iloc[0]
    material = segment[segment["revenue_share_pct"] >= 0.5]
    best_material_margin = material.loc[material["gross_margin_pct"].idxmax()]
    weakest_material_margin = material.loc[material["gross_margin_pct"].idxmin()]
    summary = {
        "reporting_window": {"first_period": "1801", "last_period": "2412", "months": 84},
        "active_segments": int(len(segment)),
        "top_segment": str(top_segment["customer_class_description"]),
        "top_segment_revenue_share_pct": float(top_segment["revenue_share_pct"]),
        "top_segment_gross_profit_share_pct": float(top_segment["gross_profit_share_pct"]),
        "top_segment_margin_pct": float(top_segment["gross_margin_pct"]),
        "top_three_growth_contribution_pct": float(
            growth.nlargest(3, "revenue_growth")["growth_contribution_pct"].sum()
        ),
        "best_material_margin_segment": str(best_material_margin["customer_class_description"]),
        "best_material_margin_pct": float(best_material_margin["gross_margin_pct"]),
        "weakest_material_margin_segment": str(weakest_material_margin["customer_class_description"]),
        "weakest_material_margin_pct": float(weakest_material_margin["gross_margin_pct"]),
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    print(SUMMARY_PATH)
    create_chart(segment)


if __name__ == "__main__":
    main()
