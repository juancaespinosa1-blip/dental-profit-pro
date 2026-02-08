import streamlit as st
import pandas as pd
from supabase import create_client, Client

# 1. CONEXIÓN BÁSICA
URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase = create_client(URL_SB, KEY_SB)

# 2. LOGIN SIN ADORNOS
if "user" not in st.session_state:
    st.title("Acceso")
    e = st.text_input("Correo")
    p = st.text_input("Clave", type="password")
    if st.button("Entrar"):
        try:
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user = res
            st.rerun()
        except: st.error("Error")
    st.stop()

u_id = st.session_state.user.user.id

# 3. CARGA DE DATOS (TABLA: Inventario)
try:
    res = supabase.table("Inventario").select("*").eq("user_id", u_id).execute()
    df = pd.DataFrame(res.data)
except:
    df = pd.DataFrame(columns=["material", "precio_compra", "cantidad_total", "unidad"])

# 4. INTERFAZ SIMPLE (Calculadora de porciones)
st.title("Calculadora Dental Pro")
opcion = st.sidebar.selectbox("Menú", ["Calculadora", "Inventario"])

if opcion == "Calculadora":
    # Costo por hora fijo para evitar NameError
    costo_h = 30.0
    
    col1, col2 = st.columns(2)
    with col1:
        minutos = st.number_input("Minutos de sillón", 5, 300, 45)
        margen = st.number_input("Margen %", 50, 500, 100)
    
    with col2:
        mats_disp = df["material"].tolist() if not df.empty else []
        sel = st.multiselect("Materiales", mats_disp)
        costo_mats = 0.0
        
        for m in sel:
            row = df[df["material"] == m].iloc[0]
            # LÓGICA DE PORCIÓN: Precio envase / contenido total
            unitario = float(row["precio_compra"]) / float(row["cantidad_total"]) if float(row["cantidad_total"]) > 0 else 0
            usado = st.number_input(f"¿Cuánto {m} ({row['unidad']})?", 0.0, 1000.0, 0.1, key=m)
            costo_mats += (usado * unitario)

    # CÁLCULO FINAL
    costo_tiempo = (minutos / 60) * costo_h
    total = (costo_tiempo + costo_mats) * (1 + margen/100)
    
    st.metric("PRECIO SUGERIDO", f"${total:,.2f}")
    st.write(f"Costo material: ${costo_mats:.2f} | Costo tiempo: ${costo_tiempo:.2f}")

elif opcion == "Inventario":
    st.subheader("Editar Insumos")
    # Solo columnas necesarias para evitar errores de API
    df_ed = st.data_editor(df[["material", "precio_compra", "cantidad_total", "unidad"]], num_rows="dynamic")
    
    if st.button("Guardar"):
        datos = df_ed.to_dict(orient='records')
        for d in datos: d['user_id'] = u_id
        supabase.table("Inventario").upsert(datos).execute()
        st.success("OK")
        st.rerun()
