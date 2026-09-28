from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class AgentCreate(BaseModel):
    name: str = Field(..., max_length=100, examples=["Analista de Mercado"])
    description: Optional[str] = Field(None, max_length=255, examples=["Pesquisa e resume tendências de tecnologia"])
    system_prompt: str = Field(..., examples=["Você é um analista experiente. Seja direto e estruturado."])
    model: str = Field(default="gemini-2.5-flash", examples=["gemini-2.5-flash"])
    temperature: float = Field(default=0.7, ge=0.0, le=1.0)


class AgentUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0)


class AgentRead(BaseModel):
    id: str
    name: str
    description: Optional[str]
    system_prompt: str
    model: str
    temperature: float
    created_at: datetime
    updated_at: datetime
