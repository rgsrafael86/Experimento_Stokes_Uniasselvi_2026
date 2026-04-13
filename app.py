import streamlit as st
import streamlit.components.v1 as components
import math
import time

# 1. Configuração do Dashboard
st.set_page_config(page_title="Laboratório Digital - Stokes", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 26px; color: #58a6ff; }
    @media (max-width: 768px) { div[data-testid="stMetricValue"] { font-size: 22px; } }
    </style>
    """, unsafe_allow_html=True)

# 2. Dados Experimentais
dados_ensaios = {
    "Maior": {"r": 5.55, "m": 5.60, "t": 0.49},
    "Media": {"r": 3.50, "m": 1.43, "t": 0.83},
    "Menor": {"r": 3.00, "m": 0.91, "t": 0.95}
}

if 'r' not in st.session_state:
    st.session_state.r, st.session_state.m, st.session_state.t = 5.55, 5.60, 0.49
    st.session_state.lancado = False

# 3. Cabeçalho Institucional
st.markdown("""
<div style="color: #8b949e; font-size: 12px; margin-top: -40px; margin-bottom: 25px; line-height: 1.6; text-transform: uppercase;">
    <b>Centro Universitário Leonardo da Vinci – UNIASSELVI</b><br>
    Faculdade de Engenharias Mecânica e Produção<br>
    <span style="color: #58a6ff;">Cristan W. | João V. | Luciane A. | Rafael G.</span>
</div>
""", unsafe_allow_html=True)

st.title("Laboratório Digital - Lei de Stokes")
st.markdown("---")

# 4. Painel de Controle
st.subheader("⚙️ Configuração do Ensaio")
col_preset, col_medicao, col_constante = st.columns([1, 1.5, 1.5])

with col_preset:
    st.markdown("**Seleção de Esfera:**")
    if st.button("Esfera Maior", use_container_width=True): st.session_state.update(dados_ensaios["Maior"]); st.session_state.lancado = False
    if st.button("Esfera Média", use_container_width=True): st.session_state.update(dados_ensaios["Media"]); st.session_state.lancado = False
    if st.button("Esfera Menor", use_container_width=True): st.session_state.update(dados_ensaios["Menor"]); st.session_state.lancado = False
    st.link_button("📹 Vídeos do Ensaio", "https://uniasselvi01-my.sharepoint.com/:f:/g/personal/7116971_aluno_uniasselvi_com_br/IgAp_RKiqd3HQI4cu6ozT_irAZtbwY9ujDkYZVANoP2A51I?e=E6TI3o", use_container_width=True)

with col_medicao:
    r_mm = st.number_input("Raio da Esfera (mm)", value=st.session_state.r, step=0.01, format="%.2f")
    m_g = st.number_input("Massa da Esfera (g)", value=st.session_state.m, step=0.01, format="%.2f")
    t_s = st.number_input("Tempo de Queda (s)", value=st.session_state.t, step=0.01, format="%.2f")

with col_constante:
    rho_l = st.number_input("Dens. Fluido (kg/m³)", value=982.2, step=0.1)
    dist_m = st.number_input("Distância de Queda (m)", value=0.435, step=0.005, format="%.3f")
    d_proveta_mm = st.number_input("Diâmetro Proveta (mm)", value=61.3, step=0.1)

# 5. Cálculos de Engenharia
g = 9.81
r_m = r_mm / 1000
d_proveta_m = d_proveta_mm / 1000
vol_m3 = (4/3) * math.pi * (r_m**3)
rho_e = (m_g / 1000) / vol_m3
v_terminal = dist_m / t_s

# Dinâmica
eta = (2 * (r_m**2) * g * (rho_e - rho_l)) / (9 * v_terminal) if v_terminal > 0 else 0
# Cinemática
nu = eta / rho_l if rho_l > 0 else 0
# Reynolds
reynolds = (rho_l * v_terminal * d_proveta_m) / eta if eta > 0 else 0

# 6. Exibição
col_visual, col_res = st.columns([2, 3], gap="large")

with col_visual:
    if st.button("🚀 LANÇAR ESFERA", use_container_width=True, type="primary"): st.session_state.lancado = True
    js_autoplay = "true" if (st.session_state.lancado and rho_e >= rho_l) else "false"
    html_content = f"""
    <div style="display:flex; flex-direction:column; align-items:center; width:100%;">
        <canvas id="stokesCanvas" width="220" height="420" style="background:#0d1117; border-radius:8px; border:1px solid #30363d;"></canvas>
        <div id="status" style="margin-top:15px; color:#58a6ff; font-family:sans-serif; font-weight:bold;">{('EM QUEDA...' if st.session_state.lancado else 'PRONTO')}</div>
    </div>
    <script>
        const canvas = document.getElementById('stokesCanvas'); const ctx = canvas.getContext('2d');
        const r_px = Math.min({r_mm} * 2.5, 30); let y = 30; const y_f = 390 - r_px; const dur = {t_s} * 1000; let start = null;
        function draw() {{
            ctx.clearRect(0,0,220,420); ctx.strokeStyle="#fff3"; ctx.lineWidth=3;
            ctx.strokeRect(60,10,100,390); ctx.fillStyle="#00bcd420"; ctx.fillRect(61,20,98,380);
            ctx.fillStyle="#f08080"; ctx.beginPath(); ctx.arc(110, y, r_px, 0, Math.PI*2); ctx.fill();
        }}
        function anim(t) {{
            if(!start) start = t; const p = (t-start)/dur;
            if(p<1){{ y = 30 + (y_f-30)*p; draw(); requestAnimationFrame(anim); }}
            else {{ y=y_f; draw(); document.getElementById('status').innerText='FUNDO ATINGIDO'; }}
        }}
        draw(); if({js_autoplay}) requestAnimationFrame(anim);
    </script>
    """
    components.html(html_content, height=480)

with col_res:
    st.subheader("Resultados")
    placeholder = st.empty()
    if not st.session_state.lancado: placeholder.info("Aguardando lançamento...")
    else:
        time.sleep(t_s)
        with placeholder.container():
            c1, c2, c3 = st.columns(3)
            c1.metric("VELOCIDADE", f"{v_terminal:.4f} m/s")
            c2.metric("DINÂMICA (η)", f"{eta:.4f} Pa·s")
            c3.metric("REYNOLDS (Re)", f"{reynolds:.2f}")
            
            c4, c5, c6 = st.columns(3)
            c4.metric("DENSIDADE (ρ_e)", f"{rho_e:.1f} kg/m³")
            c5.metric("CINEMÁTICA (ν)", f"{nu:.6f} m²/s")
            c6.metric("VISC. (cP)", f"{eta*1000:.1f} cP")

            with st.expander("📊 Memória de Cálculo Completa", expanded=True):
                st.markdown("**1. Densidade da Esfera:**")
                st.latex(rf"\rho_e = \frac{{m}}{{V_e}} = {rho_e:.2f} \, kg/m^3")
                st.markdown("**2. Viscosidade Dinâmica (η):**")
                st.latex(rf"\eta = \frac{{2r^2 g (\rho_e - \rho_L)}}{{9v}} = {eta:.4f} \, Pa \cdot s")
                st.markdown("**3. Viscosidade Cinemática (ν):**")
                st.latex(rf"\nu = \frac{{\eta}}{{\rho_L}} = {nu:.6f} \, m^2/s")
                st.markdown("**4. Número de Reynolds (Re):**")
                st.markdown("**Legenda:** Re: Reynolds | D_p: Diâmetro Proveta | v: Velocidade")
                st.latex(rf"Re = \frac{{v \cdot D_p}}{{\nu}} = \frac{{{v_terminal:.4f} \cdot {d_proveta_m}}}{{{nu:.6f}}} = \mathbf{{{reynolds:.2f}}}")

if st.session_state.lancado: st.session_state.lancado = False
