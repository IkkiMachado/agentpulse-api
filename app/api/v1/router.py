from fastapi import APIRouter
from app.api.v1.endpoints import agents, analytics, health, tasks

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(agents.router, prefix="/agents", tags=["Agents"])
api_router.include_router(tasks.router, tags=["Tasks & Traces"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Data Analytics & LLMOps"])
