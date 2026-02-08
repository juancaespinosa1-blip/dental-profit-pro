import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="DentalProfit Pro", layout="wide")

URL_SB = "https://xwblgnzewfsalfblkroy.supabase.co"
KEY_SB = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh3Ymxnbnpld2ZzYWxmYmxrcm95Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzA1NzU2MzMsImV4cCI6MjA4NjE1MTYzM30.QbnSim-l6gJU7Ycnk7IItA9ACFlA-q3XaAcvRvCRRx8"
supabase = create_client(URL_SB, KEY_SB)

if "user" not in st.session_state:
    st.title("🦷 Acceso DentalProfit")
    e = st.text_input("Email")
    p = st.text_input("Clave", type="password")
    if st.button("Iniciar sesión"):
        try:
            res = supabase.auth.sign_in_with_password({"email": e, "password": p})
            st.session_state.user = res
            st.rerun()
        except: st.error("Error de acceso")
    st.stop()

u_id = st.session_state.user.user.id

# --- CARGA INTELIGENTE ---
try:
    res = supabase.table("inventario").select("*").eq("user_id", u_id).execute()
    df = pd.DataFrame(res.data)
except Exception as e:
    st.error(f"Error de conexión con la tabla: {e}")
    df = pd.DataFrame()

# Mapeo de columnas para evitar el APIError
# Buscamos nombres comunes para 'cantidad' y 'precio'
col_map = {
    'material': 'material',
    'precio_compra': 'precio_compra',
    'cantidad_total': 'cantidad_total',
    'unidad': 'unidad'
}

if df.empty:
    df = pd.DataFrame(columns=col_map.values())
    df.loc[0] = ["Ejemplo", 0.0, 1.0, "u"]

# --- LÓGICA DE CÁLCULO (ESTÁNDAR DE ORO) ---
st.sidebar.title("DentalProfit Pro")
menu = st.sidebar.radio("Ir a:", ["Calculadora", "Inventario", "Configuración"])

if menu == "Calculadora":
    st.header("🧮 Calculadora de Costos por Porción")
    
    if 'costo_hora' not in st.session_state: st.session_state.costo_hora = 30.0
    
    c1, c2 = st.columns(2)
    with c1:
        mins = st.number_input("Minutos de sillón", 5, 300, 45)
        margen = st.slider("Margen %", 50, 300, 100)
    
    with c2:
        mats_list = df["material"].dropna().unique().tolist()
        sel = st.multiselect("Materiales:", mats_list)
        costo_mats = 0.0
        
        for m in sel:
            row = df[df["material"] == m].iloc[0]
            # Aseguramos que los valores sean numéricos para evitar errores de cálculo
            p = float(row.get("precio_compra", 0))
            c = float(row.get("cantidad_total", 1))
            u = row.get("unidad", "u")
            
            costo_unit = p / c if c > 0 else 0
            cant_u = st.number_input(f"Cantidad de {m} ({u})", 0.0, float(c)*5, 0.1, key=f"k_{m}")
            costo_mats += cant_u * costo_unit

    c_operativo = (mins / 60) * st.session_state.costo_hora
    p_final = (c_operativo + costo_mats) * (1 + margen/100)
    
    st.divider()
    res1, res2, res3 = st.columns(3)
    res1.metric("Costo Sillón", f"${c_operativo:.2f}")
    res2.metric("Costo Insumos", f"${costo_mats:.2f}")
    res3.metric("PRECIO SUGERIDO", f"${p_final:.2f}")

elif menu == "Inventario":
    st.header("📦 Inventario (Sincronizado)")
    # El editor ahora solo muestra lo que la tabla de Supabase realmente tiene
    df_ed = st.data_editor(df, num_rows="dynamic", use_container_width=True,
                           column_config={"user_id": None, "id": None, "created_at": None})
    
    if st.button("💾 Guardar y Reparar Tabla"):
        try:
            # Limpieza de datos antes de subir
            datos = df_ed.to_dict(orient='records')
            for d in datos: 
                d['user_id'] = u_id
                # Forzamos que los números sean números para evitar el APIError
                if 'precio_compra' in d: d['precio_compra'] = float(d['precio_compra'])
                if 'cantidad_total' in d: d['cantidad_total'] = float(d['cantidad_total'])

            supabase.table("inventario").upsert(datos).execute()
            st.success("¡Sincronización exitosa!")
            st.rerun()
        except Exception as e:
            st.error("Error de columnas. Verifica que en Supabase las columnas se llamen: material, precio_compra, cantidad_total y unidad.")

elif menu == "Configuración":
    st.header("⚙️ Gastos de Operación")
    gastos = st.number_input("Gastos fijos mes", value=4500.0)
    horas = st.number_input("Horas laborables mes", value=160.0)
    if st.button("Actualizar"):
        st.session_state.costo_hora = gastos / horas
        st.success(f"Costo hora: ${st.session_state.costo_hora:.2f}")
