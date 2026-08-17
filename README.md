# Analytics Dashboard — API (mock)

FastAPI backend returning mocked JSON data for all analytics dashboard
modules. No authentication — an example/development project.

## Requirements

- Python 3.14 (or any newer 3.11+ version — the code does not use any features
  specific only to 3.14)

## Install

```bash
# Create database
python src/db/create.py

# Generate database
python src/db/generate.py

# Check database
python src/db/read.py

# Delete database (optional)
python src/db/delete.py
```

## Run

```bash
# 1. unpack the archive and enter the directory
cd dash-data-blueprint-ecommerce

# 2. create a virtual environment
python -m venv venv

# 3. activate the environment
source venv/bin/activate        # Linux / macOS
source venv\Scripts\activate    # Windows

# 4. install dependencies
pip install -r requirements.txt

# 5. start the server
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

# API standards guide

Common params for lists:
type (string) - type of statement
limit (integer) - how many records to download
from (YYYY-MM-DDZ string) - date range from
to (YYYY-MM-DDZ string) - date range to
order_by (string) - sorting 'asc' | 'desc'

Commen paramt for getter:
NAME_id (string) - unique identifier from database (replace name with a name like product_, customer_, etc.)