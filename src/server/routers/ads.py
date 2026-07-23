from datetime import datetime, date as date_type
from enum import Enum
from typing import List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
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
    {"id": "camp_1", "name": "Campaign - Summer 2026", "date": "2026-07-01", "roas": 4.1, "cost": "1200.00", "revenue": "4920.00"},
    {"id": "camp_2", "name": "Campaign - New Arrivals", "date": "2026-06-15", "roas": 3.6, "cost": "900.00", "revenue": "3240.00"},
    {"id": "camp_3", "name": "Campaign - Clearance Sale", "date": "2026-05-20", "roas": 1.1, "cost": "1500.00", "revenue": "1650.00"},
    {"id": "camp_4", "name": "Campaign - Remarketing", "date": "2026-04-10", "roas": 5.2, "cost": "600.00", "revenue": "3120.00"},
]

RECOMMENDATIONS = [
    "Campaign 'Clearance Sale' has a ROAS of 1.1 - it generates a loss after accounting for margin, consider pausing it.",
    "Campaign 'Remarketing' has the highest ROAS - consider increasing its budget.",
]


class SortEnum(str, Enum):
    date = "date"
    roas = "roas"
    cost = "cost"
    revenue = "revenue"


class Campaign(BaseModel):
    id: str
    name: str
    date: date_type
    roas: float
    cost: str
    revenue: str


class EnrichedCampaign(Campaign):
    profit: str
    is_profitable: bool


class AdsListResponse(BaseModel):
    sort: SortEnum
    date_from: Optional[date_type] = None
    date_to: Optional[date_type] = None
    campaigns: List[Campaign]


class Kpis(BaseModel):
    spend: str
    roas: float
    acos: float
    clicks: int
    conversions: int


class AdsSummary(BaseModel):
    date_from: Optional[date_type] = None
    date_to: Optional[date_type] = None
    kpis: Kpis
    profitable: int
    unprofitable: int
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


def parse_date(value: str, param_name: str) -> date_type:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format in '{param_name}', expected YYYY-MM-DD",
        )


def filter_by_date_range(campaigns: list, date_from: Optional[date_type], date_to: Optional[date_type]) -> list:
    if not date_from and not date_to:
        return campaigns
    return [
        c for c in campaigns
        if (not date_from or datetime.strptime(c["date"], "%Y-%m-%d").date() >= date_from)
        and (not date_to or datetime.strptime(c["date"], "%Y-%m-%d").date() <= date_to)
    ]


@router.get(
    "/list/",
    operation_id="ads_list",
    summary="Advertising Campaigns - List",
    response_model=AdsListResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def ads_list(
    sort: SortEnum = Query(SortEnum.date, description="date, roas, cost, revenue"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="max number of campaigns to return, e.g. 3 for 'last 3 campaigns' with sort=date"),
    from_: Optional[str] = Query(
        None,
        alias="from",
        description="Start date of the range, format YYYY-MM-DD",
    ),
    to: Optional[str] = Query(
        None,
        description="End date of the range, format YYYY-MM-DD",
    ),
):
    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None

    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' cannot be later than 'to'")

    campaigns = filter_by_date_range(CAMPAIGNS, date_from, date_to)

    sort_key = {
        SortEnum.date: lambda c: c["date"],
        SortEnum.roas: lambda c: c["roas"],
        SortEnum.cost: lambda c: float(c["cost"]),
        SortEnum.revenue: lambda c: float(c["revenue"]),
    }[sort]
    campaigns = sorted(campaigns, key=sort_key, reverse=True)

    if limit is not None:
        campaigns = campaigns[:limit]

    return {
        "sort": sort,
        "date_from": date_from,
        "date_to": date_to,
        "campaigns": campaigns,
    }


@router.get(
    "/summary/",
    operation_id="ads_summary",
    summary="Advertising Campaigns - Summary",
    response_model=AdsSummary,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def ads_summary(
    min_roas: float = Query(1.5, description="profitability threshold - campaigns below this value are considered unprofitable"),
    from_: Optional[str] = Query(
        None,
        alias="from",
        description="Start date of the range, format YYYY-MM-DD",
    ),
    to: Optional[str] = Query(
        None,
        description="End date of the range, format YYYY-MM-DD",
    ),
):
    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None

    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' cannot be later than 'to'")

    enriched = [enrich(c, min_roas) for c in CAMPAIGNS]
    enriched = filter_by_date_range(enriched, date_from, date_to)

    profitable = sum(1 for c in enriched if c["is_profitable"])
    unprofitable = sum(1 for c in enriched if not c["is_profitable"])

    return {
        "date_from": date_from,
        "date_to": date_to,
        "kpis": KPIS,
        "profitable": profitable,
        "unprofitable": unprofitable,
        "recommendations": RECOMMENDATIONS,
    }