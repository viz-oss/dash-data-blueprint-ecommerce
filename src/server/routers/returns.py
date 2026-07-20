from enum import Enum
from typing import List, Any

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

PRODUCT_RETURNS = [
    {"id": "prod_1", "name": "sluchawki x200", "returns_count": 18, "orders_count": 240, "value_returned": "3200.00"},
    {"id": "prod_3", "name": "etui na telefon", "returns_count": 25, "orders_count": 180, "value_returned": "1225.00"},
    {"id": "prod_4", "name": "powerbank 10000mah", "returns_count": 9, "orders_count": 95, "value_returned": "801.00"},
    {"id": "prod_5", "name": "ladowarka bezprzewodowa", "returns_count": 6, "orders_count": 150, "value_returned": "594.00"},
    {"id": "prod_6", "name": "mysz bezprzewodowa", "returns_count": 4, "orders_count": 300, "value_returned": "236.00"},
]

RETURN_REASON_COUNTS = {
    "niezgodnosc_z_opisem": 22,
    "niewlasciwy_rozmiar": 15,
    "uszkodzenie_produktu": 12,
    "problem_z_jakoscia": 8,
    "zmiana_decyzji": 5,
}

COMPLAINTS_BY_PRODUCT = [
    {"id": "prod_3", "name": "etui na telefon", "complaints_count": 14},
    {"id": "prod_1", "name": "sluchawki x200", "complaints_count": 10},
    {"id": "prod_7", "name": "kamera sportowa", "complaints_count": 6},
    {"id": "prod_5", "name": "ladowarka bezprzewodowa", "complaints_count": 3},
]

COMMON_ISSUES = [
    {"issue": "produkt niezgodny z opisem na stronie", "count": 14},
    {"issue": "wada fabryczna lub uszkodzenie przy dostawie", "count": 11},
    {"issue": "produkt dziala niezgodnie z oczekiwaniami", "count": 8},
    {"issue": "opoznienie w wymianie lub naprawie", "count": 5},
]

RECOMMENDATIONS = [
    "produkt 'etui na telefon' ma najwyzszy wspolczynnik zwrotow - sprawdz zdjecia i opis produktu",
    "najczestszy powod zwrotow to niezgodnosc z opisem - zweryfikuj tresci ofert dla produktow z wysokim wspolczynnikiem zwrotow",
    "produkt 'etui na telefon' generuje tez najwiecej reklamacji - priorytetowo sprawdz jakosc dostawcy",
]


class ReturnReason(str, Enum):
    niezgodnosc_z_opisem = "niezgodnosc_z_opisem"
    niewlasciwy_rozmiar = "niewlasciwy_rozmiar"
    uszkodzenie_produktu = "uszkodzenie_produktu"
    problem_z_jakoscia = "problem_z_jakoscia"
    zmiana_decyzji = "zmiana_decyzji"
    inne = "inne"


class ReturnsKPIs(BaseModel):
    total_returns: int
    return_rate_pct: float
    total_returned_value: str
    returns_handling_cost: str
    complaints_count: int


class ProductReturnStat(BaseModel):
    id: str
    name: str
    returns_count: int
    orders_count: int
    return_rate_pct: float
    value_returned: str


class ReturnReasonBreakdown(BaseModel):
    reason: ReturnReason
    count: int
    share_pct: float


class ComplaintProductStat(BaseModel):
    id: str
    name: str
    complaints_count: int


class CommonIssue(BaseModel):
    issue: str
    count: int


class ReturnsResponse(BaseModel):
    kpis: ReturnsKPIs
    top_by_return_count: List[ProductReturnStat]
    top_by_return_rate: List[ProductReturnStat]
    return_reasons: List[ReturnReasonBreakdown]
    top_by_complaints: List[ComplaintProductStat]
    common_issues: List[CommonIssue]
    recommendations: List[str]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


@router.get(
    "/",
    operation_id="returns_list",
    summary="Zwroty i reklamacje",
    response_model=ReturnsResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def returns_list(
    limit: int = Query(5, ge=1, le=20, description="ile pozycji pokazac w kazdym rankingu"),
):
    enriched = [
        {**p, "return_rate_pct": round(p["returns_count"] / p["orders_count"] * 100, 1)}
        for p in PRODUCT_RETURNS
    ]

    top_by_return_count = sorted(enriched, key=lambda p: p["returns_count"], reverse=True)[:limit]
    top_by_return_rate = sorted(enriched, key=lambda p: p["return_rate_pct"], reverse=True)[:limit]

    total_returns = sum(p["returns_count"] for p in PRODUCT_RETURNS)
    total_returned_value = sum(float(p["value_returned"]) for p in PRODUCT_RETURNS)
    total_orders = sum(p["orders_count"] for p in PRODUCT_RETURNS)
    complaints_count = sum(c["complaints_count"] for c in COMPLAINTS_BY_PRODUCT)

    total_reasons = sum(RETURN_REASON_COUNTS.values())
    return_reasons = [
        {"reason": reason, "count": count, "share_pct": round(count / total_reasons * 100, 1)}
        for reason, count in RETURN_REASON_COUNTS.items()
    ]

    top_by_complaints = sorted(COMPLAINTS_BY_PRODUCT, key=lambda c: c["complaints_count"], reverse=True)[:limit]

    kpis = {
        "total_returns": total_returns,
        "return_rate_pct": round(total_returns / total_orders * 100, 1),
        "total_returned_value": f"{total_returned_value:.2f}",
        "returns_handling_cost": "1450.00",
        "complaints_count": complaints_count,
    }

    return {
        "kpis": kpis,
        "top_by_return_count": top_by_return_count,
        "top_by_return_rate": top_by_return_rate,
        "return_reasons": return_reasons,
        "top_by_complaints": top_by_complaints,
        "common_issues": COMMON_ISSUES,
        "recommendations": RECOMMENDATIONS,
    }