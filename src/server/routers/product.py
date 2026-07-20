from typing import Optional, List
from enum import Enum
from fastapi import APIRouter, Query
from pydantic import BaseModel
router = APIRouter()


class RankingPosition(BaseModel):
    position: int
    value: float


class Rankings(BaseModel):
    sales: RankingPosition
    revenue: RankingPosition
    margin: RankingPosition
    growth: RankingPosition
    rating: RankingPosition


class SalesSummary(BaseModel):
    total_sold: int
    total_revenue: str


class Reviews(BaseModel):
    average: float
    count: int


class ProductDetailResponse(BaseModel):
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
    response_model=ProductDetailResponse,
)
def products_detail(
    product_id: str = Query(
        ...,
        description="Product identifier, e.g. P-1001",
    )
):
    return PRODUCT_DETAILS.get(product_id, {**DEFAULT_PRODUCT_DETAIL, "id": product_id})