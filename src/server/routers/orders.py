from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field, computed_field

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
    date: datetime = Field(description="Data odpowiadająca aktualnemu statusowi zamówienia")
    items_count: int
    total: str


class OrderItem(BaseModel):
    product_id: str
    name: str
    image_url: Optional[str] = None
    quantity: int
    unit_price: str

    @computed_field
    @property
    def subtotal(self) -> str:
        return round(self.quantity * self.unit_price, 2)


class OrderDetail(BaseModel):
    id: str
    number: str
    status: OrderStatus
    date: datetime
    items: List[OrderItem]
    total: str


class OrdersListResponse(BaseModel):
    counts: OrderCounts
    status: Optional[OrderStatus] = Field(None, description="None gdy odpowiedź pochodzi z wyszukiwania")
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
        OrderSummary(id="zam_12345", number="12345", status=OrderStatus.new, date="2026-07-12T13:55:00Z", items_count=3, total="245.00"),
        OrderSummary(id="zam_12346", number="12346", status=OrderStatus.new, date="2026-07-12T09:10:00Z", items_count=1, total="89.00"),
    ],
    "to_ship": [
        OrderSummary(id="zam_12300", number="12300", status=OrderStatus.to_ship, date="2026-07-11T18:20:00Z", items_count=2, total="160.00"),
    ],
    "shipped": [
        OrderSummary(id="zam_12290", number="12290", status=OrderStatus.shipped, date="2026-07-10T11:05:00Z", items_count=4, total="320.00"),
    ],
    "completed": [
        OrderSummary(id="zam_12100", number="12100", status=OrderStatus.completed, date="2026-06-28T15:40:00Z", items_count=2, total="180.00"),
    ],
    "returned": [
        OrderSummary(id="zam_12050", number="12050", status=OrderStatus.returned, date="2026-06-20T10:00:00Z", items_count=1, total="65.00"),
    ],
}

ORDER_DETAILS: dict[str, OrderDetail] = {
    "zam_12345": OrderDetail(
        id="zam_12345",
        number="12345",
        status=OrderStatus.new,
        date="2026-07-12T13:55:00Z",
        items=[
            OrderItem(product_id="prod_1", name="kubek ceramiczny", image_url="https://example.com/images/prod_1.jpg", quantity=5, unit_price="20.00"),
            OrderItem(product_id="prod_2", name="talerz", image_url="https://example.com/images/prod_2.jpg", quantity=4, unit_price="15.00"),
            OrderItem(product_id="prod_3", name="doniczka", image_url="https://example.com/images/prod_3.jpg", quantity=1, unit_price="25.00"),
        ],
        total="185.00",
    ),
}

# GET /api/orders/?status=&search=
# GET /api/orders/{order_id}/

@router.get(
    "/",
    operation_id="list",
    summary="Lista zamówień",
    response_model=OrdersListResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def orders_list(
    status: OrderStatus = Query(
        OrderStatus.new,
        description="Sekcja zamówień do wyświetlenia",
    ),
    search: Optional[str] = Query(
        None,
        min_length=1,
        max_length=50,
        description="Wyszukiwanie po numerze zamówienia",
    ),
) -> OrdersListResponse:
    if search:
        matched = [o for orders in ORDERS_BY_STATUS.values() for o in orders if search in o.number]
        return OrdersListResponse(counts=COUNTS, status=None, search=search, orders=matched)

    return OrdersListResponse(counts=COUNTS, status=status, search=None, orders=ORDERS_BY_STATUS.get(status.value, []))


@router.get(
    "/{order_id}/",
    operation_id="detail",
    summary="Szczegóły zamówienia",
    response_model=OrderDetail,
    responses={
        404: {"description": "Zamówienie o podanym identyfikatorze nie zostało znalezione"},
        422: {"description": "Validation Error", "model": ValidationErrorResponse},
    },
)
def orders_detail(
    order_id: str = Path(..., description="Identyfikator zamówienia, np. zam_12345", pattern=r"^zam_\d+$"),
) -> OrderDetail:
    order = ORDER_DETAILS.get(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Zamówienie '{order_id}' nie zostało znalezione")
    return order
