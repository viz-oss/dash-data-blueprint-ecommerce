from datetime import datetime, date as date_type
from enum import Enum
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()

class OrderStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    ready_to_ship = "ready_to_ship"
    shipped = "shipped"
    delivered = "delivered"
    delivery_failed = "delivery_failed"
    return_requested = "return_requested"
    returned = "returned"
    exchange = "exchange"
    on_hold = "on_hold"
    cancelled = "cancelled"
    awaiting_payment = "awaiting_payment"
    payment_failed = "payment_failed"

class OrderCounts(BaseModel):
    pending: int
    processing: int
    ready_to_ship: int
    shipped: int
    delivered: int
    delivery_failed: int
    return_requested: int
    returned: int
    exchange: int
    on_hold: int
    cancelled: int
    awaiting_payment: int
    payment_failed: int

class OrderSummary(BaseModel):
    id: str
    number: str
    status: OrderStatus
    date: date_type = Field(description="Date corresponding to the current order status")
    items_count: int
    total: str

class OrdersListResponse(BaseModel):
    summary: OrderCounts
    status: OrderStatus
    orders: List[OrderSummary]

class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str

class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]

SUMMARY = OrderCounts(
    pending=11,
    processing=5,
    ready_to_ship=5,
    shipped=20,
    delivered=340,
    delivery_failed=2,
    return_requested=3,
    returned=5,
    exchange=1,
    on_hold=4,
    cancelled=7,
    awaiting_payment=6,
    payment_failed=2,
)

ORDERS_BY_STATUS: dict[str, List[OrderSummary]] = {
    "pending": [
        OrderSummary(id="zam_12345", number="12345", status=OrderStatus.pending, date="2026-07-12", items_count=3, total="245.00"),
        OrderSummary(id="zam_12346", number="12346", status=OrderStatus.pending, date="2026-07-12", items_count=1, total="89.00"),
    ],
    "processing": [
        OrderSummary(id="zam_12300", number="12300", status=OrderStatus.processing, date="2026-07-11", items_count=2, total="160.00"),
    ],
    "ready_to_ship": [],
    "shipped": [
        OrderSummary(id="zam_12290", number="12290", status=OrderStatus.shipped, date="2026-07-10", items_count=4, total="320.00"),
    ],
    "delivered": [
        OrderSummary(id="zam_12100", number="12100", status=OrderStatus.delivered, date="2026-06-28", items_count=2, total="180.00"),
    ],
    "delivery_failed": [],
    "return_requested": [],
    "returned": [
        OrderSummary(id="zam_12050", number="12050", status=OrderStatus.returned, date="2026-06-20", items_count=1, total="65.00"),
    ],
    "exchange": [],
    "on_hold": [],
    "cancelled": [],
    "awaiting_payment": [],
    "payment_failed": [],
}


def parse_date(value: str, param_name: str) -> date_type:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format in '{param_name}', expected YYYY-MM-DD",
        )


@router.get(
    "/",
    operation_id="orders_list",
    summary="Order List",
    response_model=OrdersListResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def orders_list(
    status: OrderStatus = Query(
        OrderStatus.pending,
        description="Order section to display",
    ),
    from_: Optional[str] = Query(
        None,
        alias="from",
        description="Start date of the range, format YYYY-MM-DD",
    ),
    to: Optional[str] = Query(
        None,
        description="End date of the range, format YYYY-MM-DD",
    ),
) -> OrdersListResponse:
    orders = ORDERS_BY_STATUS.get(status.value, [])

    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None

    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' cannot be later than 'to'")

    if date_from or date_to:
        orders = [
            o for o in orders
            if (not date_from or o.date >= date_from) and (not date_to or o.date <= date_to)
        ]

    return OrdersListResponse(summary=SUMMARY, status=status, orders=orders)