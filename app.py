import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from supabase import create_client, Client

# ───────────────────────────────────────────────
# CONFIGURACIÓN (Tus llaves ya integradas)
# ───────────────────────────────────────────────
st.set_page_config(page_title="DentalProfit Pro", page_icon="🦷", layout="wide")

URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase: Client = create_client(URL_SB, KEY_SB)

# Estilos de la interfaz
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fc; }
    .metric-card {
        background: white; padding: 1.4rem; border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06); border-left: 5px solid #0d6efd;
        margin: 0.8rem 0;
    }
    [data-testid="stMetricValue"] { font-size: 1.9rem !important; }
    </style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
# ACCESO (Protegiendo tus datos)
# ───────────────────────────────────────────────
if "user" not in st.session_state:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🦷 Acceso DentalProfit")
        e = st.text_input("Email")
        p = st.text_input("Clave de licencia", type="password")
        if st.button("Iniciar sesión", type="primary", use_container_width=True):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user = res
                st.rerun()
            except: st.error("Clave o usuario incorrecto")
    st.stop()

u_id = st.session_state.user.user.id

# ───────────────────────────────────────────────
# CARGA DE DATOS DESDE NUBE
# ───────────────────────────────────────────────
# Cargamos el inventario real de tu base de datos
res_inv = supabase.table("inventario").select("*").eq("user_id", u_id).execute()
df_db = pd.DataFrame(res_inv.data)

if df_db.empty:
    st.session_state.inventario = pd.DataFrame([
        {"Material": "Resina Filtek Supreme", "Precio": 68.50, "Cantidad": 4.0, "Unidad": "g"},
        {"Material": "Adhesivo Scotchbond", "Precio": 135.0, "Cantidad": 5.0, "Unidad": "ml"}
    ])
else:
    # Renombrar columnas para que coincidan con la lógica del código Grok
    st.session_state.inventario = df_db.rename(columns={
        "material": "Material", 
        "precio_compra": "Precio", 
        "cantidad_total": "Cantidad", 
        "unidad": "Unidad"
    })

# Cálculo del costo por unidad (la porción)
st.session_state.inventario["Costo por unidad"] = st.session_state.inventario["Precio"] / st.session_state.inventario["Cantidad"].replace(0, 1)

if 'costo_hora' not in st.session_state:
    st.session_state.costo_hora = 28.50

# ───────────────────────────────────────────────
# MENÚ LATERAL
# ───────────────────────────────────────────────
with st.sidebar:
    st.title("🦷 DentalProfit Pro")
    menu = st.radio("Menú", ["Dashboard", "Calculadora de precio", "Inventario", "Configuración"])
    if st.button("🚪 Cerrar sesión"):
        st.session_state.clear()
        st.rerun()

# ───────────────────────────────────────────────
# LÓGICA DE CÁLCULO (TU ESTÁNDAR DE ORO)
# ───────────────────────────────────────────────
if menu == "Dashboard":
    st.header("🏦 Panel de Control")
    m1, m2, m3 = st.columns(3)
    m1.metric("Costo por minuto", f"${st.session_state.costo_hora/60:.3f}")
    m2.metric("Insumos registrados", len(st.session_state.inventario))
    m3.metric("Costo hora operador", f"${st.session_state.costo_hora:.2f}")

    fig = px.pie(names=["Gastos Fijos", "Utilidad Esperada"], values=[st.session_state.costo_hora, 50], hole=0.4)
    st.plotly_chart(fig, use_container_width=True)

elif menu == "Calculadora de precio":
    st.header("🧮 Calculadora de precio realista")
    col1, col2 = st.columns([1,1])

    with col1
