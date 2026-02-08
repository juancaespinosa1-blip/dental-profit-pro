import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- 1. TUS LLAVES (ASEGÚRATE DE QUE SEAN LAS CORRECTAS) ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"

supabase: Client = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit Pro", layout="wide")

# --- LÓGICA DE ACCESO ---
if 'user' not in st.session_state:
    st.title("🦷 DentalProfit Pro")
    tab1, tab2 = st.tabs(["Ingresar", "Registrar"])
    with tab1:
        e = st.text_input("Correo")
        p = st.text_input("Password", type="password")
        if st.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user = res
                st.rerun()
            except: st.error("Datos incorrectos")
    with tab2:
        ne = st.text_input("Nuevo Correo")
        np = st.text_input("Nuevo Password", type="password")
        if st.button("Crear Cuenta"):
            try:
                supabase.auth.sign_up({"email": ne, "password": np})
                st.success("Cuenta creada. Ya puedes Ingresar.")
            except: st.error("Error al crear")
else:
    # --- 2. EL SISTEMA QUE "DESAPARECIÓ" ---
    user_id = st.session_state.user.user.id
    
    st.sidebar.write(f"Sesión: {st.session_state.user.user.email}")
    if st.sidebar.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        del st.session_state.user
        st.rerun()

    st.header("📊 Gestión de Inventario y Costos")

    # Intentar cargar datos de la tabla 'inventario'
    try:
        res = supabase.table("inventario").select("*").eq("user_id", user_id).execute()
        df = pd.DataFrame(res.data)
    except:
        df = pd.DataFrame(columns=["material", "precio", "cantidad", "unidad", "user_id"])

    if df.empty:
        df = pd.DataFrame([{"material": "", "precio": 0.0, "cantidad": 0.0, "unidad": "", "user_id": user_id}])

    st.subheader("1. Base de Insumos")
    df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True, column_config={"user_id": None, "id": None})
    
    if st.button("💾 Guardar Cambios"):
        filas = df_editado.to_dict(orient='records')
        for f in filas: f['user_id'] = user_id
        supabase.table("inventario").upsert(filas).execute()
        st.success("¡Datos guardados!")

    st.divider()
    st.subheader("2. Calculadora de Procedimientos")
    # (Aquí aparecerán los cálculos en cuanto llenes la tabla arriba)
    if not df_editado.empty and df_editado.iloc[0]['material'] != "":
        insumos = st.multiselect("Materiales para este tratamiento:", df_editado['material'].unique())
        if insumos:
            sel = df_editado[df_editado['material'].isin(insumos)]
            costo = (sel['precio'] / sel['cantidad'].replace(0,1)).sum()
            st.metric("Costo Total", f"${costo:.2f}")
