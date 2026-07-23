from datetime import datetime, date as date_type
from enum import Enum
from typing import List, Any, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()

PRODUCT_RETURNS = [
    {"id": "prod_1", "name": "Headphones X200", "returns_count": 18, "orders_count": 240, "value_returned": "3200.00"},
    {"id": "prod_3", "name": "Phone Case", "returns_count": 25, "orders_count": 180, "value_returned": "1225.00"},
    {"id": "prod_4", "name": "10000mAh Power Bank", "returns_count": 9, "orders_count": 95, "value_returned": "801.00"},
    {"id": "prod_5", "name": "Wireless Charger", "returns_count": 6, "orders_count": 150, "value_returned": "594.00"},
    {"id": "prod_6", "name": "Wireless Mouse", "returns_count": 4, "orders_count": 300, "value_returned": "236.00"},
]

RETURN_REASON_COUNTS = {
    "not_as_described": 22,
    "wrong_size": 15,
    "damaged_product": 12,
    "quality_issue": 8,
    "changed_mind": 5,
}

COMPLAINTS_BY_PRODUCT = [
    {"id": "prod_3", "name": "Phone Case", "complaints_count": 14},
    {"id": "prod_1", "name": "Headphones X200", "complaints_count": 10},
    {"id": "prod_7", "name": "Action Camera", "complaints_count": 6},
    {"id": "prod_5", "name": "Wireless Charger", "complaints_count": 3},
]

COMMON_ISSUES = [
    {"issue": "product does not match the website description", "count": 14},
    {"issue": "manufacturing defect or shipping damage", "count": 11},
    {"issue": "product does not perform as expected", "count": 8},
    {"issue": "delay in replacement or repair", "count": 5},
]

RECOMMENDATIONS = [
    "Product 'Phone Case' has the highest return rate - review the product photos and description.",
    "The most common return reason is 'not as described' - verify product listings with high return rates.",
    "Product 'Phone Case' also generates the most complaints - prioritize checking supplier quality.",
]


class ReturnReason(str, Enum):
    not_as_described = "not_as_described"
    wrong_size = "wrong_size"
    damaged_product = "damaged_product"
    quality_issue = "quality_issue"
    changed_mind = "changed_mind"
    other = "other"

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


class ReturnsListResponse(BaseModel):
    date_from: Optional[date_type] = None
    date_to: Optional[date_type] = None
    top_by_return_count: List[ProductReturnStat]
    top_by_return_rate: List[ProductReturnStat]
    return_reasons: List[ReturnReasonBreakdown]
    top_by_complaints: List[ComplaintProductStat]
    common_issues: List[CommonIssue]


class ReturnsSummary(BaseModel):
    date_from: Optional[date_type] = None
    date_to: Optional[date_type] = None

    total_returns: int
    return_rate_pct: float
    total_returned_value: str
    returns_handling_cost: str
    complaints_count: int

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


def enrich_with_rate(products: list) -> list:
    return [
        {**p, "return_rate_pct": round(p["returns_count"] / p["orders_count"] * 100, 1)}
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
    from_: Optional[str] = Query(
        None, alias="from", description="Starting date of the range, format YYYY-MM-DD"
    ),
    to: Optional[str] = Query(
        None, description="Ending date of the range, format YYYY-MM-DD"
    ),
):
    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None
    validate_date_range(date_from, date_to)

    enriched = enrich_with_rate(PRODUCT_RETURNS)

    top_by_return_count = sorted(enriched, key=lambda p: p["returns_count"], reverse=True)[:limit]
    top_by_return_rate = sorted(enriched, key=lambda p: p["return_rate_pct"], reverse=True)[:limit]

    total_reasons = sum(RETURN_REASON_COUNTS.values())
    return_reasons = [
        {
            "reason": reason,
            "count": count,
            "share_pct": round(count / total_reasons * 100, 1),
        }
        for reason, count in RETURN_REASON_COUNTS.items()
    ]

    top_by_complaints = sorted(
        COMPLAINTS_BY_PRODUCT,
        key=lambda c: c["complaints_count"],
        reverse=True,
    )[:limit]

    return {
        "date_from": date_from,
        "date_to": date_to,
        "top_by_return_count": top_by_return_count,
        "top_by_return_rate": top_by_return_rate,
        "return_reasons": return_reasons,
        "top_by_complaints": top_by_complaints,
        "common_issues": COMMON_ISSUES,
    }

@router.get(
    "/summary/",
    operation_id="returns_summary",
    summary="Returns and Complaints - Summary",
    response_model=ReturnsSummary,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def returns_summary(
    from_: Optional[str] = Query(
        None, alias="from", description="Starting date of the range, format YYYY-MM-DD"
    ),
    to: Optional[str] = Query(
        None, description="Ending date of the range, format YYYY-MM-DD"
    ),
):
    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None
    validate_date_range(date_from, date_to)

    total_returns = sum(p["returns_count"] for p in PRODUCT_RETURNS)
    total_returned_value = sum(float(p["value_returned"]) for p in PRODUCT_RETURNS)
    total_orders = sum(p["orders_count"] for p in PRODUCT_RETURNS)
    complaints_count = sum(c["complaints_count"] for c in COMPLAINTS_BY_PRODUCT)

    return {
        "date_from": date_from,
        "date_to": date_to,
        "total_returns": total_returns,
        "return_rate_pct": round(total_returns / total_orders * 100, 1),
        "total_returned_value": f"{total_returned_value:.2f}",
        "returns_handling_cost": "1450.00",
        "complaints_count": complaints_count,
        "recommendations": RECOMMENDATIONS,
    }