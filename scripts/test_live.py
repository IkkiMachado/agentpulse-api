import sys
import time
import httpx
import json

# Força codificação UTF-8 no terminal Windows
if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000/api/v1"

def print_section(title: str):
    print("\n" + "=" * 60)
    print(f"--> {title}")
    print("=" * 60)

def main():
    with httpx.Client(timeout=10.0) as client:
        # 1. Health check
        print_section("1. Testando Health Check da API")
        res = client.get(f"{BASE_URL}/health")
        print(f"Status: {res.status_code}")
        print(f"Resposta: {json.dumps(res.json(), indent=2)}")

        # 2. Criar Agente
        print_section("2. Criando um Agente Especialista")
        agent_payload = {
            "name": "Especialista em Tendencias & IA",
            "description": "Agente responsavel por analisar o mercado de inteligencia artificial",
            "system_prompt": "Voce e um analista senior de inteligencia artificial e novas tecnologias.",
            "model": "gemini-2.5-flash",
            "temperature": 0.3
        }
        res = client.post(f"{BASE_URL}/agents/", json=agent_payload)
        print(f"Status: {res.status_code}")
        agent = res.json()
        agent_id = agent["id"]
        print(f"Agente Criado com Sucesso! ID: {agent_id}")
        print(f"Nome: {agent['name']} | Modelo: {agent['model']}")

        # 3. Disparar Tarefa Assincrona
        print_section("3. Disparando Tarefa Assincrona (Asynchronous Request-Reply)")
        task_payload = {
            "input_prompt": "Quais sao as principais tendencias de tecnologia e projecoes de mercado para 2026?"
        }
        res = client.post(f"{BASE_URL}/agents/{agent_id}/tasks", json=task_payload)
        print(f"Status HTTP retornado: {res.status_code} (202 Accepted = Nao bloqueante!)")
        task_info = res.json()
        task_id = task_info["task_id"]
        print(f"Task ID: {task_id}")
        print(f"Status URL: {task_info['status_url']}")

        # 4. Polling do status da tarefa
        print_section("4. Acompanhando o Processamento em Segundo Plano (Polling)")
        max_attempts = 10
        completed_task = None
        for i in range(max_attempts):
            time.sleep(0.5)
            check_res = client.get(f"{BASE_URL}/tasks/{task_id}")
            task_status = check_res.json()
            status = task_status["status"]
            print(f"  [Tentativa {i+1}] Status atual: {status}")
            if status in ["COMPLETED", "FAILED"]:
                completed_task = task_status
                break

        if completed_task:
            print("\n[OK] Tarefa Concluida com Sucesso!")
            print(f"- Duracao Total: {completed_task['duration_ms']} ms")
            print(f"- Tokens Consumidos: {completed_task['total_tokens']} (Prompt: {completed_task['prompt_tokens']} / Resposta: {completed_task['completion_tokens']})")
            print(f"- Custo Financeiro Estimado: ${completed_task['estimated_cost_usd']:.6f} USD")
            print(f"\n[Resposta Final do Agente]:\n{completed_task['output_result']}")

        # 5. Visualizar Traces de Observabilidade (ReAct Steps)
        print_section("5. Observabilidade: Inspecionando os Traces (Passo a Passo do Agente)")
        traces_res = client.get(f"{BASE_URL}/tasks/{task_id}/traces")
        traces = traces_res.json()
        print(f"Total de passos registrados: {len(traces)}")
        for step in traces:
            print(f"\n[Passo {step['step_number']}] Tipo: {step['step_type']} ({step['duration_ms']}ms)")
            if step["thought_content"]:
                print(f"  Raciocinio: {step['thought_content']}")
            if step["tool_name"]:
                print(f"  Ferramenta: {step['tool_name']}")
                print(f"  Entrada: {step['tool_input']}")
            if step["tool_output"]:
                print(f"  Retorno: {step['tool_output']}")

        # 6. Consultar Dashboard Analitico de KPIs
        print_section("6. Data Analytics: Dashboard de KPIs do Sistema")
        analytics_res = client.get(f"{BASE_URL}/analytics/overview")
        analytics = analytics_res.json()
        print(json.dumps(analytics, indent=2))

if __name__ == "__main__":
    main()
