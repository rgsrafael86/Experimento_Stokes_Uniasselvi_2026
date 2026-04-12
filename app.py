import streamlit as st
import math

# Configuração da Página
st.set_page_config(page_title="Ensaio de Stokes", layout="centered")
st.title("Calculadora - Viscosidade (Lei de Stokes)")
st.markdown("---")

# Entradas de Dados (Sidebar)
st.sidebar.header("Parâmetros do Experimento")
r_mm = st.sidebar.number_input("Raio da Esfera (mm)", value=5.55, format="%.2f")
m_g = st.sidebar.number_input("Massa da Esfera (g)", value=5.60, format="%.2f")
rho_l = st.sidebar.number_input("Densidade do Fluido (kg/m³)", value=982.2, format="%.1f")
dist_m = st.sidebar.number_input("Distância de Queda (m)", value=0.30, format="%.3f")
t_s = st.sidebar.number_input("Tempo de Queda (s)", value=0.43, format="%.2f")

# Memória de Cálculo
r_m = r_mm / 1000
m_kg = m_g / 1000
vol_m3 = (4/3) * math.pi * (r_m ** 3)
rho_e = m_kg / vol_m3
v_ms = dist_m / t_s
g = 9.81

# Lei de Stokes
viscosidade = (2 * (r_m ** 2) * g * (rho_e - rho_l)) / (9 * v_ms)

# Painel de Resultados
st.subheader("Resultados Analíticos")
col1, col2 = st.columns(2)

with col1:
    st.metric(label="Volume da Esfera (m³)", value=f"{vol_m3:.2e}")
    st.metric(label="Velocidade Terminal (m/s)", value=f"{v_ms:.4f}")

with col2:
    st.metric(label="Densidade da Esfera (kg/m³)", value=f"{rho_e:.2f}")
    
st.markdown("---")
st.success(f"**Viscosidade Dinâmica ($\eta$):** {viscosidade:.4f} Pa.s")
