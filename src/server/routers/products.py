from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Query
from pydantic import BaseModel
router = APIRouter()

RANKING_DESCRIPTIONS = {
    "main": "overall ranking - combines all 5 criteria with weights",
    "sales": "ranking by number of units sold",
    "revenue": "ranking by generated revenue",
    "margin": "ranking by margin / profit",
    "growth": "ranking by sales growth rate",
    "rating": "ranking by average customer rating",
}

RANKINGS = {
    "main": [
        {"id": "prod_123", "name": "Headphones X200", "position": 1, "score": 92},
        {"id": "prod_456", "name": "USB-C Cable 2m", "position": 2, "score": 87},
        {"id": "prod_789", "name": "Phone Case", "position": 3, "score": 82},
        {"id": "prod_321", "name": "10000mAh Power Bank", "position": 4, "score": 78},
        {"id": "prod_654", "name": "Wireless Charger", "position": 5, "score": 74},
    ],
    "sales": [
        {"id": "prod_456", "name": "USB-C Cable 2m", "position": 1, "score": 980},
        {"id": "prod_123", "name": "Headphones X200", "position": 2, "score": 480},
        {"id": "prod_321", "name": "10000mAh Power Bank", "position": 3, "score": 310},
    ],
    "revenue": [
        {"id": "prod_123", "name": "Headphones X200", "position": 1, "score": 62000},
        {"id": "prod_654", "name": "Wireless Charger", "position": 2, "score": 41000},
        {"id": "prod_789", "name": "Phone Case", "position": 3, "score": 22000},
    ],
    "margin": [
        {"id": "prod_789", "name": "Phone Case", "position": 1, "score": 0.52},
        {"id": "prod_654", "name": "Wireless Charger", "position": 2, "score": 0.41},
        {"id": "prod_123", "name": "Headphones X200", "position": 3, "score": 0.34},
    ],
    "growth": [
        {"id": "prod_321", "name": "10000mAh Power Bank", "position": 1, "score": 0.35},
        {"id": "prod_123", "name": "Headphones X200", "position": 2, "score": 0.18},
        {"id": "prod_456", "name": "USB-C Cable 2m", "position": 3, "score": 0.09},
    ],
    "rating": [
        {"id": "prod_654", "name": "Wireless Charger", "position": 1, "score": 4.9},
        {"id": "prod_123", "name": "Headphones X200", "position": 2, "score": 4.6},
        {"id": "prod_789", "name": "Phone Case", "position": 3, "score": 4.4},
    ],
}

PRODUCT_DETAILS = {
    "prod_123": {
        "id": "prod_123",
        "name": "Headphones X200",
        "price": "129.99",
        "cost": "65.00",
        "stock": 143,
        "image_url": "https://example.com/images/prod_123.jpg",
        "overall_score": 92,
        "rankings": {
            "sales": {"position": 2, "value": 480},
            "revenue": {"position": 1, "value": 62000},
            "margin": {"position": 3, "value": "0.34"},
            "growth": {"position": 2, "value": "0.18"},
            "rating": {"position": 2, "value": "4.6"},
        },
        "sales_summary": {
            "total_sold": 480,
            "total_revenue": "62000",
        },
        "history": [
            {"date": "2026-06-01", "sales": 12, "revenue": 1500, "margin": 480},
            {"date": "2026-06-08", "sales": 15, "revenue": 1870, "margin": 590},
            {"date": "2026-06-15", "sales": 9, "revenue": 1120, "margin": 360},
            {"date": "2026-06-22", "sales": 18, "revenue": 2240, "margin": 710},
        ],
        "reviews": {"average": "4.6", "count": 210},
        "return_rate": "0.04",
        "recommendations": [
            "Margin is below the category average - consider increasing the price by about 5%.",
        ],
    },
}

DEFAULT_PRODUCT_DETAIL = PRODUCT_DETAILS["prod_123"]

# Response
class RankingType(str, Enum):
    main = "main"
    sales = "sales"
    revenue = "revenue"
    margin = "margin"
    growth = "growth"
    rating = "rating"


class RankingItem(BaseModel):
    id: str
    name: str
    position: int
    score: float


class ProductsListResponse(BaseModel):
    ranking_type: str
    ranking_description: str
    products: List[RankingItem]


@router.get(
    "/",
    operation_id="products_list",
    summary="Product Rankings",
    response_model=ProductsListResponse,
)
def products_list(
    ranking: RankingType = Query(
        RankingType.main,
        description="Product ranking type",
    ),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
):
    products = RANKINGS.get(ranking, RANKINGS["main"])
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]
    return {
        "ranking_type": ranking,
        "ranking_description": RANKING_DESCRIPTIONS.get(ranking, ""),
        "products": products[:limit],
    }

