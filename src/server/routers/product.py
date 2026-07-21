from typing import List
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter()

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
            "sold": 480,
            "revenue": "62000",
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


class RankingPosition(BaseModel):
    position: int
    value: float


class SalesSummary(BaseModel):
    sold: int
    revenue: str


class Reviews(BaseModel):
    average: float
    count: int


class Rankings(BaseModel):
    sales: RankingPosition
    revenue: RankingPosition
    margin: RankingPosition
    growth: RankingPosition
    rating: RankingPosition


class ProductDetail(BaseModel):
    id: str
    name: str
    price: str
    cost: str
    stock: int
    image_url: str
    overall_score: float
    rankings: Rankings
    sales_summary: SalesSummary
    reviews: Reviews
    return_rate: float
    recommendations: List[str]


@router.get(
    "/",
    operation_id="products_detail",
    summary="Product Details",
    response_model=ProductDetail,
)
def products_detail(id: str = Query(...)):
    return PRODUCT_DETAILS.get(id, {**DEFAULT_PRODUCT_DETAIL, "id": id})