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
    {"id": "prod_1", "name": "X200 Headphones", "our_price": "199.00", "competitor_price": "179.00"},
    {"id": "prod_2", "name": "USB-C Cable 2m", "our_price": "29.00", "competitor_price": "32.00"},
    {"id": "prod_3", "name": "Phone Case", "our_price": "49.00", "competitor_price": "45.00"},
    {"id": "prod_4", "name": "10000mAh Power Bank", "our_price": "89.00", "competitor_price": "75.00"},
    {"id": "prod_5", "name": "Wireless Charger", "our_price": "99.00", "competitor_price": "98.00"},
    {"id": "prod_6", "name": "Wireless Mouse", "our_price": "59.00", "competitor_price": "62.00"},
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
    "prod_1": "Sales dropped by 9% since the competitor lowered the price by 20 PLN.",
    "prod_4": "Sales remain stable, but the margin is below average with the current price difference.",
}

RECOMMENDATIONS = [
    "Product 'X200 Headphones' is 11% more expensive than the competition and is losing sales - consider reducing the price.",
    "Product '10000mAh Power Bank' is about 19% more expensive - check whether the margin allows for a price adjustment.",
    "Product 'USB-C Cable 2m' is cheaper than the competition and is gaining sales - good position, no changes needed.",
]


class PriceStatus(str, Enum):
    expensive = "expensive"
    cheaper = "cheaper"
    same = "same"


class SortField(str, Enum):
    name = "name"
    our_price = "our_price"
    competitor_price = "competitor_price"
    diff_pct = "diff_pct"


class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


def diff_pct(our_price: str, competitor_price: str) -> float:
    return round((float(our_price) - float(competitor_price)) / float(competitor_price) * 100, 1)


def price_status(diff: float) -> PriceStatus:
    if diff > 0:
        return PriceStatus.expensive
    if diff < 0:
        return PriceStatus.cheaper
    return PriceStatus.same


def build_comparison(products: list) -> list:
    comparison = []
    for p in products:
        diff = diff_pct(p["our_price"], p["competitor_price"])
        comparison.append({**p, "diff_pct": diff, "status": price_status(diff)})
    return comparison

class PriceComparisonItem(BaseModel):
    id: str
    name: str
    our_price: str
    competitor_price: str
    diff_pct: float
    status: PriceStatus

class CompetitionListResponse(BaseModel):
    products: List[PriceComparisonItem]

class CompetitionKPIs(BaseModel):
    avg_competitor_price: str
    price_diff_pct: float
    worse_conditions_count: int
    products_needing_action_count: int

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


class CompetitionSummaryResponse(CompetitionKPIs):
    needs_attention: List[AttentionItem]
    recommendations: List[str]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


@router.get(
    "/list/",
    operation_id="competition_list",
    summary="Competition - List",
    response_model=CompetitionListResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def competition_list(
    search: Optional[str] = Query(None, description="Search products by name"),
    sort_by: SortField = Query(SortField.diff_pct, description="Field to sort by"),
    order: SortOrder = Query(SortOrder.desc, description="Sort order"),
):
    products = PRODUCTS
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]

    comparison = build_comparison(products)
    comparison.sort(key=lambda p: p[sort_by], reverse=(order == SortOrder.desc))

    return {"products": comparison}


@router.get(
    "/summary/",
    operation_id="competition_summary",
    summary="Competition - Summary",
    response_model=CompetitionSummaryResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def competition_summary(
    action_threshold_pct: float = Query(10.0, description="Percentage threshold above which a product requires a pricing action"),
):
    attention = []
    for p in PRODUCTS:
        diff = diff_pct(p["our_price"], p["competitor_price"])
        if diff >= action_threshold_pct:
            attention.append({
                **p,
                "diff_pct": diff,
                "status": price_status(diff),
                "price_history": PRICE_HISTORY.get(p["id"], []),
                "sales_impact": SALES_IMPACT.get(p["id"], "No significant impact on sales."),
            })

    return {
        **KPIS,
        "needs_attention": attention,
        "recommendations": RECOMMENDATIONS,
    }