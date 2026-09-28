from typing import List
from sqlmodel import Session, select, func
from app.models.task import Task, TaskStatus
from app.models.trace import ExecutionTrace, StepType
from app.schemas.analytics import AnalyticsOverview, ToolUsageStat


def get_analytics_overview(session: Session) -> AnalyticsOverview:
    """
    Executa queries analíticas de agregação para compor o dashboard de KPIs.
    """
    # 1. Contagens de status
    total_tasks = session.exec(select(func.count(Task.id))).one()
    completed_tasks = session.exec(select(func.count(Task.id)).where(Task.status == TaskStatus.COMPLETED)).one()
    failed_tasks = session.exec(select(func.count(Task.id)).where(Task.status == TaskStatus.FAILED)).one()
    pending_tasks = session.exec(select(func.count(Task.id)).where(Task.status.in_([TaskStatus.PENDING, TaskStatus.RUNNING]))).one()
    
    # Taxa de sucesso
    success_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    # 2. Agregações numéricas (Tokens, Custo, Latência)
    metrics_query = select(
        func.coalesce(func.sum(Task.total_tokens), 0),
        func.coalesce(func.sum(Task.estimated_cost_usd), 0.0),
        func.coalesce(func.avg(Task.duration_ms), 0.0)
    ).where(Task.status == TaskStatus.COMPLETED)
    
    total_tokens, total_cost, avg_duration = session.exec(metrics_query).one()
    
    # 3. Estatísticas de uso de ferramentas nos traces
    tools_query = (
        select(
            ExecutionTrace.tool_name,
            func.count(ExecutionTrace.id).label("call_count"),
            func.avg(ExecutionTrace.duration_ms).label("avg_duration")
        )
        .where(ExecutionTrace.step_type == StepType.TOOL_CALL)
        .group_by(ExecutionTrace.tool_name)
        .order_by(func.count(ExecutionTrace.id).desc())
        .limit(5)
    )
    
    tool_rows = session.exec(tools_query).all()
    top_tools = [
        ToolUsageStat(
            tool_name=row[0] or "unknown",
            call_count=row[1],
            avg_duration_ms=round(float(row[2]), 2)
        )
        for row in tool_rows
    ]
    
    return AnalyticsOverview(
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        failed_tasks=failed_tasks,
        pending_tasks=pending_tasks,
        success_rate_percent=round(float(success_rate), 2),
        total_tokens_consumed=int(total_tokens),
        total_estimated_cost_usd=round(float(total_cost), 6),
        avg_duration_ms=round(float(avg_duration), 2),
        top_tools_used=top_tools
    )
