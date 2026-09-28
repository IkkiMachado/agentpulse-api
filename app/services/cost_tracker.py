from typing import Dict, Tuple

# Preços estimados por 1.000.000 (1M) de tokens em USD
# Fonte baseada na tabela oficial do Google Gemini API
PRICING_TABLE_PER_1M: Dict[str, Tuple[float, float]] = {
    # Modelo: (Prompt USD / 1M, Completion USD / 1M)
    "gemini-2.5-flash": (0.075, 0.30),
    "gemini-1.5-flash": (0.075, 0.30),
    "gemini-1.5-pro": (1.25, 5.00),
    "gemini-2.0-flash": (0.10, 0.40),
}

DEFAULT_PRICING = (0.10, 0.40)


def calculate_cost_usd(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calcula o custo financeiro aproximado de uma execução baseado nos tokens consumidos.
    """
    prompt_rate, completion_rate = PRICING_TABLE_PER_1M.get(model_name.lower(), DEFAULT_PRICING)
    
    prompt_cost = (prompt_tokens / 1_000_000) * prompt_rate
    completion_cost = (completion_tokens / 1_000_000) * completion_rate
    
    return round(prompt_cost + completion_cost, 6)
