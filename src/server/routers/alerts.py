from typing import Optional

from fastapi import APIRouter, Query

router = APIRouter()

ALERTS = [
    {"id": "alert_1", "type": "magazyn", "severity": "high", "message": "produkt 'powerbank 10000mah' - zapas na 6 dni", "created_at": "2026-07-12T08:00:00Z"},
    {"id": "alert_2", "type": "sprzedaz", "severity": "medium", "message": "spadek sprzedazy o 12% wzgledem poprzedniego tygodnia", "created_at": "2026-07-11T09:30:00Z"},
    {"id": "alert_3", "type": "zwroty", "severity": "medium", "message": "wzrost liczby zwrotow produktu 'etui na telefon'", "created_at": "2026-07-10T14:15:00Z"},
    {"id": "alert_4", "type": "marza", "severity": "low", "message": "marza calkowita spadla o 2% w ostatnim tygodniu", "created_at": "2026-07-09T17:45:00Z"},
]


@router.get("/", operation_id="list", summary="Alerty")
def alerts_list(
    type: Optional[str] = Query(None, description="magazyn|sprzedaz|zwroty|marza"),
    severity: Optional[str] = Query(None, description="low|medium|high"),
):
    alerts = ALERTS
    if type:
        alerts = [a for a in alerts if a["type"] == type]
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    return {"alerts": alerts}
