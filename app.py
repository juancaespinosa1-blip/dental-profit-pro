import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.express as px

# --- CONEXIÓN DIRECTA ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"

# Inicializar cliente solo una vez
if "supabase" not in st.session_state:
    st.session_state.supabase = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit Pro", layout="wide")

# --- LÓGICA DE LOGIN CORREGIDA (SIN DOBLE CLIC) ---
if 'user' not in st.session_state:
    st.title("🦷 DentalProfit Pro")
    t1, t2 = st.tabs(["🔐 Ingresar", "📝 Registrar"])
    
    with t1:
        e = st.text_input("Correo", key="login_email")
        p = st.text_input("Contraseña", type="password", key="login_pw")
        if st.button("Iniciar Sesión", use_container_width=True):
            try:
                # Forzar la respuesta antes de seguir
                res = st.session_state.supabase.auth.sign_in_with_password({"email": e, "password": p})
                if res.user:
                    st.session_state.user = res
                    st.rerun()
            except:
                st.error("Credenciales incorrectas. Revisa tu correo y contraseña.")

    with t2:
        ne = st.text_input("Correo Nuevo", key="reg_email")
        np = st.text_input("Contraseña Nueva", type="password", key="reg_pw")
        if st.button("Crear Cuenta", use_container_width=True):
            try:
                st.session_state.supabase.auth.sign_up({"email": ne, "password": np})
                st.success("¡Cuenta creada! Ya puedes ingresar en la otra pestaña.")
            except:
                st.error("No se pudo crear la cuenta.")
else:
    # --- APP COMPLETA TRAS LOGIN ---
    u_id = st.session_state.user.user.id
    
    st.sidebar.title("MENU")
    menu = st.sidebar.radio("Opciones:", ["📊 Dashboard y Gráficos", "📦 Mi Inventario", "🏢 Gastos Mensuales"])

    # Cargar datos
    try:
        res = st.session_state.supabase.table("inventario").select("*").eq("user_id", u_id).execute()
        df_inv = pd.DataFrame(res.data)
    except:
        df_inv = pd.DataFrame()

    if 'fijos' not in st.session_state:
        st.session_state.fijos = {"Alquiler": 0.0, "Personal": 0.0, "Servicios": 0.0, "Otros": 0.0}

    # --- CONTENIDO ---
    if menu == "📊 Dashboard y Gráficos":
        st.title("📊 Análisis de Rentabilidad")
        
        if not df_inv.empty and "precio_compra" in df_inv.columns:
            df_inv['costo_u'] = df_inv['precio_compra'] / df_inv['cantidad_en_envase'].replace(0,1)
            
            with st.container(border=True):
                st.subheader("Calculadora de Tratamiento")
                c1, c2 = st.columns([2, 1])
                with c1:
                    sel = st.multiselect("Materiales:", df_inv['material'].unique())
                    precio_v = st.number_input("Precio Venta ($)", min_value=0.0)
                
                if sel and precio_v > 0:
                    costo_mat = df_inv[df_inv['material'].isin(sel)]['costo_u'].sum()
                    utilidad = precio_v - costo_mat
                    
                    with c2:
                        st.metric("Utilidad", f"${utilidad:,.2f}")
                        st.metric("Margen", f"{(utilidad/precio_v)*100:.1f}%")
                    
                    fig = px.pie(values=[costo_mat, utilidad], names=["Costo", "Ganancia"],
                                 hole=0.4, color_discrete_sequence=["#FF4B4B", "#00CC96"])
                    st.plotly_chart(fig)

    elif menu == "📦 Mi Inventario":
        st.header("📦 Inventario")
        if df_inv.empty:
            df_inv = pd.DataFrame(columns=["material", "precio_compra", "cantidad_en_envase", "unidad"])
            df_inv.loc[0] = ["", 0.0, 1.0, "u"]

        df_ed = st.data_editor(df_inv, num_rows="dynamic", use_container_width=True,
                               column_config={"user_id": None, "id": None, "created_at": None})
        
        if st.button("💾 Guardar Datos"):
            datos = df_ed.to_dict(orient='records')
            for d in datos: d['user_id'] = u_id
            st.session_state.supabase.table("inventario").upsert(datos).execute()
            st.success("Guardado.")
            st.rerun()

    elif menu == "🏢 Gastos Mensuales":
        st.header("🏢 Gastos Fijos")
        for k in st.session_state.fijos.keys():
            st.session_state.fijos[k] = st.number_input(f"{k}", value=st.session_state.fijos[k])

    st.sidebar.divider()
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.clear()
        st.rerun()
