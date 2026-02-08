import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONEXIÓN DIRECTA (YA CONFIGURADA) ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"

supabase: Client = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit Pro", layout="wide")

if 'user' not in st.session_state:
    st.title("🦷 DentalProfit")
    t1, t2 = st.tabs(["Ingresar", "Registrar"])
    with t1:
        e = st.text_input("Correo")
        p = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user = res
                st.rerun()
            except: st.error("Error al entrar. Revisa tus datos.")
    with t2:
        ne = st.text_input("Nuevo Correo")
        np = st.text_input("Nueva Contraseña", type="password")
        if st.button("Crear Cuenta"):
            try:
                supabase.auth.sign_up({"email": ne, "password": np})
                st.success("¡Cuenta creada! Ya puedes ingresar.")
            except: st.error("No se pudo crear la cuenta.")
else:
    u_id = st.session_state.user.user.id
    st.sidebar.button("Cerrar Sesión", on_click=lambda: [supabase.auth.sign_out(), st.session_state.clear()])

    st.title("📊 Mi Gestión Dental")

    # 1. CUADRO DE GASTOS FIJOS
    st.header("🏢 Gastos Fijos")
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        alquiler = c1.number_input("Alquiler", value=0.0)
        sueldos = c2.number_input("Sueldos", value=0.0)
        servicios = c3.number_input("Servicios", value=0.0)
        otros = c4.number_input("Otros Gastos", value=0.0)
        total_fijos = alquiler + sueldos + servicios + otros
        st.subheader(f"Total Gastos Fijos: ${total_fijos:,.2f}")

    st.divider()

    # 2. CUADRO DE INSUMOS
    st.header("📦 Inventario de Insumos")
    try:
        res = supabase.table("inventario").select("*").eq("user_id", u_id).execute()
        df = pd.DataFrame(res.data)
    except:
        df = pd.DataFrame()

    columnas = ["material", "precio_compra", "cantidad_en_envase", "unidad"]
    if df.empty or not set(columnas).issubset(df.columns):
        df = pd.DataFrame(columns=columnas)
        df.loc[0] = ["", 0.0, 1.0, "u"]

    df['costo_por_uso'] = df['precio_compra'].astype(float) / df['cantidad_en_envase'].astype(float).replace(0, 1)

    df_editado = st.data_editor(
        df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "user_id": None, "id": None, "created_at": None,
            "costo_por_uso": st.column_config.NumberColumn("Costo por Uso ($)", format="$%.2f", disabled=True)
        }
    )
    
    if st.button("💾 Guardar Todo"):
        try:
            datos_finales = df_editado.drop(columns=['costo_por_uso'], errors='ignore').to_dict(orient='records')
            for d in datos_finales: d['user_id'] = u_id
            supabase.table("inventario").upsert(datos_finales).execute()
            st.success("¡Datos guardados!")
        except Exception as e:
            st.error(f"Error al guardar. Verifica el SQL en Supabase: {e}")

    st.divider()

    # 3. CALCULADORA DE GANANCIA
    st.header("💰 Calculadora de Ganancia")
    lista_materiales = df_editado['material'].unique()
    seleccion = st.multiselect("Materiales usados en el tratamiento:", [m for m in lista_materiales if m])
    
    if seleccion:
        costo_mat = df_editado[df_editado['material'].isin(seleccion)]['costo_por_uso'].sum()
        col_1, col_2 = st.columns(2)
        precio_paciente = col_1.number_input("¿Cuánto le cobras al paciente? ($)", value=0.0)
        ganancia_neta = precio_paciente - costo_mat
        m1, m2, m3 = st.columns(3)
        m1.metric("Costo Insumos", f"${costo_mat:,.2f}")
        m2.metric("Ganancia Neta", f"${ganancia_neta:,.2f}")
        if precio_paciente > 0:
            porcentaje = (ganancia_neta / precio_paciente) * 100
            m3.metric("Margen de Ganancia", f"{porcentaje:.1f}%")
