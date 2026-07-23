from typing import List, Any
from pydantic import BaseModel
from fastapi import APIRouter

router = APIRouter()

ALERTS = [
    {
        "id": "alert_1",
        "type": "inventory",
        "severity": "high",
        "message": "Product 'Power Bank 10000mAh' - only 6 days of stock remaining",
        "created_at": "2026-07-12T08:00:00Z",
    },
    {
        "id": "alert_2",
        "type": "sale",
        "severity": "medium",
        "message": "Sales decreased by 12% compared to the previous week",
        "created_at": "2026-07-11T09:30:00Z",
    },
    {
        "id": "alert_3",
        "type": "returns",
        "severity": "medium",
        "message": "Increase in returns for product 'Phone Case'",
        "created_at": "2026-07-10T14:15:00Z",
    },
    {
        "id": "alert_4",
        "type": "margin",
        "severity": "low",
        "message": "Overall margin decreased by 2% over the last week",
        "created_at": "2026-07-09T17:45:00Z",
    },
]


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
    operation_id="alerts_list",
    summary="Alerts",
    response_model=AlertsResponse,
    responses={422: {"description": "Validation Error", "model": ValidationErrorResponse}},
)
def alerts_list():
    return {"alerts": ALERTS}