import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- CONEXIÓN CONFIGURADA ---
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase = create_client(URL_SB, KEY_SB)

st.set_page_config(page_title="DentalProfit", layout="wide")

# --- LOGIN ---
if 'user' not in st.session_state:
    st.title("🦷 DentalProfit")
    e = st.text_input("Correo")
    p = st.text_input("Contraseña", type="password")
    if st.button("Acceder"):
        try:
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user = res
            st.rerun()
        except: st.error("Error de acceso. Verifica tus datos.")
else:
    u_id = st.session_state.user.user.id
    st.sidebar.button("Cerrar Sesión", on_click=lambda: [supabase.auth.sign_out(), st.session_state.clear()])

    st.title("Gestión de Clínica")

    # 1. CARGA DE DATOS (Asegurando que existan los datos)
    try:
        res = supabase.table("inventario").select("*").eq("user_id", u_id).execute()
        df = pd.DataFrame(res.data)
    except:
        df = pd.DataFrame()

    if df.empty:
        df = pd.DataFrame(columns=["material", "precio_compra", "cantidad_en_envase", "unidad"])
        df.loc[0] = ["Resina", 0.0, 1.0, "uso"]

    # 2. SECCIÓN DE INVENTARIO
    st.header("📦 1. Inventario")
    st.write("Registra tus insumos abajo. Usa el botón azul para guardar los cambios en la nube.")
    
    df_editado = st.data_editor(
        df, 
        num_rows="dynamic", 
        use_container_width=True, 
        key="editor_insumos",
        column_config={"user_id": None, "id": None, "created_at": None}
    )
    
    if st.button("💾 Guardar Inventario"):
        try:
            # Aseguramos que los datos tengan el ID de usuario
            datos_finales = df_editado.to_dict(orient='records')
            for fila in datos_finales:
                fila['user_id'] = u_id
            
            supabase.table("inventario").upsert(datos_finales).execute()
            st.success("¡Datos guardados!")
            st.rerun()
        except Exception as err:
            st.error(f"Error al guardar: {err}")

    st.divider()

    # 3. CALCULADORA DE GANANCIA (Forzando cálculos matemáticos)
    st.header("💰 2. Calculadora de Rentabilidad")
    
    # Pre-calculamos el costo por uso de lo que hay en la tabla
    calc_df = df_editado.copy()
    # Convertimos a números por si acaso
    calc_df['precio_compra'] = pd.to_numeric(calc_df['precio_compra'], errors='coerce').fillna(0)
    calc_df['cantidad_en_envase'] = pd.to_numeric(calc_df['cantidad_en_envase'], errors='coerce').fillna(1)
    
    calc_df['costo_unitario'] = calc_df['precio_compra'] / calc_df['cantidad_en_envase'].replace(0, 1)

    lista_mats = [m for m in calc_df['material'].unique() if m]
    seleccion = st.multiselect("Selecciona los materiales usados en el paciente:", lista_mats)
    
    if seleccion:
        # Sumamos los costos unitarios de los materiales seleccionados
        costo_total_insumos = calc_df[calc_df['material'].isin(seleccion)]['costo_unitario'].sum()
        
        precio_venta = st.number_input("¿Cuánto vas a cobrar por este tratamiento? ($)", min_value=0.0, step=1.0)
        
        ganancia_neta = precio_venta - costo_total_insumos
        
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Costo de Materiales", f"${costo_total_insumos:,.2f}")
        with c2:
            st.metric("Ganancia Neta", f"${ganancia_neta:,.2f}", delta=f"Margen: {0 if precio_venta == 0 else (ganancia_neta/precio_venta)*100:.1f}%")
