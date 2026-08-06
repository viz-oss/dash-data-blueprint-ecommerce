from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ...db.read import DatabaseReader
from .products import (
    OrderDirection,
    _get_sales_ranking,
    _get_revenue_ranking,
    _get_margin_ranking,
    _get_growth_ranking,
    _get_rating_ranking,
    _get_scoring_ranking,
    _to_product_id,
)

router = APIRouter()
reader = DatabaseReader()

class RankingPosition(BaseModel):
    position: int
    value: Optional[float] = None
    listing_date: Optional[str] = None


def _find_position(ranking: list[dict], product_str_id: str) -> RankingPosition:
    for item in ranking:
        if item["id"] == product_str_id:
            return RankingPosition(
                position=item["position"],
                value=item.get("score"),
                listing_date=item.get("listing_date"),
            )
    return RankingPosition(position=len(ranking) + 1, value=None, listing_date=None)


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
    listing_date: Optional[str] = None
    image_url: str
    overall_score: float
    rankings: Rankings
    sales_summary: SalesSummary
    reviews: Reviews
    return_rate: float
    recommendations: List[str]


def _parse_product_id(raw_id: str) -> int:
    if not raw_id.startswith("prod_"):
        raise HTTPException(status_code=404, detail=f"Product '{raw_id}' not found")
    try:
        return int(raw_id.removeprefix("prod_"))
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Product '{raw_id}' not found")


def _find_position(ranking: list[dict], product_str_id: str) -> RankingPosition:
    for item in ranking:
        if item["id"] == product_str_id:
            return RankingPosition(position=item["position"], value=item.get("score"))
    return RankingPosition(position=len(ranking) + 1, value=None)

HIGH_RETURN_RATE_THRESHOLD = 0.25
LOW_STOCK_TO_SALES_RATIO = 0.75 
HIGH_GROWTH_THRESHOLD = 2.0     
LOW_REVIEW_COUNT_THRESHOLD = 40  
LOW_RATING_THRESHOLD = 3.5     


def _build_recommendations(
    margin_pct: float,
    avg_margin_pct: float,
    return_rate: float,
    growth_value: Optional[float],
    stock: int,
    sold: int,
    review_avg: float,
    review_count: int,
) -> List[str]:
    recommendations: List[str] = []

    if margin_pct < 0:
        recommendations.append(
            "This product is being sold at a loss - the selling price is below cost. Review pricing immediately."
        )
    elif avg_margin_pct > 0 and margin_pct < avg_margin_pct:
        recommendations.append(
            "Margin is below the category average - consider increasing the price or negotiating a lower cost."
        )

    if return_rate >= HIGH_RETURN_RATE_THRESHOLD:
        recommendations.append(
            f"Return rate is high ({return_rate * 100:.1f}%) - review product quality or description accuracy."
        )

    if growth_value is not None and growth_value < 1.0:
        recommendations.append(
            "Sales are declining compared to the previous period - consider a promotion or price review."
        )
    elif growth_value is not None and growth_value >= HIGH_GROWTH_THRESHOLD:
        recommendations.append(
            "Sales are growing quickly compared to the previous period - consider increasing stock and ad budget to capture demand."
        )

    if sold == 0:
        recommendations.append(
            "No sales recorded in the selected period - check listing visibility, pricing, or ad exposure."
        )
    elif stock < sold * LOW_STOCK_TO_SALES_RATIO:
        recommendations.append(
            "Current stock is low relative to recent sales pace - consider restocking soon to avoid running out."
        )

    if review_count > 0 and review_avg < LOW_RATING_THRESHOLD:
        recommendations.append(
            f"Average rating is low ({review_avg:.1f}/5) - investigate product quality or listing accuracy."
        )
    elif sold >= LOW_REVIEW_COUNT_THRESHOLD * 2 and review_count < LOW_REVIEW_COUNT_THRESHOLD:
        recommendations.append(
            "Sales volume is solid but the product has very few reviews - encourage buyers to leave feedback."
        )

    if not recommendations:
        recommendations.append("No major issues detected for this product.")

    return recommendations


@router.get(
    "/",
    operation_id="products_detail",
    summary="Product Details",
    response_model=ProductDetail,
    responses={404: {"description": "Product not found"}},
)
def products_detail(id: str = Query(..., description="Product id, e.g. prod_123")):
    product_id = _parse_product_id(id)
    product = reader.get_product_by_id(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product '{id}' not found")

    str_id = _to_product_id(product_id)

    sales_ranking = _get_sales_ranking(None, None, OrderDirection.desc)
    revenue_ranking = _get_revenue_ranking(None, None, OrderDirection.desc)
    margin_ranking = _get_margin_ranking(None, None, OrderDirection.desc)
    growth_ranking = _get_growth_ranking(None, None, OrderDirection.desc)
    rating_ranking = _get_rating_ranking(None, None, OrderDirection.desc)
    scoring_ranking = _get_scoring_ranking(None, None, OrderDirection.desc)

    sales_stats = reader.get_product_sales_stats()
    own_sales = next((s for s in sales_stats if s["product_id"] == product_id), None)
    sold = own_sales["total_quantity"] if own_sales else 0
    revenue = own_sales["total_revenue"] if own_sales else 0.0
    margin = own_sales["total_margin"] if own_sales else 0.0
    margin_pct = (margin / revenue) if revenue else 0.0

    all_margin_pcts = [
        s["total_margin"] / s["total_revenue"] for s in sales_stats if s["total_revenue"]
    ]
    avg_margin_pct = sum(all_margin_pcts) / len(all_margin_pcts) if all_margin_pcts else 0.0

    stock = reader.get_product_stock(product_id)
    return_rate = reader.get_product_return_rate(product_id)

    overall_score_entry = next((p for p in scoring_ranking if p["id"] == str_id), None)
    overall_score = round(overall_score_entry["score"], 2) if overall_score_entry else 0.0

    growth_entry = next((p for p in growth_ranking if p["id"] == str_id), None)
    growth_value = growth_entry["score"] if growth_entry else None

    recommendations = _build_recommendations(
    margin_pct, avg_margin_pct, return_rate, growth_value,
    stock=stock, sold=sold, review_avg=product["review_avg"] or 0.0, review_count=product["review_count"] or 0)

    return {
        "id": str_id,
        "name": product["name"],
        "price": f"{float(product['rrp']):.2f}",
        "cost": f"{float(product['cost']):.2f}",
        "stock": stock,
        "listing_date": reader.get_product_listing_date(product_id),
        "image_url": f"https://example.com/images/{str_id}.jpg",
        "overall_score": overall_score,
        "rankings": {
            "sales": _find_position(sales_ranking, str_id),
            "revenue": _find_position(revenue_ranking, str_id),
            "margin": _find_position(margin_ranking, str_id),
            "growth": _find_position(growth_ranking, str_id),
            "rating": _find_position(rating_ranking, str_id),
        },
        "sales_summary": {
            "sold": sold,
            "revenue": f"{revenue:.2f}",
        },
        "reviews": {
            "average": product["review_avg"] or 0.0,
            "count": product["review_count"] or 0,
        },
        "return_rate": return_rate,
        "recommendations": recommendations,
    }