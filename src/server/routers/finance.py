from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Any, Optional
from datetime import datetime

MAX_DAYS = 365
router = APIRouter()

SUMMARY = {
    "revenue": "125000",
    "costs": "78000",
    "profit": "47000",
    "margin_pct": "0.376",
    "avg_order_value": "145.30",
}

REVENUE = {
    "chart": [
        {"date": "2026-06-01", "revenue": 3900.0},
        {"date": "2026-06-08", "revenue": 4200.0},
        {"date": "2026-06-15", "revenue": 5100.0},
        {"date": "2026-06-22", "revenue": 3400.0},
        {"date": "2026-06-29", "revenue": 4600.0},
        {"date": "2026-07-06", "revenue": 4400.0},
    ],
    "peak_period": "2026-06-15",
    "low_period": "2026-06-22",
    "forecast_next_period": "132000",
    "order_count_impact": "Order count increased by 8% compared to the previous period",
    "avg_order_value_impact": "Average order value decreased by 3%",
    "recommendations": [
        "Revenue is growing mainly due to a higher number of orders rather than a higher basket value - consider upselling.",
    ],
}

COSTS = {
    "total": "78000",
    "change_pct": "5.2",
    "chart": [
        {"date": "2026-06-01", "costs": 2400.0},
        {"date": "2026-06-08", "costs": 2600.0},
        {"date": "2026-06-15", "costs": 3100.0},
        {"date": "2026-06-22", "costs": 2200.0},
    ],
    "categories": [
        {
            "name": "cost_of_goods_sold",
            "value": "40000",
            "share": "0.51",
            "change_pct": "2.0",
            "trend": [
                {"date": "2026-06-01", "value": 9500.0},
                {"date": "2026-06-08", "value": 10200.0},
                {"date": "2026-06-15", "value": 9800.0},
                {"date": "2026-06-22", "value": 10500.0},
            ],
        },
        {
            "name": "delivery_costs",
            "value": "12000",
            "share": "0.15",
            "change_pct": "1.1",
            "trend": [
                {"date": "2026-06-01", "value": 2900.0},
                {"date": "2026-06-08", "value": 3000.0},
                {"date": "2026-06-15", "value": 3050.0},
                {"date": "2026-06-22", "value": 3050.0},
            ],
        },
        {
            "name": "platform_fees",
            "value": "9500",
            "share": "0.12",
            "change_pct": "0.4",
            "trend": [
                {"date": "2026-06-01", "value": 2350.0},
                {"date": "2026-06-08", "value": 2380.0},
                {"date": "2026-06-15", "value": 2370.0},
                {"date": "2026-06-22", "value": 2400.0},
            ],
        },
        {
            "name": "advertising_costs",
            "value": "9000",
            "share": "0.12",
            "change_pct": "15.3",
            "trend": [
                {"date": "2026-06-01", "value": 1800.0},
                {"date": "2026-06-08", "value": 2100.0},
                {"date": "2026-06-15", "value": 2400.0},
                {"date": "2026-06-22", "value": 2700.0},
            ],
        },
        {
            "name": "other_operating_costs",
            "value": "7500",
            "share": "0.10",
            "change_pct": "-1.2",
            "trend": [
                {"date": "2026-06-01", "value": 1900.0},
                {"date": "2026-06-08", "value": 1880.0},
                {"date": "2026-06-15", "value": 1870.0},
                {"date": "2026-06-22", "value": 1850.0},
            ],
        },
    ],
    "recommendations": [
        "Advertising costs are increasing the fastest (+15.3%) - review campaigns with low ROAS.",
    ],
}

PROFITABILITY = {
    "chart": [
        {"date": "2026-06-01", "profit": 1900.0, "margin": 0.39},
        {"date": "2026-06-08", "profit": 2100.0, "margin": 0.37},
        {"date": "2026-06-15", "profit": 1750.0, "margin": 0.32},
        {"date": "2026-06-22", "profit": 2400.0, "margin": 0.41},
    ],
    "profit_change_pct_vs_prev_period": "-4.1",
    "margin_change_pct_vs_prev_period": "-2.3",
    "cost_impact_description": (
        "Sales growth has been partially offset by increasing delivery and advertising costs, "
        "which reduced the profit margin despite higher revenue."
    ),
    "recommendations": [
        "Sales are increasing, but profit is declining - review increasing delivery and advertising costs.",
    ],
}

class FinanceSummaryResponse(BaseModel):
    revenue: str
    costs: str
    profit: str
    margin_pct: str
    avg_order_value: str


class RevenueChartPoint(BaseModel):
    date: str
    revenue: float


class RevenueBlock(BaseModel):
    chart: List[RevenueChartPoint]
    peak_period: str
    low_period: str
    forecast_next_period: str
    order_count_impact: str
    avg_order_value_impact: str
    recommendations: List[str]


class CostsChartPoint(BaseModel):
    date: str
    costs: float


class CostCategoryTrendPoint(BaseModel):
    date: str
    value: float


class CostCategory(BaseModel):
    name: str
    value: str
    share: str
    change_pct: str
    trend: List[CostCategoryTrendPoint]


class CostsBlock(BaseModel):
    total: str
    change_pct: str
    chart: List[CostsChartPoint]
    categories: List[CostCategory]
    recommendations: List[str]


class ProfitabilityChartPoint(BaseModel):
    date: str
    profit: float
    margin: float


class ProfitabilityBlock(BaseModel):
    chart: List[ProfitabilityChartPoint]
    profit_change_pct_vs_prev_period: str
    margin_change_pct_vs_prev_period: str
    cost_impact_description: str
    recommendations: List[str]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


class FinanceResponse(BaseModel):
    date_from: str = Field(alias="from")
    date_to: str = Field(alias="to")
    summary: FinanceSummaryResponse
    revenue: RevenueBlock
    costs: CostsBlock
    profitability: ProfitabilityBlock

    model_config = {
        "populate_by_name": True, 
    }

def _filter_by_date(items: List[dict], date_from: Optional[str], date_to: Optional[str]) -> List[dict]:
    result = items
    if date_from:
        result = [p for p in result if p["date"] >= date_from]
    if date_to:
        result = [p for p in result if p["date"] <= date_to]
    return result


def _filter_categories(categories: List[dict], date_from: Optional[str], date_to: Optional[str]) -> List[dict]:
    return [
        {**cat, "trend": _filter_by_date(cat["trend"], date_from, date_to)}
        for cat in categories
    ]

# GET /api/analytics/finance/?from=...&to=...

@router.get(
    "/",
    operation_id="finance",
    summary="Finance Overview (summary + revenue + costs + profitability)",
    response_model=FinanceResponse,
    responses={
        422: {
            "description": "Validation Error",
            "model": ValidationErrorResponse,
        }
    },
)
def finance(
    date_from: Optional[str] = Query(None, alias="from", description="Start date of the range (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, alias="to", description="End date of the range (YYYY-MM-DD)"),
):
    if date_from and date_to:
        start = datetime.strptime(date_from, "%Y-%m-%d")
        end = datetime.strptime(date_to, "%Y-%m-%d")

        if (end - start).days > MAX_DAYS:
            raise HTTPException(
                status_code=400,
                detail=f"Date range cannot exceed {MAX_DAYS} days."
            )

        if end < start:
            raise HTTPException(
                status_code=400,
                detail="'to' must be greater than or equal to 'from'."
            )

    revenue_chart = _filter_by_date(REVENUE["chart"], date_from, date_to)
    costs_chart = _filter_by_date(COSTS["chart"], date_from, date_to)
    costs_categories = _filter_categories(COSTS["categories"], date_from, date_to)
    profitability_chart = _filter_by_date(PROFITABILITY["chart"], date_from, date_to)

    all_dates = (
        [p["date"] for p in revenue_chart]
        + [p["date"] for p in costs_chart]
        + [p["date"] for p in profitability_chart]
    )
    resolved_from = date_from or (min(all_dates) if all_dates else "")
    resolved_to = date_to or (max(all_dates) if all_dates else "")

    return {
        "date_from": resolved_from,
        "date_to": resolved_to,
        "summary": SUMMARY,
        "revenue": {**REVENUE, "chart": revenue_chart},
        "costs": {**COSTS, "chart": costs_chart, "categories": costs_categories},
        "profitability": {**PROFITABILITY, "chart": profitability_chart},
    }