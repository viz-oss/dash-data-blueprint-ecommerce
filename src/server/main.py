from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    dashboard,
    products,
    product,
    finance,
    inventory,
    customers,
    customer,
    orders,
    order,
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
app.include_router(product.router, prefix="/api/product", tags=["product"])
# 2. Finance
app.include_router(finance.router, prefix="/api/finance", tags=["finance"])
# 3. Inventory
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
# 4. Customers
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
app.include_router(customer.router, prefix="/api/customer", tags=["customer"])
# 5. Orders
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
app.include_router(order.router, prefix="/api/order", tags=["order"])
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
        "product": "/api/product/",
        "finance": "/api/finance/summary/",
        "inventory": "/api/inventory/",
        "customers": "/api/customers/",
        "customer": "/api/customer/",
        "orders": "/api/orders/",
        "order": "/api/order/",
        "ads": "/api/ads/",
        "competition": "/api/competition/",
        "returns": "/api/returns/",
        "forecasts": "/api/forecasts/",
        "alerts": "/api/alerts/",
        "docs": "/docs",
    }