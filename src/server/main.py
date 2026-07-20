from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    dashboard,
    products,
    finance,
    inventory,
    customers,
    orders,
    ads,
    competition,
    returns,
    forecasts,
    alerts,
)

app = FastAPI(
    title="Analytics Dashboard - API (mock)",
    description=(
        "Mock API for an e-commerce store analytics dashboard. "
        "All endpoints return predefined test data."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 0. Dashboard
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
# 1. Products
app.include_router(products.router, prefix="/api/products", tags=["products"])
# 2. Finance
app.include_router(finance.router, prefix="/api/finance", tags=["finance"])
# 3. Inventory
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
# 4. Customers
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
# 5. Orders
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
# 6. Ads
app.include_router(ads.router, prefix="/api/ads", tags=["ads"])
# 7. Competition
app.include_router(competition.router, prefix="/api/competition", tags=["competition"])
# 8. Returns and complaints
app.include_router(returns.router, prefix="/api/returns", tags=["returns"])
# 9. Forecasts
app.include_router(forecasts.router, prefix="/api/forecasts", tags=["forecasts"])
# 10. Alerts
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])


@app.get("/api/", operation_id="overview", tags=["index"], summary="List of available resources")
def api_index():
    return {
        "dashboard": "/api/dashboard/",
        "products": "/api/products/",
        "finance": "/api/finance/summary/",
        "inventory": "/api/inventory/",
        "customers": "/api/customers/",
        "orders": "/api/orders/",
        "ads": "/api/ads/",
        "competition": "/api/competition/",
        "returns": "/api/returns/",
        "forecasts": "/api/forecasts/",
        "alerts": "/api/alerts/",
        "docs": "/docs",
    }