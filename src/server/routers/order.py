from datetime import date as date_type
from pathlib import Path
from typing import Any, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, computed_field

from ...db.read import DatabaseReader
from .orders import OrderStatus

router = APIRouter()
DB_PATH = Path(__file__).resolve().parents[3] / "db.sqlite"
db_reader = DatabaseReader(db_path=str(DB_PATH))


class OrderItem(BaseModel):
    product_id: str
    name: str
    quantity: int
    unit_price: str

    @computed_field
    @property
    def subtotal(self) -> str:
        return f"{self.quantity * float(self.unit_price):.2f}"


class Delivery(BaseModel):
    # invoice = True (faktura na firmę): first_name = nazwa firmy, last_name = NIP
    # invoice = False (paragon / os. prywatna): zwykłe imię i nazwisko odbiorcy
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None
    country_code: str | None = None
    city: str | None = None
    street: str | None = None
    postal_code: str | None = None
    courier: str | None = None
    cost: str | None = None


class OrderDetail(BaseModel):
    id: str
    status: OrderStatus
    date: date_type
    invoice: bool
    delivery: Delivery
    items: List[OrderItem]
    total: str

    @computed_field
    @property
    def company_name(self) -> str | None:
        return self.delivery.first_name if self.invoice else None

    @computed_field
    @property
    def nip(self) -> str | None:
        return self.delivery.last_name if self.invoice else None


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


@router.get(
    "/",
    operation_id="order_detail",
    summary="Order Details",
    response_model=OrderDetail,
    responses={
        404: {"description": "Order with the specified identifier was not found"},
        422: {"description": "Validation Error", "model": ValidationErrorResponse},
    },
)
def orders_detail(
    order_id: int = Query(
        ...,
        description="Order identifier (order_id)",
        gt=0,
    ),
) -> OrderDetail:
    order = db_reader.get_order_by_id(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' was not found")

    items = db_reader.get_order_items(order_id)

    return OrderDetail(
        id=str(order["order_id"]),
        status=order["order_status"],
        date=order["order_date"][:10],
        invoice=bool(order["invoice"]),
        delivery=Delivery(
            first_name=order["delivery_first_name"],
            last_name=order["delivery_last_name"],
            phone=order["delivery_phone"],
            country_code=order["delivery_country_code"],
            city=order["delivery_city"],
            street=order["delivery_street"],
            postal_code=order["delivery_postal_code"],
            courier=order["courier"],
            cost=order["delivery_cost"],
        ),
        items=[
            OrderItem(
                product_id=str(item["product_id"]),
                name=item["name"],
                quantity=item["quantity"],
                unit_price=item["selling_price"],
            )
            for item in items
        ],
        total=order["order_total"],
    )