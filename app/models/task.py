from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel


def generate_uuid() -> str:
    return str(uuid.uuid4())


class TaskStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Task(SQLModel, table=True):
    __tablename__ = "tasks"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    agent_id: str = Field(foreign_key="agents.id", index=True)
    input_prompt: str = Field(description="Prompt ou tarefa enviada pelo usuário")
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    output_result: Optional[str] = Field(default=None, description="Resposta final gerada pelo agente")

    # Telemetria & Métricas de Execução
    prompt_tokens: int = Field(default=0)
    completion_tokens: int = Field(default=0)
    total_tokens: int = Field(default=0)
    estimated_cost_usd: float = Field(default=0.0, description="Custo calculado em dólares")
    duration_ms: int = Field(default=0, description="Tempo total de execução em milissegundos")
    error_message: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    finished_at: Optional[datetime] = Field(default=None)
