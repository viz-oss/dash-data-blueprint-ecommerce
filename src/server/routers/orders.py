from datetime import datetime, date as date_type
from enum import Enum
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()

class OrderStatus(str, Enum):
    pending = "pending"
    awaiting_payment = "awaiting_payment"
    payment_failed = "payment_failed"
    processing = "processing"
    ready_to_ship = "ready_to_ship"
    shipped = "shipped"
    delivered_end = "delivered_end"
    delivery_failed = "delivery_failed"
    return_requested = "return_requested"
    return_accepted = "return_accepted"
    return_rejected = "return_rejected"
    returned = "returned"
    refunded_end = "refunded_end"
    exchanged_end = "exchanged_end"
    on_hold = "on_hold"
    cancelled_end = "cancelled_end"
    buyer_canceled_end = "buyer_canceled_end"

class OrderCounts(BaseModel):
    pending: int
    awaiting_payment: int
    payment_failed: int
    processing: int
    ready_to_ship: int
    shipped: int
    delivered_end: int
    delivery_failed: int
    return_requested: int
    return_accepted: int
    return_rejected: int
    returned: int
    refunded_end: int
    exchanged_end: int
    on_hold: int
    cancelled_end: int
    buyer_canceled_end: int

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
    awaiting_payment=6,
    payment_failed=2,
    processing=5,
    ready_to_ship=5,
    shipped=20,
    delivered_end=340,
    delivery_failed=2,
    return_requested=3,
    return_accepted=2,
    return_rejected=1,
    returned=5,
    refunded_end=4,
    exchanged_end=1,
    on_hold=4,
    cancelled_end=7,
    buyer_canceled_end=3,
)

ORDERS_BY_STATUS: dict[str, List[OrderSummary]] = {
    "pending": [
        OrderSummary(id="zam_12345", number="12345", status=OrderStatus.pending, date="2026-07-12", items_count=3, total="245.00"),
        OrderSummary(id="zam_12346", number="12346", status=OrderStatus.pending, date="2026-07-12", items_count=1, total="89.00"),
    ],
    "awaiting_payment": [
        OrderSummary(id="zam_12360", number="12360", status=OrderStatus.awaiting_payment, date="2026-07-13", items_count=2, total="120.00"),
    ],
    "payment_failed": [
        OrderSummary(id="zam_12361", number="12361", status=OrderStatus.payment_failed, date="2026-07-13", items_count=1, total="59.00"),
    ],
    "processing": [
        OrderSummary(id="zam_12300", number="12300", status=OrderStatus.processing, date="2026-07-11", items_count=2, total="160.00"),
    ],
    "ready_to_ship": [],
    "shipped": [
        OrderSummary(id="zam_12290", number="12290", status=OrderStatus.shipped, date="2026-07-10", items_count=4, total="320.00"),
    ],
    "delivered_end": [
        OrderSummary(id="zam_12100", number="12100", status=OrderStatus.delivered_end, date="2026-06-28", items_count=2, total="180.00"),
    ],
    "delivery_failed": [],
    "return_requested": [],
    "return_accepted": [
        OrderSummary(id="zam_12060", number="12060", status=OrderStatus.return_accepted, date="2026-06-22", items_count=1, total="75.00"),
    ],
    "return_rejected": [],
    "returned": [
        OrderSummary(id="zam_12050", number="12050", status=OrderStatus.returned, date="2026-06-20", items_count=1, total="65.00"),
    ],
    "refunded_end": [
        OrderSummary(id="zam_12040", number="12040", status=OrderStatus.refunded_end, date="2026-06-18", items_count=1, total="65.00"),
    ],
    "exchanged_end": [],
    "on_hold": [],
    "cancelled_end": [],
    "buyer_canceled_end": [],
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