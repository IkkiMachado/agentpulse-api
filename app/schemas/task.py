from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.task import TaskStatus


class TaskCreate(BaseModel):
    input_prompt: str = Field(..., min_length=2, examples=["Pesquise as 3 principais tendências de IA em 2026 e resuma."])


class TaskAcceptedResponse(BaseModel):
    task_id: str
    agent_id: str
    status: TaskStatus
    message: str = "Tarefa aceita para processamento assíncrono."
    status_url: str


class TaskRead(BaseModel):
    id: str
    agent_id: str
    input_prompt: str
    status: TaskStatus
    output_result: Optional[str] = None
    
    # Métricas & Telemetria
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    duration_ms: int
    error_message: Optional[str] = None
    
    created_at: datetime
    finished_at: Optional[datetime] = None
