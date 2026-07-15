# Panel Analityczny — API (mock)

Backend FastAPI zwracający zmockowane dane JSON dla wszystkich modułów panelu
analitycznego. Bez autoryzacji — projekt przykładowy/deweloperski.

## Wymagania

- Python 3.14 (lub nowszy 3.11+ — kod nie używa żadnych funkcji specyficznych
  wyłącznie dla 3.14)

## Uruchomienie

```bash
# 1. rozpakuj archiwum i wejdź do katalogu
cd dash-data-blueprint-ecommerce

# 2. utwórz środowisko wirtualne
python3.14 -m venv venv

# 3. aktywuj środowisko
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 4. zainstaluj zależności
pip install -r requirements.txt

# 5. odpal serwer
cd src/server
uvicorn main:app --reload
```

Serwer wystartuje pod `http://127.0.0.1:8000`.

- `GET /api/` — lista wszystkich dostępnych zasobów
- `GET /docs` — interaktywna dokumentacja Swagger (opcjonalnie, do testowania w przeglądarce)

| # | Modul | Strona | Endpoint | Parametry |
|---|---|---|---|---|
| 0 | Dashboard | `/` | `GET /api/dashboard/` | - |
| 1 | Produkty | `/produkty` | `GET /api/products/` | ranking, limit, search |
| 1 | Produkty | `/produkty/:id` | `GET /api/products/{id}/` | - |
| 2 | Finanse | `/finanse` | `GET /api/finance/summary/` | zakres dat |
| 2 | Finanse | `/finanse/przychody` | `GET /api/finance/revenue/` | granulacja, zakres dat |
| 2 | Finanse | `/finanse/koszty` | `GET /api/finance/costs/` | granulacja, zakres dat |
| 2 | Finanse | `/finanse/rentownosc` | `GET /api/finance/profitability/` | zakres dat |
| 3 | Magazyn | `/magazyn` | `GET /api/inventory/` | view (stan/uwaga), filter |
| 4 | Klienci | `/klienci` | `GET /api/customers/` | segment |
| 4 | Klienci | `/klienci/:id` | `GET /api/customers/{id}/` | - |
| 5 | Zamowienia | `/zamowienia` | `GET /api/orders/` | status, search |
| 5 | Zamowienia | `/zamowienia/:id` | `GET /api/orders/{id}/` | - |
| 6 | Reklamy | `/reklamy` | `GET /api/ads/` | sort |
| 7 | Konkurencja | `/konkurencja` | `GET /api/competition/` | view (ceny/ranking) |
| 8 | Zwroty | `/zwroty` | `GET /api/returns/` | view (zwroty/reklamacje) |
| 9 | Prognozy | `/prognozy` | `GET /api/forecasts/` | - |
| 10 | Alerty | `/alerty` | `GET /api/alerts/` | type, severity |
