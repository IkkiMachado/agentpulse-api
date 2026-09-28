# ⚡ AgentPulse — AI Agent Orchestration & Observability Platform

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/Google_Gemini_API-8E75C2?style=for-the-badge&logo=google&logoColor=white" alt="Gemini" />
  <img src="https://img.shields.io/badge/SQLModel-2D3748?style=for-the-badge&logo=pydantic&logoColor=white" alt="SQLModel" />
  <img src="https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest" />
</p>

Plataforma de alta performance para **Orquestração e Observabilidade de Agentes Autônomos de IA (LLMOps)** com telemetria financeira, rastreamento passo a passo (*Traces*) e métricas analíticas consolidadas (*Data Analytics*).

---

## 📌 Padrões Arquiteturais Implementados

1. **Asynchronous Request-Reply Pattern:** A API aceita a solicitação do agente retornando imediatamente o código HTTP `202 Accepted` com `task_id` para acompanhamento via polling, evitando problemas de timeout em tarefas longas.
2. **ReAct Pattern (Reasoning + Acting):** O agente opera em um loop contínuo de raciocínio, acionando ferramentas externas conforme a necessidade antes de formular a resposta final.
3. **Distributed Tracing (Estilo OpenTelemetry / Langfuse):** Cada passo do agente (pensamentos, chamadas de ferramentas, parâmetros e retornos) é registrado individualmente no banco de dados para auditoria e depuração.
4. **Usage Metering Pattern:** Telemetria de consumo em tempo real (`prompt_tokens`, `completion_tokens`) e cálculo automatizado do custo em dólares (USD) baseado no modelo utilizado.
5. **Layered Architecture:** Separação estrita entre Presentation Layer (FastAPI Routers), Service/Orchestration Layer e Persistence Layer (SQLModel/Database).

---

## 🎬 Fluxo de Execução & Demonstração Visual

<!-- Coloque sua gravação em agentpulse-api/docs/agentpulse-demo.gif -->
<p align="center">
  <img src="docs/agentpulse-demo.gif" alt="AgentPulse API Flow - Asynchronous Request-Reply & ReAct Tracing" width="100%" />
</p>

### 🔄 Diagrama de Sequência (Asynchronous Request-Reply + ReAct)

```mermaid
sequenceDiagram
    autonumber
    actor User as Cliente / Frontend
    participant API as FastAPI Router
    participant Worker as Background Worker (ReAct)
    participant LLM as Google Gemini API
    participant Tools as Tool Registry
    participant DB as SQLite / PostgreSQL

    User->>API: POST /api/v1/agents/{id}/tasks (Prompt da Missão)
    API->>DB: Cria Task (status=PENDING)
    API-->>User: HTTP 202 Accepted { "task_id": "uuid", "status": "PENDING" }
    
    API-)Worker: Despacha execução assíncrona (run_agent_task)
    Worker->>DB: Atualiza Task (status=RUNNING)
    
    loop Polling de Status (a cada 600ms)
        User->>API: GET /api/v1/tasks/{task_id}
        API-->>User: HTTP 200 { "status": "RUNNING" }
    end

    Note over Worker,LLM: Ciclo ReAct & Tool Execution
    Worker->>DB: Grava Trace [THOUGHT] (Raciocínio interno)
    Worker->>LLM: generate_content(prompt, tools)
    LLM-->>Worker: Tool Call (search_knowledge_base)
    Worker->>DB: Grava Trace [TOOL_CALL]
    Worker->>Tools: Executa search_knowledge_base(query)
    Tools-->>Worker: Resultado dos dados
    Worker->>DB: Grava Trace [TOOL_RESULT]
    Worker->>DB: Grava Trace [FINAL_ANSWER]

    Worker->>DB: Atualiza Task (status=COMPLETED, tokens, cost_usd, duration_ms)

    User->>API: GET /api/v1/tasks/{task_id}
    API-->>User: HTTP 200 { "status": "COMPLETED", "output_result": "...", "estimated_cost_usd": 0.000075 }
    User->>API: GET /api/v1/tasks/{task_id}/traces
    API-->>User: HTTP 200 [ Lista cronológica dos passos ReAct ]
```

---

## 🏗️ Estrutura do Projeto

```
agentpulse-api/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py        # Verificação de status da API
│   │       │   ├── agents.py        # CRUD e gerenciamento de agentes
│   │       │   ├── tasks.py         # Disparo assíncrono de missões e consulta de traces
│   │       │   └── analytics.py     # Endpoints de KPIs e métricas consolidadas
│   │       └── router.py            # Agregador central de rotas v1
│   ├── core/
│   │   ├── config.py                # Configurações de ambiente com Pydantic Settings
│   │   └── database.py              # Engine SQLModel e injeção de dependência de sessão
│   ├── models/                      # Modelos de banco de dados (Agent, Task, ExecutionTrace)
│   ├── schemas/                     # Contratos Pydantic de entrada e saída (DTOs)
│   ├── services/
│   │   ├── runner.py                # Motor de execução do agente (ReAct + Gemini API)
│   │   ├── cost_tracker.py          # Tabela de preços e cálculo de custo por token
│   │   ├── tools.py                 # Registro de ferramentas (Function Calling)
│   │   └── analytics_service.py     # Agregações analíticas via SQL
│   └── main.py                      # Ponto de entrada FastAPI com documentação Swagger
├── tests/                           # Suíte de testes automatizados com Pytest
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 Como Executar o Projeto Localmente

### 1. Clonar e Acessar o Diretório
```bash
cd agentpulse-api
```

### 2. Ativar o Ambiente Virtual
* **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
* **Linux / Mac:**
  ```bash
  source .venv/bin/activate
  ```

### 3. Configurar as Variáveis de Ambiente
Copie o arquivo de exemplo:
```bash
cp .env.example .env
```
*(Opcional: insira sua `GEMINI_API_KEY`. Se deixada em branco, o sistema executa automaticamente em modo de simulação/demo).*

### 4. Iniciar o Servidor
```bash
uvicorn app.main:app --reload --port 8000
```

Acesse a documentação interativa e teste todos os endpoints diretamente no navegador:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)** (Swagger UI)  
👉 **[http://localhost:8000/redoc](http://localhost:8000/redoc)** (ReDoc)

---

## 🧪 Executando os Testes Automatizados

A suíte de testes valida o health check, a criação de agentes, o fluxo assíncrono de execução, os traces gerados e o dashboard de métricas:

```bash
pytest -v
```

---

## 📊 Endpoints Principais

| Método | Endpoint | Descrição |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Status de integridade da API |
| `POST` | `/api/v1/agents/` | Cadastra um novo agente com modelo e prompt do sistema |
| `GET` | `/api/v1/agents/` | Lista todos os agentes cadastrados |
| `POST` | `/api/v1/agents/{id}/tasks` | Dispara execução de tarefa (Retorna `202 Accepted`) |
| `GET` | `/api/v1/tasks/{id}` | Consulta status, resposta, tokens e custo financeiro |
| `GET` | `/api/v1/tasks/{id}/traces` | Retorna o passo a passo auditável do agente (ReAct) |
| `GET` | `/api/v1/analytics/overview` | Dashboard de KPIs (taxa de sucesso, gastos e latência) |
