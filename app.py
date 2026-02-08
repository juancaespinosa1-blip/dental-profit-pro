import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE NIVEL EMPRESARIAL ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"

if "supabase" not in st.session_state:
    st.session_state.supabase = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit Premier", layout="wide", page_icon="🦷")

# --- ESTILO CSS DE ALTO IMPACTO ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    [data-testid="stMetric"] { background-color: #1E293B; border: 1px solid #334155; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    [data-testid="stMetricValue"] { color: #38BDF8; font-weight: 800; }
    .stButton>button { background: linear-gradient(90deg, #3B82F6 0%, #2563EB 100%); color: white; border: none; font-weight: 600; border-radius: 8px; transition: 0.3s; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.5); }
    .stDataFrame { border: 1px solid #334155; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'user' not in st.session_state:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; color: #38BDF8; font-size: 3rem;'>🦷 DentalProfit</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94A3B8;'>Sistema Inteligente de Rentabilidad Odontológica</p>", unsafe_allow_html=True)
        
        tab_log, tab_reg = st.tabs(["🔑 Acceso Seguro", "🚀 Nueva Licencia"])
        with tab_log:
            e = st.text_input("Usuario (Email)")
            p = st.text_input("Contraseña", type="password")
            if st.button("AUTENTICAR", use_container_width=True):
                try:
                    res = st.session_state.supabase.auth.sign_in_with_password({"email": e, "password": p})
                    if res.user: 
                        st.session_state.user = res
                        st.rerun()
                except: st.error("Error de autenticación.")
        with tab_reg:
            ne = st.text_input("Email Corporativo")
            np = st.text_input("Contraseña de Seguridad", type="password")
            if st.button("REGISTRAR CLÍNICA", use_container_width=True):
                try:
                    st.session_state.supabase.auth.sign_up({"email": ne, "password": np})
                    st.success("Cuenta creada. Por favor, inicie sesión.")
                except: st.error("Error en el registro.")
else:
    u_id = st.session_state.user.user.id
    
    # --- DASHBOARD ---
    with st.sidebar:
        st.markdown("<h2 style='color: #38BDF8;'>Premier Panel</h2>", unsafe_allow_html=True)
        menu = st.selectbox("MÓDULO", ["📊 Inteligencia de Negocio", "📦 Gestión de Stock", "🏢 Estructura de Costos"])
        st.divider()
        st.caption(f"Usuario: {st.session_state.user.user.email}")
        if st.button("Cerrar Sistema"):
            st.session_state.clear()
            st.rerun()

    # Carga de datos optimizada
    try:
        res = st.session_state.supabase.table("inventario").select("*").eq("user_id", u_id).execute()
        df_inv = pd.DataFrame(res.data)
    except: df_inv = pd.DataFrame()

    if menu == "📊 Inteligencia de Negocio":
        st.markdown("<h1>📊 Dashboard Ejecutivo</h1>", unsafe_allow_html=True)
        
        if df_inv.empty:
            st.info("💡 Bienvenido. Comience registrando sus materiales en el módulo de Stock.")
            # Demo chart
            fig = px.pie(names=['Insumos', 'Ganancia Esperada'], values=[40, 60], hole=0.7,
                         color_discrete_sequence=['#1E293B', '#38BDF8'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig, use_container_width=True)
        else:
            df_inv['costo_u'] = df_inv['precio_compra'].astype(float) / df_inv['cantidad_en_envase'].astype(float).replace(0,1)
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown("### 🧬 Calculador de Margen")
                sel = st.multiselect("Materiales del Procedimiento", df_inv['material'].unique())
                precio_v = st.number_input("Precio de Venta ($)", min_value=0.0, step=10.0)
                
                if sel and precio_v > 0:
                    costo_m = df_inv[df_inv['material'].isin(sel)]['costo_u'].sum()
                    utilidad = precio_v - costo_m
                    st.metric("GANANCIA NETA", f"${utilidad:,.2f}", delta=f"{((utilidad/precio_v)*100):.1f}% MARGEN")
            
            with c2:
                if sel and precio_v > 0:
                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = (utilidad/precio_v)*100,
                        title = {'text': "Eficiencia del Tratamiento (%)"},
                        gauge = {'axis': {'range': [0, 100]},
                                 'bar': {'color': "#38BDF8"},
                                 'steps' : [
                                     {'
