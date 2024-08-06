import streamlit as st
import plotly.graph_objects as go
import numpy as np

def show():
    st.title('Producto Maquilado Terminado')
    st.write('Contenido del primer dashboard')
    # Agrega gráficos, tablas o cualquier otro contenido aquí
    # Genera gráficos de ejemplo con Plotly
    # Define las variables necesarias
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    fig1 = go.Figure(data=go.Scatter(x=x, y=y1, mode='lines', name='Seno'))
    fig1.update_layout(title="Seno", width=600, height=400)

    fig2 = go.Figure(data=go.Scatter(x=x, y=y2, mode='lines', name='Coseno'))
    fig2.update_layout(title="Coseno", width=400, height=400)

    fig3 = go.Figure(data=go.Scatter(x=x, y=y1 + y2, mode='lines', name='Seno + Coseno'))
    fig3.update_layout(title="Seno + Coseno", width=800, height=400)

    # Configura el layout de la página para tener varias columnas
    col1, col2, col3 = st.columns([2, 2, 2])  # Ancho relativo de cada columna

    with col1:
        st.subheader("Gráfica 1")
        st.plotly_chart(fig1,use_container_width=True)

    with col2:
        st.subheader("Gráfica 2")
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        st.subheader("Gráfica 3")
        st.plotly_chart(fig3, use_container_width=True)
