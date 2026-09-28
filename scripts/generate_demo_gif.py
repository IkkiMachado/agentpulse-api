import os
import sys
import time
import subprocess
import urllib.request
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(r"c:\Users\Henrique\Downloads\Learning")
API_DIR = BASE_DIR / "agentpulse-api"
WEB_DIR = BASE_DIR / "agentpulse-web"
PYTHON_EXE = API_DIR / ".venv" / "Scripts" / "python.exe"

OUT_WEB_GIF = WEB_DIR / "docs" / "agentpulse-demo.gif"
OUT_API_GIF = API_DIR / "docs" / "agentpulse-demo.gif"
OUT_POSTER = WEB_DIR / "docs" / "agentpulse-poster.png"

def is_url_ok(url: str) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=2) as res:
            return res.status in (200, 404, 307)
    except Exception:
        return False

def wait_for_server(url: str, name: str, timeout: int = 30):
    print(f"Aguardando {name} ficar pronto em {url}...")
    start = time.time()
    while time.time() - start < timeout:
        if is_url_ok(url):
            print(f"✅ {name} está ativo!")
            return True
        time.sleep(1)
    raise TimeoutError(f"Servidor {name} não respondeu em {timeout} segundos.")

def start_servers_if_needed():
    procs = []
    
    # 1. Backend na porta 8000
    if not is_url_ok("http://localhost:8000/api/v1/health"):
        print("Iniciando backend FastAPI na porta 8000...")
        p_api = subprocess.Popen(
            [str(PYTHON_EXE), "-m", "uvicorn", "app.main:app", "--port", "8000"],
            cwd=str(API_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        procs.append(p_api)
        wait_for_server("http://localhost:8000/api/v1/health", "Backend FastAPI")
    else:
        print("Backend FastAPI já está em execução na porta 8000.")

    # 2. Frontend na porta 5173
    if not is_url_ok("http://localhost:5173"):
        print("Iniciando frontend Vite na porta 5173...")
        p_web = subprocess.Popen(
            ["npm.cmd", "run", "dev"],
            cwd=str(WEB_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        )
        procs.append(p_web)
        wait_for_server("http://localhost:5173", "Frontend Vite")
    else:
        print("Frontend Vite já está em execução na porta 5173.")

    return procs

def record_demo():
    print("=" * 60)
    print("🎬 INICIANDO GRAVAÇÃO AUTOMATIZADA HEADLESS DO AGENTPULSE")
    print("=" * 60)

    server_procs = start_servers_if_needed()

    frames = []
    durations = []

    def capture(page, duration_ms=250):
        png_bytes = page.screenshot(type="png")
        img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
        frames.append(img)
        durations.append(duration_ms)

    import io

    try:
        with sync_playwright() as p:
            print("Iniciando navegador Chromium...")
            browser = p.chromium.launch(channel="chrome", headless=True)
            context = browser.new_context(
                viewport={"width": 1280, "height": 780},
                device_scale_factor=1.25
            )
            page = context.new_page()

            print("1. Acessando Dashboard Web...")
            page.goto("http://localhost:5173")
            page.wait_for_load_state("networkidle")
            time.sleep(1.5)

            # Salva screenshot estático de alta resolução do Dashboard inicial
            OUT_POSTER.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(OUT_POSTER))
            print(f"📸 Poster estático salvo em: {OUT_POSTER}")

            # 2. Mostra tela inicial (Dashboard com KPIs)
            for _ in range(3):
                capture(page, 400)

            # 3. Navega para a aba Playground
            print("2. Acessando Playground...")
            btn_playground = page.locator("button:has-text('Playground')")
            btn_playground.click()
            time.sleep(0.8)
            for _ in range(3):
                capture(page, 300)

            # 4. Clica na sugestão de prompt
            print("3. Inserindo prompt de tendências de IA...")
            prompt_chip = page.locator("button:has-text('Quais as 3 principais tendências')")
            if prompt_chip.count() > 0:
                prompt_chip.first.click()
            else:
                page.locator("textarea").fill("Quais as 3 principais tendências de tecnologia e projeções para 2026?")
            
            time.sleep(0.5)
            for _ in range(4):
                capture(page, 350)

            # 5. Clica no botão de Disparar Tarefa (Async)
            print("4. Disparando tarefa assíncrona (HTTP 202 Accepted)...")
            btn_dispatch = page.locator("button:has-text('Disparar Tarefa')")
            btn_dispatch.click()

            # Captura a transição e o polling (status em background)
            start_wait = time.time()
            completed = False
            while time.time() - start_wait < 15:
                capture(page, 250)
                # Verifica se o botão "Ver Traces" apareceu ou se o texto final foi renderizado
                if page.locator("button:has-text('Ver Traces')").count() > 0:
                    completed = True
                    break
                time.sleep(0.2)

            print(f"Status da execução concluída: {completed}")
            # Pausa para o espectador ler o resultado e ver a telemetria (custo em USD e tokens)
            for _ in range(6):
                capture(page, 500)

            # 6. Clica em "Ver Traces" para inspecionar o ciclo ReAct
            print("5. Inspecionando árvore ReAct no TraceViewer...")
            btn_traces = page.locator("button:has-text('Ver Traces')")
            if btn_traces.count() > 0:
                btn_traces.first.click()
            else:
                page.locator("button:has-text('Traces & ReAct')").click()

            time.sleep(1.2)
            # Captura a árvore de traces
            for _ in range(5):
                capture(page, 450)

            # Rola suavemente na lista de traces se houver overflow
            page.mouse.wheel(0, 150)
            time.sleep(0.4)
            for _ in range(3):
                capture(page, 400)

            # 7. Volta para a aba Dashboard para mostrar KPIs consolidados
            print("6. Retornando ao Dashboard analítico...")
            page.locator("button:has-text('Dashboard')").click()
            time.sleep(1.0)
            for _ in range(6):
                capture(page, 400)

            browser.close()

    finally:
        # Se nós abrimos os processos e quisermos manter ou fechar:
        # Deixamos o ambiente estável
        pass

    print(f"\nTotal de quadros capturados: {len(frames)}")
    print("Otimizando e compilando animação GIF...")

    # Redimensiona mantendo proporção para otimização do GitHub (< 5MB)
    target_width = 960
    opt_frames = []
    for f in frames:
        w, h = f.size
        target_height = int(h * (target_width / w))
        resized = f.resize((target_width, target_height), Image.Resampling.LANCZOS)
        # Quantização com paleta adaptativa de 128 cores
        quantized = resized.quantize(colors=128, method=Image.Quantize.MEDIANCUT)
        opt_frames.append(quantized)

    OUT_WEB_GIF.parent.mkdir(parents=True, exist_ok=True)
    OUT_API_GIF.parent.mkdir(parents=True, exist_ok=True)

    print(f"Salvando GIF em: {OUT_WEB_GIF}")
    opt_frames[0].save(
        str(OUT_WEB_GIF),
        save_all=True,
        append_images=opt_frames[1:],
        duration=durations,
        loop=0,
        optimize=True
    )

    import shutil
    shutil.copyfile(str(OUT_WEB_GIF), str(OUT_API_GIF))
    print(f"Copiado para: {OUT_API_GIF}")

    size_mb = os.path.getsize(str(OUT_WEB_GIF)) / (1024 * 1024)
    print(f"🎉 SUCESSO! GIF gerado com tamanho: {size_mb:.2f} MB")
    print("=" * 60)

if __name__ == "__main__":
    record_demo()
