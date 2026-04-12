import streamlit as st
import streamlit.components.v1 as components
import math
import time

# 1. Configuração do Dashboard
st.set_page_config(page_title="Simulador de Stokes", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #f0f2f6; }
    div[data-testid="stSidebar"] { border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. Entradas Paramétricas (Barra Lateral)
with st.sidebar:
    st.header("Controles do Ensaio")
    st.markdown("Ajuste os parâmetros antes do lançamento.")
    r_mm = st.slider("Raio da Esfera (mm)", 1.0, 10.0, 3.0, 0.1)
    m_g = st.slider("Massa da Esfera (g)", 0.1, 10.0, 0.91, 0.01)
    rho_l = st.slider("Densidade do Fluido (kg/m³)", 800.0, 1500.0, 982.2, 0.1)
    dist_m = st.slider("Distância de Queda (m)", 0.1, 1.0, 0.435, 0.005)
    t_s = st.slider("Tempo de Queda (s)", 0.1, 5.0, 0.73, 0.01)

# 3. Processamento Analítico (Background)
g = 9.81
r_m = r_mm / 1000
vol_m3 = (4/3) * math.pi * (r_m**3)
rho_e = (m_g / 1000) / vol_m3
v_terminal = dist_m / t_s
viscosidade = (2 * (r_m**2) * g * (rho_e - rho_l)) / (9 * v_terminal)

is_floating = rho_e < rho_l

# 4. Layout Principal (Visão Total)
st.title("Análise de Viscosidade - Lei de Stokes")
st.markdown("---")

col_dados, col_visual = st.columns([3, 2])

# Gerenciador de Estado do Lançamento
if 'lancado' not in st.session_state:
    st.session_state.lancado = False

with col_dados:
    st.subheader("Laudo Analítico")
    placeholder_resultados = st.empty()
    
    # Botão de Ação Primária
    if st.button("🚀 LANÇAR ESFERA", use_container_width=True, type="primary"):
        st.session_state.lancado = True

    # Lógica de Revelação
    if not st.session_state.lancado:
        placeholder_resultados.info("Aguardando inicialização do ensaio. Ajuste os parâmetros na barra lateral e clique em 'Lançar Esfera'.")
    else:
        with placeholder_resultados.container():
            if is_floating:
                st.error("⚠️ FALHA: Densidade da esfera menor que a do fluido. O empuxo impede a descida.")
            else:
                # O painel renderiza um aviso, aguarda 1.5s (tempo da animação) e exibe os dados
                with st.spinner("Analisando cinemática de queda..."):
                    time.sleep(1.5) 
                
                st.success("✅ Equilíbrio de Stokes calculado com sucesso.")
                m1, m2, m3 = st.columns(3)
                m1.metric("VESF (M/S)", f"{v_terminal:.4f}")
                m2.metric("VISCOSIDADE (PA.S)", f"{viscosidade:.4f}")
                m3.metric("DENS. ESF (KG/M³)", f"{rho_e:.2f}")

with col_visual:
    # 5. Motor de Renderização HTML/JS (Proveta no Canto)
    # A variável js_autoplay define se a esfera cai ao carregar o iframe
    js_autoplay = "true" if (st.session_state.lancado and not is_floating) else "false"
    
    html_content = f"""
    <div style="display: flex; flex-direction: column; align-items: center; background: #161b22; padding: 20px; border-radius: 10px; height: 100%;">
        <div style="color: #8b949e; margin-bottom: 10px; font-family: sans-serif; font-size: 14px;">Monitoramento da Proveta</div>
        <canvas id="stokesCanvas" width="180" height="420" style="border: 3px solid #30363d; border-top: none; background: #0d1117; border-bottom-left-radius: 15px; border-bottom-right-radius: 15px;"></canvas>
        <div id="status" style="margin-top: 15px; color: #58a6ff; font-weight: bold; font-family: sans-serif;">{'PRONTO PARA LANÇAMENTO' if not st.session_state.lancado else ('FALHA DE EMPUXO' if is_floating else 'EM QUEDA...')}</div>
    </div>

    <script>
        const canvas = document.getElementById('stokesCanvas');
        const ctx = canvas.getContext('2d');
        const statusText = document.getElementById('status');
        
        const autoPlay = {js_autoplay};
        const r_pixel = Math.min({r_mm} * 2.5, 40); // Escala visual do raio
        
        let y = 30; // Posição inicial no topo
        const y_final = 420 - r_pixel - 10; // Fundo da proveta
        
        // A animação dura exatamente 1.5s (90 frames a 60fps) para sincronizar com o Python time.sleep(1.5)
        const v_pixel = (y_final - y) / 90; 

        function drawCylinder() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Líquido
            ctx.fillStyle = "rgba(0, 188, 212, 0.15)";
            ctx.fillRect(0, 20, canvas.width, canvas.height);
            
            // Nível do Líquido
            ctx.beginPath();
            ctx.moveTo(0, 20); ctx.lineTo(canvas.width, 20);
            ctx.strokeStyle = "rgba(0, 188, 212, 0.8)"; ctx.stroke();

            // Graduação
            ctx.strokeStyle = "rgba(255,255,255,0.2)";
            ctx.fillStyle = "#8b949e";
            ctx.font = "10px sans-serif";
            for(let i=1; i<=4; i++) {{
                let h = 420 - (i * 85);
                ctx.beginPath(); ctx.moveTo(0, h); ctx.lineTo(15, h); ctx.stroke();
                ctx.fillText(((i * {dist_m}/4).toFixed(2) + "m"), 20, h+4);
            }}

            // Esfera
            ctx.beginPath();
            ctx.arc(canvas.width/2, y, r_pixel, 0, Math.PI*2);
            ctx.fillStyle = "#f08080";
            ctx.fill();
            
            // Brilho da esfera
            ctx.beginPath();
            ctx.arc(canvas.width/2 - r_pixel*0.3, y - r_pixel*0.3, r_pixel*0.2, 0, Math.PI*2);
            ctx.fillStyle = "rgba(255,255,255,0.3)";
            ctx.fill();
        }}

        function animate() {{
            if(y < y_final) {{
                y += v_pixel;
                drawCylinder();
                requestAnimationFrame(animate);
            }} else {{
                statusText.innerText = "FUNDO ATINGIDO";
                statusText.style.color = "#3fb950"; // Verde Sucesso
            }}
        }}

        drawCylinder();
        
        if(autoPlay) {{
            requestAnimationFrame(animate);
        }} else if ({is_floating}) {{
            y = y_final; // Desenha no fundo se estiver flutuando
            drawCylinder();
        }}
    </script>
    """
    # A altura de 500px garante que a proveta não crie barras de rolagem
    components.html(html_content, height=520)

# Reseta o estado para permitir novos laudos caso o usuário mude um slider
if st.session_state.lancado:
    st.session_state.lancado = False
