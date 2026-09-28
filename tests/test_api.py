import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel

from app.core.config import settings
from app.core.database import create_db_and_tables, engine, get_session
from app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    create_db_and_tables()
    yield
    # Limpa dados após a sessão de testes, se necessário
    pass


@pytest.fixture(name="client")
def client_fixture():
    with TestClient(app) as client:
        yield client


def test_health_check(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "AgentPulse" in data["project"]


def test_create_and_get_agent(client: TestClient):
    payload = {
        "name": "Agente Analítico de Teste",
        "description": "Agente criado durante a suíte de testes unitários",
        "system_prompt": "Você é um assistente de testes conciso.",
        "model": "gemini-2.5-flash",
        "temperature": 0.5,
    }
    
    # 1. Cria o agente
    create_res = client.post("/api/v1/agents/", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    agent_id = created_data["id"]
    assert created_data["name"] == payload["name"]

    # 2. Busca o agente
    get_res = client.get(f"/api/v1/agents/{agent_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == agent_id


def test_task_execution_and_analytics_flow(client: TestClient):
    # 1. Cria um agente
    agent_res = client.post("/api/v1/agents/", json={
        "name": "Pesquisador de Tendências",
        "system_prompt": "Você pesquisa tendências do mercado de tecnologia.",
        "model": "gemini-2.5-flash",
    })
    assert agent_res.status_code == 201
    agent_id = agent_res.json()["id"]

    # 2. Dispara uma tarefa (Asynchronous Request-Reply)
    task_res = client.post(f"/api/v1/agents/{agent_id}/tasks", json={
        "input_prompt": "Quais as principais tendências de tecnologia para 2026?"
    })
    assert task_res.status_code == 202
    task_data = task_res.json()
    task_id = task_data["task_id"]
    assert "status_url" in task_data

    # 3. Consulta a tarefa (No TestClient, background_tasks rodam na resposta)
    task_detail = client.get(f"/api/v1/tasks/{task_id}")
    assert task_detail.status_code == 200
    task_json = task_detail.json()
    assert task_json["status"] == "COMPLETED"
    assert task_json["total_tokens"] > 0
    assert task_json["estimated_cost_usd"] > 0
    
    # 4. Consulta os Traces (Observabilidade)
    traces_res = client.get(f"/api/v1/tasks/{task_id}/traces")
    assert traces_res.status_code == 200
    traces = traces_res.json()
    assert isinstance(traces, list)
    assert len(traces) >= 3  # THOUGHT, TOOL_CALL, TOOL_RESULT, FINAL_ANSWER
    
    # 5. Consulta o Dashboard de Analytics
    analytics_res = client.get("/api/v1/analytics/overview")
    assert analytics_res.status_code == 200
    analytics_data = analytics_res.json()
    assert analytics_data["total_tasks"] >= 1
    assert analytics_data["completed_tasks"] >= 1
    assert analytics_data["success_rate_percent"] > 0.0
