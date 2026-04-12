import streamlit as st
import streamlit.components.v1 as components
import math

# Configuração da Página
st.set_page_config(page_title="Simulador de Stokes", layout="wide")
st.title("Simulador Fenomenológico - Lei de Stokes")
st.markdown("Insira os parâmetros, lance a esfera e aguarde a conclusão do ensaio para obter o laudo técnico.")
st.markdown("---")

# 1. Entradas de Dados (Sidebar)
st.sidebar.header("Parâmetros do Experimento")
r_mm = st.sidebar.number_input("Raio da Esfera (mm)", value=3.00, format="%.2f")
m_g = st.sidebar.number_input("Massa da Esfera (g)", value=0.91, format="%.2f")
rho_l = st.sidebar.number_input("Densidade do Fluido (kg/m³)", value=982.2, format="%.1f")
dist_m = st.sidebar.number_input("Distância de Queda (m)", value=0.435, format="%.3f")
t_s = st.sidebar.number_input("Tempo de Queda (s)", value=0.73, format="%.2f")

# 2. Processamento do Backend (Python)
r_m = r_mm / 1000
m_kg = m_g / 1000
vol_m3 = (4/3) * math.pi * (r_m ** 3)
rho_e = m_kg / vol_m3
v_ms = dist_m / t_s
g = 9.81

if v_ms > 0:
    viscosidade = (2 * (r_m ** 2) * g * (rho_e - rho_l)) / (9 * v_ms)
else:
    viscosidade = 0

# Verificação de Fluabilidade
is_floating = rho_e < rho_l

# 3. Construção do Frontend Assíncrono (HTML/JS Injetado)
html_simulador = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: "Source Sans Pro", sans-serif; color: #FAFAFA; background-color: #0E1117; margin: 0; padding: 0; display: flex; flex-direction: row; gap: 40px; }}
    
    /* Coluna da Simulação */
    .sim-container {{ flex: 1; display: flex; flex-direction: column; align-items: center; background-color: #262730; padding: 20px; border-radius: 10px; }}
    canvas {{ border: 4px solid #555; border-top: none; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; background-color: #00bcd4; opacity: 0.8; margin-bottom: 20px; }}
    button {{ padding: 12px 24px; background-color: #2e7b32; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%; max-width: 200px; }}
    button:hover {{ background-color: #3b9b40; }}
    button:disabled {{ background-color: #555; cursor: not-allowed; }}
    
    /* Coluna de Resultados (Oculta Inicialmente) */
    .results-container {{ flex: 1; display: none; flex-direction: column; gap: 15px; padding-top: 20px; }}
    .metric-box {{ background-color: #262730; padding: 15px 20px; border-radius: 8px; }}
    .metric-title {{ font-size: 14px; color: #a1a1aa; margin-bottom: 5px; display: block; }}
    .metric-value {{ font-size: 24px; font-weight: 600; }}
    .success-box {{ background-color: #0e3b20; border: 1px solid #1a6b3b; color: #4ade80; }}
    .error-box {{ background-color: #4a0e0e; border: 1px solid #6b1a1a; color: #ff6b6b; }}
</style>
</head>
<body>

    <div class="sim-container">
        <canvas id="provetaCanvas" width="120" height="400"></canvas>
        <button id="btnLancar" onclick="iniciarQueda()">Lançar Esfera</button>
    </div>

    <div class="results-container" id="painelResultados">
        <h2 style="margin-top:0;">Laudo Técnico</h2>
        <div class="metric-box">
            <span class="metric-title">Volume da Esfera (m³)</span>
            <span class="metric-value">{vol_m3:.2e}</span>
        </div>
        <div class="metric-box">
            <span class="metric-title">Densidade da Esfera (kg/m³)</span>
            <span class="metric-value">{rho_e:.2f}</span>
        </div>
        <div class="metric-box">
            <span class="metric-title">Velocidade Terminal (m/s)</span>
            <span class="metric-value">{v_ms:.4f}</span>
        </div>
        
        <div class="metric-box {'error-box' if is_floating else 'success-box'}">
            <span class="metric-title">{'Erro Físico Detectado' if is_floating else 'Viscosidade Dinâmica (η)'}</span>
            <span class="metric-value">{'Esfera Flutuará (Empuxo > Peso)' if is_floating else f"{viscosidade:.4f} Pa.s"}</span>
        </div>
    </div>

    <script>
        const canvas = document.getElementById('provetaCanvas');
        const ctx = canvas.getContext('2d');
        const btnLancar = document.getElementById('btnLancar');
        const painelResultados = document.getElementById('painelResultados');
        
        // Dados injetados do Python
        const r_pixel = Math.max(5, Math.min({r_mm} * 2, 50));
        const velocidade = {v_ms};
        const flutua = {'true' if is_floating else 'false'} === 'true';
        
        // Cinemática
        const vel_animacao = velocidade * 15; 
        const pos_inicial = 30;
        const pos_final = 400 - r_pixel - 5;
        let y = pos_inicial;
        let animacao;
        let emMovimento = false;

        function desenharCena(posY) {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Fluido e Graduações
            ctx.strokeStyle = 'rgba(255,255,255,0.4)';
            for(let i = 50; i < 400; i += 50) {{
                ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(15, i); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(105, i); ctx.lineTo(120, i); ctx.stroke();
            }}

            // Sólido
            ctx.beginPath();
            ctx.arc(60, posY, r_pixel, 0, Math.PI * 2);
            ctx.fillStyle = '#222';
            ctx.fill();
            ctx.strokeStyle = '#000';
            ctx.stroke();
            
            // Reflexo Especular
            ctx.beginPath();
            ctx.arc(55, posY - r_pixel*0.3, r_pixel * 0.25, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.fill();
        }}

        function loopFisica() {{
            if (!flutua) {{
                y += vel_animacao;
                if (y >= pos_final) {{
                    y = pos_final;
                    finalizarEnsaio();
                    return;
                }}
            }} else {{
                y -= vel_animacao * 0.5; 
                if (y <= pos_inicial) {{
                    y = pos_inicial;
                    finalizarEnsaio();
                    return;
                }}
            }}
            
            desenharCena(y);
            animacao = requestAnimationFrame(loopFisica);
        }}

        function iniciarQueda() {{
            if (emMovimento) return;
            // Reseta UI
            painelResultados.style.display = 'none';
            btnLancar.disabled = true;
            btnLancar.innerText = 'Em Análise...';
            
            // Ponto de partida
            y = flutua ? pos_final : pos_inicial;
            emMovimento = true;
            loopFisica();
        }}

        function finalizarEnsaio() {{
            emMovimento = false;
            cancelAnimationFrame(animacao);
            desenharCena(y);
            
            // Aciona Gatilho UI - Revela os dados
            btnLancar.innerText = 'Ensaio Concluído';
            painelResultados.style.display = 'flex';
        }}

        // Estado Zero (Posição inicial baseada na densidade)
        desenharCena(flutua ? pos_final : pos_inicial);
    </script>
</body>
</html>
"""

# Renderiza a interface do app (Define altura suficiente para evitar barras de rolagem)
components.html(html_simulador, height=500)
