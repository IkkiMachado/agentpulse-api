from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.trace import StepType


class TraceRead(BaseModel):
    id: str
    task_id: str
    step_number: int
    step_type: StepType
    tool_name: Optional[str] = None
    tool_input: Optional[str] = None
    tool_output: Optional[str] = None
    thought_content: Optional[str] = None
    duration_ms: int
    created_at: datetime
