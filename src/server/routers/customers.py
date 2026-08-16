from datetime import datetime
from enum import Enum
from typing import List, Optional, Any
from fastapi import APIRouter, Query
from pydantic import BaseModel

from ...db.read import DatabaseReader

router = APIRouter()
reader = DatabaseReader()

TOP_SEGMENT_LIMIT = 10
NEW_SEGMENT_LIMIT = 10

WIN_BACK_INACTIVE_DAYS = 100        
BIG_INFREQUENT_MAX_ORDERS = 2        
BIG_INFREQUENT_VALUE_MULTIPLIER = 1.5 
VIP_MIN_ORDERS = 3              
VIP_MIN_TOTAL_SPENT = 40000         

class SegmentEnum(str, Enum):
    new = "new"
    top = "top"

class CustomerSummary(BaseModel):
    id: str
    name: str
    total_spent: str
    orders: int
    days_since_last_order: Optional[int] = None
    avg_order_value: str

class Kpis(BaseModel):
    total: int
    new_this_month: int
    avg_orders_per_customer: float

class CustomersListResponse(BaseModel):
    kpis: Kpis
    segment: SegmentEnum
    customers: List[CustomerSummary]
    recommendations: List[str]

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

def build_customer_metrics(c: dict) -> dict:
    all_order_dates = reader.get_customer_all_order_dates(c["customer_id"])
    return {
        "id": str(c["customer_id"]),
        "name": c["identifier"],
        "total_spent": f"{c['total_spent']:.2f}",
        "orders": c["orders_count"],
        "days_since_last_order": days_since_last_order(all_order_dates),
    }


def build_top_customers() -> list[dict]:
    """Lista do wyświetlenia na stronie - tylko top N wg total_spent."""
    top = reader.get_top_customers(limit=TOP_SEGMENT_LIMIT)
    return [build_customer_metrics(c) for c in top]


def build_recommendation_candidates() -> list[dict]:
    all_customers = reader.get_top_customers(limit=None)
    return [build_customer_metrics(c) for c in all_customers]


def build_new_customers() -> list[dict]:
    new = reader.get_new_customers(limit=NEW_SEGMENT_LIMIT)
    customers = []
    for c in new:
        all_order_dates = reader.get_customer_all_order_dates(c["customer_id"])
        customers.append(
            {
                "id": str(c["customer_id"]),
                "name": c["identifier"],
                "total_spent": f"{c['total_spent']:.2f}",
                "orders": c["orders_count"],
                "days_since_last_order": days_since_last_order(all_order_dates),
            }
        )
    return customers


def build_recommendations(segment: SegmentEnum, customers: list[dict]) -> list[str]:
    if not customers:
        return []

    if segment == SegmentEnum.new:
        return [
            f"Send a welcome email with a discount code to your {len(customers)} new customers "
            "from this month to encourage a second purchase."
        ]

    recommendations = []

    inactive = [
        c for c in customers
        if c["days_since_last_order"] is not None and c["days_since_last_order"] > WIN_BACK_INACTIVE_DAYS
    ]
    inactive.sort(key=lambda c: c["days_since_last_order"], reverse=True)
    if inactive:
        ids = ", ".join(c["id"] for c in inactive)
        recommendations.append(
            f"Customer {ids} has not ordered in a while - "
            "send them an encouraging email with a discount code to bring them back."
        )
    vip = [
        c for c in customers
        if c["orders"] >= VIP_MIN_ORDERS and float(c["total_spent"]) >= VIP_MIN_TOTAL_SPENT
    ]
    vip.sort(key=lambda c: float(c["total_spent"]), reverse=True)
    if vip:
        ids = ", ".join(c["id"] for c in vip)
        recommendations.append(
            f"Customer {ids} orders often and spends a lot - "
            "consider giving them VIP status with perks like free shipping or early access to new products."
        )

    top_spender = customers[0]
    recommendations.append(
        f"Customer {top_spender['id']} is your highest-spending customer - "
        "consider a personal thank-you note or early access to new products."
    )

    avg_values = [float(c["total_spent"]) / c["orders"] for c in customers if c["orders"]]
    overall_avg_order_value = sum(avg_values) / len(avg_values) if avg_values else 0.0
    big_infrequent = []
    for c in customers:
        if c["orders"] and c["orders"] <= BIG_INFREQUENT_MAX_ORDERS:
            avg_order_value = float(c["total_spent"]) / c["orders"]
            if avg_order_value > overall_avg_order_value * BIG_INFREQUENT_VALUE_MULTIPLIER:
                big_infrequent.append(c)
    big_infrequent.sort(key=lambda c: float(c["total_spent"]) / c["orders"], reverse=True)
    if big_infrequent:
        ids = ", ".join(c["id"] for c in big_infrequent)
        recommendations.append(
            f"Customer {ids} places large but infrequent orders - "
            "consider offering bundle deals or personalized recommendations to increase order frequency."
        )

    return recommendations


@router.get(
    "/",
    operation_id="customers_list",
    summary="Customer Statistics",
    response_model=CustomersListResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def customers_list(segment: SegmentEnum = Query(SegmentEnum.top)):
    kpis = reader.get_customer_kpis()

    customers = build_top_customers() if segment == SegmentEnum.top else build_new_customers()
    recommendation_pool = build_recommendation_candidates() if segment == SegmentEnum.top else customers

    enriched = [
        {
            "id": c["id"],
            "name": c["name"],
            "total_spent": c["total_spent"],
            "orders": c["orders"],
            "days_since_last_order": c["days_since_last_order"],
            "avg_order_value": (
                f"{float(c['total_spent']) / c['orders']:.2f}" if c["orders"] else "0.00"
            ),
        }
        for c in customers
    ]
    if segment == SegmentEnum.top:
        enriched.sort(key=lambda c: float(c["total_spent"]), reverse=True)

    return {
        "kpis": kpis,
        "segment": segment,
        "customers": enriched,
        "recommendations": build_recommendations(segment, recommendation_pool),
    }