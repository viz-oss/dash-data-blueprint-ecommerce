from fastapi import APIRouter, Query

router = APIRouter()

SUMMARY = {
    "revenue": 125000,
    "costs": 78000,
    "profit": 47000,
    "margin_pct": 0.376,
    "avg_order_value": 145.30,
}

REVENUE = {
    "chart": [
        {"date": "2026-06-01", "revenue": 3900},
        {"date": "2026-06-08", "revenue": 4200},
        {"date": "2026-06-15", "revenue": 5100},
        {"date": "2026-06-22", "revenue": 3400},
        {"date": "2026-06-29", "revenue": 4600},
        {"date": "2026-07-06", "revenue": 4400},
    ],
    "peak_period": "2026-06-15",
    "low_period": "2026-06-22",
    "forecast_next_period": 132000,
    "order_count_impact": "wzrost liczby zamowien o 8% wzgledem poprzedniego okresu",
    "avg_order_value_impact": "srednia wartosc koszyka spadla o 3%",
    "recommendations": [
        "przychod rosnie glownie dzieki wiekszej liczbie zamowien, nie wartosci koszyka - rozwaz upselling",
    ],
}

COSTS = {
    "total": 78000,
    "change_pct": 5.2,
    "chart": [
        {"date": "2026-06-01", "costs": 2400},
        {"date": "2026-06-08", "costs": 2600},
        {"date": "2026-06-15", "costs": 3100},
        {"date": "2026-06-22", "costs": 2200},
    ],
    "categories": [
        {"name": "koszt_zakupu_towarow", "value": 40000, "share": 0.51, "change_pct": 2.0},
        {"name": "koszty_dostawy", "value": 12000, "share": 0.15, "change_pct": 1.1},
        {"name": "prowizje_platform", "value": 9500, "share": 0.12, "change_pct": 0.4},
        {"name": "koszty_reklam", "value": 9000, "share": 0.12, "change_pct": 15.3},
        {"name": "pozostale_koszty_operacyjne", "value": 7500, "share": 0.10, "change_pct": -1.2},
    ],
    "recommendations": [
        "koszty reklam rosna najszybciej (+15.3%) - sprawdz kampanie o niskim roas",
    ],
}

PROFITABILITY = {
    "chart": [
        {"date": "2026-06-01", "profit": 1900, "margin": 0.39},
        {"date": "2026-06-08", "profit": 2100, "margin": 0.37},
        {"date": "2026-06-15", "profit": 1750, "margin": 0.32},
        {"date": "2026-06-22", "profit": 2400, "margin": 0.41},
    ],
    "profit_change_pct_vs_prev_period": -4.1,
    "recommendations": [
        "sprzedaz rosnie, ale zysk spada - sprawdz rosnace koszty dostawy i reklam",
    ],
}

# GET /api/analytics/finance/summary/
# GET /api/analytics/finance/revenue/
# GET /api/analytics/finance/costs/
# GET /api/analytics/finance/profitability/


@router.get("/summary/", operation_id="summary", summary="Glowne wskazniki finansowe")
def finance_summary():
    return SUMMARY


@router.get("/revenue/", operation_id="revenue", summary="Przychody")
def finance_revenue(granularity: str = Query("week", description="day|week|month")):
    return {**REVENUE, "granularity": granularity}


@router.get("/costs/", operation_id="costs", summary="Koszty")
def finance_costs(granularity: str = Query("week", description="day|week|month|year")):
    return {**COSTS, "granularity": granularity}


@router.get("/profitability/", operation_id="profitability", summary="Rentownosc")
def finance_profitability():
    return PROFITABILITY
