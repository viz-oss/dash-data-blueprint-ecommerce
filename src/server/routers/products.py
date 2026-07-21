from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

DESCRIPTIONS = {
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


class RankingType(str, Enum):
    main = "main"
    sales = "sales"
    revenue = "revenue"
    margin = "margin"
    growth = "growth"
    rating = "rating"


class Product(BaseModel):
    id: str
    name: str
    position: int
    score: float


class ProductsResponse(BaseModel):
    type: RankingType
    products: List[Product]


def _build_endpoint_description() -> str:
    lines = ["Available types (`type`):", ""]
    lines += [f"- **{key}** - {desc}" for key, desc in DESCRIPTIONS.items()]
    return "\n".join(lines)


@router.get(
    "/",
    operation_id="products_list",
    summary="Product Rankings",
    description=_build_endpoint_description(),
    response_model=ProductsResponse,
)
def products_list(
    type: RankingType = Query(RankingType.main),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
):
    products = RANKINGS.get(type, RANKINGS["main"])
    if search:
        products = [p for p in products if search.lower() in p["name"].lower()]
    return {
        "type": type,
        "products": products[:limit],
    }