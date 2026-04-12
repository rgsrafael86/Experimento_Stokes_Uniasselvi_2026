import streamlit as st
import streamlit.components.v1 as components
import math
import time

# 1. Configuração do Dashboard
st.set_page_config(page_title="Simulador de Stokes - Ensaios", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #f0f2f6; }
    div[data-testid="stSidebar"] { border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. Gerenciamento de Dados (Ensaios Reais)
dados_ensaios = {
    "Ensaio 1": {"r": 5.55, "m": 5.60, "t": 0.43},
    "Ensaio 2": {"r": 3.50, "m": 1.43, "t": 0.60},
    "Ensaio 3": {"r": 3.00, "m": 0.91, "t": 0.73}
}

# Inicialização do Session State
if 'r' not in st.session_state:
    st.session_state.r = 3.00
    st.session_state.m = 0.91
    st.session_state.t = 0.73
    st.session_state.lancado = False

# 3. Sidebar com Botões de Preset
with st.sidebar:
    st.header("Presets de Experimento")
    col_b1, col_b2, col_b3 = st.columns(3)
    
    if col_b1.button("E1"):
        st.session_state.r = dados_ensaios["Ensaio 1"]["r"]
        st.session_state.m = dados_ensaios["Ensaio 1"]["m"]
        st.session_state.t = dados_ensaios["Ensaio 1"]["t"]
        st.session_state.lancado = False

    if col_b2.button("E2"):
        st.session_state.r = dados_ensaios["Ensaio 2"]["r"]
        st.session_state.m = dados_ensaios["Ensaio 2"]["m"]
        st.session_state.t = dados_ensaios["Ensaio 2"]["t"]
        st.session_state.lancado = False

    if col_b3.button("E3"):
        st.session_state.r = dados_ensaios["Ensaio 3"]["r"]
        st.session_state.m = dados_ensaios["Ensaio 3"]["m"]
        st.session_state.t = dados_ensaios["Ensaio 3"]["t"]
        st.session_state.lancado = False

    st.markdown("---")
    st.header("Ajuste Fino")
    
    r_mm = st.number_input("Raio (mm)", value=st.session_state.r, step=0.01, format="%.2f")
    m_g = st.number_input("Massa (g)", value=st.session_state.m, step=0.01, format="%.2f")
    t_s = st.number_input("Tempo (s)", value=st.session_state.t, step=0.01, format="%.2f")
    
    rho_l = st.number_input("Dens. Fluido (kg/m³)", value=982.2, step=0.1)
    dist_m = st.number_input("Distância (m)", value=0.435, step=0.005, format="%.3f")

# 4. Processamento Analítico
g = 9.81
r_m = r_mm / 1000
vol_m3 = (4/3) * math.pi * (r_m**3)
rho_e = (m_g / 1000) / vol_m3
v_terminal = dist_m / t_s
viscosidade = (2 * (r_m**2) * g * (rho_e - rho_l)) / (9 * v_terminal)
is_floating = rho_e < rho_l

# 5. Interface Principal
st.title("Laboratório Digital - Stokes")
st.markdown("---")

col_dados, col_visual = st.columns([3, 2])

with col_dados:
    st.subheader("Laudo Analítico")
    if st.button("🚀 LANÇAR ESFERA", use_container_width=True, type="primary"):
        st.session_state.lancado = True

    placeholder = st.empty()
    
    if not st.session_state.lancado:
        placeholder.info("Selecione um ensaio na barra lateral ou ajuste os dados para iniciar.")
    else:
        with placeholder.container():
            if is_floating:
                st.error("⚠️ FALHA: Densidade da esfera insuficiente para vencer o empuxo.")
            else:
                with st.spinner("Simulando queda..."):
                    time.sleep(1.5)
                
                st.success("✅ Resultados Consolidados")
                m1, m2, m3 = st.columns(3)
                m1.metric("V. TERM (M/S)", f"{v_terminal:.4f}")
                m2.metric("VISCOSIDADE (Pa·s)", f"{viscosidade:.4f}")
                m3.metric("DENS. ESF (kg/m³)", f"{rho_e:.1f}")
                
                st.markdown("#### Memória de Cálculo")
                st.latex(rf"\eta = \frac{{2 \cdot {r_m:.4f}^2 \cdot 9.81 \cdot ({rho_e:.1f} - {rho_l:.1f})}}{{9 \cdot {v_terminal:.4f}}} = {viscosidade:.4f} \, Pa \cdot s")

with col_visual:
    # Motor Visual
    js_autoplay = "true" if (st.session_state.lancado and not is_floating) else "false"
    html_content = f"""
    <div style="display: flex; flex-direction: column; align-items: center; background: #161b22; padding: 20px; border-radius: 10px;">
        <canvas id="stokesCanvas" width="180" height="420" style="border: 3px solid #30363d; background: #0d1117; border-radius: 0 0 15px 15px;"></canvas>
        <div id="status" style="margin-top:15px; color:#58a6ff; font-family:sans-serif; font-weight:bold;">
            {('EM QUEDA...' if st.session_state.lancado and not is_floating else 'SISTEMA PRONTO')}
        </div>
    </div>
    <script>
        const canvas = document.getElementById('stokesCanvas');
        const ctx = canvas.getContext('2d');
        const r_px = Math.min({r_mm} * 2.5, 35);
        let y = 30;
        const y_f = 420 - r_px - 10;
        const v_px = (y_f - y) / 90;

        function draw() {{
            ctx.clearRect(0,0,180,420);
            ctx.fillStyle = "rgba(0,188,212,0.15)";
            ctx.fillRect(0,20,180,400);
            ctx.beginPath();
            ctx.arc(90, y, r_px, 0, Math.PI*2);
            ctx.fillStyle = "#f08080"; ctx.fill();
        }}

        if({js_autoplay}) {{
            function anim() {{
                if(y < y_f) {{ y += v_px; draw(); requestAnimationFrame(anim); }}
                else {{ document.getElementById('status').innerText = 'FUNDO ATINGIDO'; }}
            }}
            anim();
        }} else {{ draw(); }}
    </script>
    """
    components.html(html_content, height=550)

# Reset automático ao mudar parâmetros
if st.session_state.lancado:
    st.session_state.lancado = False
