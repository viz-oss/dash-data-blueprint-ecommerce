from datetime import datetime, date as date_type
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...db.read import DatabaseReader

router = APIRouter()
DB_PATH = Path(__file__).resolve().parents[3] / "db.sqlite"
db_reader = DatabaseReader(db_path=str(DB_PATH))


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


class OrderSummary(BaseModel):
    id: str
    status: OrderStatus
    date: date_type = Field(description="Date corresponding to the current order status")
    total: str

class OrdersListResponse(BaseModel):
    status: OrderStatus
    orders: List[OrderSummary]

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



def get_orders_by_status(
    status: OrderStatus,
    date_from: Optional[date_type] = None,
    date_to: Optional[date_type] = None,
) -> List[OrderSummary]:
    rows = db_reader.get_orders_by_status(
        status.value,
        date_from.isoformat() if date_from else None,
        date_to.isoformat() if date_to else None,
    )
    return [
        OrderSummary(
            id=str(row["order_id"]),
            status=row["order_status"],
            date=row["order_date"][:10],
            total=row["order_total"],
        )
        for row in rows
    ]


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
    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None

    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' cannot be later than 'to'")

    orders = get_orders_by_status(status, date_from, date_to)

    return OrdersListResponse(status=status, orders=orders)