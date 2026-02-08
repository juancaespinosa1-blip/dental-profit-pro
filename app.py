import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DentalProfit Pro", layout="wide")

URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase = create_client(URL_SB, KEY_SB)

if "user" not in st.session_state:
    st.title("🦷 Acceso DentalProfit")
    e = st.text_input("Email")
    p = st.text_input("Clave", type="password")
    if st.button("Iniciar sesión"):
        try:
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user = res
            st.rerun()
        except: st.error("Error de acceso")
    st.stop()

u_id = st.session_state.user.user.id

# --- CARGA DESDE 'Inventario' (CON MAYÚSCULA) ---
try:
    # Cambiado a 'Inventario' para coincidir con tu esquema
    res = supabase.table("Inventario").select("*").eq("user_id", u_id).execute()
    df = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error crítico de tabla: {e}")
    df = pd.DataFrame()

if df.empty:
    # Estructura base si no hay datos
    df = pd.DataFrame(columns=["material", "precio_compra", "cantidad_total", "unidad"])
    df.loc[0] = ["Ejemplo", 0.0, 1.0, "u"]

# --- LÓGICA DE CÁLCULO ---
st.sidebar.title("DentalProfit Pro")
menu = st.sidebar.radio("Ir a:", ["Calculadora", "Inventario", "Configuración"])

if menu == "Calculadora":
    st.header("🧮 Calculadora de Costos por Porción")
    
    if 'costo_hora' not in st.session_state: st.session_state.costo_hora = 30.0
    
    c1, c2 = st.columns(2)
    with c1:
        mins = st.number_input("Minutos de sillón", 5, 300, 45)
        margen = st.slider("Margen %", 50, 300, 100)
    
    with c2:
        mats_list = df["material"].dropna().unique().tolist()
        sel = st.multise
