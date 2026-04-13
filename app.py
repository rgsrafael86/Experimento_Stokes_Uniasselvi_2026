import streamlit as st
import streamlit.components.v1 as components
import math
import time

# 1. Configuração do Dashboard (Responsivo)
st.set_page_config(page_title="Laboratório Digital - Stokes", layout="wide", initial_sidebar_state="collapsed")

# CSS para métricas e layout
st.markdown("""
    <style>
    div[data-testid="stMetricValue"] { font-size: 24px; color: #58a6ff; }
    @media (max-width: 768px) { div[data-testid="stMetricValue"] { font-size: 20px; } }
    </style>
    """, unsafe_allow_html=True)

# 2. Dados Experimentais (Extração via Vídeo)
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
<div style="color: #8b949e; font-size: 12px; margin-top: -40px; margin-bottom: 25px; line-height: 1.6; text-transform: uppercase; letter-spacing: 0.5px;">
    <b>Centro Universitário Leonardo da Vinci – UNIASSELVI</b><br>
    Faculdade de Engenharias Mecânica e Produção<br>
    <span style="color: #58a6ff;">Cristan W. | João V. | Luciane A. | Rafael G.</span>
</div>
""", unsafe_allow_html=True)

st.title("Laboratório Digital - Lei de Stokes")
st.markdown("---")

# 4. PAINEL DE CONTROLE 
st.subheader("⚙️ Configuração do Ensaio")
col_preset, col_medicao, col_constante = st.columns([1, 1.5, 1.5])

with col_preset:
    st.markdown("**Seleção de Esfera:**")
    if st.button("Esfera Maior", use_container_width=True): 
        st.session_state.update(dados_ensaios["Maior"]); st.session_state.lancado = False
    if st.button("Esfera Média", use_container_width=True): 
        st.session_state.update(dados_ensaios["Media"]); st.session_state.lancado = False
    if st.button("Esfera Menor", use_container_width=True): 
        st.session_state.update(dados_ensaios["Menor"]); st.session_state.lancado = False
    st.link_button("📹 Vídeos do Ensaio", "https://uniasselvi01-my.sharepoint.com/:f:/g/personal/7116971_aluno_uniasselvi_com_br/IgAp_RKiqd3HQI4cu6ozT_irAZtbwY9ujDkYZVANoP2A51I?e=E6TI3o", use_container_width=True)

with col_medicao:
    r_mm = st.number_input("Raio da Esfera (mm)", value=st.session_state.r, step=0.01, format="%.2f")
    m_g = st.number_input("Massa da Esfera (g)", value=st.session_state.m, step=0.01, format="%.2f")
    t_s = st.number_input("Tempo de Queda (s)", value=st.session_state.t, step=0.01, format="%.2f")

with col_constante:
    rho_l = st.number_input("Dens. Fluido (kg/m³)", value=982.2, step=0.1)
    dist_m = st.number_input("Distância (m)", value=0.435, step=0.005, format="%.3f")
    d_prov_mm = st.number_input("Diâmetro Proveta (mm)", value=61.30, step=0.1)

st.markdown("---")

# 5. Processamento Analítico
g, r_m = 9.81, r_mm / 1000
vol_m3 = (4/3) * math.pi * (r_m**3)
rho_e = (m_g / 1000) / vol_m3
v_term = dist_m / t_s
# Viscosidades
eta = (2 * (r_m**2) * g * (rho_e - rho_l)) / (9 * v_term) if v_term > 0 else 0
nu = eta / rho_l if rho_l > 0 else 0
# Reynolds (Baseado no diâmetro da esfera para validação de Stokes)
reynolds = (rho_l * v_term * (2 * r_m)) / eta if eta > 0 else 0

# 6. SIMULAÇÃO E RESULTADOS
col_visual, col_res = st.columns([2, 3], gap="large")

with col_visual:
    st.subheader("Análise Cinemática")
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
        with placeholder.container():
            time.sleep(t_s); st.success("Análise Concluída")
            r1c1, r1c2 = st.columns(2)
            r1c1.metric("VELOCIDADE", f"{v_term:.4f} m/s")
            r1c2.metric("DENSIDADE (ρ_e)", f"{rho_e:.1f} kg/m³")
            
            r2c1, r2c2 = st.columns(2)
            r2c1.metric("VISC. DINÂMICA (η)", f"{eta:.4f} Pa·s", f"{eta*1000:.1f} cP")
            r2c2.metric("VISC. CINEMÁTICA (ν)", f"{nu:.6f} m²/s", f"{nu*1e6:.1f} cSt")
            
            st.metric("NÚMERO DE REYNOLDS (Re)", f"{reynolds:.4f}")

            with st.expander("📊 Acessar Memória de Cálculo", expanded=True):
                st.markdown("**1. Densidade da Esfera (ρ_e):**")
                st.markdown("**Legenda:** Ve: Volume (m3) | r: Raio (m) | m: Massa (kg) | ρ_e: Densidade (kg/m3)")
                st.latex(rf"V_e = \frac{{4}}{{3}} \pi r^3 = {vol_m3:.3e} \, m^3 \quad \rightarrow \quad \rho_e = \frac{{m}}{{V_e}} = {rho_e:.1f} \, kg/m^3")

                st.markdown("**2. Velocidade Terminal (v):**")
                st.markdown("**Legenda:** v: Velocidade (m/s) | d: Distância (m) | t: Tempo (s)")
                st.latex(rf"v = \frac{{d}}{{t}} = \frac{{{dist_m}}}{{{t_s}}} = {v_term:.4f} \, m/s")

                st.markdown("**3. Viscosidade Dinâmica (η) e Cinemática (ν):**")
                st.markdown("**Legenda:** η: Viscosidade Dinâmica (Pa·s) | ν: Viscosidade Cinemática (m2/s) | ρ_L: Dens. Fluido")
                st.latex(rf"\eta = \frac{{2r^2 g (\rho_e - \rho_L)}}{{9v}} = {eta:.4f} \, Pa \cdot s \quad \rightarrow \quad \nu = \frac{{\eta}}{{\rho_L}} = {nu:.6f} \, m^2/s")

                st.markdown("**4. Número de Reynolds (Re):**")
                st.markdown("**Legenda:** Re: Reynolds | D: Diâmetro Esfera (m) | ρ_L: Dens. Fluido | η: Visc. Dinâmica")
                st.latex(rf"Re = \frac{{\rho_L \cdot v \cdot (2r)}}{{\eta}} = \frac{{{rho_l} \cdot {v_term:.4f} \cdot {2*r_m:.4f}}}{{{eta:.4f}}} = \mathbf{{{reynolds:.4f}}}")

if st.session_state.lancado: st.session_state.lancado = False
