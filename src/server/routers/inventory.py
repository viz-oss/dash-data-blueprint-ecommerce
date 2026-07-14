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
    "aktywne-oferty": "Aktywne oferty",
    "niski-stan": "Niski stan magazynowy",
    "braki-w-magazynie": "Braki w magazynie",
    "szybko-sie-koncza": "Szybko się wyprzedają",
    "zalegajace-produkty": "Zalegające produkty",
}

PRODUCTS = {
    "aktywne-oferty": [
        {"id": "prod_123", "name": "sluchawki x200", "stock": 84, "status": "ok"},
        {"id": "prod_456", "name": "kabel usb-c 2m", "stock": 210, "status": "ok"},
        {"id": "prod_789", "name": "etui na telefon", "stock": 0, "status": "unavailable"},
        {"id": "prod_111", "name": "mysz bezprzewodowa", "stock": 60, "status": "ok"},
        {"id": "prod_222", "name": "klawiatura mechaniczna", "stock": 34, "status": "ok"},
        {"id": "prod_333", "name": "podkładka pod mysz", "stock": 120, "status": "ok"},
        {"id": "prod_444", "name": "hub usb-c 6w1", "stock": 27, "status": "ok"},
    ],
    "niski-stan": [
        {"id": "prod_321", "name": "powerbank 10000mah", "stock": 3, "status": "low_stock", "days_until_out": 6},
        {"id": "prod_654", "name": "ladowarka bezprzewodowa", "stock": 5, "status": "low_stock", "days_until_out": 9},
    ],
    "braki-w-magazynie": [
        {"id": "prod_789", "name": "etui na telefon", "stock": 0, "status": "unavailable", "days_since_out": 12},
    ],
    "szybko-sie-koncza": [
        {"id": "prod_321", "name": "powerbank 10000mah", "stock": 3, "status": "low_stock", "days_until_out": 6, "sales_velocity": "wysoka"},
        {"id": "prod_654", "name": "ladowarka bezprzewodowa", "stock": 5, "status": "low_stock", "days_until_out": 9, "sales_velocity": "srednia"},
    ],
    "zalegajace-produkty": [
        {"id": "prod_999", "name": "stary model sluchawek", "stock": 45, "status": "stale", "days_without_sale": 60},
        {"id": "prod_888", "name": "etui rocznika 2023", "stock": 30, "status": "stale", "days_without_sale": 45},
    ],
}

RECOMMENDATIONS = [
    "produkt 'powerbank 10000mah' wyczerpie sie za ok. 6 dni - zloz zamowienie u dostawcy",
    "produkt 'etui na telefon' zalega jako niedostepny od 12 dni",
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
