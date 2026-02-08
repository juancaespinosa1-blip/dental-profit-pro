import streamlit as st
import pandas as pd
from fpdf import FPDF
import plotly.express as px

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="DentalProfit Pro", page_icon="🦷", layout="wide")

# --- SISTEMA DE LOGIN ---
def login():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.image("https://cdn-icons-png.flaticon.com/512/3774/3774278.png", width=80)
            st.title("Bienvenido a DentalProfit Pro")
            st.subheader("Gestión de Rentabilidad Clínica")
            password = st.text_input("Introduce tu Clave de Licencia", type="password")
            if st.button("Iniciar Sesión"):
                if password == "dental2026": # Esta sería la clave que vendes
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.error("Clave incorrecta. Por favor, contacta a soporte.")
        return False
    return True

# --- SOLO SI ESTÁ AUTENTICADO ---
if login():
    # --- ESTILOS PERSONALIZADOS ---
    st.markdown("""
        <style>
        .main { background-color: #f8f9fa; }
        div.stButton > button:first-child { background-color: #007bff; color: white; border-radius: 10px; }
        .stMetric { background-color: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        </style>
        """, unsafe_allow_html=True)

    # --- INICIALIZAR DATOS ---
    if 'inventario' not in st.session_state:
        st.session_state.inventario = pd.DataFrame([
            {"Material": "Resina Filtek", "Precio": 65.0, "Cantidad": 4, "Unidad": "gr"},
            {"Material": "Adhesivo Bond", "Precio": 120.0, "Cantidad": 5, "Unidad": "ml"},
            {"Material": "Anestesia", "Precio": 45.0, "Cantidad": 50, "Unidad": "u"}
        ])

    # --- NAVEGACIÓN LATERAL ---
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3774/3774278.png", width=60)
        st.title("DentalProfit")
        menu = st.radio("Menú Principal", ["Dashboard", "Calculadora", "Inventario", "Configuración"])
        st.divider()
        if st.button("Cerrar Sesión"):
            st.session_state.authenticated = False
            st.rerun()

    # --- LÓGICA DE GASTOS FIJOS ---
    if 'costo_hora' not in st.session_state: st.session_state.costo_hora = 25.0

    if menu == "Dashboard":
        st.header("📊 Resumen del Consultorio")
        col1, col2, col3 = st.columns(3)
        col1.metric("Costo por Hora", f"${st.session_state.costo_hora:.2f}")
        col2.metric("Insumos en Inventario", f"{len(st.session_state.inventario)}")
        col3.metric("Margen Promedio", "40%")
        
        # Gráfico de ejemplo
        st.subheader("Distribución de Costos Típica")
        df_pie = pd.DataFrame({'Categoría': ['Materiales', 'Sueldos', 'Renta', 'Utilidad'], 
                             'Valores': [20, 30, 15, 35]})
        fig = px.pie(df_pie, values='Valores', names='Categoría', hole=.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig)

    elif menu == "Calculadora":
        st.header("🧮 Calculadora de Tratamientos")
        with st.container():
            col_info1, col_info2 = st.columns(2)
            with col_info1:
                tratamiento = st.text_input("Nombre del Tratamiento", value="Limpieza / Resina")
                tiempo = st.number_input("Minutos de sillón", value=45, step=5)
            with col_info2:
                margen_deseado = st.slider("% Margen de Utilidad", 10, 500, 150)

            st.subheader("Materiales Utilizados")
            seleccionados = st.multiselect("Añadir materiales:", st.session_state.inventario["Material"])
            
            costo_materiales = 0.0
            for mat in seleccionados:
                row = st.session_state.inventario[st.session_state.inventario["Material"] == mat].iloc[0]
                cant = st.number_input(f"Cantidad de {mat} ({row['Unidad']})", key=mat, value=1.0)
                costo_materiales += (row["Precio"] / row["Cantidad"]) * cant

            costo_operativo = (tiempo / 60) * st.session_state.costo_hora
            costo_total = costo_materiales + costo_operativo
            precio_final = costo_total * (1 + margen_deseado / 100)

            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Costo Operativo", f"${costo_operativo:.2f}")
            c2.metric("Costo Materiales", f"${costo_materiales:.2f}")
            c3.subheader(f"Precio Sugerido: ${precio_final:.2f}")
            
            if st.button("Descargar Reporte para el Paciente"):
                st.info("Función de PDF lista para conectar.")

    elif menu == "Inventario":
        st.header("📦 Control de Insumos")
        st.write("Mantén tus precios actualizados para que el cálculo sea exacto.")
        st.session_state.inventario = st.data_editor(st.session_state.inventario, num_rows="dynamic")

    elif menu == "Configuración":
        st.header("⚙️ Configuración de la Clínica")
        st.write("Define tus costos fijos mensuales para calcular el precio por minuto.")
        renta = st.number_input("Renta y Servicios Mensuales", value=1500.0)
        sueldos = st.number_input("Sueldos y Asistentes", value=2000.0)
        horas = st.number_input("Horas laborables al mes", value=160)
        st.session_state.costo_hora = (renta + sueldos) / horas
        st.success(f"Costo por hora configurado: ${st.session_state.costo_hora:.2f}")