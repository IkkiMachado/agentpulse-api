import json
import time
from datetime import datetime, timezone
import os

from sqlmodel import Session
from app.core.config import settings
from app.core.database import engine
from app.models.agent import Agent
from app.models.task import Task, TaskStatus
from app.models.trace import ExecutionTrace, StepType
from app.services.cost_tracker import calculate_cost_usd
from app.services.tools import AVAILABLE_TOOLS, execute_tool


def run_agent_task(task_id: str) -> None:
    """
    Função executada em segundo plano (Background Worker).
    Implementa o ciclo ReAct do agente, grava os Traces e calcula métricas financeiras/tokens.
    """
    start_time = time.time()
    
    with Session(engine) as session:
        task = session.get(Task, task_id)
        if not task:
            return
        
        agent = session.get(Agent, task.agent_id)
        if not agent:
            task.status = TaskStatus.FAILED
            task.error_message = f"Agente '{task.agent_id}' não encontrado."
            session.add(task)
            session.commit()
            return
        
        # 1. Atualiza status para RUNNING
        task.status = TaskStatus.RUNNING
        session.add(task)
        session.commit()
        
        step_counter = 1
        
        try:
            api_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
            
            # Se a chave da Gemini API estiver configurada, executa com o modelo real
            if api_key and api_key != "your-gemini-api-key-here":
                from google import genai
                from google.genai import types
                
                client = genai.Client(api_key=api_key)
                tools_list = list(AVAILABLE_TOOLS.values())
                
                # Passo 1: Registra início do raciocínio
                step_start = time.time()
                
                response = client.models.generate_content(
                    model=agent.model,
                    contents=task.input_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=agent.system_prompt,
                        temperature=agent.temperature,
                        tools=tools_list,
                    ),
                )
                
                step_duration = int((time.time() - step_start) * 1000)
                
                # Verifica se o modelo solicitou chamada de ferramenta
                if response.function_calls:
                    for call in response.function_calls:
                        tool_name = call.name
                        tool_args = dict(call.args) if call.args else {}
                        
                        # Trace do TOOL_CALL
                        trace_call = ExecutionTrace(
                            task_id=task.id,
                            step_number=step_counter,
                            step_type=StepType.TOOL_CALL,
                            tool_name=tool_name,
                            tool_input=json.dumps(tool_args),
                            duration_ms=step_duration
                        )
                        session.add(trace_call)
                        step_counter += 1
                        
                        # Executa a ferramenta
                        t_tool_start = time.time()
                        tool_res = execute_tool(tool_name, tool_args)
                        t_tool_duration = int((time.time() - t_tool_start) * 1000)
                        
                        # Trace do TOOL_RESULT
                        trace_res = ExecutionTrace(
                            task_id=task.id,
                            step_number=step_counter,
                            step_type=StepType.TOOL_RESULT,
                            tool_name=tool_name,
                            tool_output=json.dumps(tool_res),
                            duration_ms=t_tool_duration
                        )
                        session.add(trace_res)
                        step_counter += 1
                
                # Metadados de tokens
                usage = getattr(response, "usage_metadata", None)
                p_tokens = getattr(usage, "prompt_token_count", 150) if usage else 150
                c_tokens = getattr(usage, "candidates_token_count", 250) if usage else 250
                
                final_text = response.text or "Tarefa concluída com sucesso."
                
            else:
                # MODO DEMO / SIMULAÇÃO (Permite testar a arquitetura sem precisar de chave de API imediatamente)
                step_start = time.time()
                
                # Simula o raciocínio e chamada de ferramenta
                tool_to_call = "search_knowledge_base"
                tool_args = {"query": task.input_prompt}
                
                trace_thought = ExecutionTrace(
                    task_id=task.id,
                    step_number=step_counter,
                    step_type=StepType.THOUGHT,
                    thought_content=f"Analisando a solicitação: '{task.input_prompt}'. Decidindo acionar a base interna de conhecimento.",
                    duration_ms=180
                )
                session.add(trace_thought)
                step_counter += 1
                
                # Simula TOOL_CALL
                trace_call = ExecutionTrace(
                    task_id=task.id,
                    step_number=step_counter,
                    step_type=StepType.TOOL_CALL,
                    tool_name=tool_to_call,
                    tool_input=json.dumps(tool_args),
                    duration_ms=120
                )
                session.add(trace_call)
                step_counter += 1
                
                # Executa a ferramenta real
                tool_output = execute_tool(tool_to_call, tool_args)
                trace_res = ExecutionTrace(
                    task_id=task.id,
                    step_number=step_counter,
                    step_type=StepType.TOOL_RESULT,
                    tool_name=tool_to_call,
                    tool_output=json.dumps(tool_output),
                    duration_ms=95
                )
                session.add(trace_res)
                step_counter += 1
                
                p_tokens = 185
                c_tokens = 320
                final_text = (
                    f"Com base na análise das fontes e dados coletados:\n\n"
                    f"{tool_output}\n\n"
                    f"Síntese: O agente concluiu a operação seguindo as diretrizes de {agent.name}."
                )
            
            # Trace da resposta final
            trace_final = ExecutionTrace(
                task_id=task.id,
                step_number=step_counter,
                step_type=StepType.FINAL_ANSWER,
                thought_content="Consolidação e formatação da resposta final para entrega ao cliente.",
                duration_ms=80
            )
            session.add(trace_final)
            
            # 2. Consolidação de Métricas e Telemetria
            total_duration_ms = int((time.time() - start_time) * 1000)
            cost_usd = calculate_cost_usd(agent.model, p_tokens, c_tokens)
            
            task.status = TaskStatus.COMPLETED
            task.output_result = final_text
            task.prompt_tokens = p_tokens
            task.completion_tokens = c_tokens
            task.total_tokens = p_tokens + c_tokens
            task.estimated_cost_usd = cost_usd
            task.duration_ms = total_duration_ms
            task.finished_at = datetime.now(timezone.utc)
            
            session.add(task)
            session.commit()
            
        except Exception as e:
            total_duration_ms = int((time.time() - start_time) * 1000)
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.duration_ms = total_duration_ms
            task.finished_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()
