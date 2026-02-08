# --- ESTILOS AVANZADOS (CSS) ---
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #f0f2f6;
    }
    
    /* Estilo para las tarjetas de métricas */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        color: #007bff;
    }
    
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        border-left: 5px solid #007bff;
        margin-bottom: 20px;
    }

    /* Botones más modernos */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,123,255,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

# --- RE-DISEÑO DEL DASHBOARD ---
if menu == "Dashboard":
    st.markdown("<h2 style='color: #1f3b64;'>🏦 Panel de Control Clínico</h2>", unsafe_allow_html=True)
    st.write("Bienvenido, Dr. Aquí tiene el estado financiero de su clínica hoy.")
    
    st.divider()

    # Tarjetas de Métricas usando columnas
    m1, m2, m3 = st.columns(3)
    
    with m1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("⏳ Valor Minuto Clínica", f"${(st.session_state.costo_hora/60):.2f}")
        st.caption("Costo operativo por cada minuto de sillón")
        st.markdown('</div>', unsafe_allow_html=True)

    with m2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📦 Stock de Insumos", f"{len(st.session_state.inventario)} items")
        st.caption("Materiales registrados en base de datos")
        st.markdown('</div>', unsafe_allow_html=True)

    with m3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📈 Margen Objetivo", "60%", "+5%")
        st.caption("Rendimiento promedio deseado")
        st.markdown('</div>', unsafe_allow_html=True)

    # Espacio para gráficos profesionales
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.subheader("📊 Distribución de Costos Operativos")
        # Gráfico más elegante
        df_plot = pd.DataFrame({
            'Gasto': ['Personal', 'Insumos', 'Servicios', 'Marketing', 'Utilidad'],
            'Monto': [35, 20, 15, 10, 20]
        })
        fig = px.bar(df_plot, x='Gasto', y='Monto', color='Gasto', 
                     text_auto=True, template="plotly_white")
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("💡 Tip de Rentabilidad")
        st.info("""
        **¿Sabía que...?**
        Reducir 5 minutos el tiempo de sillón en una limpieza puede aumentar su margen mensual en un **12%**. 
        ¡Optimice sus tiempos!
        """)
        st.warning("⚠️ Hay 2 materiales con stock bajo.")