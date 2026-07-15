from typing import List, Optional, Any
from pydantic import BaseModel
from fastapi import APIRouter, Query
from enum import Enum
router = APIRouter()

ALERTS = [
    {"id": "alert_1", "type": "magazyn", "severity": "high", "message": "produkt 'powerbank 10000mah' - zapas na 6 dni", "created_at": "2026-07-12T08:00:00Z"},
    {"id": "alert_2", "type": "sprzedaz", "severity": "medium", "message": "spadek sprzedazy o 12% wzgledem poprzedniego tygodnia", "created_at": "2026-07-11T09:30:00Z"},
    {"id": "alert_3", "type": "zwroty", "severity": "medium", "message": "wzrost liczby zwrotow produktu 'etui na telefon'", "created_at": "2026-07-10T14:15:00Z"},
    {"id": "alert_4", "type": "marza", "severity": "low", "message": "marza calkowita spadla o 2% w ostatnim tygodniu", "created_at": "2026-07-09T17:45:00Z"},
]
class AlertType(str, Enum):
    inventory = "inventory"
    sale = "sale"
    returns = "returns"
    margin = "margin"

class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Alert(BaseModel):
    id: str
    type: str
    severity: str
    message: str
    created_at: str
 
class AlertsResponse(BaseModel):
    alerts: List[Alert]
 
class ValidationErrorItem(BaseModel):
    loc: List[Any]
    msg: str
    type: str
 
class ValidationErrorResponse(BaseModel):
    detail: List[ValidationErrorItem]
 
 
@router.get(
    "/",
    operation_id="list",
    summary="Alerty",
    response_model=AlertsResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def alerts_list(
    type: AlertType | None = Query(
        None,
        description="Alert type"
    ),
    severity: Severity | None = Query(
        None,
        description="Alert severity"
    ),
):
    alerts = ALERTS
    if type:
        alerts = [a for a in alerts if a["type"] == type]
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    return {"alerts": alerts}
 