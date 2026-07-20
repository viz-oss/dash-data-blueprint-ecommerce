from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Any

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

# response
class FinanceSummaryResponse(BaseModel):
    revenue: str
    costs: str
    profit: str
    margin_pct: str
    avg_order_value: str


class RevenueChartPoint(BaseModel):
    date: str
    revenue: float


class RevenueResponse(BaseModel):
    chart: List[RevenueChartPoint]
    granularity: str
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


class CostsResponse(BaseModel):
    total: str
    change_pct: str
    chart: List[CostsChartPoint]
    granularity: str
    categories: List[CostCategory]
    recommendations: List[str]
 
class ProfitabilityChartPoint(BaseModel):
    date: str
    profit: float
    margin: float
 
class ProfitabilityResponse(BaseModel):
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

# GET /api/analytics/finance/summary/
# GET /api/analytics/finance/revenue/
# GET /api/analytics/finance/costs/
# GET /api/analytics/finance/profitability/

@router.get(
    "/summary/",
    operation_id="finance_summary",
    summary="Key Financial Metrics",
    response_model=FinanceSummaryResponse,
    responses={
        422: {
            "description": "Validation Error",
            "model": ValidationErrorResponse,
        }
    },
)
def finance_summary():
    return SUMMARY

def finance_summary():
    return SUMMARY


@router.get(
    "/revenue/",
    operation_id="revenue",
    summary="Revenue",
    response_model=RevenueResponse,
)
def finance_revenue(granularity: str = Query("week", description="day|week|month|year")):
    return {**REVENUE, "granularity": granularity}


@router.get(
    "/costs/",
    operation_id="costs",
    summary="Costs",
    response_model=CostsResponse,
)
def finance_costs(granularity: str = Query("week", description="day|week|month|year")):
    return {**COSTS, "granularity": granularity}


@router.get(
    "/profitability/",
    operation_id="profitability",
    summary="Profitability",
    response_model=ProfitabilityResponse,
    responses={
        422: {
            "description": "Validation Error",
            "model": ValidationErrorResponse,
        }
    },
)
def finance_profitability(
    granularity: str = Query("week", description="day|week|month|year"),
    date_from: str = Query(None, description="Start date of the range (YYYY-MM-DD)"),
    date_to: str = Query(None, description="End date of the range (YYYY-MM-DD)"),
):
    chart = PROFITABILITY["chart"]

    if date_from:
        chart = [p for p in chart if p["date"] >= date_from]
    if date_to:
        chart = [p for p in chart if p["date"] <= date_to]

    return {
        **PROFITABILITY,
        "chart": chart,
        "granularity": granularity,
        "date_from": date_from or (chart[0]["date"] if chart else ""),
        "date_to": date_to or (chart[-1]["date"] if chart else ""),
    }