from fastapi import APIRouter, Query

router = APIRouter()

KPIS = {"spend": 9000, "roas": 3.2, "acos": 0.28, "clicks": 4200, "conversions": 310}

CAMPAIGNS = [
    {"id": "camp_1", "name": "kampania - lato 2026", "roas": 4.1, "cost": 1200.00, "revenue": 4920.00},
    {"id": "camp_2", "name": "kampania - nowosci", "roas": 3.6, "cost": 900.00, "revenue": 3240.00},
    {"id": "camp_3", "name": "kampania - wyprzedaz", "roas": 1.1, "cost": 1500.00, "revenue": 1650.00},
    {"id": "camp_4", "name": "kampania - remarketing", "roas": 5.2, "cost": 600.00, "revenue": 3120.00},
]

RECOMMENDATIONS = [
    "kampania 'wyprzedaz' ma roas 1.1 - generuje strate po odliczeniu marzy, rozwaz wstrzymanie",
    "kampania 'remarketing' ma najwyzszy roas - rozwaz zwiekszenie budzetu",
]

# GET /api/ads/?sort=roas|cost|revenue


@router.get("/", operation_id="list", summary="Kampanie reklamowe")
def ads_list(sort: str = Query("roas", description="roas|cost|revenue")):
    campaigns = sorted(CAMPAIGNS, key=lambda c: c.get(sort, 0), reverse=True)
    return {"kpis": KPIS, "sort": sort, "campaigns": campaigns, "recommendations": RECOMMENDATIONS}
