from fastapi import APIRouter, Query

router = APIRouter()

KPIS = {
    "total": 2100,
    "new_this_month": 85,
    "returning": 640,
    "avg_orders_per_customer": 1.8,
    "avg_rating": 4.5,
}

SEGMENTS = {
    "new": [
        {"id": "cust_10", "name": "klient a.k.", "total_spent": 145.00, "orders": 1, "frequency_days": None},
        {"id": "cust_11", "name": "klient m.w.", "total_spent": 89.00, "orders": 1, "frequency_days": None},
    ],
    "returning": [
        {"id": "cust_5", "name": "klient j.n.", "total_spent": 780.00, "orders": 4, "frequency_days": 22},
        {"id": "cust_6", "name": "klient p.s.", "total_spent": 560.00, "orders": 3, "frequency_days": 30},
    ],
    "top": [
        {"id": "cust_1", "name": "klient r.k.", "total_spent": 4200.00, "orders": 12, "frequency_days": 18},
        {"id": "cust_2", "name": "klient t.b.", "total_spent": 3100.00, "orders": 9, "frequency_days": 21},
    ],
}

CUSTOMER_DETAILS = {
    "cust_1": {
        "id": "cust_1",
        "first_purchase_date": "2025-01-12",
        "orders_count": 12,
        "total_spent": 4200.00,
        "orders": [
            {"date": "2026-06-20", "value": 350.00},
            {"date": "2026-05-15", "value": 420.00},
            {"date": "2026-04-02", "value": 290.00},
        ],
        "purchase_frequency_trend": [
            {"month": "2026-05", "orders": 1},
            {"month": "2026-06", "orders": 2},
        ],
        "status": "lojalny",
    },
}
DEFAULT_CUSTOMER_DETAIL = CUSTOMER_DETAILS["cust_1"]

# GET /api/customers/?segment=new|returning|top
# GET /api/customers/{customer_id}/


@router.get("/", operation_id="list", summary="Klienci wg segmentu")
def customers_list(segment: str = Query("top", description="new|returning|top")):
    return {"kpis": KPIS, "segment": segment, "customers": SEGMENTS.get(segment, SEGMENTS["top"])}


@router.get("/{customer_id}/", operation_id="detail", summary="Karta klienta")
def customers_detail(customer_id: str):
    return CUSTOMER_DETAILS.get(customer_id, {**DEFAULT_CUSTOMER_DETAIL, "id": customer_id})
