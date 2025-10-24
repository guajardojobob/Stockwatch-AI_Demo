from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class RecommendReq(BaseModel):
    site_id: str = Field(..., description="Site code, e.g. 'SLC-660'")
    service_level: float = 0.98
    review_period_days: int = 7

class Rationale(BaseModel):
    summary: str
    bullets: List[str] = []
    citations: List[str] = []

class ItemRecommendation(BaseModel):
    item_id: str
    current_par: int
    forecast: Dict[str, Any]
    safety_stock: int
    rop: int
    proposed_par: int
    reorder_qty: int
    constraints: Dict[str, Any]
    metrics: Dict[str, Any]
    rationale: Optional[Rationale] = None

class RecommendResponse(BaseModel):
    generated_at: str
    site_id: str
    items: List[ItemRecommendation]
