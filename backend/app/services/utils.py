import numpy as np
import pandas as pd
from typing import Dict, Any

Z = {0.90:1.2816, 0.95:1.6449, 0.98:2.0537, 0.99:2.3263}

def croston(y):
    y = np.array(y, dtype=float)
    nz = np.where(y>0)[0]
    if len(nz)==0:
        return {"avg_daily":0.0,"sigma_daily":0.0}
    demand = y[nz]
    gaps = np.diff(np.concatenate(([nz[0]], nz)))
    q_hat = demand.mean()
    p_hat = gaps.mean() if gaps.size else max(1, int(len(y)/len(demand)))
    avg_daily = q_hat / max(p_hat,1e-6)
    sigma_daily = demand.std(ddof=1) / max(p_hat,1)
    return {"avg_daily":float(avg_daily), "sigma_daily":float(sigma_daily)}

def forecast_item(hist_df: pd.DataFrame, lead_time_days: int) -> Dict[str, Any]:
    s = hist_df.set_index("day")["qty"].asfreq("D", fill_value=0)
    base = croston(s.values)
    by_wd = s.groupby(s.index.weekday).mean()
    mean = s.mean() if s.mean() else 1.0
    wd_mult = (by_wd/mean).reindex(range(7)).fillna(1.0).mean()
    avg_daily = base["avg_daily"] * float(wd_mult)
    sigma_daily = max(1e-6, base["sigma_daily"])
    mu = avg_daily * lead_time_days
    sigma = sigma_daily * (lead_time_days ** 0.5)
    return {"avg_daily": float(avg_daily), "mu_lead": float(mu), "sigma_lead": float(sigma), "lead_time_days": int(lead_time_days)}

def optimize_par(item_row: dict, fc: Dict[str, Any], service_level=0.98, review_days=7) -> Dict[str, Any]:
    z = Z.get(round(service_level,2), 2.0537)
    ss = z * fc["sigma_lead"]
    rop = int(np.ceil(fc["mu_lead"] + ss))
    current_par = int(item_row.get("current_par",0))
    proposed_par = max(current_par, rop + int(np.ceil(fc["avg_daily"] * review_days)))
    min_order_qty = int(item_row.get("min_order_qty", 1))
    reorder_qty = max(min_order_qty, int(np.ceil(fc["avg_daily"] * (review_days + fc["lead_time_days"]))))
    return {
        "item_id": item_row["item_id"],
        "current_par": current_par,
        "forecast": {"avg_daily": round(fc["avg_daily"],2), "lead_time_days": fc["lead_time_days"], "sigma_lead": round(fc["sigma_lead"],2)},
        "safety_stock": int(np.ceil(ss)),
        "rop": int(rop),
        "proposed_par": int(proposed_par),
        "reorder_qty": int(reorder_qty),
        "constraints": {"min_order_qty": min_order_qty, "backorder": False},
        "metrics": {}
    }

def simple_explain(rec: Dict[str, Any], unit_cost: float = 1.0) -> Dict[str, Any]:
    avg = rec["forecast"]["avg_daily"]
    lt = rec["forecast"]["lead_time_days"]
    ss = rec["safety_stock"]
    rop = rec["rop"]
    par = rec["proposed_par"]
    delta = par - rec["current_par"]
    monthly_holding = round(max(delta,0)*unit_cost*0.18/12, 2)
    summary = f"Increasing PAR to {par} protects a {lt}-day lead time (ROP {rop}, safety stock {ss}). Est. holding impact ${monthly_holding}/mo."
    bullets = [
        f"Avg daily demand ≈ {avg}",
        f"Lead time demand ≈ {round(avg*lt,2)}",
        "98% service level assumption",
        f"Min order qty: {rec['constraints']['min_order_qty']}"
    ]
    return {"summary": summary, "bullets": bullets, "citations": []}
