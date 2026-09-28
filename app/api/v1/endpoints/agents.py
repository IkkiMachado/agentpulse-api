from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentRead, AgentUpdate

router = APIRouter()


@router.post("/", response_model=AgentRead, status_code=status.HTTP_201_CREATED)
def create_agent(agent_in: AgentCreate, session: Session = Depends(get_session)):
    """Cadastra uma nova definição de agente no sistema."""
    agent = Agent.model_validate(agent_in)
    session.add(agent)
    session.commit()
    session.refresh(agent)
    return agent


@router.get("/", response_model=List[AgentRead])
def list_agents(skip: int = 0, limit: int = 50, session: Session = Depends(get_session)):
    """Lista todos os agentes cadastrados."""
    agents = session.exec(select(Agent).offset(skip).limit(limit)).all()
    return agents


@router.get("/{agent_id}", response_model=AgentRead)
def get_agent(agent_id: str, session: Session = Depends(get_session)):
    """Obtém detalhes de um agente específico."""
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agente com ID '{agent_id}' não encontrado."
        )
    return agent


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: str, session: Session = Depends(get_session)):
    """Remove um agente do sistema."""
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agente com ID '{agent_id}' não encontrado."
        )
    session.delete(agent)
    session.commit()
    return None
