from fastapi import APIRouter

router = APIRouter()

FORECASTS = {
    "sales_forecast": [
        {"date": "2026-07-13", "value": 42},
        {"date": "2026-07-20", "value": 47},
        {"date": "2026-07-27", "value": 51},
    ],
    "revenue_forecast": [
        {"date": "2026-07-13", "value": 4600},
        {"date": "2026-07-20", "value": 5100},
        {"date": "2026-07-27", "value": 5400},
    ],
    "profit_forecast": [
        {"date": "2026-07-13", "value": 1700},
        {"date": "2026-07-20", "value": 1900},
        {"date": "2026-07-27", "value": 2000},
    ],
    "orders_forecast": [
        {"date": "2026-07-13", "value": 30},
        {"date": "2026-07-20", "value": 34},
        {"date": "2026-07-27", "value": 37},
    ],
    "inventory_depletion_forecast": [
        {"id": "prod_321", "name": "powerbank 10000mah", "days_until_out": 6},
        {"id": "prod_654", "name": "ladowarka bezprzewodowa", "days_until_out": 9},
    ],
    "ai_insights": [
        "sezonowy wzrost sprzedazy oczekiwany w sierpniu",
        "produkt 'powerbank 10000mah' wymaga wczesniejszego uzupelnienia zapasow",
    ],
}


@router.get("/", operation_id="overview", summary="Prognozy")
def forecasts():
    return FORECASTS
