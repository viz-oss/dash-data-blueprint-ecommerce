from datetime import datetime, date as date_type
from enum import Enum
from typing import Any, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, computed_field

router = APIRouter()


class OrderStatus(str, Enum):
    new = "new"
    to_ship = "to_ship"
    shipped = "shipped"
    completed = "completed"
    returned = "returned"


class OrderItem(BaseModel):
    product_id: str
    name: str
    image_url: Optional[str] = None
    quantity: int
    unit_price: str

    @computed_field
    @property
    def subtotal(self) -> str:
        return f"{self.quantity * float(self.unit_price):.2f}"


class OrderDetail(BaseModel):
    id: str
    number: str
    status: OrderStatus
    date: date_type
    items: List[OrderItem]
    total: str


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


ORDER_DETAILS: dict[str, OrderDetail] = {
    "zam_12345": OrderDetail(
        id="zam_12345",
        number="12345",
        status=OrderStatus.new,
        date="2026-07-12",
        items=[
            OrderItem(
                product_id="prod_1",
                name="Ceramic Mug",
                image_url="https://example.com/images/prod_1.jpg",
                quantity=5,
                unit_price="20.00",
            ),
            OrderItem(
                product_id="prod_2",
                name="Plate",
                image_url="https://example.com/images/prod_2.jpg",
                quantity=4,
                unit_price="15.00",
            ),
            OrderItem(
                product_id="prod_3",
                name="Flower Pot",
                image_url="https://example.com/images/prod_3.jpg",
                quantity=1,
                unit_price="25.00",
            ),
        ],
        total="185.00",
    ),
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
    "/order/",
    operation_id="order_detail",
    summary="Order Details",
    response_model=OrderDetail,
    responses={
        404: {"description": "Order with the specified identifier was not found"},
        422: {"description": "Validation Error", "model": ValidationErrorResponse},
    },
)
def orders_detail(
    order_id: str = Query(
        ...,
        description="Order identifier, e.g. zam_12345",
        pattern=r"^zam_\d+$",
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
) -> OrderDetail:
    order = ORDER_DETAILS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' was not found")

    date_from = parse_date(from_, "from") if from_ else None
    date_to = parse_date(to, "to") if to else None

    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="'from' cannot be later than 'to'")

    if (date_from and order.date < date_from) or (date_to and order.date > date_to):
        raise HTTPException(
            status_code=404,
            detail=f"Order '{order_id}' is outside the specified date range",
        )

    return order