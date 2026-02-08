import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONEXIÓN INICIAL ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase: Client = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit", layout="wide")

# --- LOGIN SIMPLE ---
if 'user' not in st.session_state:
    st.title("🦷 DentalProfit")
    e = st.text_input("Correo")
    p = st.text_input("Password", type="password")
    if st.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user = res
            st.rerun()
        except: st.error("Error de acceso")
else:
    u_id = st.session_state.user.user.id
    st.sidebar.button("Cerrar Sesión", on_click=lambda: [supabase.auth.sign_out(), st.session_state.clear()])

    st.title("Panel de Control")

    # 1. GASTOS FIJOS
    st.header("🏢 Gastos Fijos")
    c1, c2, c3 = st.columns(3)
    alq = c1.number_input("Alquiler", 0.0)
    per = c2.number_input("Personal", 0.0)
    ser = c3.number_input("Servicios", 0.0)
    st.write(f"**Total Mensual:** ${alq + per + ser:,.2f}")

    # 2. INVENTARIO
    st.header("📦 Inventario de Insumos")
    
    # Cargar datos de Supabase
    try:
        res = supabase.table("inventario").select("*").eq("user_id", u_id).execute()
        df = pd.DataFrame(res.data)
    except:
        df = pd.DataFrame()

    # Si la tabla está vacía, crear estructura básica
    if df.empty:
        df = pd.DataFrame(columns=["material", "precio_compra", "cantidad_en_envase", "unidad"])
        df.loc[0] = ["", 0.0, 1.0, "u"]

    # Cálculo del costo por uso (sin gráficos raros)
    df['costo_por_uso'] = df['precio_compra'].astype(float) / df['cantidad_en_envase'].astype(float).replace(0, 1)

    df_editado = st.data_editor(
        df, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "user_id": None, "id": None, "created_at": None,
            "costo_por_uso": st.column_config.NumberColumn("Costo Uso ($)", disabled=True, format="$%.2f")
        }
    )
    
    if st.button("Guardar Cambios"):
        # Limpiar para guardar
        datos_a_guardar = df_editado.drop(columns=['costo_por_uso'], errors='ignore').to_dict(orient='records')
        for d in datos_a_guardar: d['user_id'] = u_id
        supabase.table("inventario").upsert(datos_a_guardar).execute()
        st.success("Guardado correctamente")

    # 3. CALCULADORA
    st.header("💰 Calculadora de Ganancia")
    materiales_lista = df_editado['material'].unique()
    seleccion = st.multiselect("Materiales usados en el paciente:", [m for m in materiales_lista if m])
    
    if seleccion:
        costo_insumos = df_editado[df_editado['material'].isin(seleccion)]['costo_por_uso'].sum()
        precio_paciente = st.number_input("Precio del tratamiento", 0.0)
        
        st.subheader(f"Costo de materiales: ${costo_insumos:,.2f}")
        st.subheader(f"Ganancia: ${precio_paciente - costo_insumos:,.2f}")
