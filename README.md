# StockWatch-GPT (Full stack)

FastAPI backend + React (Vite) frontend. Forecasts intermittent demand, computes safety stock & ROP, proposes PAR & reorder qty, and provides rationale. Includes synthetic CSVs. No PHI/PII.

## Option A — Quick demo (fallback HTML only)
```bash
docker compose up --build
# open http://localhost:8000
```

## Option B — Build the React UI (recommended)
```bash
cd frontend
npm install
npm run build        # emits static bundle into ../backend/static
cd ..
docker compose up --build
# open http://localhost:8000 (now serves the React app)
```

## API
POST /recommend
```json
{
  "site_id": "SLC-660",
  "service_level": 0.98,
  "review_period_days": 7
}
```

## Ingest data
```bash
curl -F "items=@backend/app/data/items.csv"      -F "site_items=@backend/app/data/site_items.csv"      -F "usage=@backend/app/data/usage.csv"      http://localhost:8000/ingest
```

## Guajardo from Explorer Project Folder Create Date 2025-10-21  a
