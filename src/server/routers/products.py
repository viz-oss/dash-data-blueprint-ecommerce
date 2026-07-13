from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter()

RANKING_DESCRIPTIONS = {
    "main": "ranking ogolny - laczy wszystkie 5 kryteriow z wagami",
    "sales": "ranking wg liczby sprzedanych sztuk",
    "revenue": "ranking wg wygenerowanego przychodu",
    "margin": "ranking wg marzy / zysku",
    "growth": "ranking wg dynamiki wzrostu sprzedazy",
    "rating": "ranking wg sredniej oceny klientow",
}

RANKINGS = {
    "main": [
        {"id": "prod_123", "name": "sluchawki x200", "position": 1, "score": 92},
        {"id": "prod_456", "name": "kabel usb-c 2m", "position": 2, "score": 87},
        {"id": "prod_789", "name": "etui na telefon", "position": 3, "score": 82},
        {"id": "prod_321", "name": "powerbank 10000mah", "position": 4, "score": 78},
        {"id": "prod_654", "name": "ladowarka bezprzewodowa", "position": 5, "score": 74},
    ],
    "sales": [
        {"id": "prod_456", "name": "kabel usb-c 2m", "position": 1, "score": 980},
        {"id": "prod_123", "name": "sluchawki x200", "position": 2, "score": 480},
        {"id": "prod_321", "name": "powerbank 10000mah", "position": 3, "score": 310},
    ],
    "revenue": [
        {"id": "prod_123", "name": "sluchawki x200", "position": 1, "score": 62000},
        {"id": "prod_654", "name": "ladowarka bezprzewodowa", "position": 2, "score": 41000},
        {"id": "prod_789", "name": "etui na telefon", "position": 3, "score": 22000},
    ],
    "margin": [
        {"id": "prod_789", "name": "etui na telefon", "position": 1, "score": 0.52},
        {"id": "prod_654", "name": "ladowarka bezprzewodowa", "position": 2, "score": 0.41},
        {"id": "prod_123", "name": "sluchawki x200", "position": 3, "score": 0.34},
    ],
    "growth": [
        {"id": "prod_321", "name": "powerbank 10000mah", "position": 1, "score": 0.35},
        {"id": "prod_123", "name": "sluchawki x200", "position": 2, "score": 0.18},
        {"id": "prod_456", "name": "kabel usb-c 2m", "position": 3, "score": 0.09},
    ],
    "rating": [
        {"id": "prod_654", "name": "ladowarka bezprzewodowa", "position": 1, "score": 4.9},
        {"id": "prod_123", "name": "sluchawki x200", "position": 2, "score": 4.6},
        {"id": "prod_789", "name": "etui na telefon", "position": 3, "score": 4.4},
    ],
}

PRODUCT_DETAILS = {
    "prod_123": {
        "id": "prod_123",
        "name": "sluchawki x200",
        "price": 129.99,
        "cost": 65.00,
        "image_url": "https://example.com/images/prod_123.jpg",
        "overall_score": 92,
        "rankings": {
            "sales": {"position": 2, "value": 480},
            "revenue": {"position": 1, "value": 62000},
            "margin": {"position": 3, "value": 0.34},
            "growth": {"position": 2, "value": 0.18},
            "rating": {"position": 2, "value": 4.6},
        },
        "history": [
            {"date": "2026-06-01", "sales": 12, "revenue": 1500, "margin": 480},
            {"date": "2026-06-08", "sales": 15, "revenue": 1870, "margin": 590},
            {"date": "2026-06-15", "sales": 9, "revenue": 1120, "margin": 360},
            {"date": "2026-06-22", "sales": 18, "revenue": 2240, "margin": 710},
        ],
        "reviews": {"average": 4.6, "count": 210},
        "return_rate": 0.04,
        "recommendations": [
            "marza ponizej sredniej kategorii - rozwaz podniesienie ceny o ok. 5%",
        ],
    },
}
DEFAULT_PRODUCT_DETAIL = PRODUCT_DETAILS["prod_123"]

# GET /api/products/?ranking=main|sales|revenue|margin|growth|rating&limit=10&search=
# GET /api/products/{product_id}/


@router.get("/", operation_id="list", summary="Rankingi produktow")
def products_list(
    ranking: str = Query("main", description="main|sales|revenue|margin|growth|rating"),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
):
    products = RANKINGS.get(ranking, RANKINGS["main"])
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]
    return {
        "ranking_type": ranking,
        "ranking_description": RANKING_DESCRIPTIONS.get(ranking, ""),
        "products": products[:limit],
    }


@router.get("/{product_id}/", operation_id="detail", summary="Karta produktu")
def products_detail(product_id: str):
    return PRODUCT_DETAILS.get(product_id, {**DEFAULT_PRODUCT_DETAIL, "id": product_id})
