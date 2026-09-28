from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa as tabelas do banco de dados na inicialização
    create_db_and_tables()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    ## ⚡ AgentPulse — AI Agent Orchestration & Observability Platform
    
    API REST para orquestração assíncrona de **Agentes Autônomos de IA**, 
    rastreamento passo a passo (**ReAct Traces**), medição de tokens e custos (**LLMOps**) 
    e métricas consolidadas (**Data Analytics**).
    
    * **Async Job Pattern**: Tarefas executadas em background sem bloquear o cliente.
    * **Observabilidade**: Visualização de cada Tool Call e raciocínio do modelo.
    * **Analytics**: Agregações de custos em USD, taxa de conversão e latência.
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configuração de CORS para permitir requisições de frontends locais ou externos
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra as rotas da versão 1
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", include_in_schema=False)
def root_redirect():
    """Redireciona a raiz para a documentação interativa do Swagger."""
    return RedirectResponse(url="/docs")
