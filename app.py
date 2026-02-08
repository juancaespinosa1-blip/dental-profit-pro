import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 1. CONFIGURACIÓN CERO ERRORES
st.set_page_config(page_title="DentalProfit Pro", layout="wide")

URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase: Client = create_client(URL_SB, KEY_SB)

# 2. ACCESO DIRECTO
if "user" not in st.session_state:
    st.title("🦷 Acceso DentalProfit")
    e = st.text_input("Email")
    p = st.text_input("Clave", type="password")
    if st.button("Iniciar sesión"):
        try:
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user = res
            st.rerun()
        except: st.error("Error de credenciales")
    st.stop()

u_id = st.session_state.user.user.id

# 3. CARGA LIMPIA DE DATOS
if 'costo_hora' not in st.session_state:
    st.session_state.costo_hora = 28.50

# Traer datos directamente
res = supabase.table("inventario").select("*").eq("user_id", u_id).execute()
df = pd.DataFrame(res.data)

# Si está vacío, crear estructura con los nombres correctos
if df.empty:
    df = pd.DataFrame(columns=["material", "precio_compra", "cantidad_total", "unidad"])
    df.loc[0] = ["Resina Ejemplo", 60.0, 4.0, "g"]

# 4. INTERFAZ
menu = st.sidebar.radio("Menú", ["Calculadora", "Inventario", "Configuración"])

if menu == "Calculadora":
    st.header("🧮 Calculadora de Precio Real (Estandar de Oro)")
    
    col1, col2 = st.columns(2)
    with col1:
        minutos = st.number_input("Minutos en sillón", 5, 300, 45)
        margen = st.slider("Margen de ganancia %", 50, 300, 100)
    
    with col2:
        st.subheader("Insumos")
        seleccionados = st.multiselect("Materiales:", df["material"].tolist())
        costo_mats = 0.0
        
        for m in seleccionados:
            # Extraer fila de forma segura
            row = df[df["material"] == m].iloc[0]
            p_envase = float(row["precio_compra"])
            c_envase = float(row["cantidad_total"])
            
            # Cálculo de porción
            costo_unitario = p_envase / c_envase if c_envase > 0 else 0
            cant_usada = st.number_input(f"Cantidad usada de {m} ({row['unidad']})", 0.0, float(c_envase)*2, 0.1, key=f"k_{m}")
            costo_mats += cant_usada * costo_unitario

    # Resultados
    costo_personal = (minutos / 60) * st.session_state.costo_hora
    cost
