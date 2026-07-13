"""Calculate Question 1 summary metrics and create the portfolio SVG."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = PROJECT_ROOT / "SOLUTION" / "outputs"
SQL_DIR = PROJECT_ROOT / "SOLUTION" / "sql"
ANNUAL_PATH = OUTPUTS / "01_annual_revenue_margin.csv"
MONTHLY_PATH = OUTPUTS / "01_monthly_revenue_margin.csv"
SEASONALITY_PATH = OUTPUTS / "01_revenue_seasonality.csv"
VALIDATION_PATH = OUTPUTS / "01_validation_checks.csv"
ANNUAL_SQL_PATH = SQL_DIR / "01_revenue_margin_trends.sql"
MONTHLY_SQL_PATH = SQL_DIR / "01_monthly_revenue_margin.sql"
SEASONALITY_SQL_PATH = SQL_DIR / "01_revenue_seasonality.sql"
VALIDATION_SQL_PATH = SQL_DIR / "01_validation_checks.sql"
DATABASE_PATH = (
    PROJECT_ROOT / "data" / "processed" / "distributor_case_study.sqlite"
)
SUMMARY_PATH = OUTPUTS / "01_analysis_summary.json"
SVG_PATH = (
    PROJECT_ROOT
    / "SOLUTION"
    / "visualizations"
    / "01_revenue_margin_trends.svg"
)


def pct_change(first: float, last: float) -> float:
    return 100.0 * (last / first - 1.0)


def cagr(first: float, last: float, years: int) -> float:
    return 100.0 * ((last / first) ** (1.0 / years) - 1.0)


def make_svg(annual: pd.DataFrame) -> str:
    width, height = 1200, 760
    plot_left, plot_right = 115, 1080
    top_y, top_height = 170, 315
    margin_y, margin_height = 575, 105
    bar_width = 76
    years = annual["per_year"].astype(int).tolist()
    revenue = (annual["total_revenue"] / 1_000_000).tolist()
    cost = (annual["total_cost"] / 1_000_000).tolist()
    gross_profit = (annual["gross_profit"] / 1_000_000).tolist()
    margin = annual["gross_margin_pct"].tolist()
    x_positions = [
        plot_left + index * (plot_right - plot_left) / (len(years) - 1)
        for index in range(len(years))
    ]
    max_revenue = 140.0

    def top_scale(value: float) -> float:
        return top_y + top_height - value / max_revenue * top_height

    def margin_scale(value: float) -> float:
        minimum, maximum = 18.5, 22.5
        return margin_y + margin_height - (value - minimum) / (maximum - minimum) * margin_height

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title description">',
        '<title id="title">Revenue growth is translating into stronger profitability</title>',
        '<desc id="description">Stacked annual bars show recognized revenue growing from 79.4 million dollars in 2018 to 131.0 million dollars in 2024. Gross margin rises from 19.2 percent to 22.0 percent.</desc>',
        '<rect width="1200" height="760" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#20384a}.title{font-size:30px;font-weight:700}.subtitle{font-size:17px;fill:#607184}.axis{font-size:14px;fill:#607184}.label{font-size:15px;font-weight:700}.note{font-size:13px;fill:#607184}.grid{stroke:#d9e0e7;stroke-width:1}.margin-line{fill:none;stroke:#d36a32;stroke-width:4}.margin-dot{fill:#ffffff;stroke:#d36a32;stroke-width:3}</style>',
        '<text x="70" y="60" class="title">Revenue Growth Is Translating Into Stronger Profitability</text>',
        '<text x="70" y="93" class="subtitle">Recognized-period performance | Complete reporting years 2018-2024</text>',
        '<rect x="755" y="118" width="18" height="18" fill="#d8e5f1"/><text x="782" y="132" class="axis">Cost</text>',
        '<rect x="845" y="118" width="18" height="18" fill="#2b74b7"/><text x="872" y="132" class="axis">Gross profit</text>',
        '<line x1="955" y1="127" x2="980" y2="127" stroke="#d36a32" stroke-width="4"/><text x="990" y="132" class="axis">Gross margin</text>',
        '<text x="70" y="155" class="label">Recognized revenue composition ($M)</text>',
    ]

    for tick in [0, 35, 70, 105, 140]:
        y = top_scale(tick)
        parts.append(f'<line x1="{plot_left}" y1="{y:.1f}" x2="{plot_right}" y2="{y:.1f}" class="grid"/>')
        parts.append(f'<text x="65" y="{y + 5:.1f}" text-anchor="end" class="axis">${tick}</text>')

    for index, (year, x, total, annual_cost, gp) in enumerate(
        zip(years, x_positions, revenue, cost, gross_profit)
    ):
        cost_y = top_scale(annual_cost)
        total_y = top_scale(total)
        bottom_y = top_scale(0)
        parts.append(
            f'<rect x="{x - bar_width / 2:.1f}" y="{cost_y:.1f}" width="{bar_width}" height="{bottom_y - cost_y:.1f}" fill="#d8e5f1"/>'
        )
        parts.append(
            f'<rect x="{x - bar_width / 2:.1f}" y="{total_y:.1f}" width="{bar_width}" height="{cost_y - total_y:.1f}" fill="#2b74b7"/>'
        )
        parts.append(f'<text x="{x:.1f}" y="{bottom_y + 28:.1f}" text-anchor="middle" class="axis">{year}</text>')
        if index in (0, len(years) - 1):
            parts.append(f'<text x="{x:.1f}" y="{total_y - 10:.1f}" text-anchor="middle" class="label">${total:.1f}M</text>')

    parts.extend(
        [
            '<text x="70" y="550" class="label">Gross margin</text>',
        ]
    )
    for tick in [19, 20, 21, 22]:
        y = margin_scale(tick)
        parts.append(f'<line x1="{plot_left}" y1="{y:.1f}" x2="{plot_right}" y2="{y:.1f}" class="grid"/>')
        parts.append(f'<text x="65" y="{y + 5:.1f}" text-anchor="end" class="axis">{tick}%</text>')

    path_points = " ".join(
        f"{'M' if index == 0 else 'L'} {x:.1f} {margin_scale(value):.1f}"
        for index, (x, value) in enumerate(zip(x_positions, margin))
    )
    parts.append(f'<path d="{path_points}" class="margin-line"/>')
    for index, (x, value) in enumerate(zip(x_positions, margin)):
        y = margin_scale(value)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" class="margin-dot"/>')
        if index in (0, len(years) - 1):
            anchor = "start" if index == 0 else "end"
            offset = 12 if index == 0 else -12
            parts.append(f'<text x="{x + offset:.1f}" y="{y - 12:.1f}" text-anchor="{anchor}" class="label">{value:.1f}%</text>')

    parts.extend(
        [
            '<text x="70" y="730" class="note">Financial totals include recognized returns and adjustments. Four partial-period rows in 2017 are retained in the database but excluded from the complete-year trend.</text>',
            '</svg>',
        ]
    )
    return "\n".join(parts)


def main() -> None:
    with sqlite3.connect(DATABASE_PATH) as connection:
        annual = pd.read_sql_query(
            ANNUAL_SQL_PATH.read_text(encoding="utf-8"), connection
        )
        monthly = pd.read_sql_query(
            MONTHLY_SQL_PATH.read_text(encoding="utf-8"), connection
        )
        seasonality = pd.read_sql_query(
            SEASONALITY_SQL_PATH.read_text(encoding="utf-8"), connection
        )
        validation = pd.read_sql_query(
            VALIDATION_SQL_PATH.read_text(encoding="utf-8"), connection
        )

    annual.to_csv(ANNUAL_PATH, index=False)
    monthly.to_csv(MONTHLY_PATH, index=False)
    seasonality.to_csv(SEASONALITY_PATH, index=False)
    validation.to_csv(VALIDATION_PATH, index=False)

    if len(annual) != 7 or annual["reported_months"].ne(12).any():
        raise ValueError("Question 1 requires seven complete annual periods")
    if len(monthly) != 84 or monthly["period"].nunique() != 84:
        raise ValueError("Question 1 requires 84 unique monthly periods")
    if len(seasonality) != 12:
        raise ValueError("Seasonality output must contain all 12 calendar months")

    if not validation["status"].eq("PASS").all():
        failed_checks = validation.loc[
            validation["status"].ne("PASS"), "check_name"
        ].tolist()
        raise ValueError(f"Question 1 validation failed: {failed_checks}")

    first = annual.iloc[0]
    last = annual.iloc[-1]
    highest_month = seasonality.loc[
        seasonality["average_annual_revenue_share_pct"].idxmax()
    ]
    lowest_month = seasonality.loc[
        seasonality["average_annual_revenue_share_pct"].idxmin()
    ]
    negative_yoy = monthly[monthly["revenue_yoy_pct"].notna() & (monthly["revenue_yoy_pct"] < 0)]
    q4_share = seasonality.loc[
        seasonality["per_month"].isin([10, 11, 12]),
        "average_annual_revenue_share_pct",
    ].sum()
    q4_gp_share = seasonality.loc[
        seasonality["per_month"].isin([10, 11, 12]),
        "average_annual_gross_profit_share_pct",
    ].sum()
    summary = {
        "reporting_window": {"first_period": "1801", "last_period": "2412", "months": 84},
        "revenue": {
            "2018": float(first["total_revenue"]),
            "2024": float(last["total_revenue"]),
            "total_growth_pct": pct_change(first["total_revenue"], last["total_revenue"]),
            "cagr_pct": cagr(first["total_revenue"], last["total_revenue"], 6),
        },
        "gross_profit": {
            "2018": float(first["gross_profit"]),
            "2024": float(last["gross_profit"]),
            "total_growth_pct": pct_change(first["gross_profit"], last["gross_profit"]),
            "cagr_pct": cagr(first["gross_profit"], last["gross_profit"], 6),
        },
        "cost": {
            "2018": float(first["total_cost"]),
            "2024": float(last["total_cost"]),
            "total_growth_pct": pct_change(first["total_cost"], last["total_cost"]),
            "cagr_pct": cagr(first["total_cost"], last["total_cost"], 6),
        },
        "margin": {
            "2018_pct": float(first["gross_margin_pct"]),
            "2024_pct": float(last["gross_margin_pct"]),
            "change_pp": float(last["gross_margin_pct"] - first["gross_margin_pct"]),
            "years_expanding": int((annual["margin_change_pp"].fillna(0) > 0).sum()),
            "years_compressing": int((annual["margin_change_pp"].fillna(0) < 0).sum()),
        },
        "growth_pattern": {
            "highest_revenue_growth_year": int(
                annual.loc[annual["revenue_yoy_pct"].idxmax(), "per_year"]
            ),
            "highest_revenue_growth_pct": float(annual["revenue_yoy_pct"].max()),
            "2024_revenue_growth_pct": float(last["revenue_yoy_pct"]),
            "2024_gross_profit_growth_pct": float(last["gross_profit_yoy_pct"]),
            "negative_yoy_month_count": int(len(negative_yoy)),
        },
        "seasonality": {
            "highest_month": str(highest_month["month_name"]),
            "highest_average_revenue_share_pct": float(
                highest_month["average_annual_revenue_share_pct"]
            ),
            "lowest_month": str(lowest_month["month_name"]),
            "lowest_average_revenue_share_pct": float(
                lowest_month["average_annual_revenue_share_pct"]
            ),
            "q4_average_revenue_share_pct": float(q4_share),
            "q4_average_gross_profit_share_pct": float(q4_gp_share),
        },
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    SVG_PATH.write_text(make_svg(annual), encoding="utf-8")
    print(SUMMARY_PATH)
    print(SVG_PATH)
    print(ANNUAL_PATH)
    print(MONTHLY_PATH)
    print(SEASONALITY_PATH)
    print(VALIDATION_PATH)


if __name__ == "__main__":
    main()
