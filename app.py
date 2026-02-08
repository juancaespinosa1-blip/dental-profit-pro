import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONEXIÓN ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase: Client = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit Pro", layout="wide")

# --- LOGIN ---
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
            except: st.error("Error: Revisa tus datos")
    with t2:
        ne = st.text_input("Nuevo Correo")
        np = st.text_input("Nuevo Password", type="password")
        if st.button("Crear Cuenta"):
            try:
                supabase.auth.sign_up({"email": ne, "password": np})
                st.success("¡Cuenta creada! Ya puedes ingresar.")
            except: st.error("Error al registrar")
else:
    # --- APP DE GROK (ESTRUCTURA ORIGINAL) ---
    user_id = st.session_state.user.user.id
    
    st.sidebar.title("Configuración")
    st.sidebar.write(f"Usuario: {st.session_state.user.user.email}")
    if st.sidebar.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        del st.session_state.user
        st.rerun()

    st.title("📊 Calculadora de Rentabilidad Dental")

    # 1. GASTOS FIJOS (Lógica de Grok)
    with st.expander("🏢 Configurar Gastos Fijos Mensuales", expanded=True):
        c1, c2, c3 = st.columns(3)
        alquiler = c1.number_input("Alquiler/Local", value=0.0)
        personal = c2.number_input("Personal/Asistentes", value=0.0)
        servicios = c3.number_input("Servicios y Otros", value=0.0)
        
        total_fijos = alquiler + personal + servicios
        st.info(f"Total Gastos Fijos: ${total_fijos:.2f}")

    # 2. TABLA DE INSUMOS (Columnas de Grok)
    st.header("📦 Inventario de Insumos")
    try:
        res = supabase.table("inventario").select("*").eq("user_id", user_id).execute()
        df = pd.DataFrame(res.data)
    except:
        df = pd.DataFrame()

    if df.empty:
        df = pd.DataFrame([{"material": "", "precio_compra": 0.0, "unidades_envase": 1.0, "costo_por_unidad": 0.0, "user_id": user_id}])

    # Calculamos el costo por unidad automáticamente (Lógica Grok)
    df['costo_por_unidad'] = df['precio_compra'] / df['unidades_envase'].replace(0, 1)

    df_editado = st.data_editor(
        df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "user_id": None, "id": None, 
            "costo_por_unidad": st.column_config.Number_column("Costo por Uso ($)", disabled=True)
        }
    )
    
    if st.button("💾 Guardar Cambios en la Nube"):
        datos = df_editado.to_dict(orient='records')
        for d in datos: d['user_id'] = user_id
        supabase.table("inventario").upsert(datos).execute()
        st.success("¡Datos guardados con éxito!")

    # 3. CALCULADORA DE PROCEDIMIENTOS (Escandallo)
    st.divider()
    st.header("🧪 Escandallo de Procedimiento")
    
    if not df_editado.empty and df_editado.iloc[0]['material'] != "":
        seleccion = st.multiselect("Selecciona los materiales usados:", df_editado['material'].unique())
        
        if seleccion:
            insumos_usados = df_editado[df_editado['material'].isin(seleccion)]
            costo_materiales = insumos_usados['costo_por_unidad'].sum()
            
            st.subheader("Análisis de Precio")
            col_a, col_b = st.columns(2)
            pvp = col_a.number_input("Precio de Venta al Público ($)", value=0.0)
            margen_deseado = col_b.slider("% Margen deseado", 0, 100, 30)
            
            utilidad = pvp - costo_materiales
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Costo Insumos", f"${costo_materiales:.2f}")
            m2.metric("Utilidad Bruta", f"${utilidad:.2f}")
            if pvp > 0:
                m3.metric("Margen Real", f"{(utilidad/pvp)*100:.1f}%")

            # Sugerencia de precio según Grok
            sugerido = costo_materiales / (1 - (margen_deseado/100)) if margen_deseado < 100 else 0
            st.warning(f"💡 Para ganar el {margen_deseado}%, deberías cobrar al menos: **${sugerido:.2f}**")
