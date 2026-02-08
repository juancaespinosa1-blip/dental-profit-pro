import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# ───────────────────────────────────────────────
# INICIALIZACIÓN TEMPRANA DE TODAS LAS VARIABLES DE ESTADO
# (debe ir ANTES de cualquier if, widget o página)
# ───────────────────────────────────────────────
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'inventario' not in st.session_state:
    st.session_state.inventario = pd.DataFrame([
        {"Material": "Resina Filtek Supreme",   "Precio": 68.50, "Cantidad": 4.0,  "Unidad": "g",   "Costo por unidad": 68.50/4},
        {"Material": "Adhesivo Scotchbond",     "Precio": 135.0, "Cantidad": 5.0,  "Unidad": "ml",  "Costo por unidad": 135/5},
        {"Material": "Anestesia Articaina 1:100k","Precio": 48.90, "Cantidad": 50,   "Unidad": "carp","Costo por unidad": 48.90/50},
        {"Material": "Guantes nitrilo",         "Precio": 18.50, "Cantidad": 200,  "Unidad": "u",   "Costo por unidad": 18.50/200},
        {"Material": "Matrix sección",          "Precio": 92.0,  "Cantidad": 50,   "Unidad": "u",   "Costo por unidad": 92/50},
    ])

if 'costo_hora' not in st.session_state:
    st.session_state.costo_hora = 28.50

if 'historial_precios' not in st.session_state:
    st.session_state.historial_precios = pd.DataFrame(columns=["Fecha", "Procedimiento", "Precio", "Minutos", "Margen"])

# ───────────────────────────────────────────────
# AHORA sí: el resto del código (config, estilos, login, sidebar, etc.)
# ───────────────────────────────────────────────

st.set_page_config(page_title="DentalProfit Pro", page_icon="🦷", layout="wide")

# Estilos ...
st.markdown(""" ... """, unsafe_allow_html=True)

# Login ...
if not st.session_state.authenticated:
    # ... código de login ...
    st.stop()

# Sidebar ...
with st.sidebar:
    # ...
    menu = st.radio(...)

# Páginas ...
if menu == "Dashboard":
    # Aquí ya puedes usar st.session_state.historial_precios sin miedo
    st.metric("Registros guardados", len(st.session_state.historial_precios))
    # ...
