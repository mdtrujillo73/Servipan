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

    # Excluir la ciudad 'Hard Discount' de los datos
    data = data[data['Ciudad'].str.strip() != 'Hard Discount']

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

    # Filtra los datos por año y mes
    if month == "Todos":
        filtered_data = data[data['Año'] == year]
    else:
        month_number = meses_espanol.index(month) + 1
        filtered_data = data[(data['Año'] == year) & (data['Mes'] == month_number)]

    # Aplicar filtro de ciudad si se selecciona (diferente a 'Todos')
    if city_filter != "Todos":
        filtered_data = filtered_data[filtered_data['Ciudad'] == city_filter]

    # Calcular los valores totales para las tarjetas
    total_venta_bruta = filtered_data['VentaBruta'].sum()
    total_devoluciones = filtered_data['Devoluciones'].sum()
    total_devoluciones_maquilado = filtered_data['DevolucionesM'].sum()

    # Agrupa por ciudad y suma las ventas brutas
    venta_bruta_por_ciudad = filtered_data.groupby('Ciudad')['VentaBruta'].sum().reset_index()

    # Calcula las devoluciones totales
    filtered_data['DevolucionesTotales'] = (filtered_data['Devoluciones'] + filtered_data['DevolucionesM']) * -1
    
    # Agrupa por ciudad y suma las devoluciones totales
    devoluciones_por_ciudad = filtered_data.groupby('Ciudad')['DevolucionesTotales'].sum().reset_index()

    # Crear el gráfico de pastel con porcentajes
    fig_venta = px.pie(
        venta_bruta_por_ciudad,
        names='Ciudad',
        values='VentaBruta',
        title=f"Venta Bruta por Ciudad en {month} de {year}",
        hole=0.3,
        labels={'Ciudad': 'Ciudad', 'VentaBruta': 'Venta Bruta'},
        template='plotly_white'
    )

    fig_venta.update_traces(
        textinfo='percent+label',
        textfont_size=18,
        pull=[0.1] * len(venta_bruta_por_ciudad)
    )

    # Crear un gráfico de barras para devoluciones totales
    fig_devoluciones_barras = px.bar(
        devoluciones_por_ciudad,
        x='Ciudad',
        y='DevolucionesTotales',
        title=f"Devoluciones Totales por Ciudad en {month} de {year}",
        labels={'Ciudad': 'Ciudad', 'DevolucionesTotales': 'Devoluciones Totales'},
        template='plotly_white'
    )

    # Añadir espacio entre la barra más alta y el límite superior
    max_y = devoluciones_por_ciudad['DevolucionesTotales'].max()
    margin = max_y * 0.1  # 10% de la altura máxima como margen
    fig_devoluciones_barras.update_layout(
        yaxis=dict(
            range=[0, max_y + margin]  # Establece el rango del eje y con margen adicional
        )
    )

    fig_devoluciones_barras.update_traces(
        texttemplate='$%{y:,.2f}',  # Formato de moneda con separación de miles y dos decimales
        textposition='outside',  # Posiciona el texto fuera de las barras
        marker=dict(
            color='brown',  # Color marrón para las barras
            line=dict(color='rgba(255, 255, 255, 0.5)', width=2)  # Opcional: Borde blanco con opacidad
        )
    )

    # Agrupa por punto de venta y ciudad, y suma la venta bruta
    ventas_por_punto = filtered_data.groupby(['Punto de Venta', 'Ciudad'])['VentaBruta'].sum().reset_index()

    # Filtra los puntos de venta con venta bruta total diferente de cero
    ventas_por_punto_no_cero = ventas_por_punto[ventas_por_punto['VentaBruta'] != 0]

    # Ordena por venta bruta en orden descendente y selecciona los top 5
    top_5_puntos = ventas_por_punto_no_cero.sort_values(by='VentaBruta', ascending=False).head(5)

    # Ordena por venta bruta en orden ascendente y selecciona los 5 peores
    peores_5_puntos = ventas_por_punto_no_cero.sort_values(by='VentaBruta').head(5)

    # Agrupa por punto de venta y ciudad, y suma las devoluciones totales
    devoluciones_por_punto = filtered_data.groupby(['Punto de Venta', 'Ciudad'])['DevolucionesTotales'].sum().reset_index()

    # Ordena por devoluciones totales en orden descendente y selecciona los top 5
    top_5_devoluciones = devoluciones_por_punto.sort_values(by='DevolucionesTotales', ascending=False).head(5)

    # Agrupa por almacén y suma la venta del producto terminado
    ventas_por_almacen = filtered_data.groupby('Almacen').agg({
        'ProductoTerminado': 'sum',
        'ProductoMaquilado': 'sum'
    }).reset_index()

    top_5_almacenes = ventas_por_almacen.sort_values(by='ProductoTerminado', ascending=False).head(5)
    
    # Formatear las columnas como moneda
    top_5_puntos['VentaBruta'] = top_5_puntos['VentaBruta'].apply(lambda x: f"${x:,.2f}")
    peores_5_puntos['VentaBruta'] = peores_5_puntos['VentaBruta'].apply(lambda x: f"${x:,.2f}")
    top_5_devoluciones['DevolucionesTotales'] = top_5_devoluciones['DevolucionesTotales'].apply(lambda x: f"${x:,.2f}")

    top_5_almacenes['ProductoTerminado'] = top_5_almacenes['ProductoTerminado'].apply(lambda x: f"${x:,.2f}")
    top_5_almacenes['ProductoMaquilado'] = top_5_almacenes['ProductoMaquilado'].apply(lambda x: f"${x:,.2f}")

    # Agrupar por mes y año en los datos filtrados para la tendencia
    ventas_mensuales = filtered_data.groupby(['Año', 'Mes'])['VentaBruta'].sum().reset_index()

    # Ordenar por año y mes
    ventas_mensuales = ventas_mensuales.sort_values(by=['Año', 'Mes'])

    # Crear gráfico de línea para ventas mensuales
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

    # Agrupar por mes, año y almacén en los datos filtrados para la tendencia
    ventas_mensuales_almacen = filtered_data.groupby(['Año', 'Mes', 'Almacen'])['VentaBruta'].sum().reset_index()

    # Crear gráfico de línea para ventas mensuales por almacén
    fig_tendencia_almacen = px.line(
        ventas_mensuales_almacen,
        x='Mes',
        y='VentaBruta',
        color='Almacen',
        title='Tendencia de Venta Bruta Mensual por Almacen',
        labels={'Mes': 'Mes', 'VentaBruta': 'Venta Bruta'},
        template='plotly_white'
    )

    fig_tendencia_almacen.update_layout(
        xaxis=dict(tickvals=list(range(1, 13)), ticktext=meses_espanol),
        yaxis_title='Venta Bruta'
    )

    # Crear la interfaz en columnas
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        st.subheader("Venta Bruta por Ciudad")
        st.plotly_chart(fig_venta, use_container_width=True)
        
        # Crear la tabla resumen del Top 5 puntos de venta
        st.subheader("Top 5 Puntos de Venta por Venta Bruta")
        st.dataframe(top_5_puntos, use_container_width=True, hide_index=True)
    
    with col2:
        st.subheader("Devoluciones Totales por Ciudad")
        st.plotly_chart(fig_devoluciones_barras, use_container_width=True)
        
        # Crear la tabla resumen del Top 5 puntos de venta por devoluciones
        st.subheader("Top 5 Puntos de Venta por Devoluciones Totales")
        st.dataframe(top_5_devoluciones, use_container_width=True, hide_index=True)

    with col3:
        st.subheader("Resumen")

        # Tarjetas en la tercera columna
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

        st.write("")
        st.write("")
        
        st.subheader("Top 5 Venta Producto Terminado por Almacen")
        # Mostrar la tabla del top 5 de almacenes
        st.dataframe(top_5_almacenes, use_container_width=True, hide_index=True)

    # Crear una fila adicional para el gráfico de tendencia temporal
    st.subheader("Tendencia de Venta Bruta Mensual")
    st.plotly_chart(fig_tendencia, use_container_width=True)

    # Crear una fila adicional para el gráfico de tendencia por almacén
    st.subheader("Tendencia de Venta Bruta Mensual por Almacen")
    st.plotly_chart(fig_tendencia_almacen, use_container_width=True)

    # Crear una fila adicional para el gráfico de los peores puntos de venta
    st.subheader("Peores 5 Puntos de Venta por Venta Bruta")
    st.dataframe(peores_5_puntos, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    show()
