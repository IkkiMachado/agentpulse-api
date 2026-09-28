from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_session
from app.schemas.analytics import AnalyticsOverview
from app.services.analytics_service import get_analytics_overview

router = APIRouter()


@router.get("/overview", response_model=AnalyticsOverview, summary="Dashboard analítico de KPIs de LLMOps")
def get_analytics(session: Session = Depends(get_session)):
    """
    Retorna métricas consolidadas: taxa de sucesso (%), tokens consumidos,
    custo estimado em USD, tempo médio de resposta e ferramentas mais utilizadas.
    """
    return get_analytics_overview(session)
