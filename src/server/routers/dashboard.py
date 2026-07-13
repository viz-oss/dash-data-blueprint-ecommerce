from fastapi import APIRouter

router = APIRouter()

DASHBOARD = {
    "kpis": {
        "revenue": 125000,
        "costs": 78000,
        "profit": 47000,
        "orders": 340,
        "customers": 210,
        "ad_spend": 9000,
        "low_stock_count": 12,
    },
    "trend": [
        {"date": "2026-07-06", "revenue": 3800},
        {"date": "2026-07-07", "revenue": 4100},
        {"date": "2026-07-08", "revenue": 3950},
        {"date": "2026-07-09", "revenue": 4600},
        {"date": "2026-07-10", "revenue": 4200},
        {"date": "2026-07-11", "revenue": 4400},
        {"date": "2026-07-12", "revenue": 4700},
    ],
    "top_recommendations": [
        "kategoria 'akcesoria kuchenne' generuje najwiecej zwrotow - sprawdz opisy produktow",
        "marza w module finanse spadla o 4% wzgledem poprzedniego miesiaca",
        "produkt 'sluchawki x200' ma zapas na 6 dni - uzupelnij magazyn",
    ],
}


@router.get("/", operation_id="overview", summary="Dashboard glowny")
def dashboard():
    return DASHBOARD
