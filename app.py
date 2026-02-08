import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONEXIÓN DIRECTA ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase: Client = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit Pro", layout="wide")

# --- SISTEMA DE ACCESO ---
if 'user' not in st.session_state:
    st.title("🦷 DentalProfit: Gestión Profesional")
    tab1, tab2 = st.tabs(["🔑 Ingresar", "📝 Registrarse"])
    with tab1:
        e = st.text_input("Correo")
        p = st.text_input("Contraseña", type="password")
        if st.button("Iniciar Sesión"):
            try:
                res = supabase.auth.sign_in_with_password({"email": e, "password": p})
                st.session_state.user = res
                st.rerun()
            except: st.error("Datos incorrectos. Verifica tu correo.")
    with tab2:
        ne = st.text_input("Tu Correo")
        np = st.text_input("Crea una Contraseña", type="password")
        if st.button("Crear mi Cuenta"):
            try:
                supabase.auth.sign_up({"email": ne, "password": np})
                st.success("¡Cuenta creada con éxito! Ahora puedes ingresar.")
            except: st.error("Error al registrar. Intenta con otro correo.")
else:
    # --- LA APP COMPLETA DE GROK ---
    u_id = st.session_state.user.user.id
    st.sidebar.title("👨‍⚕️ Panel Dental")
    st.sidebar.info(f"Conectado como: \n{st.session_state.user.user.email}")
    if st.sidebar.button("Cerrar Sesión"):
        supabase.auth.sign_out()
        del st.session_state.user
        st.rerun()

    st.title("📊 Análisis de Costos y Rentabilidad")

    # 1. GASTOS FIJOS
    st.header("1️⃣ Gastos Fijos Mensuales")
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        alq = c1.number_input("Alquiler", value=0.0)
        per = c2.number_input("Personal", value=0.0)
        ser = c3.number_input("Servicios", value=0.0)
        ot = c4.number_input("Otros", value=0.0)
        total_fijos = alq + per + ser + ot
        st.subheader(f"Total Gastos Fijos: ${total_fijos:,.2f}")

    st.divider()

    # 2. INVENTARIO (Lógica Grok de costos por unidad)
    st.header("2️⃣ Inventario de Materiales")
    try:
        res = supabase.table("inventario").select("*").eq("user_id", u_id).execute()
        df = pd.DataFrame(res.data)
    except:
        df = pd.DataFrame()

    if df.empty:
        df = pd.DataFrame([{"material": "", "precio_compra": 0.0, "unidades_envase": 1.0, "unidad_medida": "ml/gr/u", "user_id": u_id}])

    # Calculamos automáticamente el costo por uso
    df['costo_por_uso'] = df['precio_compra'] / df['unidades_envase'].replace(0, 1)

    df_editado = st.data_editor(
        df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "user_id": None, "id": None,
            "costo_por_uso": st.column_config.Number_column("Costo por Uso ($)", disabled=True, format="$%.2f")
        }
    )
    
    if st.button("💾 Guardar Inventario en la Nube"):
        final_data = df_editado.to_dict(orient='records')
        for d in final_data: d['user_id'] = u_id
        supabase.table("inventario").upsert(final_data).execute()
        st.success("¡Base de datos actualizada!")

    st.divider()

    # 3. CALCULADORA DE PROCEDIMIENTOS
    st.header("3️⃣ Escandallo de Tratamiento")
    if not df_editado.empty and df_editado.iloc[0]['material'] != "":
        sel = st.multiselect("Selecciona materiales para el procedimiento:", df_editado['material'].unique())
        
        if sel:
            items = df_editado[df_editado['material'].isin(sel)]
            costo_materiales = items['costo_por_uso'].sum()
            
            with st.container(border=True):
                col_izq, col_der = st.columns(2)
                pvp = col_izq.number_input("Precio que cobras al paciente ($)", value=0.0)
                utilidad = pvp - costo_materiales
                
                m1, m2, m3 = st.columns(3)
                m1.metric("Costo Insumos", f"${costo_materiales:,.2f}")
                m2.metric("Utilidad", f"${utilidad:,.2f}")
                if pvp > 0:
                    margen = (utilidad / pvp) * 100
                    m3.metric("Margen Real", f"{margen:.1f}%")
                
                st.progress(min(max(utilidad/pvp, 0.0), 1.0) if pvp > 0 else 0.0)
