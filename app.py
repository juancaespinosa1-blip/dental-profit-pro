import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="DentalProfit Pro", layout="wide")

URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase = create_client(URL_SB, KEY_SB)

# Inicializar variables críticas para evitar NameError
if 'costo_hora' not in st.session_state:
    st.session_state.costo_hora = 30.0

# --- 2. AUTENTICACIÓN ---
if "user" not in st.session_state:
    st.title("🦷 Acceso DentalProfit")
    email_input = st.text_input("Correo electrónico")
    pass_input = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        try:
            res_auth = supabase.auth.sign_in_with_password({"email": email_input, "password": pass_input})
            st.session_state.user = res_auth
            st.rerun()
        except:
            st.error("Credenciales incorrectas")
    st.stop()

# Si llegamos aquí, el usuario existe
u_id = st.session_state.user.user.id

# --- 3. CARGA DE DATOS SEGUROS ---
try:
    # Usamos 'Inventario' con mayúscula como descubrimos antes
    response = supabase.table("Inventario").select("*").eq("user_id", u_id).execute()
    data_list = response.data if response.data else []
    df_global = pd.DataFrame(data_list)
except Exception as e:
    st.error(f"Error de conexión: {e}")
    df_global = pd.DataFrame()

# Asegurar columnas mínimas para que la calculadora no de NameError
columnas_necesarias = ["material", "precio_compra", "cantidad_total", "unidad"]
for col in columnas_necesarias:
    if col not in df_global.columns:
        df_global[col] = 0.0 if col != "material" and col != "unidad" else ""

# --- 4. INTERFAZ ---
st.sidebar.title("Menú Principal")
opcion = st.sidebar.radio("Ir a:", ["Calculadora", "Inventario", "Configuración"])

if opcion == "Calculadora":
    st.header
