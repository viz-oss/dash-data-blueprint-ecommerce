from datetime import date, timedelta
from enum import Enum
from typing import List, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

TODAY = date(2026, 7, 15)

GRANULARITY_DAYS = {"day": 1, "week": 7, "month": 30, "year": 365}

SALES_BASE = {"value": 850, "growth_pct": 3.0}
REVENUE_BASE = {"value": 4400.00, "growth_pct": 3.0}
PROFIT_BASE = {"value": 1900.00, "growth_pct": 2.0}
ORDERS_BASE = {"value": 310, "growth_pct": 4.0}

STOCK_DEPLETION = [
    {"id": "prod_321", "name": "powerbank 10000mah", "current_stock": 3, "predicted_days_until_out": 6},
    {"id": "prod_654", "name": "ladowarka bezprzewodowa", "current_stock": 5, "predicted_days_until_out": 9},
    {"id": "prod_222", "name": "klawiatura mechaniczna", "current_stock": 34, "predicted_days_until_out": 45},
    {"id": "prod_111", "name": "mysz bezprzewodowa", "current_stock": 60, "predicted_days_until_out": 80},
]

RECOMMENDATIONS = [
    "prognozowany wzrost sprzedazy w nadchodzacym okresie - przygotuj wieksze zapasy kluczowych produktow",
    "produkt 'powerbank 10000mah' wyczerpie sie wg prognozy za okolo 6 dni - zloz zamowienie u dostawcy",
    "zysk rosnie wolniej niz przychod - sprawdz rosnace koszty operacyjne",
]


class Trend(str, Enum):
    rosnie = "rosnie"
    spada = "spada"
    stabilny = "stabilny"


def trend_from_growth(growth_pct: float) -> Trend:
    if growth_pct > 0:
        return Trend.rosnie
    if growth_pct < 0:
        return Trend.spada
    return Trend.stabilny


def build_chart(base_value: float, growth_pct: float, horizon: int, step_days: int):
    chart = []
    value = base_value
    current_date = TODAY
    for _ in range(horizon):
        current_date = current_date + timedelta(days=step_days)
        value = value * (1 + growth_pct / 100)
        chart.append({"date": current_date.isoformat(), "value": value})
    return chart


class SalesForecastPoint(BaseModel):
    date: str
    predicted_units: int


class SalesForecast(BaseModel):
    granularity: str
    chart: List[SalesForecastPoint]
    next_period_units: int
    change_pct_vs_prev_period: float
    trend: Trend


class RevenueForecastPoint(BaseModel):
    date: str
    predicted_revenue: str


class RevenueForecast(BaseModel):
    granularity: str
    chart: List[RevenueForecastPoint]
    next_period_revenue: str
    change_pct_vs_prev_period: float
    trend: Trend


class ProfitForecastPoint(BaseModel):
    date: str
    predicted_profit: str


class ProfitForecast(BaseModel):
    granularity: str
    chart: List[ProfitForecastPoint]
    next_period_profit: str
    change_pct_vs_prev_period: float
    trend: Trend


class OrdersForecastPoint(BaseModel):
    date: str
    predicted_orders: int


class OrdersForecast(BaseModel):
    granularity: str
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


class ForecastResponse(BaseModel):
    granularity: str
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


class GranularityEnum(str, Enum):
    day = "day"
    week = "week"
    month = "month"
    year = "year"


@router.get(
    "/",
    operation_id="forecasts_list",
    summary="Prognozy",
    response_model=ForecastResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def forecast_list(
    granularity: GranularityEnum = Query(GranularityEnum.week, description="day, week, month, year"),
    horizon: int = Query(4, ge=1, le=52, description="liczba okresow do przodu"),
    stock_alert_days: int = Query(14, ge=1, description="prog dni ponizej ktorego produkt jest oznaczony jako zagrozony wyczerpaniem"),
):
    step_days = GRANULARITY_DAYS[granularity.value]

    sales_chart = build_chart(SALES_BASE["value"], SALES_BASE["growth_pct"], horizon, step_days)
    revenue_chart = build_chart(REVENUE_BASE["value"], REVENUE_BASE["growth_pct"], horizon, step_days)
    profit_chart = build_chart(PROFIT_BASE["value"], PROFIT_BASE["growth_pct"], horizon, step_days)
    orders_chart = build_chart(ORDERS_BASE["value"], ORDERS_BASE["growth_pct"], horizon, step_days)

    sales = {
        "granularity": granularity,
        "chart": [{"date": p["date"], "predicted_units": round(p["value"])} for p in sales_chart],
        "next_period_units": round(sales_chart[0]["value"]),
        "change_pct_vs_prev_period": SALES_BASE["growth_pct"],
        "trend": trend_from_growth(SALES_BASE["growth_pct"]),
    }

    revenue = {
        "granularity": granularity,
        "chart": [{"date": p["date"], "predicted_revenue": f"{p['value']:.2f}"} for p in revenue_chart],
        "next_period_revenue": f"{revenue_chart[0]['value']:.2f}",
        "change_pct_vs_prev_period": REVENUE_BASE["growth_pct"],
        "trend": trend_from_growth(REVENUE_BASE["growth_pct"]),
    }

    profit = {
        "granularity": granularity,
        "chart": [{"date": p["date"], "predicted_profit": f"{p['value']:.2f}"} for p in profit_chart],
        "next_period_profit": f"{profit_chart[0]['value']:.2f}",
        "change_pct_vs_prev_period": PROFIT_BASE["growth_pct"],
        "trend": trend_from_growth(PROFIT_BASE["growth_pct"]),
    }

    orders = {
        "granularity": granularity,
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
                "predicted_out_of_stock_date": (TODAY + timedelta(days=p["predicted_days_until_out"])).isoformat(),
                "at_risk": p["predicted_days_until_out"] <= stock_alert_days,
            }
            for p in stock_items
        ]
    }

    return {
        "granularity": granularity,
        "horizon": horizon,
        "sales": sales,
        "revenue": revenue,
        "profit": profit,
        "orders": orders,
        "stock_depletion": stock_depletion,
        "recommendations": RECOMMENDATIONS,
    }