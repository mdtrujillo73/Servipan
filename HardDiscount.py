import streamlit as st
import pandas as pd
import plotly.express as px

def load_data():
    try:
        file_path = "archivo_excelSS.xlsx"  # Asegúrate de colocar la ruta correcta
        data = pd.read_excel(file_path, sheet_name="Sheet1")
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo de datos: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

def show():
    # Carga los datos
    data = load_data()
    if data.empty:
        return

    # Filtrar para incluir solo la ciudad 'Hard Discount'
    data = data[data['Ciudad'].str.strip() == 'Hard Discount']

    # Configuración de los filtros en la barra lateral
    st.sidebar.header("Filtros")
    year = st.sidebar.selectbox("Selecciona el Año", options=sorted(data['Año'].unique()))
    
    # Añadir opción "Todos" al filtro de mes
    meses = sorted(data['Mes'].unique())
    meses_espanol = [
        "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
        "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]
    mes_opciones = ["Todos"] + [meses_espanol[m-1] for m in meses]
    month = st.sidebar.selectbox("Selecciona el Mes", options=mes_opciones)

    # Filtra los datos por año y mes
    if month == "Todos":
        filtered_data = data[data['Año'] == year]
    else:
        month_number = meses_espanol.index(month) + 1
        filtered_data = data[(data['Año'] == year) & (data['Mes'] == month_number)]

    # Calcula la venta bruta
    filtered_data['VentaBruta'] = filtered_data['ProductoTerminado'] 

    # Calcular los valores totales para las tarjetas
    total_venta_bruta = filtered_data['VentaBruta'].sum()
    total_devoluciones = filtered_data['Devoluciones'].sum()
    total_devoluciones_maquilado = filtered_data['ProductoMaquilado'].sum()

    # Agrupa por punto de venta y suma las ventas brutas
    ventas_por_punto = filtered_data.groupby('Punto de Venta')['VentaBruta'].sum().reset_index()

    # Ordena por ventas brutas de mayor a menor y selecciona el top 10
    ventas_por_punto = ventas_por_punto.sort_values(by='VentaBruta', ascending=False).head(10)

    # Crear un gráfico de treemap para ventas por punto de venta
    fig_venta_treemap = px.treemap(
        ventas_por_punto,
        path=['Punto de Venta'],
        values='VentaBruta',
        title=f"Venta Bruta por Punto de Venta en {month} de {year}",
        labels={'Punto de Venta': 'Punto de Venta', 'VentaBruta': 'Venta Bruta'},
        template='plotly_white'
    )

    # Agrupar por mes y calcular ventas totales para la tendencia
    ventas_mensuales = filtered_data.groupby(['Año', 'Mes'])['VentaBruta'].sum().reset_index()

    # Crear gráfico de línea para ventas mensuales
    fig_tendencia = px.line(
        ventas_mensuales,
        x='Mes',
        y='VentaBruta',
        color='Año',
        title='Tendencia de Ventas por Mes',
        labels={'Mes': 'Mes', 'VentaBruta': 'Venta Bruta'},
        template='plotly_white'
    )

    # Formatear las columnas como moneda
    ventas_por_punto['VentaBruta'] = ventas_por_punto['VentaBruta'].apply(lambda x: f"${x:,.2f}")

    # Crear la interfaz en columnas
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Venta Bruta por Punto de Venta")
        st.plotly_chart(fig_venta_treemap, use_container_width=True)

        st.subheader("Tendencia de Ventas Mensuales")
        st.plotly_chart(fig_tendencia, use_container_width=True)

    with col2:
        st.subheader("Resumen")

        # Tarjetas en la segunda columna
        st.markdown(
        f"""
        <div style="display: flex; flex-direction: column; gap: 15px;">
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h4 style="margin: 0; color: #333;">Venta Bruta Total</h4>
                <p style="font-size: 20px; margin: 0; color: #007BFF;"><strong>${total_venta_bruta:,.2f}</strong></p>
            </div>
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h4 style="margin: 0; color: #333;">Devoluciones Producto Terminado</h4>
                <p style="font-size: 20px; margin: 0; color: #dc3545;"><strong>${total_devoluciones:,.2f}</strong></p>
            </div>
            <div style="background-color: #f4f4f4; padding: 15px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
                <h4 style="margin: 0; color: #333;">Devoluciones Producto Maquilado</h4>
                <p style="font-size: 20px; margin: 0; color: #dc3545;"><strong>${total_devoluciones_maquilado:,.2f}</strong></p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
        )
        st.subheader("Top 10 Venta Bruta por Punto de Venta")
        # Mostrar la tabla del top 10 de puntos de venta
        st.dataframe(ventas_por_punto, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    show()
