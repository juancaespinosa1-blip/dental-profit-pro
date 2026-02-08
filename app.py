import streamlit as st
import pandas as pd
import plotly.express as px


# ───────────────────────────────────────────────
# CONFIGURACIÓN
# ───────────────────────────────────────────────
st.set_page_config(page_title="DentalProfit Pro", page_icon="🦷", layout="wide")

# Estilos
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fc; }
    .metric-card {
        background: white;
        padding: 1.4rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        border-left: 5px solid #0d6efd;
        margin: 0.8rem 0;
    }
    [data-testid="stMetricValue"] { font-size: 1.9rem !important; }
    .stButton>button { border-radius: 8px; font-weight: 600; }
    </style>
""", unsafe_allow_html=True)

# ───────────────────────────────────────────────
# AUTENTICACIÓN SIMPLE
# ───────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2.5, 1])
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3774/3774278.png", width=90)
        st.markdown("<h2 style='text-align:center;'>DentalProfit Pro</h2>", unsafe_allow_html=True)
        st.markdown("<h4 style='text-align:center; color:#6c757d;'>Gestión de costos y precios odontológicos</h4>", unsafe_allow_html=True)
        
        pwd = st.text_input("Clave de licencia", type="password", key="login_pwd")
        if st.button("Iniciar sesión", type="primary", use_container_width=True):
            if pwd.strip() == "dental2026":
                st.session_state.authenticated = True
                st.success("¡Bienvenido!")
                st.rerun()
            else:
                st.error("Clave incorrecta")
    st.stop()

# ───────────────────────────────────────────────
# DATOS INICIALES
# ───────────────────────────────────────────────
if 'inventario' not in st.session_state:
    st.session_state.inventario = pd.DataFrame([
        {"Material": "Resina Filtek Supreme",   "Precio": 68.50, "Cantidad": 4.0,  "Unidad": "g",   "Costo por unidad": 68.50/4},
        {"Material": "Adhesivo Scotchbond",     "Precio": 135.0, "Cantidad": 5.0,  "Unidad": "ml",  "Costo por unidad": 135/5},
        {"Material": "Anestesia Articaina 1:100k","Precio": 48.90, "Cantidad": 50,   "Unidad": "carp","Costo por unidad": 48.90/50},
        {"Material": "Guantes nitrilo",         "Precio": 18.50, "Cantidad": 200,  "Unidad": "u",   "Costo por unidad": 18.50/200},
        {"Material": "Matrix sección",          "Precio": 92.0,  "Cantidad": 50,   "Unidad": "u",   "Costo por unidad": 92/50},
    ])

if 'costo_hora' not in st.session_state:
    st.session_state.costo_hora = 28.50   # valor más realista 2025-2026

if 'historial_precios' not in st.session_state:
    st.session_state.historial_precios = pd.DataFrame(columns=["Fecha","Procedimiento","Precio","Minutos","Margen"])

# ───────────────────────────────────────────────
# BARRA LATERAL
# ───────────────────────────────────────────────
with st.sidebar:
    st.title("🦷 DentalProfit Pro")
    menu = st.radio("Menú principal", 
                    ["Dashboard", "Calculadora de precio", "Inventario", "Historial", "Configuración"],
                    index=1)
    st.divider()
    if st.button("🚪 Cerrar sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ───────────────────────────────────────────────
# PÁGINAS
# ───────────────────────────────────────────────
if menu == "Dashboard":
    st.header("🏦 Panel de Control")
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Costo por minuto", f"${st.session_state.costo_hora/60:.3f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Materiales registrados", len(st.session_state.inventario))
        st.markdown('</div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Costo hora operador", f"${st.session_state.costo_hora:.2f}")
        st.markdown('</div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Registros guardados", len(st.session_state.historial_precios))
        st.markdown('</div>', unsafe_allow_html=True)

    st.subheader("Distribución típica de costos (ejemplo)")
    df_ej = pd.DataFrame({
        "Concepto": ["Personal", "Materiales", "Otros gastos", "Utilidad"],
        "Porcentaje": [45, 18, 17, 20]
    })
    fig = px.pie(df_ej, values="Porcentaje", names="Concepto", hole=0.4,
                 color_discrete_sequence=px.colors.qualitative.Bold)
    st.plotly_chart(fig, use_container_width=True)


elif menu == "Calculadora de precio":
    st.header("🧮 Calculadora de precio realista")

    col1, col2 = st.columns([1,1])

    with col1:
        procedimiento = st.text_input("Nombre del procedimiento", "Reconstrucción clase II")
        minutos_sillon = st.number_input("Minutos en sillón", min_value=5, max_value=240, value=45, step=5)
        margen_deseado = st.slider("Margen de ganancia deseado (%)", 40, 180, 100, step=5)

    with col2:
        st.subheader("Materiales utilizados")
        
        # Mejora importante: permitir cantidad usada
        materiales_disponibles = st.session_state.inventario["Material"].tolist()
        
        materiales_seleccionados = st.multiselect("Seleccionar materiales", materiales_disponibles)
        
        uso_materiales = {}
        costo_materiales = 0.0
        
        for mat in materiales_seleccionados:
            row = st.session_state.inventario[st.session_state.inventario["Material"] == mat].iloc[0]
            cant_usada = st.number_input(f"{mat}  ({row['Unidad']})", 
                                        min_value=0.01, max_value=row["Cantidad"]*1.5, 
                                        value=0.1, step=0.05, key=f"mat_{mat}")
            costo = cant_usada * row["Costo por unidad"]
            costo_materiales += costo
            uso_materiales[mat] = cant_usada

    costo_personal = (minutos_sillon / 60) * st.session_state.costo_hora
    costo_total = costo_personal + costo_materiales
    precio_final = costo_total * (1 + margen_deseado / 100)

    st.divider()

    c1, c2, c3 = st.columns([2,2,1])
    with c1:
        st.info(f"**Costo de personal**: ${costo_personal:.2f}")
    with c2:
        st.info(f"**Materiales**: ${costo_materiales:.2f}")
    with c3:
        st.metric("**Precio sugerido**", f"${precio_final:.2f}", delta=f"{margen_deseado}%")

    if st.button("💾 Guardar este cálculo en historial", type="primary"):
        nuevo_registro = pd.DataFrame({
            "Fecha": [datetime.now().strftime("%Y-%m-%d %H:%M")],
            "Procedimiento": [procedimiento],
            "Precio": [round(precio_final, 2)],
            "Minutos": [minutos_sillon],
            "Margen": [margen_deseado]
        })
        st.session_state.historial_precios = pd.concat([st.session_state.historial_precios, nuevo_registro], ignore_index=True)
        st.success("¡Cálculo guardado en historial!")


elif menu == "Inventario":
    st.header("📦 Gestión de inventario")

    edited_df = st.data_editor(
        st.session_state.inventario,
        column_config={
            "Precio": st.column_config.NumberColumn(format="$%.2f"),
            "Cantidad": st.column_config.NumberColumn(min_value=0.0, step=0.1),
            "Costo por unidad": st.column_config.NumberColumn(format="$%.4f", disabled=True),
        },
        num_rows="dynamic",
        use_container_width=True
    )

    # Actualizar costo por unidad automáticamente
    edited_df["Costo por unidad"] = edited_df["Precio"] / edited_df["Cantidad"].replace(0, 1e-10)
    st.session_state.inventario = edited_df


elif menu == "Historial":
    st.header("📜 Historial de precios calculados")

    if len(st.session_state.historial_precios) == 0:
        st.info("Aún no hay cálculos guardados")
    else:
        st.dataframe(
            st.session_state.historial_precios.sort_values("Fecha", ascending=False),
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            label="Descargar historial (CSV)",
            data=st.session_state.historial_precios.to_csv(index=False).encode('utf-8'),
            file_name="historial_precios_dentalprofit.csv",
            mime="text/csv"
        )


elif menu == "Configuración":
    st.header("⚙️ Configuración general")

    st.subheader("Costo horario del profesional")
    gastos_mensuales = st.number_input("Gastos operativos mensuales totales ($)", min_value=500.0, value=4800.0, step=100.0)
    horas_trabajo_mes = st.number_input("Horas efectivas al mes", min_value=40.0, value=160.0, step=10.0)

    nuevo_costo_hora = gastos_mensuales / horas_trabajo_mes
    st.metric("Costo por hora actualizado", f"${nuevo_costo_hora:.2f}", 
              delta=f"{nuevo_costo_hora - st.session_state.costo_hora:.2f}")

    if st.button("Aplicar nuevo costo horario"):
        st.session_state.costo_hora = nuevo_costo_hora
        st.success(f"Nuevo costo horario aplicado: ${nuevo_costo_hora:.2f}")
