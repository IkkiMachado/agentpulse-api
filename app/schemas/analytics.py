from typing import List, Optional
from pydantic import BaseModel


class ToolUsageStat(BaseModel):
    tool_name: str
    call_count: int
    avg_duration_ms: float


class AnalyticsOverview(BaseModel):
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    pending_tasks: int
    success_rate_percent: float
    total_tokens_consumed: int
    total_estimated_cost_usd: float
    avg_duration_ms: float
    top_tools_used: List[ToolUsageStat] = []
