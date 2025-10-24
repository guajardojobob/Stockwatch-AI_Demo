from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from .models import RecommendReq, RecommendResponse
from .services.utils import forecast_item, optimize_par, simple_explain

app = FastAPI(title="StockWatch-GPT", version="0.1.0")

BASE = Path(__file__).resolve().parent.parent
DATA = BASE / "data"
DATA.mkdir(exist_ok=True, parents=True)

def _load_csvs(site_id: str):
    items = pd.read_csv(DATA / "items.csv")
    site_items = pd.read_csv(DATA / "site_items.csv")
    usage = pd.read_csv(DATA / "usage.csv")
    usage["day"] = pd.to_datetime(usage["day"])
    return items, site_items[site_items.site_id==site_id], usage[usage.site_id==site_id]

@app.post("/ingest")
async def ingest(items: UploadFile = File(None), site_items: UploadFile = File(None), usage: UploadFile = File(None)):
    saved = []
    for f, name in [(items, "items.csv"), (site_items, "site_items.csv"), (usage, "usage.csv")]:
        if f is not None:
            dest = DATA / name
            content = await f.read()
            dest.write_bytes(content)
            saved.append(name)
    return {"saved": saved}

@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendReq):
    items_df, site_items_df, usage_df = _load_csvs(req.site_id)
    out: List[Dict[str, Any]] = []
    for _, row in site_items_df.iterrows():
        hist = usage_df[usage_df.item_id == row["item_id"]].sort_values("day")
        if hist.empty:
            continue
        fc = forecast_item(hist, int(row.get("lead_time_days", 7)))
        rec = optimize_par(row.to_dict(), fc, req.service_level, req.review_period_days)
        unit_cost = float(items_df[items_df.item_id==row["item_id"]].unit_cost.values[0])
        rec["rationale"] = simple_explain(rec, unit_cost=unit_cost)
        out.append(rec)
    resp = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "site_id": req.site_id,
        "items": out
    }
    return resp

@app.get("/healthz")
def healthz():
    return {"status":"ok"}

# Serve static frontend (built React or minimal page)
static_dir = BASE / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
