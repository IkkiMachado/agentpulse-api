from typing import List
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from app.core.config import settings
from app.core.database import get_session
from app.models.agent import Agent
from app.models.task import Task, TaskStatus
from app.models.trace import ExecutionTrace
from app.schemas.task import TaskAcceptedResponse, TaskCreate, TaskRead
from app.schemas.trace import TraceRead
from app.services.runner import run_agent_task

router = APIRouter()


@router.post(
    "/agents/{agent_id}/tasks",
    response_model=TaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Dispara uma tarefa assíncrona para o agente (Asynchronous Job Pattern)"
)
def create_task_for_agent(
    agent_id: str,
    task_in: TaskCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Recebe a solicitação do usuário, registra no banco com status PENDING
    e enfileira a execução para o worker em segundo plano.
    """
    agent = session.get(Agent, agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agente com ID '{agent_id}' não encontrado."
        )
    
    # 1. Cria a tarefa no banco
    task = Task(
        agent_id=agent_id,
        input_prompt=task_in.input_prompt,
        status=TaskStatus.PENDING
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    
    # 2. Agenda a execução assíncrona no BackgroundTasks
    background_tasks.add_task(run_agent_task, task.id)
    
    # 3. Monta URL de status para polling
    base_url = str(request.base_url).rstrip("/")
    status_url = f"{base_url}{settings.API_V1_STR}/tasks/{task.id}"
    
    return TaskAcceptedResponse(
        task_id=task.id,
        agent_id=agent_id,
        status=task.status,
        status_url=status_url
    )


@router.get("/tasks/{task_id}", response_model=TaskRead, summary="Consulta status e resultado de uma tarefa")
def get_task(task_id: str, session: Session = Depends(get_session)):
    """Retorna detalhes da tarefa, incluindo status, resposta final e métricas de tokens/custo."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa com ID '{task_id}' não encontrada."
        )
    return task


@router.get(
    "/tasks/{task_id}/traces",
    response_model=List[TraceRead],
    summary="Consulta a árvore de traces e raciocínio do agente (Observabilidade)"
)
def get_task_traces(task_id: str, session: Session = Depends(get_session)):
    """Retorna o passo a passo (ReAct steps, chamadas de ferramentas e raciocínio)."""
    task = session.get(Task, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tarefa com ID '{task_id}' não encontrada."
        )
    
    traces = session.exec(
        select(ExecutionTrace)
        .where(ExecutionTrace.task_id == task_id)
        .order_by(ExecutionTrace.step_number.asc())
    ).all()
    
    return traces


@router.get("/tasks", response_model=List[TaskRead], summary="Lista as tarefas mais recentes")
def list_tasks(skip: int = 0, limit: int = 30, session: Session = Depends(get_session)):
    """Lista tarefas ordenadas das mais recentes para as mais antigas."""
    tasks = session.exec(
        select(Task).order_by(Task.created_at.desc()).offset(skip).limit(limit)
    ).all()
    return tasks
