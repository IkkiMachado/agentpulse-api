from datetime import datetime, timezone
from enum import Enum
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel


def generate_uuid() -> str:
    return str(uuid.uuid4())


class StepType(str, Enum):
    THOUGHT = "THOUGHT"
    TOOL_CALL = "TOOL_CALL"
    TOOL_RESULT = "TOOL_RESULT"
    FINAL_ANSWER = "FINAL_ANSWER"


class ExecutionTrace(SQLModel, table=True):
    __tablename__ = "execution_traces"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    task_id: str = Field(foreign_key="tasks.id", index=True)
    step_number: int = Field(default=1, index=True)
    step_type: StepType = Field(index=True)
    
    # Detalhes da Ação
    tool_name: Optional[str] = Field(default=None, max_length=100)
    tool_input: Optional[str] = Field(default=None, description="Parâmetros de entrada serializados em JSON")
    tool_output: Optional[str] = Field(default=None, description="Retorno da ferramenta serializado em JSON")
    thought_content: Optional[str] = Field(default=None, description="Raciocínio interno do agente")
    
    duration_ms: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
