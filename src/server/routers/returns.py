from datetime import datetime, date as date_type
from typing import List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...db.read import DatabaseReader
from ...db.generate import ReturnReason, RETURN_REASONS 

router = APIRouter()
db = DatabaseReader()

RETURNS_HANDLING_COST_PER_UNIT = 12.50  # placeholder — brak realnej kolumny kosztu obsługi zwrotu w bazie


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
    share_of_returns_pct: float


class CommonIssue(BaseModel):
    issue: str
    count: int


class ReturnsListResponse(BaseModel):
    date_from: Optional[date_type] = None
    date_to: Optional[date_type] = None
    top_by_return_count: List[ProductReturnStat]
    top_by_return_rate: List[ProductReturnStat]
    return_reasons: List[ReturnReasonBreakdown]

class ReturnsSummary(BaseModel):
    date_from: Optional[date_type] = None
    date_to: Optional[date_type] = None

    total_returns: int
    return_rate_pct: float
    total_returned_value: str
    returns_handling_cost: str
    recommendations: List[str]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


def parse_date(value: str, param_name: str) -> date_type:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format in '{param_name}', expected YYYY-MM-DD",
        )


def validate_date_range(date_from: Optional[date_type], date_to: Optional[date_type]) -> None:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' can not be after 'to'")


def enrich_with_rate(products: list[dict]) -> list[dict]:
    return [
        {
            **p,
            "id": str(p["product_id"]),
            "return_rate_pct": round(p["returns_count"] / p["orders_count"] * 100, 1)
            if p["orders_count"]
            else 0.0,
            "value_returned": f"{p['value_returned']:.2f}",
        }
        for p in products
    ]


@router.get(
    "/list/",
    operation_id="returns_list",
    summary="Returns and Complaints - List",
    response_model=ReturnsListResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def returns_list(
    limit: int = Query(5, ge=1, le=20, description="Number of items to display in each ranking"),
    from_: Optional[str] = Query(None, alias="from", description="Starting date of the range, format YYYY-MM-DD"),
    to: Optional[str] = Query(None, description="Ending date of the range, format YYYY-MM-DD"),
):
    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None
    validate_date_range(date_from, date_to)

    df = date_from.isoformat() if date_from else None
    dt = date_to.isoformat() if date_to else None

    stats = db.get_return_stats_by_product(df, dt)
    enriched = enrich_with_rate(stats)

    top_by_return_count = sorted(enriched, key=lambda p: p["returns_count"], reverse=True)[:limit]
    top_by_return_rate = sorted(enriched, key=lambda p: p["return_rate_pct"], reverse=True)[:limit]

    reason_counts = db.get_return_reason_counts(df, dt)
    total_reasons = sum(reason_counts.values()) or 1 
    return_reasons = sorted(
            [
                {
                    "reason": reason,
                    "count": reason_counts.get(reason, 0),
                    "share_of_returns_pct": round(reason_counts.get(reason, 0) / total_reasons * 100, 1),
                }
                for reason in RETURN_REASONS
            ],
            key=lambda r: r["count"],
            reverse=True,
        )
    return {
        "date_from": date_from,
        "date_to": date_to,
        "top_by_return_count": top_by_return_count,
        "top_by_return_rate": top_by_return_rate,
        "return_reasons": return_reasons,

    }


@router.get(
    "/summary/",
    operation_id="returns_summary",
    summary="Returns and Complaints - Summary",
    response_model=ReturnsSummary,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def returns_summary(
    from_: Optional[str] = Query(None, alias="from", description="Starting date of the range, format YYYY-MM-DD"),
    to: Optional[str] = Query(None, description="Ending date of the range, format YYYY-MM-DD"),
):
    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None
    validate_date_range(date_from, date_to)

    totals = db.get_returns_totals(
        date_from.isoformat() if date_from else None,
        date_to.isoformat() if date_to else None,
    )

    return_rate_pct = (
        round(totals["total_returns"] / totals["total_orders"] * 100, 1)
        if totals["total_orders"]
        else 0.0
    )

    return {
        "date_from": date_from,
        "date_to": date_to,
        "total_returns": totals["total_returns"],
        "return_rate_pct": return_rate_pct,
        "total_returned_value": f"{totals['total_returned_value']:.2f}",
        "returns_handling_cost": f"{totals['total_returns'] * RETURNS_HANDLING_COST_PER_UNIT:.2f}",
        "recommendations": [],
    }