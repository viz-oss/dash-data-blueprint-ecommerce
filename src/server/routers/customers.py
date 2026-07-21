from enum import Enum
from typing import List, Optional, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

KPIS = {
    "total": 2100,
    "new_this_month": 85,
    "avg_orders_per_customer": 1.8,
    "avg_rating": 4.5,
}

SEGMENTS = {
    "new": [
        {"id": "cust_10", "name": "Customer A.K.", "total_spent": "145.00", "orders": 1, "frequency_days": None},
        {"id": "cust_11", "name": "Customer M.W.", "total_spent": "89.00", "orders": 1, "frequency_days": None},
    ],
    "top": [
        {"id": "cust_1", "name": "Customer R.K.", "total_spent": "4200.00", "orders": 12, "frequency_days": 18},
        {"id": "cust_2", "name": "Customer T.B.", "total_spent": "3100.00", "orders": 9, "frequency_days": 21},
    ],
}

RECOMMENDATIONS = [
    "Customer 'Customer P.S.' has not placed an order for 34 days - consider sending a reminder or a discount.",
    "New customers ('Customer A.K.', 'Customer M.W.') - consider sending a welcome discount code for their next purchase.",
]


class SegmentEnum(str, Enum):
    new = "new"
    top = "top"


class CustomerSummary(BaseModel):
    id: str
    name: str
    total_spent: str
    orders: int
    frequency_days: Optional[int] = None
    avg_order_value: str


class Kpis(BaseModel):
    total: int
    new_this_month: int
    avg_orders_per_customer: float
    avg_rating: float


class CustomersListResponse(BaseModel):
    kpis: Kpis
    segment: SegmentEnum
    customers: List[CustomerSummary]
    recommendations: List[str]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


@router.get(
    "/",
    operation_id="customers_list",
    summary="Customer Statistics",
    response_model=CustomersListResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def customers_list(segment: SegmentEnum = Query(SegmentEnum.top)):
    customers = SEGMENTS[segment.value]
    enriched = [
        {**c, "avg_order_value": f"{float(c['total_spent']) / c['orders']:.2f}"}
        for c in customers
    ]
    if segment == SegmentEnum.top:
        enriched.sort(key=lambda c: float(c["total_spent"]), reverse=True)
    return {
        "kpis": KPIS,
        "segment": segment,
        "customers": enriched,
        "recommendations": RECOMMENDATIONS,
    }