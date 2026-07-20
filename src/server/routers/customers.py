from enum import Enum
from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException, Query
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

CUSTOMER_DETAILS = {
    "cust_1": {
        "id": "cust_1",
        "name": "Customer R.K.",
        "first_purchase_date": "2025-01-12",
        "orders_count": 12,
        "total_spent": "4200.00",
        "frequency_days": 18,
        "orders": [
            {"date": "2026-06-20", "value": "350.00"},
            {"date": "2026-05-15", "value": "420.00"},
            {"date": "2026-04-02", "value": "290.00"},
        ],
    },
    "cust_2": {
        "id": "cust_2",
        "name": "Customer T.B.",
        "first_purchase_date": "2025-03-04",
        "orders_count": 9,
        "total_spent": "3100.00",
        "frequency_days": 21,
        "orders": [
            {"date": "2026-06-18", "value": "310.00"},
            {"date": "2026-05-28", "value": "280.00"},
        ],
    },
    "cust_10": {
        "id": "cust_10",
        "name": "Customer A.K.",
        "first_purchase_date": "2026-06-28",
        "orders_count": 1,
        "total_spent": "145.00",
        "frequency_days": None,
        "orders": [
            {"date": "2026-06-28", "value": "145.00"},
        ],
    },
    "cust_11": {
        "id": "cust_11",
        "name": "Customer M.W.",
        "first_purchase_date": "2026-07-01",
        "orders_count": 1,
        "total_spent": "89.00",
        "frequency_days": None,
        "orders": [
            {"date": "2026-07-01", "value": "89.00"},
        ],
    },
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


class Order(BaseModel):
    id: str
    date: str
    value: str
    image_url: str


class CustomerDetailResponse(BaseModel):
    id: str
    name: str
    first_purchase_date: str
    orders_count: int
    total_spent: str
    avg_order_value: str
    frequency_days: Optional[int] = None
    orders: List[Order]


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


@router.get(
    "/customer/",
    operation_id="customers_detail",
    summary="Customer Profile",
    response_model=CustomerDetailResponse,
    responses={
        404: {"description": "Customer not found"},
        422: {"description": "Validation Error", "model": ValidationErrorResponse},
    },
)
def customers_detail(
    customer_id: str = Query(..., description="Customer identifier, e.g. C-501"),
):
    customer = CUSTOMER_DETAILS.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer not found: {customer_id}")
    avg_order_value = f"{float(customer['total_spent']) / customer['orders_count']:.2f}"
    return {**customer, "avg_order_value": avg_order_value}