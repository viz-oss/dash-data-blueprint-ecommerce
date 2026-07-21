from typing import List, Optional, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()

CUSTOMER_DETAILS = {
    "cust_1": {
        "id": "cust_1",
        "name": "Customer R.K.",
        "first_purchase_date": "2025-01-12",
        "orders_count": 12,
        "total_spent": "4200.00",
        "frequency_days": 18,
        "orders": [
            {"id": "ord_1_1", "date": "2026-06-20", "value": "350.00", "image_url": "https://picsum.photos/seed/ord_1_1/200"},
            {"id": "ord_1_2", "date": "2026-05-15", "value": "420.00", "image_url": "https://picsum.photos/seed/ord_1_2/200"},
            {"id": "ord_1_3", "date": "2026-04-02", "value": "290.00", "image_url": "https://picsum.photos/seed/ord_1_3/200"},
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
            {"id": "ord_2_1", "date": "2026-06-18", "value": "310.00", "image_url": "https://picsum.photos/seed/ord_2_1/200"},
            {"id": "ord_2_2", "date": "2026-05-28", "value": "280.00", "image_url": "https://picsum.photos/seed/ord_2_2/200"},
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
            {"id": "ord_10_1", "date": "2026-06-28", "value": "145.00", "image_url": "https://picsum.photos/seed/ord_10_1/200"},
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
            {"id": "ord_11_1", "date": "2026-07-01", "value": "89.00", "image_url": "https://picsum.photos/seed/ord_11_1/200"},
        ],
    },
}

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