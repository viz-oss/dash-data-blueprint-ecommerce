# Analytics Dashboard — API (mock)

FastAPI backend returning mocked JSON data for all analytics dashboard
modules. No authentication — an example/development project.

## Requirements

- Python 3.14 (or any newer 3.11+ version — the code does not use any features
  specific only to 3.14)

## Run

```bash
# 1. unpack the archive and enter the directory
cd dash-data-blueprint-ecommerce

# 2. create a virtual environment
python3.14 -m venv venv

# 3. activate the environment
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 4. install dependencies
pip install -r requirements.txt

# 5. start the server
cd src/server
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

- `GET /api/` — list of all available resources
- `GET /docs` — interactive Swagger documentation (optional, for browser testing)

| # | Module | Page | Endpoint | Parameters |
|---|---|---|---|---|
| 0 | Dashboard | `/` | `GET /api/dashboard/` | - |
| 1 | Products | `/products` | `GET /api/products/` | ranking, limit, search |
| 1 | Products | `/products/:id` | `GET /api/products/{id}/` | - |
| 2 | Finance | `/finance` | `GET /api/finance/summary/` | date range |
| 2 | Finance | `/finance/revenue` | `GET /api/finance/revenue/` | granularity, date range |
| 2 | Finance | `/finance/costs` | `GET /api/finance/costs/` | granularity, date range |
| 2 | Finance | `/finance/profitability` | `GET /api/finance/profitability/` | date range |
| 3 | Inventory | `/inventory` | `GET /api/inventory/` | view (stock/alert), filter |
| 4 | Customers | `/customers` | `GET /api/customers/` | segment |
| 4 | Customers | `/customers/:id` | `GET /api/customers/{id}/` | - |
| 5 | Orders | `/orders` | `GET /api/orders/` | status, search |
| 5 | Orders | `/orders/:id` | `GET /api/orders/{id}/` | - |
| 6 | Ads | `/ads` | `GET /api/ads/` | sort |
| 7 | Competition | `/competition` | `GET /api/competition/` | view (prices/ranking) |
| 8 | Returns | `/returns` | `GET /api/returns/` | view (returns/claims) |
| 9 | Forecasts | `/forecasts` | `GET /api/forecasts/` | - |
| 10 | Alerts | `/alerts` | `GET /api/alerts/` | type, severity |
