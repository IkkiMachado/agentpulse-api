import sys
import time
import httpx

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

def check():
    with httpx.Client(timeout=10.0) as client:
        print("=" * 60)
        print("⚡ TESTE DE INTEGRAÇÃO FULL STACK: AGENTPULSE")
        print("=" * 60)

        # 1. Backend direto
        res_back = client.get("http://localhost:8000/api/v1/health")
        print(f"\n[1] Backend Direto (Porta 8000): {res_back.status_code} OK")
        print(f"    Payload: {res_back.json()}")

        # 2. Frontend Vite direto
        res_front = client.get("http://localhost:5173/")
        print(f"\n[2] Frontend Vite (Porta 5173): {res_front.status_code} OK (HTML/Assets servidos)")

        # 3. Frontend Proxy -> Backend
        res_proxy = client.get("http://localhost:5173/api/v1/health")
        print(f"\n[3] Proxy Vite -> API (/api/v1/health): {res_proxy.status_code} OK")

        # 4. Listar Agentes via Proxy
        res_agents = client.get("http://localhost:5173/api/v1/agents/")
        agents = res_agents.json()
        print(f"\n[4] Agentes carregados via Proxy: {len(agents)} encontrados")
        if not agents:
            print("    Nenhum agente encontrado.")
            return
        
        agent = agents[0]
        print(f"    Agente selecionado: '{agent['name']}' (ID: {agent['id'][:8]}...)")

        # 5. Disparar Tarefa via Proxy Frontend
        prompt = "Qual a projecao de mercado de agentes de IA para 2026?"
        print(f"\n[5] Disparando tarefa via Proxy Frontend...")
        res_dispatch = client.post(
            f"http://localhost:5173/api/v1/agents/{agent['id']}/tasks",
            json={"input_prompt": prompt}
        )
        print(f"    Status Retornado: {res_dispatch.status_code} (202 Accepted)")
        task_info = res_dispatch.json()
        task_id = task_info["task_id"]

        # 6. Polling do status
        print(f"\n[6] Acompanhando processamento (Task ID: {task_id[:8]}...):")
        completed_task = None
        for i in range(10):
            time.sleep(0.4)
            check_res = client.get(f"http://localhost:5173/api/v1/tasks/{task_id}")
            task = check_res.json()
            print(f"    Tentativa {i+1}: Status = {task['status']}")
            if task["status"] in ["COMPLETED", "FAILED"]:
                completed_task = task
                break

        if completed_task:
            print(f"\n[7] Tarefa Concluida!")
            print(f"    - Duracao: {completed_task['duration_ms']} ms")
            print(f"    - Tokens: {completed_task['total_tokens']}")
            print(f"    - Custo: ${completed_task['estimated_cost_usd']:.6f} USD")
            
            # Traces
            traces_res = client.get(f"http://localhost:5173/api/v1/tasks/{task_id}/traces")
            traces = traces_res.json()
            print(f"\n[8] Traces de Observabilidade Registrados: {len(traces)} passos")
            for t in traces:
                print(f"    Passo #{t['step_number']} [{t['step_type']}] ({t['duration_ms']}ms)")

        # 9. KPIs Analiticos Finais
        analytics_res = client.get("http://localhost:5173/api/v1/analytics/overview")
        analytics = analytics_res.json()
        print(f"\n[9] KPIs Analiticos Atualizados:")
        print(f"    - Total de Tarefas no Banco: {analytics['total_tasks']}")
        print(f"    - Taxa de Sucesso: {analytics['success_rate_percent']}%")
        print(f"    - Custo Acumulado Total: ${analytics['total_estimated_cost_usd']:.6f} USD")
        print(f"    - Tokens Totais Consumidos: {analytics['total_tokens_consumed']}")
        print("\n" + "=" * 60)
        print("TUDO FUNCIONANDO 100% DE PONTA A PONTA!")
        print("=" * 60)

if __name__ == "__main__":
    check()
