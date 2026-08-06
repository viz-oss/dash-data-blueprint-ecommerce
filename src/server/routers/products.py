from typing import Any, List, Optional
from enum import Enum
from datetime import date
from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from ...db.read import DatabaseReader
router = APIRouter()

reader = DatabaseReader()

DESCRIPTIONS = {
    "scoring": "overall ranking - combines all 5 criteria with weights",
    "sales": "ranking by number of units sold",
    "revenue": "ranking by generated revenue",
    "margin": "ranking by margin / profit",
    "growth": "ranking by sales growth rate (products with no comparison period are listed separately, sorted by recent units sold)",
    "rating": "ranking by average customer rating",
}

SCORING_WEIGHTS = {
    "sales": 0.25,
    "revenue": 0.15,
    "margin": 0.3,
    "growth": 0.15,
    "rating": 0.15,
}

GROWTH_WINDOW_DAYS = 30
RATING_MIN_VOTES = 20
NEUTRAL_GROWTH_RATE = 1.0

DATE_FROM_DESCRIPTION = (
    "Start date of the range (YYYY-MM-DD)."
)

DATE_TO_DESCRIPTION = (
    "End date of the range (YYYY-MM-DD)."
)


class RankingType(str, Enum):
    scoring = "scoring"
    sales = "sales"
    revenue = "revenue"
    margin = "margin"
    growth = "growth"
    rating = "rating"


class OrderDirection(str, Enum):
    asc = "asc"
    desc = "desc"


class Product(BaseModel):
    id: str
    name: str
    position: int
    score: Optional[float] = None
    note: Optional[str] = None
    listing_date: Optional[str] = None


class ProductsResponse(BaseModel):
    type: RankingType
    products: List[Product]


class ProductsSummary(BaseModel):
    total_products: int
    total_score: float
    top_products: List[Product] = []


class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str


class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]


def _build_endpoint_description() -> str:
    lines = ["Available types (`type`):", ""]
    lines += [f"- **{key}** - {desc}" for key, desc in DESCRIPTIONS.items()]
    return "\n".join(lines)


def _to_product_id(product_id: int) -> str:
    return f"prod_{product_id}"


def _validate_date_range(date_from: date | None, date_to: date | None) -> None:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=422, detail="from must be <= to")


def _rank(items: list[dict], score_key: str, order_by: OrderDirection) -> list[dict]:
    """Sorts by score_key (descending for 'desc', ascending for 'asc'), assigns
    positions 1..n, and attaches each product's listing_date (from Offer) -
    None if the product currently has no offer with stock > 0."""
    reverse = order_by == OrderDirection.desc
    ordered = sorted(items, key=lambda item: item[score_key], reverse=reverse)
    return [
        {
            "id": _to_product_id(item["product_id"]),
            "name": item["name"],
            "position": position,
            "score": round(item[score_key], 4),
            "note": None,
            "listing_date": reader.get_product_listing_date(item["product_id"]),
        }
        for position, item in enumerate(ordered, start=1)
    ]


def _get_sales_ranking(
    date_from: str | None, date_to: str | None, order_by: OrderDirection
) -> list[dict]:
    stats = reader.get_product_sales_stats(from_=date_from, to=date_to)
    return _rank(stats, "total_quantity", order_by)


def _get_revenue_ranking(
    date_from: str | None, date_to: str | None, order_by: OrderDirection
) -> list[dict]:
    stats = reader.get_product_sales_stats(from_=date_from, to=date_to)
    return _rank(stats, "total_revenue", order_by)


def _get_margin_ranking(
    date_from: str | None, date_to: str | None, order_by: OrderDirection
) -> list[dict]:
    stats = reader.get_product_sales_stats(from_=date_from, to=date_to)
    return _rank(stats, "total_margin", order_by)


def _get_growth_ranking(
    date_from: str | None, date_to: str | None, order_by: OrderDirection
) -> list[dict]:
    stats = reader.get_product_growth_stats(
        recent_days=GROWTH_WINDOW_DAYS, from_=date_from, to=date_to
    )

    with_comparison = [item for item in stats if item["growth_rate"] is not None]
    ranked = _rank(with_comparison, "growth_rate", order_by)

    new_products = [
        item for item in stats
        if item["growth_rate"] is None and item["recent_quantity"] > 0
    ]
    new_products.sort(key=lambda item: item["recent_quantity"], reverse=True)

    next_position = len(ranked) + 1
    for item in new_products:
        ranked.append(
            {
                "id": _to_product_id(item["product_id"]),
                "name": item["name"],
                "position": next_position,
                "score": None,
                "note": (
                    "No sales in the previous period to compare against - "
                    f"ranked by recent units sold instead ({item['recent_quantity']} units sold)."
                ),
                "listing_date": reader.get_product_listing_date(item["product_id"]),
            }
        )
        next_position += 1

    return ranked


def _get_rating_ranking(
    date_from: str | None, date_to: str | None, order_by: OrderDirection
) -> list[dict]:
    stats = reader.get_product_rating_stats(min_votes=RATING_MIN_VOTES)
    return _rank(stats, "weighted_rating", order_by)


def _normalize(values: dict[int, float]) -> dict[int, float]:
    """Min-max normalization to a 0-100 range."""
    if not values:
        return {}
    vmin, vmax = min(values.values()), max(values.values())
    if vmax == vmin:
        return {key: 100.0 for key in values}
    return {key: (value - vmin) / (vmax - vmin) * 100 for key, value in values.items()}


def _get_scoring_ranking(
    date_from: str | None, date_to: str | None, order_by: OrderDirection
) -> list[dict]:
    sales_stats = reader.get_product_sales_stats(from_=date_from, to=date_to)
    growth_stats = reader.get_product_growth_stats(
        recent_days=GROWTH_WINDOW_DAYS, from_=date_from, to=date_to
    )
    rating_stats = reader.get_product_rating_stats(min_votes=RATING_MIN_VOTES)

    sales_map = {row["product_id"]: row for row in sales_stats}

    growth_map = {
        row["product_id"]: row["growth_rate"]
        for row in growth_stats
        if row["growth_rate"] is not None
    }
    rating_map = {row["product_id"]: row["weighted_rating"] for row in rating_stats}

    names: dict[int, str] = {row["product_id"]: row["name"] for row in sales_stats}
    all_ids = set(sales_map)
    if not all_ids:
        return []

    raw_sales = {pid: sales_map[pid]["total_quantity"] for pid in all_ids}
    raw_revenue = {pid: sales_map[pid]["total_revenue"] for pid in all_ids}
    raw_margin = {pid: sales_map[pid]["total_margin"] for pid in all_ids}
    raw_growth = {pid: growth_map.get(pid, NEUTRAL_GROWTH_RATE) for pid in all_ids}
    raw_rating = {pid: rating_map.get(pid, 0.0) for pid in all_ids}

    norm_sales = _normalize(raw_sales)
    norm_revenue = _normalize(raw_revenue)
    norm_margin = _normalize(raw_margin)
    norm_growth = _normalize(raw_growth)
    norm_rating = _normalize(raw_rating)

    scored = []
    for pid in all_ids:
        total_score = (
            norm_sales.get(pid, 0) * SCORING_WEIGHTS["sales"]
            + norm_revenue.get(pid, 0) * SCORING_WEIGHTS["revenue"]
            + norm_margin.get(pid, 0) * SCORING_WEIGHTS["margin"]
            + norm_growth.get(pid, 0) * SCORING_WEIGHTS["growth"]
            + norm_rating.get(pid, 0) * SCORING_WEIGHTS["rating"]
        )
        scored.append({"product_id": pid, "name": names.get(pid, "Unknown"), "score": total_score})

    return _rank(scored, "score", order_by)


RANKING_BUILDERS = {
    RankingType.scoring: _get_scoring_ranking,
    RankingType.sales: _get_sales_ranking,
    RankingType.revenue: _get_revenue_ranking,
    RankingType.margin: _get_margin_ranking,
    RankingType.growth: _get_growth_ranking,
    RankingType.rating: _get_rating_ranking,
}


@router.get(
    "/list/",
    operation_id="products_list",
    summary="Product Rankings - List",
    description=_build_endpoint_description(),
    response_model=ProductsResponse,
    response_model_exclude_none=True,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def products_list(
    type: RankingType = Query(RankingType.scoring),
    limit: int = Query(10, ge=1, le=100),
    from_: date | None = Query(None, alias="from", description=DATE_FROM_DESCRIPTION),
    to: date | None = Query(None, description=DATE_TO_DESCRIPTION),
    order_by: OrderDirection = Query(OrderDirection.desc),
):
    _validate_date_range(from_, to)

    if type == RankingType.rating and (from_ or to):
        raise HTTPException(
            status_code=422,
            detail="`rating` ranking does not support date filtering (reviews have no stored date); omit `from`/`to` for this type.",
        )

    products = RANKING_BUILDERS[type](
        from_.isoformat() if from_ else None,
        to.isoformat() if to else None,
        order_by,
    )
    return {
        "type": type,
        "products": products[:limit],
    }


@router.get(
    "/summary/",
    operation_id="products_summary",
    summary="Product Rankings - Summary",
    response_model=ProductsSummary,
    response_model_exclude_none=True,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def products_summary(
    top: int = Query(5, ge=1, le=100, description="How many top products to return"),
    from_: date | None = Query(None, alias="from", description=DATE_FROM_DESCRIPTION),
    to: date | None = Query(None, description=DATE_TO_DESCRIPTION),
    order_by: OrderDirection = Query(OrderDirection.desc),
):
    _validate_date_range(from_, to)

    ranking = _get_scoring_ranking(
        from_.isoformat() if from_ else None,
        to.isoformat() if to else None,
        order_by,
    )

    total_products = len(ranking)
    total_score = round(sum(p["score"] for p in ranking), 2)
    top_products = ranking[:top]

    return {
        "total_products": total_products,
        "total_score": total_score,
        "top_products": top_products,
    }