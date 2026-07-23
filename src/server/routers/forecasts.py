from datetime import datetime, date, timedelta
from enum import Enum
from math import ceil
from typing import List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()

DEFAULT_ANCHOR_DATE = date(2026, 7, 15)

SALES_BASE = {"value": 850, "growth_pct": 3.0}
REVENUE_BASE = {"value": 4400.00, "growth_pct": 3.0}
PROFIT_BASE = {"value": 1900.00, "growth_pct": 2.0}
ORDERS_BASE = {"value": 310, "growth_pct": 4.0}

STOCK_DEPLETION = [
    {"id": "prod_321", "name": "10000mAh Power Bank", "current_stock": 3, "predicted_days_until_out": 6},
    {"id": "prod_654", "name": "Wireless Charger", "current_stock": 5, "predicted_days_until_out": 9},
    {"id": "prod_222", "name": "Mechanical Keyboard", "current_stock": 34, "predicted_days_until_out": 45},
    {"id": "prod_111", "name": "Wireless Mouse", "current_stock": 60, "predicted_days_until_out": 80},
]

RECOMMENDATIONS = [
    "Sales are forecast to increase in the upcoming period - prepare higher inventory levels for key products.",
    "Product '10000mAh Power Bank' is forecast to run out of stock in approximately 6 days - place an order with the supplier.",
    "Profit is growing more slowly than revenue - review increasing operating costs.",
]


class Trend(str, Enum):
    increasing = "increasing"
    decreasing = "decreasing"
    stable = "stable"


def trend_from_growth(growth_pct: float) -> Trend:
    if growth_pct > 0:
        return Trend.increasing
    if growth_pct < 0:
        return Trend.decreasing
    return Trend.stable


def parse_date(value: str, param_name: str) -> date:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format in '{param_name}', expected YYYY-MM-DD",
        )


def build_chart(base_value: float, growth_pct: float, horizon: int, step_days: int, anchor_date: date):
    chart = []
    value = base_value
    current_date = anchor_date
    for _ in range(horizon):
        current_date = current_date + timedelta(days=step_days)
        value = value * (1 + growth_pct / 100)
        chart.append({"date": current_date.isoformat(), "value": value})
    return chart


class SalesForecastPoint(BaseModel):
    date: str
    predicted_units: int


class SalesForecast(BaseModel):
    chart: List[SalesForecastPoint]
    next_period_units: int
    change_pct_vs_prev_period: float
    trend: Trend


class RevenueForecastPoint(BaseModel):
    date: str
    predicted_revenue: str


class RevenueForecast(BaseModel):
    chart: List[RevenueForecastPoint]
    next_period_revenue: str
    change_pct_vs_prev_period: float
    trend: Trend


class ProfitForecastPoint(BaseModel):
    date: str
    predicted_profit: str


class ProfitForecast(BaseModel):
    chart: List[ProfitForecastPoint]
    next_period_profit: str
    change_pct_vs_prev_period: float
    trend: Trend


class OrdersForecastPoint(BaseModel):
    date: str
    predicted_orders: int


class OrdersForecast(BaseModel):
    chart: List[OrdersForecastPoint]
    next_period_orders: int
    change_pct_vs_prev_period: float
    trend: Trend


class StockDepletionItem(BaseModel):
    id: str
    name: str
    current_stock: int
    predicted_days_until_out: int
    predicted_out_of_stock_date: str
    at_risk: bool


class StockDepletionForecast(BaseModel):
    items: List[StockDepletionItem]


class ForecastPeriod(BaseModel):
    from_: str
    to: Optional[str] = None


class ForecastResponse(BaseModel):
    period: ForecastPeriod
    horizon: int
    sales: SalesForecast
    revenue: RevenueForecast
    profit: ProfitForecast
    orders: OrdersForecast
    stock_depletion: StockDepletionForecast
    recommendations: List[str]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


@router.get(
    "/",
    operation_id="forecasts_list",
    summary="Forecasts",
    response_model=ForecastResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def forecast_list(
    horizon: int = Query(4, ge=1, le=52, description="Number of future periods to forecast (ignored if 'to' is provided)"),
    stock_alert_days: int = Query(
        14,
        ge=1,
        description="Threshold in days below which a product is marked as at risk of running out of stock",
    ),
    from_: Optional[str] = Query(
        None, alias="from", description="Forecast anchor (start) date, format YYYY-MM-DD"
    ),
    to: Optional[str] = Query(
        None, description="Forecast end date, format YYYY-MM-DD (if set, overrides 'horizon')"
    ),
):
    anchor_date = parse_date(from_, "from") if from_ else DEFAULT_ANCHOR_DATE
    end_date = parse_date(to, "to") if to else None

    if end_date and end_date <= anchor_date:
        raise HTTPException(status_code=422, detail="'from' cannot be later than or equal to 'to'")


    sales_chart = build_chart(SALES_BASE["value"], SALES_BASE["growth_pct"], horizon,  anchor_date)
    revenue_chart = build_chart(REVENUE_BASE["value"], REVENUE_BASE["growth_pct"], horizon,  anchor_date)
    profit_chart = build_chart(PROFIT_BASE["value"], PROFIT_BASE["growth_pct"], horizon,  anchor_date)
    orders_chart = build_chart(ORDERS_BASE["value"], ORDERS_BASE["growth_pct"], horizon,  anchor_date)

    sales = {
        "chart": [{"date": p["date"], "predicted_units": round(p["value"])} for p in sales_chart],
        "next_period_units": round(sales_chart[0]["value"]),
        "change_pct_vs_prev_period": SALES_BASE["growth_pct"],
        "trend": trend_from_growth(SALES_BASE["growth_pct"]),
    }

    revenue = {
        "chart": [{"date": p["date"], "predicted_revenue": f"{p['value']:.2f}"} for p in revenue_chart],
        "next_period_revenue": f"{revenue_chart[0]['value']:.2f}",
        "change_pct_vs_prev_period": REVENUE_BASE["growth_pct"],
        "trend": trend_from_growth(REVENUE_BASE["growth_pct"]),
    }

    profit = {
        "chart": [{"date": p["date"], "predicted_profit": f"{p['value']:.2f}"} for p in profit_chart],
        "next_period_profit": f"{profit_chart[0]['value']:.2f}",
        "change_pct_vs_prev_period": PROFIT_BASE["growth_pct"],
        "trend": trend_from_growth(PROFIT_BASE["growth_pct"]),
    }

    orders = {
        "chart": [{"date": p["date"], "predicted_orders": round(p["value"])} for p in orders_chart],
        "next_period_orders": round(orders_chart[0]["value"]),
        "change_pct_vs_prev_period": ORDERS_BASE["growth_pct"],
        "trend": trend_from_growth(ORDERS_BASE["growth_pct"]),
    }

    stock_items = sorted(STOCK_DEPLETION, key=lambda p: p["predicted_days_until_out"])
    stock_depletion = {
        "items": [
            {
                **p,
                "predicted_out_of_stock_date": (
                    anchor_date + timedelta(days=p["predicted_days_until_out"])
                ).isoformat(),
                "at_risk": p["predicted_days_until_out"] <= stock_alert_days,
            }
            for p in stock_items
        ]
    }

    return {
        "period": {"from_": anchor_date.isoformat(), "to": end_date.isoformat() if end_date else None},
        "horizon": horizon,
        "sales": sales,
        "revenue": revenue,
        "profit": profit,
        "orders": orders,
        "stock_depletion": stock_depletion,
        "recommendations": RECOMMENDATIONS,
    }