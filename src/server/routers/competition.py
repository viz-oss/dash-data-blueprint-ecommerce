from enum import Enum
from typing import List, Optional, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

KPIS = {
    "avg_competitor_price": "129.90",
    "price_diff_pct": -4.5,
    "worse_conditions_count": 8,
    "products_needing_action_count": 3,
}

PRODUCTS = [
    {"id": "prod_1", "name": "sluchawki x200", "our_price": "199.00", "competitor_price": "179.00"},
    {"id": "prod_2", "name": "kabel usb-c 2m", "our_price": "29.00", "competitor_price": "32.00"},
    {"id": "prod_3", "name": "etui na telefon", "our_price": "49.00", "competitor_price": "45.00"},
    {"id": "prod_4", "name": "powerbank 10000mah", "our_price": "89.00", "competitor_price": "75.00"},
    {"id": "prod_5", "name": "ladowarka bezprzewodowa", "our_price": "99.00", "competitor_price": "98.00"},
    {"id": "prod_6", "name": "mysz bezprzewodowa", "our_price": "59.00", "competitor_price": "62.00"},
]

PRICE_HISTORY = {
    "prod_1": [
        {"date": "2026-05-01", "our_price": "219.00", "competitor_price": "189.00"},
        {"date": "2026-06-01", "our_price": "199.00", "competitor_price": "179.00"},
    ],
    "prod_4": [
        {"date": "2026-05-01", "our_price": "89.00", "competitor_price": "82.00"},
        {"date": "2026-06-01", "our_price": "89.00", "competitor_price": "75.00"},
    ],
}

SALES_IMPACT = {
    "prod_1": "sprzedaz spadla o 9% od kiedy konkurencja obnizyla cene o 20 zl",
    "prod_4": "sprzedaz stabilna, ale marza jest ponizej sredniej przy tej roznicy cen",
}

RECOMMENDATIONS = [
    "produkt 'sluchawki x200' jest o 11% drozszy niz konkurencja i traci sprzedaz - rozwaz obnizke ceny",
    "produkt 'powerbank 10000mah' jest drozszy o ok. 19% - sprawdz czy marza pozwala na korekte ceny",
    "produkt 'kabel usb-c 2m' jest tanszy niz konkurencja i zyskuje na sprzedazy - dobra pozycja, bez zmian",
]


class PriceStatus(str, Enum):
    expensive = "expensive"
    cheaper = "cheaper"
    same = "same"


def diff_pct(our_price: str, competitor_price: str) -> float:
    return round((float(our_price) - float(competitor_price)) / float(competitor_price) * 100, 1)


def price_status(diff: float) -> PriceStatus:
    if diff > 0:
        return PriceStatus.expensive
    if diff < 0:
        return PriceStatus.cheaper
    return PriceStatus.same

class CompetitionKPIs(BaseModel):
    avg_competitor_price: str
    price_diff_pct: float
    worse_conditions_count: int
    products_needing_action_count: int
 
class PriceComparisonItem(BaseModel):
    id: str
    name: str
    our_price: str
    competitor_price: str
    diff_pct: float
    status: PriceStatus


class PriceHistoryPoint(BaseModel):
    date: str
    our_price: str
    competitor_price: str


class AttentionItem(BaseModel):
    id: str
    name: str
    our_price: str
    competitor_price: str
    diff_pct: float
    status: PriceStatus
    price_history: List[PriceHistoryPoint]
    sales_impact: str


class CompetitionResponse(BaseModel):
    kpis: CompetitionKPIs
    price_comparison: List[PriceComparisonItem]
    needs_attention: List[AttentionItem]
    recommendations: List[str]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


@router.get(
    "/",
    operation_id="list",
    summary="Konkurencja",
    response_model=CompetitionResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def competition_list(
    search: Optional[str] = Query(None, description="szukaj produktu po nazwie w porownaniu cen"),
    action_threshold_pct: float = Query(10.0, description="prog % powyzej ktorego produkt wymaga reakcji cenowej"),
):
    products = PRODUCTS
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]

    comparison = []
    attention = []

    for p in products:
        diff = diff_pct(p["our_price"], p["competitor_price"])
        status = price_status(diff)

        comparison.append({**p, "diff_pct": diff, "status": status})

        if diff >= action_threshold_pct:
            attention.append({
                **p,
                "diff_pct": diff,
                "status": status,
                "price_history": PRICE_HISTORY.get(p["id"], []),
                "sales_impact": SALES_IMPACT.get(p["id"], "brak istotnego wplywu na sprzedaz"),
            })

    return {
        "kpis": KPIS,
        "price_comparison": comparison,
        "needs_attention": attention,
        "recommendations": RECOMMENDATIONS,
    }