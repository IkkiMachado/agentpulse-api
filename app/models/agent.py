from datetime import datetime, timezone
import uuid
from typing import Optional
from sqlmodel import Field, SQLModel


def generate_uuid() -> str:
    return str(uuid.uuid4())


class AgentBase(SQLModel):
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=255)
    system_prompt: str = Field(description="Instruções mestras de comportamento e tom do agente")
    model: str = Field(default="gemini-2.5-flash", max_length=50)
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class Agent(AgentBase, table=True):
    __tablename__ = "agents"

    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
