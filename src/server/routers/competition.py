from fastapi import APIRouter, Query

router = APIRouter()

KPIS = {
    "avg_competitor_price": 115.00,
    "price_diff_pct": -4.2,
    "better_offer_count": 18,
    "needs_action_count": 7,
}

PRICES = [
    {"id": "prod_123", "name": "sluchawki x200", "our_price": 129.99, "competitor_price": 119.00, "status": "drozszy"},
    {"id": "prod_456", "name": "kabel usb-c 2m", "our_price": 19.99, "competitor_price": 24.99, "status": "tanszy"},
]

RANKING = [
    {"id": "prod_456", "name": "kabel usb-c 2m", "competitiveness": "bardziej_atrakcyjny"},
    {"id": "prod_123", "name": "sluchawki x200", "competitiveness": "wymaga_poprawy"},
]

RECOMMENDATIONS = [
    "cena 'sluchawki x200' jest wyzsza niz u konkurencji o ok. 9% - rozwaz korekte",
]

# GET /api/competition/?view=ceny|ranking


@router.get("/", operation_id="list", summary="Konkurencja")
def competition_list(view: str = Query("ceny", description="ceny|ranking")):
    products = RANKING if view == "ranking" else PRICES
    return {"kpis": KPIS, "view": view, "products": products, "recommendations": RECOMMENDATIONS}
