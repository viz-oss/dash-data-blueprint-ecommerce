from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter()

COUNTS = {"new": 12, "to_ship": 8, "shipped": 20, "completed": 340, "returned": 5}

ORDERS_BY_STATUS = {
    "new": [
        {"id": "zam_12345", "number": "12345", "date": "2026-07-12T13:55:00Z", "items_count": 3, "total": 245.00},
        {"id": "zam_12346", "number": "12346", "date": "2026-07-12T09:10:00Z", "items_count": 1, "total": 89.00},
    ],
    "to_ship": [
        {"id": "zam_12300", "number": "12300", "date": "2026-07-11T18:20:00Z", "items_count": 2, "total": 160.00},
    ],
    "shipped": [
        {"id": "zam_12290", "number": "12290", "date": "2026-07-10T11:05:00Z", "items_count": 4, "total": 320.00},
    ],
    "completed": [
        {"id": "zam_12100", "number": "12100", "date": "2026-06-28T15:40:00Z", "items_count": 2, "total": 180.00},
    ],
    "returned": [
        {"id": "zam_12050", "number": "12050", "date": "2026-06-20T10:00:00Z", "items_count": 1, "total": 65.00},
    ],
}

ORDER_DETAILS = {
    "zam_12345": {
        "id": "zam_12345",
        "number": "12345",
        "status": "new",
        "date": "2026-07-12T13:55:00Z",
        "items": [
            {"product_id": "prod_1", "name": "kubek ceramiczny", "image_url": "https://example.com/images/prod_1.jpg", "quantity": 5, "unit_price": 20.00},
            {"product_id": "prod_2", "name": "talerz", "image_url": "https://example.com/images/prod_2.jpg", "quantity": 4, "unit_price": 15.00},
            {"product_id": "prod_3", "name": "doniczka", "image_url": "https://example.com/images/prod_3.jpg", "quantity": 1, "unit_price": 25.00},
        ],
        "total": 185.00,
    },
}
DEFAULT_ORDER_DETAIL = ORDER_DETAILS["zam_12345"]

# GET /api/orders/?status=&search=
# GET /api/orders/{order_id}/


@router.get("/", operation_id="list", summary="Lista zamowien")
def orders_list(
    status: str = Query("new", description="new|to_ship|shipped|completed|returned"),
    search: Optional[str] = Query(None, description="wyszukiwanie po numerze zamowienia"),
):
    if search:
        all_orders = [o for orders in ORDERS_BY_STATUS.values() for o in orders]
        matched = [o for o in all_orders if search in o["number"]]
        return {"counts": COUNTS, "status": None, "search": search, "orders": matched}
    return {"counts": COUNTS, "status": status, "orders": ORDERS_BY_STATUS.get(status, [])}


@router.get("/{order_id}/", operation_id="detail", summary="Szczegoly zamowienia")
def orders_detail(order_id: str):
    return ORDER_DETAILS.get(order_id, {**DEFAULT_ORDER_DETAIL, "id": order_id})
