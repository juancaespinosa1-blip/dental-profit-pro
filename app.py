import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- 1. TUS LLAVES (PÉGALAS AQUÍ) ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"

# Conexión técnica
supabase: Client = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit Pro", layout="wide")

# --- 2. LÓGICA DE ACCESO (LOGIN) ---
def login_screen():
    st.title("🦷 DentalProfit Pro")
    st.markdown("### Acceso al Sistema de Gestión")
    
    tab1, tab2 = st.tabs(["Ingresar", "Crear Cuenta"])
    
    with tab1:
        email = st.text_input("Correo electrónico")
        pw = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión", type="primary"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": pw})
                st.session_state.user = res
                st.rerun()
            except:
                st.error("Correo o contraseña incorrectos")

    with tab2:
        new_email = st.text_input("Nuevo correo")
        new_pw = st.text_input("Nueva contraseña (mín. 6 caracteres)", type="password")
        if st.button("Registrar mi cuenta"):
            try:
                supabase.auth.sign_up({"email": new_email, "password": new_pw})
                st.success("¡Cuenta creada! Revisa tu email para confirmar y luego inicia sesión.")
            except:
                st.error("Error al registrar cuenta")

# --- 3. APLICACIÓN PRINCIPAL (EL PRODUCTO) ---
def main_app():
    user_id = st.session_state.user.user.id
    st.sidebar.title("Configuración")
    if st.sidebar.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        del st.session_state.user
        st.rerun()

    st.header("📊 Gestión de Costos e Inventario")

    # Cargar datos filtrados por el usuario logueado
    try:
        res = supabase.table("inventario").select("*").eq("user_id", user_id).execute()
        df = pd.DataFrame(res.data)
    except:
        df = pd.DataFrame(columns=["material", "precio", "cantidad", "unidad", "user_id"])

    # --- INVENTARIO ---
    st.subheader("1. Tu Base de Insumos")
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True, column_config={"user_id": None})
    
    if st.button("💾 Guardar Inventario"):
        # Preparamos los datos para que cada fila tenga el ID del usuario actual
        filas = df_editado.to_dict(orient='records')
        for f in filas:
            f['user_id'] = user_id
        
        supabase.table("inventario").upsert(filas).execute()
        st.success("Cambios guardados permanentemente.")

    # --- CALCULADORA ---
    st.divider()
    st.subheader("2. Calculadora de Procedimiento")
    if not df_editado.empty:
        col1, col2 = st.columns(2)
        with col1:
            procedimiento = st.text_input("Procedimiento", "Ej: Resina")
            precio_vta = st.number_input("Precio al paciente ($)", value=100.0)
            insumos = st.multiselect("Materiales utilizados", df_editado['material'].tolist())
        
        if insumos:
            df_sel = df_editado[df_editado['material'].isin(insumos)]
            # Evitamos división por cero
            costo_t = (df_sel['precio'] / df_sel['cantidad'].replace(0, 1)).sum()
            utilidad = precio_vta - costo_t
            
            with col2:
                st.metric("Costo de Materiales", f"${costo_t:.2f}")
                st.metric("Utilidad Estimada", f"${utilidad:.2f}", delta=f"{(utilidad/precio_vta)*100:.1f}% Margen")

# --- CONTROLADOR ---
if 'user' not in st.session_state:
    login_screen()
else:
    main_app()
