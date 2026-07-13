from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter()

KPIS = {
    "listed": 320,
    "in_stock_units": 15400,
    "low_stock_count": 12,
    "unavailable_count": 5,
}

PRODUCTS_STAN = [
    {"id": "prod_123", "name": "sluchawki x200", "stock": 84, "status": "ok"},
    {"id": "prod_456", "name": "kabel usb-c 2m", "stock": 210, "status": "ok"},
    {"id": "prod_789", "name": "etui na telefon", "stock": 0, "status": "unavailable"},
]

PRODUCTS_UWAGA = [
    {"id": "prod_321", "name": "powerbank 10000mah", "stock": 3, "status": "low_stock", "days_until_out": 6},
    {"id": "prod_654", "name": "ladowarka bezprzewodowa", "stock": 5, "status": "low_stock", "days_until_out": 9},
    {"id": "prod_789", "name": "etui na telefon", "stock": 0, "status": "unavailable", "days_until_out": 0},
]

RECOMMENDATIONS = [
    "produkt 'powerbank 10000mah' wyczerpie sie za ok. 6 dni - zloz zamowienie u dostawcy",
    "produkt 'etui na telefon' zalega jako niedostepny od 12 dni",
]

# GET /api/inventory/?view=stan|uwaga&filter=low_stock|out_of_stock|declining|stale


@router.get("/", operation_id="list", summary="Magazyn")
def inventory_list(
    view: str = Query("stan", description="stan|uwaga"),
    filter: Optional[str] = Query(None, description="low_stock|out_of_stock|declining|stale (tylko przy view=uwaga)"),
):
    products = PRODUCTS_UWAGA if view == "uwaga" else PRODUCTS_STAN
    if view == "uwaga" and filter:
        products = [p for p in products if p["status"] == filter]
    return {"kpis": KPIS, "view": view, "products": products, "recommendations": RECOMMENDATIONS}
