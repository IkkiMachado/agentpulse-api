import json
from typing import Any, Callable, Dict


def calculate_math(expression: str) -> str:
    """Calcula operações matemáticas simples de forma segura. Ex: '150 * 12' ou '2500 / 4'."""
    allowed_chars = "0123456789+-*/(). "
    if not all(c in allowed_chars for c in expression):
        return "Erro: Expressão matemática contém caracteres não permitidos."
    try:
        # Avalia expressão aritmética simples
        result = eval(expression, {"__builtins__": None}, {})
        return str(result)
    except Exception as e:
        return f"Erro no cálculo: {str(e)}"


def search_knowledge_base(query: str) -> str:
    """Pesquisa dados e fatos relevantes na base de conhecimento interna."""
    query_lower = query.lower()
    knowledge_db = {
        "tendências": "As 3 principais tendências de tecnologia em 2026 são: 1. Agentes de IA Autônomos em Produção; 2. Computação com foco em eficiência energética; 3. Segurança e Governança de LLMs (LLMOps).",
        "mercado": "O mercado global de agentes inteligentes tem projeção de crescimento composto anual de 38% até 2030, liderado por automação de processos e copilotos corporativos.",
        "preço": "Nossa tabela de preços padrão de consultoria em IA é: Plano Básico $500/mês, Plano Pro $2.000/mês e Enterprise sob consulta.",
    }
    
    matches = [val for key, val in knowledge_db.items() if key in query_lower]
    if matches:
        return " ".join(matches)
    return f"Nenhum documento específico encontrado para '{query}'. Recomenda-se prosseguir com raciocínio padrão."


def get_stock_price(ticker: str) -> str:
    """Consulta cotação estimada de uma ação ou ativo."""
    ticker_clean = ticker.upper().strip()
    mock_stocks = {
        "AAPL": "Apple Inc. (AAPL): $224.50 (+1.2%)",
        "GOOGL": "Alphabet Inc. (GOOGL): $182.30 (+2.1%)",
        "MSFT": "Microsoft Corp. (MSFT): $435.10 (+0.8%)",
        "NVDA": "NVIDIA Corp. (NVDA): $132.80 (+3.5%)",
    }
    return mock_stocks.get(ticker_clean, f"Ativo '{ticker_clean}' não encontrado na base de cotações em tempo real.")


# Registro central de ferramentas disponíveis para os agentes
AVAILABLE_TOOLS: Dict[str, Callable[..., Any]] = {
    "calculate_math": calculate_math,
    "search_knowledge_base": search_knowledge_base,
    "get_stock_price": get_stock_price,
}


def execute_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Executa com segurança uma ferramenta registrada e retorna o resultado como string."""
    tool_func = AVAILABLE_TOOLS.get(name)
    if not tool_func:
        return f"Ferramenta '{name}' não está registrada no sistema."
    try:
        result = tool_func(**arguments)
        return str(result)
    except Exception as e:
        return f"Erro ao executar a ferramenta '{name}': {str(e)}"
