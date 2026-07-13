from fastapi import APIRouter, Query

router = APIRouter()

KPIS = {
    "returns_count": 45,
    "return_rate": 0.06,
    "returned_value": 5400.00,
    "handling_cost": 800.00,
    "complaints_count": 12,
}

ZWROTY = {
    "returns_over_time": [
        {"date": "2026-06-01", "count": 5},
        {"date": "2026-06-08", "count": 8},
        {"date": "2026-06-15", "count": 6},
        {"date": "2026-06-22", "count": 11},
    ],
    "top_return_products": [
        {"id": "prod_789", "name": "etui na telefon", "returns": 9},
        {"id": "prod_321", "name": "powerbank 10000mah", "returns": 6},
    ],
    "return_reasons": [
        {"reason": "niezgodnosc_z_opisem", "count": 14},
        {"reason": "niewlasciwy_rozmiar", "count": 9},
        {"reason": "uszkodzenie", "count": 7},
        {"reason": "problem_z_jakoscia", "count": 6},
        {"reason": "zmiana_decyzji", "count": 6},
        {"reason": "inne", "count": 3},
    ],
}

REKLAMACJE = {
    "top_complaint_products": [
        {"id": "prod_321", "name": "powerbank 10000mah", "complaints": 5},
        {"id": "prod_654", "name": "ladowarka bezprzewodowa", "complaints": 3},
    ],
    "common_issues": [
        "produkt przestaje dzialac po kilku tygodniach",
        "brak elementow w zestawie",
    ],
}

RECOMMENDATIONS = [
    "produkt 'etui na telefon' generuje najwiecej zwrotow - sprawdz zgodnosc opisu ze zdjeciami",
]

# GET /api/returns/?view=zwroty|reklamacje


@router.get("/", operation_id="list", summary="Zwroty i reklamacje")
def returns_list(view: str = Query("zwroty", description="zwroty|reklamacje")):
    detail = REKLAMACJE if view == "reklamacje" else ZWROTY
    return {"kpis": KPIS, "view": view, **detail, "recommendations": RECOMMENDATIONS}
