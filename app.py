import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONEXIÓN ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase: Client = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit Pro", layout="wide")

if 'user' not in st.session_state:
    st.title("🦷 DentalProfit Pro")
    t1, t2 = st.tabs(["Ingresar", "Registrar"])
    with t1:
        e = st.text_input("Correo")
        p = st.text_input("Password", type="password")
        if st.button("Entrar"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user = res
                st.rerun()
            except: st.error("Error de acceso")
    with t2:
        ne = st.text_input("Nuevo Correo")
        np = st.text_input("Nuevo Password", type="password")
        if st.button("Crear Cuenta"):
            try:
                supabase.auth.sign_up({"email": ne, "password": np})
                st.success("Cuenta creada. Ya puedes ingresar.")
            except: st.error("Error al registrar")
else:
    u_id = st.session_state.user.user.id
    st.sidebar.button("Cerrar Sesión", on_click=lambda: [supabase.auth.sign_out(), st.session_state.clear()])

    st.title("📊 Panel Dental Profit")

    # 1. GASTOS FIJOS
    with st.expander("🏢 Gastos Fijos", expanded=True):
        c1, c2, c3 = st.columns(3)
        alq = c1.number_input("Alquiler", 0.0)
        per = c2.number_input("Personal", 0.0)
        ser = c3.number_input("Servicios", 0.0)
        st.write(f"**Total Fijos:** ${alq + per + ser:,.2f}")

    # 2. INVENTARIO (Lógica Robusta)
    st.header("📦 Inventario")
    
    # Intentamos leer de Supabase, si falla creamos tabla vacía
    try:
        res = supabase.table("inventario").select("*").eq("user_id", u_id).execute()
        df = pd.DataFrame(res.data)
    except:
        df = pd.DataFrame()

    # Si no hay columnas correctas, las forzamos
    columnas_grok = ["material", "precio_compra", "unidades_envase", "unidad_medida"]
    if df.empty or not set(columnas_grok).issubset(df.columns):
        df = pd.DataFrame(columns=columnas_grok)
        df.loc[0] = ["", 0.0, 1.0, "u"]

    # Cálculo automático
    df['costo_por_uso'] = df['precio_compra'].astype(float) / df['unidades_envase'].astype(float).replace(0, 1)

    df_editado = st.data_editor(
        df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "user_id": None, "id": None, "created_at": None,
            "costo_por_uso": st.column_config.NumberColumn("Costo Uso ($)", format="$%.2f", disabled=True)
        }
    )
    
    if st.button("💾 Guardar Todo"):
        try:
            dict_data = df_editado.drop(columns=['costo_por_uso'], errors='ignore').to_dict(orient='records')
            for d in dict_data: d['user_id'] = u_id
            supabase.table("inventario").upsert(dict_data).execute()
            st.success("¡Guardado!")
        except Exception as err:
            st.error(f"Error al guardar: {err}. Asegúrate de haber corrido el SQL en Supabase.")

    # 3. CALCULADORA
    st.header("🧪 Escandallo")
    materiales = df_editado['material'].unique()
    sel = st.multiselect("Materiales usados:", [m for m in materiales if m])
    
    if sel:
        costo_t = df_editado[df_editado['material'].isin(sel)]['costo_por_uso'].sum()
        pvp = st.number_input("Precio Venta", 0.0)
        st.metric("Utilidad", f"${pvp - costo_t:,.2f}", delta=f"Costo: ${costo_t:,.2f}")
