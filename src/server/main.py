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
    title="Panel Analityczny - API (mock)",
    description=(
        "Zmockowane API dla panelu analitycznego sklepu e-commerce. "
        "Wszystkie endpointy zwracaja na sztywno zdefiniowane dane testowe."
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
# 1. Produkty
app.include_router(products.router, prefix="/api/products", tags=["products"])
# 2. Finanse
app.include_router(finance.router, prefix="/api/finance", tags=["finance"])
# 3. Magazyn
app.include_router(inventory.router, prefix="/api/inventory", tags=["inventory"])
# 4. Klienci
app.include_router(customers.router, prefix="/api/customers", tags=["customers"])
# 5. Zamowienia
app.include_router(orders.router, prefix="/api/orders", tags=["orders"])
# 6. Reklamy
app.include_router(ads.router, prefix="/api/ads", tags=["ads"])
# 7. Konkurencja
app.include_router(competition.router, prefix="/api/competition", tags=["competition"])
# 8. Zwroty i reklamacje
app.include_router(returns.router, prefix="/api/returns", tags=["returns"])
# 9. Prognozy
app.include_router(forecasts.router, prefix="/api/forecasts", tags=["forecasts"])
# 10. Alerty
app.include_router(alerts.router, prefix="/api/alerts", tags=["alerts"])


@app.get("/api/", operation_id="overview", tags=["index"], summary="Lista dostepnych zasobow")
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
