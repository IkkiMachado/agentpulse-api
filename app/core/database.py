from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from app.core.config import settings

# Conexão SQLite (check_same_thread=False é necessário para SQLite com FastAPI async)
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args
)


def create_db_and_tables() -> None:
    """Cria as tabelas no banco de dados se não existirem."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Dependency injection para sessões de banco de dados nos endpoints."""
    with Session(engine) as session:
        yield session
