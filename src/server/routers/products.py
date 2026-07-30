from typing import Any, List
from enum import Enum
from fastapi import APIRouter, Query
from pydantic import BaseModel

from ...db.read import DatabaseReader
router = APIRouter()

reader = DatabaseReader()

DESCRIPTIONS = {
    "main": "overall ranking - combines all 5 criteria with weights",
    "sales": "ranking by number of units sold",
    "revenue": "ranking by generated revenue",
    "margin": "ranking by margin / profit",
    "growth": "ranking by sales growth rate",
    "rating": "ranking by average customer rating",
}

MAIN_WEIGHTS = {
    "sales": 0.25,
    "revenue": 0.15,
    "margin": 0.3,
    "growth": 0.15,
    "rating": 0.15,
}

GROWTH_WINDOW_DAYS = 30
RATING_MIN_VOTES = 20


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


def _rank(items: list[dict], score_key: str) -> list[dict]:
    """Sortuje malejąco po score_key i nadaje pozycje 1..n."""
    ordered = sorted(items, key=lambda item: item[score_key], reverse=True)
    return [
        {
            "id": _to_product_id(item["product_id"]),
            "name": item["name"],
            "position": position,
            "score": round(item[score_key], 4),
        }
        for position, item in enumerate(ordered, start=1)
    ]


def _get_sales_ranking() -> list[dict]:
    stats = reader.get_product_sales_stats()
    return _rank(stats, "total_quantity")


def _get_revenue_ranking() -> list[dict]:
    stats = reader.get_product_sales_stats()
    return _rank(stats, "total_revenue")


def _get_margin_ranking() -> list[dict]:
    stats = reader.get_product_sales_stats()
    return _rank(stats, "total_margin")


def _get_growth_ranking() -> list[dict]:
    stats = reader.get_product_growth_stats(recent_days=GROWTH_WINDOW_DAYS)
    return _rank(stats, "growth_rate")


def _get_rating_ranking() -> list[dict]:
    stats = reader.get_product_rating_stats(min_votes=RATING_MIN_VOTES)
    return _rank(stats, "weighted_rating")


def _normalize(values: dict[int, float]) -> dict[int, float]:
    """Min-max normalizacja do zakresu 0-100."""
    if not values:
        return {}
    vmin, vmax = min(values.values()), max(values.values())
    if vmax == vmin:
        return {key: 100.0 for key in values}
    return {key: (value - vmin) / (vmax - vmin) * 100 for key, value in values.items()}


def _get_main_ranking() -> list[dict]:
    sales_stats = reader.get_product_sales_stats()
    growth_stats = reader.get_product_growth_stats(recent_days=GROWTH_WINDOW_DAYS)
    rating_stats = reader.get_product_rating_stats(min_votes=RATING_MIN_VOTES)

    sales_map = {row["product_id"]: row for row in sales_stats}
    growth_map = {row["product_id"]: row["growth_rate"] for row in growth_stats}
    rating_map = {row["product_id"]: row["weighted_rating"] for row in rating_stats}

    names: dict[int, str] = {}
    for row in sales_stats:
        names[row["product_id"]] = row["name"]
    for row in growth_stats:
        names.setdefault(row["product_id"], row["name"])
    for row in rating_stats:
        names.setdefault(row["product_id"], row["name"])

    all_ids = set(sales_map) | set(growth_map) | set(rating_map)
    if not all_ids:
        return []

    raw_sales = {pid: sales_map[pid]["total_quantity"] if pid in sales_map else 0 for pid in all_ids}
    raw_revenue = {pid: sales_map[pid]["total_revenue"] if pid in sales_map else 0 for pid in all_ids}
    raw_margin = {pid: sales_map[pid]["total_margin"] if pid in sales_map else 0 for pid in all_ids}
    raw_growth = {pid: growth_map.get(pid, 0.0) for pid in all_ids}
    raw_rating = {pid: rating_map.get(pid, 0.0) for pid in all_ids}

    norm_sales = _normalize(raw_sales)
    norm_revenue = _normalize(raw_revenue)
    norm_margin = _normalize(raw_margin)
    norm_growth = _normalize(raw_growth)
    norm_rating = _normalize(raw_rating)

    scored = []
    for pid in all_ids:
        total_score = (
            norm_sales.get(pid, 0) * MAIN_WEIGHTS["sales"]
            + norm_revenue.get(pid, 0) * MAIN_WEIGHTS["revenue"]
            + norm_margin.get(pid, 0) * MAIN_WEIGHTS["margin"]
            + norm_growth.get(pid, 0) * MAIN_WEIGHTS["growth"]
            + norm_rating.get(pid, 0) * MAIN_WEIGHTS["rating"]
        )
        scored.append({"product_id": pid, "name": names.get(pid, "Unknown"), "score": total_score})

    return _rank(scored, "score")


RANKING_BUILDERS = {
    RankingType.main: _get_main_ranking,
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
)
def products_list(
    type: RankingType = Query(RankingType.main),
    limit: int = Query(10, ge=1, le=100),
):
    products = RANKING_BUILDERS[type]()
    return {
        "type": type,
        "products": products[:limit],
    }


@router.get(
    "/summary/",
    operation_id="products_summary",
    summary="Product Rankings - Summary",
    response_model=ProductsSummary,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def products_summary(
    top: int = Query(5, ge=1, le=100, description="How many top products to return"),
):
    ranking = _get_main_ranking()

    total_products = len(ranking)
    total_score = round(sum(p["score"] for p in ranking), 2)
    top_products = ranking[:top]

    return {
        "total_products": total_products,
        "total_score": total_score,
        "top_products": top_products,
    }