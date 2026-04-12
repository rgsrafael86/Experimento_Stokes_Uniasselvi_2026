import streamlit as st
import streamlit.components.v1 as components
import math

# Configuração da Página
st.set_page_config(page_title="Simulador de Stokes", layout="wide")
st.title("Simulador Fenomenológico - Lei de Stokes")
st.markdown("---")

# 1. Entradas de Dados (Sidebar)
st.sidebar.header("Parâmetros do Experimento")
r_mm = st.sidebar.number_input("Raio da Esfera (mm)", value=5.55, format="%.2f")
m_g = st.sidebar.number_input("Massa da Esfera (g)", value=5.60, format="%.2f")
rho_l = st.sidebar.number_input("Densidade do Fluido (kg/m³)", value=982.2, format="%.1f")
dist_m = st.sidebar.number_input("Distância de Queda (m)", value=0.300, format="%.3f")
t_s = st.sidebar.number_input("Tempo de Queda (s)", value=0.43, format="%.2f")

# 2. Memória de Cálculo Base
r_m = r_mm / 1000
m_kg = m_g / 1000
vol_m3 = (4/3) * math.pi * (r_m ** 3)
rho_e = m_kg / vol_m3
v_ms = dist_m / t_s
g = 9.81

# Lei de Stokes (Cálculo da Viscosidade)
if v_ms > 0:
    viscosidade = (2 * (r_m ** 2) * g * (rho_e - rho_l)) / (9 * v_ms)
else:
    viscosidade = 0

# 3. Layout de Apresentação (Colunas)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Resultados Analíticos")
    st.metric(label="Volume da Esfera (m³)", value=f"{vol_m3:.2e}")
    st.metric(label="Densidade da Esfera (kg/m³)", value=f"{rho_e:.2f}")
    st.metric(label="Velocidade Terminal (m/s)", value=f"{v_ms:.4f}")
    
    st.markdown("---")
    if rho_e < rho_l:
        st.error("⚠️ Atenção: A densidade da esfera é menor que a do fluido. A esfera irá flutuar (Empuxo > Peso).")
    else:
        st.success(f"**Viscosidade Dinâmica ($\eta$):** {viscosidade:.4f} Pa.s")

with col2:
    st.subheader("Simulação Cinemática")
    st.markdown("Visualização da descida baseada na Velocidade Terminal calculada.")
    
    # 4. Motor de Renderização HTML5/Canvas (Frontend)
    # Variáveis injetadas do backend Python para o script JS
    
    html_simulador = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
        .canvas-container {{ display: flex; justify-content: center; align-items: center; flex-direction: column; background-color: #1e1e1e; padding: 20px; border-radius: 10px; }}
        canvas {{ border-left: 4px solid #555; border-right: 4px solid #555; border-bottom: 4px solid #555; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px; background-color: #00bcd4; opacity: 0.8; }}
        button {{ margin-top: 15px; padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; font-weight: bold; }}
        button:hover {{ background-color: #45a049; }}
    </style>
    </head>
    <body>
        <div class="canvas-container">
            <canvas id="provetaCanvas" width="120" height="400"></canvas>
            <button onclick="iniciarQueda()">Lançar Esfera</button>
        </div>
        <script>
            const canvas = document.getElementById('provetaCanvas');
            const ctx = canvas.getContext('2d');
            
            // Parâmetros Físicos do Backend (Python -> JS)
            const raio_pixel = Math.max(5, Math.min({r_mm} * 2, 50)); // Limites de escala visual
            const velocidade_ms = {v_ms};
            const gravidade_aparente = {rho_e} > {rho_l} ? 1 : -1; // Verifica se afunda ou flutua
            
            // Fator de escala temporal (pixels por frame)
            const fator_velocidade = velocidade_ms * 15; 
            
            const pos_inicial = 30;
            const pos_final = 400 - raio_pixel - 10;
            let y = pos_inicial;
            let animacao;
            let caindo = false;

            function desenharCena(posY) {{
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                // Marcas de calibração da proveta
                ctx.strokeStyle = 'rgba(255,255,255,0.5)';
                for(let i = 50; i < 400; i += 50) {{
                    ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(15, i); ctx.stroke();
                    ctx.beginPath(); ctx.moveTo(105, i); ctx.lineTo(120, i); ctx.stroke();
                }}

                // Esfera
                ctx.beginPath();
                ctx.arc(60, posY, raio_pixel, 0, Math.PI * 2);
                ctx.fillStyle = '#333'; // Cor da esfera (aço)
                ctx.fill();
                ctx.strokeStyle = '#000';
                ctx.stroke();
                
                // Efeito de brilho na esfera
                ctx.beginPath();
                ctx.arc(55, posY - 2, raio_pixel * 0.3, 0, Math.PI * 2);
                ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
                ctx.fill();
            }}

            function loopFisica() {{
                if (gravidade_aparente > 0) {{
                    y += fator_velocidade;
                    if (y >= pos_final) {{
                        y = pos_final;
                        caindo = false;
                        cancelAnimationFrame(animacao);
                    }} else {{
                        animacao = requestAnimationFrame(loopFisica);
                    }}
                }} else {{
                    // Esfera flutuando
                    y -= fator_velocidade * 0.5; 
                    if (y <= pos_inicial) {{
                        y = pos_inicial;
                        caindo = false;
                        cancelAnimationFrame(animacao);
                    }} else {{
                        animacao = requestAnimationFrame(loopFisica);
                    }}
                }}
                desenharCena(y);
            }}

            function iniciarQueda() {{
                if (caindo) return;
                y = gravidade_aparente > 0 ? pos_inicial : pos_final;
                caindo = true;
                loopFisica();
            }}

            // Renderiza o estado zero
            desenharCena(gravidade_aparente > 0 ? pos_inicial : pos_final);
        </script>
    </body>
    </html>
    """
    
    # Injeção do HTML no Streamlit com altura fixa
    components.html(html_simulador, height=550)
