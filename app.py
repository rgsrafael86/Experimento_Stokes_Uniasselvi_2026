import streamlit as st
import streamlit.components.v1 as components
import math
import time

# 1. Configuração do Dashboard
st.set_page_config(page_title="Laboratório Digital - Stokes", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #f0f2f6; }
    div[data-testid="stSidebar"] { border-right: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

# 2. Dados Experimentais de Bancada
dados_ensaios = {
    "Ensaio 1": {"r": 5.55, "m": 5.60, "t": 0.43},
    "Ensaio 2": {"r": 3.50, "m": 1.43, "t": 0.60},
    "Ensaio 3": {"r": 3.00, "m": 0.91, "t": 0.73}
}

if 'r' not in st.session_state:
    st.session_state.r = 3.00
    st.session_state.m = 0.91
    st.session_state.t = 0.73
    st.session_state.lancado = False

# 3. Sidebar (Controles)
with st.sidebar:
    st.header("Presets de Experimento")
    col_b1, col_b2, col_b3 = st.columns(3)
    
    if col_b1.button("E1"):
        st.session_state.update(dados_ensaios["Ensaio 1"])
        st.session_state.lancado = False
    if col_b2.button("E2"):
        st.session_state.update(dados_ensaios["Ensaio 2"])
        st.session_state.lancado = False
    if col_b3.button("E3"):
        st.session_state.update(dados_ensaios["Ensaio 3"])
        st.session_state.lancado = False

    st.markdown("---")
    st.header("Ajuste Fino")
    r_mm = st.number_input("Raio (mm)", value=st.session_state.r, step=0.01, format="%.2f")
    m_g = st.number_input("Massa (g)", value=st.session_state.m, step=0.01, format="%.2f")
    t_s = st.number_input("Tempo (s)", value=st.session_state.t, step=0.01, format="%.2f")
    rho_l = st.number_input("Dens. Fluido (kg/m³)", value=982.2, step=0.1)
    dist_m = st.number_input("Distância (m)", value=0.435, step=0.005, format="%.3f")

# 4. Processamento Analítico (Matemática Rigorosa)
g = 9.81
r_m = r_mm / 1000
vol_m3 = (4/3) * math.pi * (r_m**3)
rho_e = (m_g / 1000) / vol_m3

# Forças (Newtons)
peso_N = (m_g / 1000) * g
empuxo_N = rho_l * vol_m3 * g

# Cinemática
v_terminal = dist_m / t_s
viscosidade_aparente = (2 * (r_m**2) * g * (rho_e - rho_l)) / (9 * v_terminal) if v_terminal > 0 else 0

# Correção de Efeito de Parede (Ladenburg)
raio_proveta_mm = 30.65
fator_ladenburg = 1 + 2.1 * (r_mm / raio_proveta_mm)
v_corrigida = v_terminal * fator_ladenburg
viscosidade_corrigida = viscosidade_aparente / fator_ladenburg if fator_ladenburg > 0 else 0

is_floating = rho_e < rho_l

# 5. Interface Principal
st.title("Laboratório Digital - Lei de Stokes")
st.markdown("---")

col_dados, col_visual = st.columns([3, 2])

with col_dados:
    st.subheader("Controle de Ensaio")
    
    # Botões de Ação Horizontal
    btn_col1, btn_col2 = st.columns([1, 1])
    with btn_col1:
        if st.button("🚀 LANÇAR ESFERA", use_container_width=True, type="primary"):
            st.session_state.lancado = True
    with btn_col2:
        st.link_button("📹 Acessar Vídeos do Ensaio", "https://uniasselvi01-my.sharepoint.com/:f:/g/personal/7116971_aluno_uniasselvi_com_br/IgAp_RKiqd3HQI4cu6ozT_irAZtbwY9ujDkYZVANoP2A51I?e=E6TI3o", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder = st.empty()
    
    if not st.session_state.lancado:
        placeholder.info("Aguardando lançamento. Os dados de metrologia serão exibidos após o término da queda.")
    else:
        with placeholder.container():
            if is_floating:
                st.error("⚠️ FALHA: A densidade da esfera é inferior à do fluido. Empuxo superior ao Peso.")
            else:
                with st.spinner(f"Monitorando cinemática de queda... Aguardando {t_s}s."):
                    time.sleep(t_s)
                
                st.success("✅ Fundo atingido. Equilíbrio de Stokes calculado.")
                m1, m2, m3 = st.columns(3)
                m1.metric("VEL. CORRIGIDA", f"{v_corrigida:.4f} m/s")
                m2.metric("VISCOSIDADE REAL", f"{viscosidade_corrigida:.4f} Pa·s")
                m3.metric("FATOR LADENBURG", f"{fator_ladenburg:.3f}")
                
                # Memória de Cálculo Expansível e Completa
                with st.expander("📊 Acessar Memória de Cálculo Completa", expanded=True):
                    st.markdown("**1. Parâmetros Volumétricos e Balanço de Forças:**")
                    st.latex(rf"V_e = \frac{{4}}{{3}} \pi r^3 = {vol_m3:.3e} \, m^3")
                    st.latex(rf"\rho_e = \frac{{m}}{{V_e}} = {rho_e:.1f} \, kg/m^3")
                    st.latex(rf"Peso \, (P) = m \cdot g = {peso_N:.4e} \, N")
                    st.latex(rf"Empuxo \, (E) = \rho_L \cdot V_e \cdot g = {empuxo_N:.4e} \, N")

                    st.markdown("**2. Viscosidade Aparente (Sem Correção):**")
                    st.latex(rf"v_{{medida}} = \frac{{d}}{{t}} = \frac{{{dist_m}}}{{{t_s}}} = {v_terminal:.4f} \, m/s")
                    st.latex(rf"\eta_{{aparente}} = \frac{{2r^2 g (\rho_e - \rho_L)}}{{9 v_{{medida}}}} = {viscosidade_aparente:.4f} \, Pa \cdot s")

                    st.markdown("**3. Efeito de Parede (Fator de Ladenburg):**")
                    st.info("O raio da proveta (30,65 mm) freia o escoamento ao redor da esfera. A correção é obrigatória.")
                    st.latex(rf"F_L = 1 + 2,1 \left(\frac{{r}}{{R_{{proveta}}}}\right) = 1 + 2,1 \left(\frac{{{r_mm:.2f}}}{{30,65}}\right) = {fator_ladenburg:.4f}")
                    st.latex(rf"v_{{corrigida}} = v_{{medida}} \cdot F_L = {v_corrigida:.4f} \, m/s")
                    
                    st.markdown("**4. Viscosidade Dinâmica Corrigida ($\eta_c$):**")
                    st.latex(rf"\eta_c = \frac{{\eta_{{aparente}}}}{{F_L}} = \mathbf{{{viscosidade_corrigida:.4f} \, Pa \cdot s}}")

with col_visual:
    js_autoplay = "true" if (st.session_state.lancado and not is_floating) else "false"
    
    html_content = f"""
    <div style="display: flex; flex-direction: column; align-items: center; background: #161b22; padding: 20px; border-radius: 10px; height: 100%;">
        <div style="color: #8b949e; margin-bottom: 15px; font-family: sans-serif; font-size: 14px;">Proveta Graduada</div>
        <canvas id="stokesCanvas" width="220" height="420" style="background: #0d1117;"></canvas>
        <div id="status" style="margin-top:15px; color:#58a6ff; font-family:sans-serif; font-weight:bold;">
            {('AQUISIÇÃO DE DADOS...' if st.session_state.lancado and not is_floating else 'SISTEMA PRONTO')}
        </div>
    </div>
    <script>
        const canvas = document.getElementById('stokesCanvas');
        const ctx = canvas.getContext('2d');
        
        const r_px = Math.min({r_mm} * 2.5, 30);
        const y_start = 30;
        const y_final = 390 - r_px;
        let y = y_start;
        
        const duration = {t_s} * 1000; 
        let startTime = null;

        function drawCylinder() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            ctx.strokeStyle = "rgba(255,255,255,0.6)";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(60, 10); ctx.lineTo(60, 400); 
            ctx.lineTo(160, 400);                    
            ctx.lineTo(160, 10);                     
            ctx.stroke();

            ctx.fillStyle = "rgba(0, 188, 212, 0.25)";
            ctx.fillRect(61.5, 20, 97, 378.5);
            
            ctx.beginPath();
            ctx.moveTo(61.5, 20); ctx.lineTo(158.5, 20);
            ctx.strokeStyle = "rgba(0, 188, 212, 0.9)";
            ctx.lineWidth = 2;
            ctx.stroke();

            ctx.fillStyle = "#8b949e";
            ctx.font = "11px monospace";
            ctx.lineWidth = 1;
            const marks = 5;
            for(let i=0; i<=marks; i++) {{
                let mark_y = 390 - (i * (370/marks));
                let mark_val = (i * ({dist_m}/marks)).toFixed(3);
                
                ctx.beginPath(); ctx.moveTo(60, mark_y); ctx.lineTo(70, mark_y); ctx.stroke();
                ctx.beginPath(); ctx.moveTo(150, mark_y); ctx.lineTo(160, mark_y); ctx.stroke();
                
                if (i !== 0) ctx.fillText(mark_val + "m", 5, mark_y + 4);
                else ctx.fillText("0.000m", 5, mark_y + 4);
            }}

            ctx.beginPath();
            ctx.arc(110, y, r_px, 0, Math.PI*2);
            ctx.fillStyle = "#f08080"; 
            ctx.fill();
            
            ctx.beginPath();
            ctx.arc(110 - r_px*0.3, y - r_px*0.3, r_px*0.2, 0, Math.PI*2);
            ctx.fillStyle = "rgba(255,255,255,0.4)";
            ctx.fill();
        }}

        function anim(timestamp) {{
            if (!startTime) startTime = timestamp;
            const progress = (timestamp - startTime) / duration;
            
            if (progress < 1) {{
                y = y_start + (y_final - y_start) * progress;
                drawCylinder();
                requestAnimationFrame(anim);
            }} else {{
                y = y_final;
                drawCylinder();
                document.getElementById('status').innerText = 'FUNDO ATINGIDO';
                document.getElementById('status').style.color = '#3fb950';
            }}
        }}

        drawCylinder();
        
        if({js_autoplay}) {{
            requestAnimationFrame(anim);
        }}
    </script>
    """
    components.html(html_content, height=520)

if st.session_state.lancado:
    st.session_state.lancado = False
