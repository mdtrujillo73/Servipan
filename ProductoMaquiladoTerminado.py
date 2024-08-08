import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def load_data():
    try:
        file_path = "archivo_excelSS.xlsx"  # Asegúrate de colocar la ruta correcta
        sheet1 = pd.read_excel(file_path, sheet_name="Sheet1")
        sheet2 = pd.read_excel(file_path, sheet_name="Sheet2")
        
        # Unir las hojas en función del 'Punto de Venta'
        data = pd.merge(sheet1, sheet2, on="Punto de Venta", how="left")
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo de datos: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error

def format_currency(value):
    """Formatea el valor en formato de moneda."""
    return "${:,.2f}".format(value)

def show():
    # Carga los datos
    data = load_data()
    if data.empty:
        return

    # Excluir 'Hard Discount' en la columna 'Ciudad'
    data = data[~data['Ciudad'].str.strip().str.contains('Hard Discount', case=False, na=False)]

    # Calcular la venta bruta
    data['VentaBruta'] = data['ProductoTerminado'] + data['ProductoMaquilado']

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
    
    city_filter = st.sidebar.selectbox("Selecciona la Ciudad", options=["Todos"] + list(data['Ciudad'].unique()))
    zone_filter = st.sidebar.selectbox("Selecciona la Zona", options=["Todos"] + list(data['Zona'].unique()))

    # Filtra los datos por año, mes, ciudad y zona
    if month == "Todos":
        filtered_data = data[data['Año'] == year]
    else:
        month_number = meses_espanol.index(month) + 1
        filtered_data = data[(data['Año'] == year) & (data['Mes'] == month_number)]

    if city_filter != "Todos":
        filtered_data = filtered_data[filtered_data['Ciudad'] == city_filter]

    if zone_filter != "Todos":
        filtered_data = filtered_data[filtered_data['Zona'] == zone_filter]

    # Agrupa por zona y suma las ventas de ProductoTerminado y ProductoMaquilado
    ventas_por_zona = filtered_data.groupby('Zona').agg({
        'ProductoTerminado': 'sum',
        'ProductoMaquilado': 'sum'
    }).reset_index()

    # Crear el gráfico de doble barra para ProductoTerminado y ProductoMaquilado
    fig_doble_barra = go.Figure()

    fig_doble_barra.add_trace(
        go.Bar(
            x=ventas_por_zona['Zona'],
            y=ventas_por_zona['ProductoTerminado'],
            name='Producto Terminado',
            marker_color='blue'
        )
    )

    fig_doble_barra.add_trace(
        go.Bar(
            x=ventas_por_zona['Zona'],
            y=ventas_por_zona['ProductoMaquilado'],
            name='Producto Maquilado',
            marker_color='orange'
        )
    )

    fig_doble_barra.update_layout(
        title=f"Ventas de Producto Terminado y Maquilado por Zona en {month} de {year}",
        xaxis_title='Zona',
        yaxis_title='Ventas',
        barmode='group',  # Para mostrar las barras lado a lado
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        xaxis=dict(tickmode='linear'),  # Asegura que los valores del eje X sean visibles
        template='plotly_white'
    )

    # Crear un gráfico de tendencia mensual de ventas brutas
    ventas_mensuales = filtered_data.groupby(['Año', 'Mes'])['VentaBruta'].sum().reset_index()
    ventas_mensuales = ventas_mensuales.sort_values(by=['Año', 'Mes'])

    fig_tendencia = px.line(
        ventas_mensuales,
        x='Mes',
        y='VentaBruta',
        color='Año',
        title='Tendencia de Venta Bruta Mensual',
        labels={'Mes': 'Mes', 'VentaBruta': 'Venta Bruta'},
        template='plotly_white'
    )

    fig_tendencia.update_layout(
        xaxis=dict(tickvals=list(range(1, 13)), ticktext=meses_espanol),
        yaxis_title='Venta Bruta'
    )

    # Crear la interfaz en columnas
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Ventas de Producto Terminado y Maquilado por Zona")
        st.plotly_chart(fig_doble_barra, use_container_width=True)

        # Tabla de los 5 mejores puntos de venta
        top_5_puntos_venta = filtered_data.groupby(['Punto de Venta', 'Zona'])['VentaBruta'].sum().reset_index()
        top_5_puntos_venta = top_5_puntos_venta.sort_values(by='VentaBruta', ascending=False).head(5)
        top_5_puntos_venta['VentaBruta'] = top_5_puntos_venta['VentaBruta'].apply(format_currency)
        st.subheader("Top 5 Puntos de Venta")
        st.write(top_5_puntos_venta.to_html(index=False, escape=False), unsafe_allow_html=True)

    with col2:
        st.subheader("Tendencia de Venta Bruta Mensual")
        st.plotly_chart(fig_tendencia, use_container_width=True)

        # Tabla de los 10 puntos de venta con menores ventas (mayores a cero)
        lowest_10_puntos_venta = filtered_data[filtered_data['VentaBruta'] > 0]
        lowest_10_puntos_venta = lowest_10_puntos_venta.groupby(['Punto de Venta', 'Zona'])['VentaBruta'].sum().reset_index()
        lowest_10_puntos_venta = lowest_10_puntos_venta.sort_values(by='VentaBruta').head(10)
        lowest_10_puntos_venta['VentaBruta'] = lowest_10_puntos_venta['VentaBruta'].apply(format_currency)
        st.subheader("10 Puntos de Venta con Menores Ventas")
        st.write(lowest_10_puntos_venta.to_html(index=False, escape=False), unsafe_allow_html=True)

if __name__ == "__main__":
    show()
