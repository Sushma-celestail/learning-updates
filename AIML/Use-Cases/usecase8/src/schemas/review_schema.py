from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any

class ReviewDecision(BaseModel):
    reviewer_id: str
    decision: Literal["approve", "reject", "edit"]
    reason: Optional[str] = None

    #  ADD THIS
    edited_args: Optional[Dict[str, Any]] = None