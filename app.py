import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DentalProfit Pro", layout="wide")

URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase = create_client(URL_SB, KEY_SB)

# --- LOGIN ---
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

# --- CARGA DE DATOS SEGURA ---
try:
    # IMPORTANTE: Nombre de tabla 'Inventario' con mayúscula como detectamos antes
    response = supabase.table("Inventario").select("*").eq("user_id", u_id).execute()
    # Acceso seguro a los datos
    raw_data = response.data if hasattr(response, 'data') else []
    df = pd.DataFrame(raw_data)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df = pd.DataFrame()

# VALIDACIÓN DE COLUMNAS (Evita el AttributeError)
required_cols = ["material", "precio_compra", "cantidad_total", "unidad"]
for col in required_cols:
    if col not in df.columns:
        df[col] = 0.0 if col != "material" and col != "unidad" else ""

# --- LÓGICA DE INTERFAZ ---
st.sidebar.title("DentalProfit Pro")
menu = st.sidebar.radio("Ir a:", ["Calculadora", "Inventario", "Configuración"])

if menu == "Calculadora":
    st.header("🧮 Calculadora de Costos (Estandar de Oro)")
    
    if 'costo_hora' not in st.session_state: 
        st.session_state.costo_hora = 30.0
    
    col1, col2
