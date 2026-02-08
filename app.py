import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN VISUAL ---
st.set_page_config(page_title="DentalProfit Pro", page_icon="🦷", layout="wide")

# Estilos para que no parezca un texto plano
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fc; }
    .main-header { color: #1E3A8A; font-size: 2rem; font-weight: bold; }
    .metric-container { background-color: white; padding: 15px; border-radius: 10px; border-left: 5px solid #3B82F6; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    </style>
""", unsafe_allow_html=True)

# --- 2. CONEXIÓN ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase = create_client(URL_SB, KEY_SB)

if 'costo_hora' not in st.session_state:
    st.session_state.costo_hora = 30.0

# --- 3. LOGIN VISUAL ---
if "user" not in st.session_state:
    st.markdown("<p class='main-header'>🦷 DentalProfit Pro</p>", unsafe_allow_html=True)
    with st.container():
        e = st.text_input("Correo electrónico")
        p = st.text_input("Contraseña", type="password")
        if st.button("INGRESAR AL SISTEMA", type="primary"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user = res
                st.rerun()
            except: st.error("Acceso denegado. Revisa tus datos.")
    st.stop()

# --- 4. CARGA DE DATOS ---
u_id = st.session_state.user.user.id
try:
    # Usando 'Inventario' con la I mayúscula que detectamos
    res = supabase.table("Inventario").select("*").eq("user_id", u_id).execute()
    df = pd.DataFrame(res.data)
except:
    df = pd.DataFrame()

columnas = ["material", "precio_compra", "cantidad_total", "unidad"]
for c in columnas:
    if c not in df.columns: df[c] = 0.0 if c != "material" and c != "unidad" else ""

# --- 5. INTERFAZ DE USUARIO ---
st.sidebar.title("MENÚ DENTALPROFIT")
opcion = st.sidebar.selectbox("Seleccione una sección:", ["📊 Calculadora de Ganancia", "📦 Gestión de Inventario", "⚙️ Configuración Clínica"])

if opcion == "📊 Calculadora de Ganancia":
    st.markdown("<p class='main-
