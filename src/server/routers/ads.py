from enum import Enum
from typing import List, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

KPIS = {
    "spend": "9000.00",
    "roas": 3.2,
    "acos": 0.28,
    "clicks": 4200,
    "conversions": 310,
}

CAMPAIGNS = [
    {"id": "camp_1", "name": "Campaign - Summer 2026", "roas": 4.1, "cost": "1200.00", "revenue": "4920.00"},
    {"id": "camp_2", "name": "Campaign - New Arrivals", "roas": 3.6, "cost": "900.00", "revenue": "3240.00"},
    {"id": "camp_3", "name": "Campaign - Clearance Sale", "roas": 1.1, "cost": "1500.00", "revenue": "1650.00"},
    {"id": "camp_4", "name": "Campaign - Remarketing", "roas": 5.2, "cost": "600.00", "revenue": "3120.00"},
]

RECOMMENDATIONS = [
    "Campaign 'Clearance Sale' has a ROAS of 1.1 - it generates a loss after accounting for margin, consider pausing it.",
    "Campaign 'Remarketing' has the highest ROAS - consider increasing its budget.",
]


class SortEnum(str, Enum):
    roas = "roas"
    cost = "cost"
    revenue = "revenue"


class Campaign(BaseModel):
    id: str
    name: str
    roas: float
    cost: str
    revenue: str
    profit: str
    is_profitable: bool


class AdsResponse(BaseModel):
    kpis: dict
    sort: SortEnum
    campaigns: List[Campaign]
    top_by_roas: List[Campaign]
    unprofitable: List[Campaign]
    recommendations: List[str]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


def enrich(campaign: dict, min_roas: float) -> dict:
    profit = float(campaign["revenue"]) - float(campaign["cost"])
    return {
        **campaign,
        "profit": f"{profit:.2f}",
        "is_profitable": campaign["roas"] >= min_roas,
    }


@router.get(
    "/",
    operation_id="ads_list",
    summary="Advertising Campaigns",
    response_model=AdsResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def ads_list(
    sort: SortEnum = Query(SortEnum.roas, description="roas, cost, revenue"),
    limit: int = Query(3, ge=1, le=10, description="number of campaigns to display in the top ROAS ranking"),
    min_roas: float = Query(1.5, description="profitability threshold - campaigns below this value are considered unprofitable"),
):
    enriched = [enrich(c, min_roas) for c in CAMPAIGNS]

    sort_key = {
        SortEnum.roas: lambda c: c["roas"],
        SortEnum.cost: lambda c: float(c["cost"]),
        SortEnum.revenue: lambda c: float(c["revenue"]),
    }[sort]
    campaigns = sorted(enriched, key=sort_key, reverse=True)

    top_by_roas = sorted(enriched, key=lambda c: c["roas"], reverse=True)[:limit]
    unprofitable = sorted(
        [c for c in enriched if not c["is_profitable"]],
        key=lambda c: c["roas"],
    )

    return {
        "kpis": KPIS,
        "sort": sort,
        "campaigns": campaigns,
        "top_by_roas": top_by_roas,
        "unprofitable": unprofitable,
        "recommendations": RECOMMENDATIONS,
    }