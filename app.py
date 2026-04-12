import streamlit as st
import streamlit.components.v1 as components
import math

# Configuração de Interface Técnica
st.set_page_config(page_title="Simulador de Stokes - Engenharia", layout="wide")

# Estilização customizada para simular o Dashboard da imagem
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { font-size: 28px; color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

st.title("Simulador da Lei de Stokes")
st.caption("Análise de Viscosidade em Fluidos Newtonianos - Fenômenos de Transporte")

# --- BLOCO DE CÁLCULO (BACKEND PYTHON) ---
# Inputs via Sliders na base da página (conforme imagem)
col_in1, col_in2, col_in3 = st.columns(3)
with col_in1:
    r_mm = st.slider("Raio da Esfera (mm)", 1.0, 10.0, 3.0, 0.1)
    m_g = st.slider("Massa da Esfera (g)", 0.1, 10.0, 0.91, 0.01)
with col_in2:
    rho_l = st.slider("Densidade do Fluido (kg/m³)", 800.0, 1500.0, 982.2, 0.1)
    dist_m = st.slider("Distância de Queda (m)", 0.1, 1.0, 0.435, 0.005)
with col_in3:
    t_s = st.slider("Tempo de Queda (s)", 0.1, 5.0, 0.73, 0.01)

# Processamento Analítico
g = 9.81
r_m = r_mm / 1000
vol_m3 = (4/3) * math.pi * (r_m**3)
rho_e = (m_g / 1000) / vol_m3
v_terminal = dist_m / t_s
viscosidade = (2 * (r_m**2) * g * (rho_e - rho_l)) / (9 * v_terminal)

# --- EXIBIÇÃO DE KPIS (TOPO) ---
st.markdown("---")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("VESF (M/S)", f"{v_terminal:.4f}")
kpi2.metric("VISCOSIDADE (PA.S)", f"{viscosidade:.4f}")
kpi3.metric("DENS. ESF (KG/M³)", f"{rho_e:.2f}")

# --- COMPONENTE VISUAL (HTML5/CANVAS) ---
# Este bloco injeta o visual da proveta graduada
html_content = f"""
<div style="display: flex; flex-direction: column; align-items: center; background: #161b22; padding: 20px; border-radius: 15px;">
    <div style="color: #8b949e; margin-bottom: 10px;">Equilíbrio de Stokes calculado com sucesso.</div>
    <canvas id="stokesCanvas" width="200" height="400" style="border: 2px solid #30363d; background: #0d1117;"></canvas>
    <button onclick="startSim()" style="margin-top: 15px; padding: 10px 30px; background: #238636; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold;">Lançar Esfera</button>
    <div id="status" style="margin-top: 10px; color: #58a6ff; font-weight: bold;"></div>
</div>

<script>
    const canvas = document.getElementById('stokesCanvas');
    const ctx = canvas.getContext('2d');
    const status = document.getElementById('status');
    
    let y = 50;
    let animating = false;
    const v = {v_terminal} * 50; // Escala de animação
    const r = {r_mm} * 2;

    function draw() {{
        ctx.clearRect(0, 0, 200, 400);
        
        // Desenha Líquido
        ctx.fillStyle = "rgba(0, 188, 212, 0.2)";
        ctx.fillRect(50, 20, 100, 360);
        
        // Graduação
        ctx.strokeStyle = "#30363d";
        for(let i=0; i<=5; i++) {{
            let h = 380 - (i * 72);
            ctx.beginPath(); ctx.moveTo(40, h); ctx.lineTo(60, h); ctx.stroke();
            ctx.fillStyle = "#8b949e";
            ctx.fillText(((i * {dist_m}/5).toFixed(2) + "m"), 10, h+5);
        }}

        // Esfera
        ctx.beginPath();
        ctx.arc(100, y, r, 0, Math.PI*2);
        ctx.fillStyle = "#f08080";
        ctx.fill();
        ctx.stroke();
    }}

    function startSim() {{
        if(animating) return;
        y = 50;
        animating = true;
        status.innerText = "";
        animate();
    }}

    function animate() {{
        if(y < 380 - r) {{
            y += v;
            draw();
            requestAnimationFrame(animate);
        }} else {{
            animating = false;
            status.innerText = "FUNDO ATINGIDO";
        }}
    }}
    draw();
</script>
"""
components.html(html_content, height=550)

# --- DETALHAMENTO TÉCNICO (MEMÓRIA DE CÁLCULO) ---
with st.expander("Visualizar Memória de Cálculo (Rigor de Engenharia)"):
    st.markdown(f"""
    **1. Volume da Esfera ($V_e$):**
    $$V_e = \\frac{{4}}{{3}} \pi r^3 = \\frac{{4}}{{3}} \pi ({r_m:.6f})^3 = {vol_m3:.4e} \, m^3$$

    **2. Densidade da Esfera ($\\rho_e$):**
    $$\\rho_e = \\frac{{m}}{{V_e}} = \\frac{{{m_g/1000:.6f}}}{{{vol_m3:.4e}}} = {rho_e:.2f} \, kg/m^3$$

    **3. Velocidade de Queda ($v$):**
    $$v = \\frac{{d}}{{t}} = \\frac{{{dist_m}}}{{{t_s}}} = {v_terminal:.4f} \, m/s$$

    **4. Viscosidade Dinâmica ($\\eta$):**
    $$\\eta = \\frac{{2 r^2 g (\\rho_e - \\rho_l)}}{{9 v}} = {viscosidade:.4f} \, Pa \cdot s$$
    """)
