from typing import List, Optional, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

KPIS = {
    "listed": 320,
    "in_stock_units": 15400,
    "low_stock_count": 12,
    "unavailable_count": 5,
}

SECTION_LABELS = {
    "active-offers": "Active Offers",
    "low-stock": "Low Stock",
    "out-of-stock": "Out of Stock",
    "fast-selling": "Fast Selling",
    "stale-products": "Stale Products",
}

PRODUCTS = {
    "active-offers": [
        {"id": "prod_123", "name": "X200 Headphones", "stock": 84, "status": "ok"},
        {"id": "prod_456", "name": "USB-C Cable 2m", "stock": 210, "status": "ok"},
        {"id": "prod_789", "name": "Phone Case", "stock": 0, "status": "unavailable"},
        {"id": "prod_111", "name": "Wireless Mouse", "stock": 60, "status": "ok"},
        {"id": "prod_222", "name": "Mechanical Keyboard", "stock": 34, "status": "ok"},
        {"id": "prod_333", "name": "Mouse Pad", "stock": 120, "status": "ok"},
        {"id": "prod_444", "name": "USB-C 6-in-1 Hub", "stock": 27, "status": "ok"},
    ],
    "low-stock": [
        {
            "id": "prod_321",
            "name": "10000mAh Power Bank",
            "stock": 3,
            "status": "low_stock",
            "days_until_out": 6,
        },
        {
            "id": "prod_654",
            "name": "Wireless Charger",
            "stock": 5,
            "status": "low_stock",
            "days_until_out": 9,
        },
    ],
    "out-of-stock": [
        {
            "id": "prod_789",
            "name": "Phone Case",
            "stock": 0,
            "status": "unavailable",
            "days_since_out": 12,
        },
    ],
    "fast-selling": [
        {
            "id": "prod_321",
            "name": "10000mAh Power Bank",
            "stock": 3,
            "status": "low_stock",
            "days_until_out": 6,
            "sales_velocity": "high",
        },
        {
            "id": "prod_654",
            "name": "Wireless Charger",
            "stock": 5,
            "status": "low_stock",
            "days_until_out": 9,
            "sales_velocity": "medium",
        },
    ],
    "stale-products": [
        {
            "id": "prod_999",
            "name": "Old Headphones Model",
            "stock": 45,
            "status": "stale",
            "days_without_sale": 60,
        },
        {
            "id": "prod_888",
            "name": "2023 Phone Case",
            "stock": 30,
            "status": "stale",
            "days_without_sale": 45,
        },
    ],
}

RECOMMENDATIONS = [
    "Product '10000mAh Power Bank' will run out of stock in approximately 6 days - place an order with the supplier.",
    "Product 'Phone Case' has been out of stock for 12 days.",
]

class Product(BaseModel):
    id: str
    name: str
    stock: int
    status: str
    days_until_out: Optional[int] = None
    days_since_out: Optional[int] = None
    days_without_sale: Optional[int] = None
    sales_velocity: Optional[str] = None


class Section(BaseModel):
    key: str
    label: str
    count: int
    products: List[Product]


class InventoryResponse(BaseModel):
    kpis: dict
    sections: List[Section]
    recommendations: List[str]


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


@router.get(
    "/",
    operation_id="inventory_list",
    summary="Magazyn",
    response_model=InventoryResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def inventory_list(limit: int = Query(10, ge=1, le=100)):
    sections = [
        {"key": key, "label": SECTION_LABELS[key], "count": len(products), "products": products[:limit]}
        for key, products in PRODUCTS.items()
    ]
    return {"kpis": KPIS, "sections": sections, "recommendations": RECOMMENDATIONS}
