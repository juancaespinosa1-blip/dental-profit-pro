import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONFIGURACIÓN DE NIVEL EMPRESARIAL ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"

if "supabase" not in st.session_state:
    st.session_state.supabase = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit Premier", layout="wide")

# --- ESTILO CSS OSCURO ---
st.markdown("""
    <style>
    .stApp { background-color: #0F172A; color: #F8FAFC; }
    [data-testid="stMetric"] { background-color: #1E293B; border: 1px solid #334155; padding: 20px; border-radius: 12px; }
    [data-testid="stMetricValue"] { color: #38BDF8; font-weight: 800; }
    .stButton>button { background: #3B82F6; color: white; border-radius: 8px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIN ---
if 'user' not in st.session_state:
    st.title("🦷 DentalProfit Premier")
    tab_log, tab_reg = st.tabs(["🔑 Acceso", "🚀 Registro"])
    with tab_log:
        e = st.text_input("Email")
        p = st.text_input("Contraseña", type="password")
        if st.button("ENTRAR"):
            try:
                res = st.session_state.supabase.auth.sign_in_with_password({"email": e, "password": p})
                if res.user: 
                    st.session_state.user = res
                    st.rerun()
            except: st.error("Fallo de acceso.")
    with tab_reg:
        ne = st.text_input("Nuevo Email")
        np = st.text_input("Nueva Contraseña", type="password")
        if st.button("CREAR CUENTA"):
            try:
                st.session_state.supabase.auth.sign_up({"email": ne, "password": np})
                st.success("Cuenta creada. Ya puede entrar.")
            except: st.error("Error al registrar.")
else:
    u_id = st.session_state.user.user.id
    
    # --- MENÚ ---
    menu = st.sidebar.selectbox("MÓDULO", ["📊 Dashboard", "📦 Inventario", "🏢 Gastos"])
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()

    # Carga de datos
    try:
        res = st.session_state.supabase.table("inventario").select("*").eq("user_id", u_id).execute()
        df_inv = pd.DataFrame(res.data)
    except: df_inv = pd.DataFrame()

    if menu == "📊 Dashboard":
        st.title("📊 Análisis de Negocio")
        
        if df_inv.empty or len(df_inv.columns) < 2:
            st.warning("⚠️ Primero llena tu inventario en el módulo correspondiente.")
        else:
            # Asegurar que las columnas existen antes de calcular
            for col in ["precio_compra", "cantidad_en_envase"]:
                if col not in df_inv.columns: df_inv[col] = 0.0
            
            df_inv['costo_u'] = df_inv['precio_compra'].astype(float) / df_inv['cantidad_en_envase'].astype(float).replace(0,1)
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.subheader("Calculadora")
                sel = st.multiselect("Materiales", df_inv['material'].unique())
                precio_v = st.number_input("Precio Venta ($)", min_value=0.0)
                
                if sel and precio_v > 0:
                    costo_m = df_inv[df_inv['material'].isin(sel)]['costo_u'].sum()
                    utilidad = precio_v - costo_m
                    st.metric("GANANCIA", f"${utilidad:,.2f}")
                    st.metric("MARGEN", f"{(utilidad/precio_v)*100:.1f}%")
            
            with c2:
                if sel and precio_v > 0:
                    # Gráfico nativo de Streamlit (No requiere librerías extras)
                    chart_data = pd.DataFrame({
                        'Categoría': ['Costo', 'Ganancia'],
                        'Monto': [costo_mat, utilidad]
                    })
                    st.bar_chart(data=chart_data, x='Categoría', y='Monto')

    elif menu == "📦 Inventario":
        st.title("📦 Gestión de Materiales")
        if df_inv.empty:
            df_inv = pd.DataFrame(columns=["material", "precio_compra", "cantidad_en_envase", "unidad"])
        
        df_ed = st.data_editor(df_inv, num_rows="dynamic", use_container_width=True,
                               column_config={"user_id": None, "id": None, "created_at": None})
        
        if st.button("GUARDAR EN LA NUBE"):
            datos = df_ed.to_dict(orient='records')
            for d in datos: d['user_id'] = u_id
            st.session_state.supabase.table("inventario").upsert(datos).execute()
            st.success("Sincronizado.")
            st.rerun()
