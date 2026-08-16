from datetime import datetime
from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...db.read import DatabaseReader

router = APIRouter()
reader = DatabaseReader()

class Order(BaseModel):
    id: str
    date: str
    value: str
 
class CustomerDetailResponse(BaseModel):
    id: str
    name: str
    first_purchase_date: str
    orders_count: int
    total_spent: str
    avg_order_value: str
    days_since_last_order: Optional[int] = None
    orders: List[Order]
 
class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str
 
 
class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]
 
 
def parse_order_date(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
  
def days_since_last_order(order_dates: list[str]) -> Optional[int]:
    if not order_dates:
        return None
    last_order_dt = parse_order_date(sorted(order_dates)[-1])
    return (datetime.now() - last_order_dt).days
 
@router.get(
    "/",
    operation_id="customers_detail",
    summary="Customer Profile",
    response_model=CustomerDetailResponse,
    responses={
        404: {"description": "Customer not found"},
        422: {"description": "Validation Error", "model": ValidationErrorResponse},
    },
)
def customers_detail(
    customer_id: int = Query(..., description="Customer identifier, e.g. 13"),
):
    customer = reader.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer not found: {customer_id}")
 
    orders = reader.get_customer_orders(customer_id)
    if not orders:
        raise HTTPException(status_code=404, detail=f"Customer {customer_id} has no orders.")
 
    order_dates = [o["order_date"] for o in orders]
    total_spent = sum(o["order_total"] for o in orders)
    orders_count = len(orders)
    avg_order_value = total_spent / orders_count if orders_count else 0.0
 
    return {
        "id": str(customer["customer_id"]),
        "name": customer["identifier"],
        "first_purchase_date": min(order_dates),
        "orders_count": orders_count,
        "total_spent": f"{total_spent:.2f}",
        "avg_order_value": f"{avg_order_value:.2f}",
        "days_since_last_order": days_since_last_order(order_dates),
        "orders": [
            {
                "id": str(o["order_id"]),
                "date": o["order_date"],
                "value": f"{o['order_total']:.2f}",
            }
            for o in orders
        ],
    }