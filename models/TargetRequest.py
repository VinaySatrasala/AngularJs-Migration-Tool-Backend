from typing import Dict, Any
from pydantic import BaseModel

class TargetRequest(BaseModel):
    target_structure: Dict[str, Any]  # Fixed: Correct type annotation
    project_id: str
    changes: bool
