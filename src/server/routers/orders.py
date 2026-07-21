from datetime import datetime, date as date_type
from enum import Enum
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


class OrderStatus(str, Enum):
    new = "new"
    to_ship = "to_ship"
    shipped = "shipped"
    completed = "completed"
    returned = "returned"


class OrderCounts(BaseModel):
    new: int
    to_ship: int
    shipped: int
    completed: int
    returned: int


class OrderSummary(BaseModel):
    id: str
    number: str
    status: OrderStatus
    date: date_type = Field(description="Date corresponding to the current order status")
    items_count: int
    total: str


class OrdersListResponse(BaseModel):
    counts: OrderCounts
    status: Optional[OrderStatus] = Field(None, description="None when the response comes from a search")
    search: Optional[str] = None
    orders: List[OrderSummary]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


COUNTS = OrderCounts(new=12, to_ship=8, shipped=20, completed=340, returned=5)

ORDERS_BY_STATUS: dict[str, List[OrderSummary]] = {
    "new": [
        OrderSummary(id="zam_12345", number="12345", status=OrderStatus.new, date="2026-07-12", items_count=3, total="245.00"),
        OrderSummary(id="zam_12346", number="12346", status=OrderStatus.new, date="2026-07-12", items_count=1, total="89.00"),
    ],
    "to_ship": [
        OrderSummary(id="zam_12300", number="12300", status=OrderStatus.to_ship, date="2026-07-11", items_count=2, total="160.00"),
    ],
    "shipped": [
        OrderSummary(id="zam_12290", number="12290", status=OrderStatus.shipped, date="2026-07-10", items_count=4, total="320.00"),
    ],
    "completed": [
        OrderSummary(id="zam_12100", number="12100", status=OrderStatus.completed, date="2026-06-28", items_count=2, total="180.00"),
    ],
    "returned": [
        OrderSummary(id="zam_12050", number="12050", status=OrderStatus.returned, date="2026-06-20", items_count=1, total="65.00"),
    ],
}


def parse_date(value: str, param_name: str) -> date_type:
    try:
        return datetime.strptime(value, "%Y.%m.%d").date()
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid date format in '{param_name}', expected YYYY.MM.DD",
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
        OrderStatus.new,
        description="Order section to display",
    ),
    search: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        description="Search by order number",
    ),
    from_: Optional[str] = Query(
        None,
        alias="from",
        description="Start date of the range, format YYYY.MM.DD",
    ),
    to: Optional[str] = Query(
        None,
        description="End date of the range, format YYYY.MM.DD",
    ),
) -> OrdersListResponse:
    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None

    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' cannot be later than 'to'")

    def in_range(order: OrderSummary) -> bool:
        if date_from and order.date < date_from:
            return False
        if date_to and order.date > date_to:
            return False
        return True

    if search:
        matched = [o for orders in ORDERS_BY_STATUS.values() for o in orders if search in o.number]
        matched = [o for o in matched if in_range(o)]
        return OrdersListResponse(counts=COUNTS, status=None, search=search, orders=matched)

    orders = [o for o in ORDERS_BY_STATUS.get(status.value, []) if in_range(o)]
    return OrdersListResponse(counts=COUNTS, status=status, search=None, orders=orders)