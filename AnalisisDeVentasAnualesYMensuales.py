import streamlit as st
import pandas as pd
import plotly.express as px

# Mapeo de números de meses a nombres en español
month_mapping = {
    1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO',
    7: 'JULIO', 8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
}

# Lista de nombres de meses en orden
ordered_months = [month_mapping[i] for i in range(1, 13)]

def load_current_year_data():
    try:
        file_path = "archivo_excelSS.xlsx"
        data = pd.read_excel(file_path, sheet_name="Sheet1")
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo de datos del año actual: {e}")
        return pd.DataFrame()

def load_historical_data():
    try:
        file_path = "Historico.xlsx"
        sheets = pd.read_excel(file_path, sheet_name=None)
        # Combinar todas las hojas en un solo DataFrame
        df_list = [sheets[year].assign(Año=year) for year in sheets]
        data = pd.concat(df_list, ignore_index=True)
        return data
    except Exception as e:
        st.error(f"Error al cargar el archivo de datos histórico: {e}")
        return pd.DataFrame()

def show():
    st.title("Análisis de Ventas Anuales y Mensuales")

    # Cargar datos
    current_year_data = load_current_year_data()
    historical_data = load_historical_data()

    if current_year_data.empty or historical_data.empty:
        return

    # Eliminar espacios al comienzo y al final de los nombres de almacén
    current_year_data['Almacen'] = current_year_data['Almacen'].str.strip()

    current_year_data['VentaBruta'] = current_year_data[['ProductoTerminado', 'ProductoMaquilado']].sum(axis=1)
    current_year_data['Mes'] = current_year_data['Mes'].map(month_mapping)  # Convertir el mes a nombre
    current_year_data['Mes'] = current_year_data['Mes'].str.upper()  # Convertir a mayúsculas
    current_year_data['Año'] = 2024  # Año actual

    # Limpieza y preparación de datos históricos
    historical_data = historical_data.melt(id_vars=['Almacen', 'Año'], var_name='Mes', value_name='VentaBruta')
    historical_data['Almacen'] = historical_data['Almacen'].str.strip()
    historical_data['Mes'] = historical_data['Mes'].str.upper()  # Convertir a mayúsculas
    historical_data['VentaBruta'] = historical_data['VentaBruta'].replace({'\$': '', ',': ''}, regex=True).astype(float)

    # Unir datos históricos y actuales
    all_data = pd.concat([historical_data, current_year_data[['Almacen', 'Año', 'Mes', 'VentaBruta']]], ignore_index=True)

    # Reemplazar valores None por ceros
    all_data.fillna(0, inplace=True)

    # Asegurarse de que los datos estén ordenados por mes
    all_data['Mes'] = pd.Categorical(all_data['Mes'], categories=ordered_months, ordered=True)
    all_data.sort_values(by=['Año', 'Mes'], inplace=True)


    # Agregar venta bruta por año y mes
    monthly_sales = all_data.groupby(['Año', 'Mes'])['VentaBruta'].sum().reset_index()

    # Crear gráfico de ventas brutas mensuales por año
    fig_annual_sales = px.line(
        monthly_sales,
        x='Mes',
        y='VentaBruta',
        color='Año',
        title='Venta Bruta Mensual por Año',
        labels={'Mes': 'Mes', 'VentaBruta': 'Venta Bruta'},
        template='plotly_white'
    )
    fig_annual_sales.update_layout(
        xaxis=dict(
            tickvals=list(month_mapping.values()),
            ticktext=ordered_months
        ),
        yaxis_title='Venta Bruta'
    )

    st.subheader("Venta Bruta Mensual por Año")
    st.plotly_chart(fig_annual_sales, use_container_width=True)

    # Crear gráfico para cada almacén por separado
    almacen_sales = all_data.groupby(['Almacen', 'Año', 'Mes'])['VentaBruta'].sum().reset_index()

    # Generar gráficos separados por almacén
    almacenes = almacen_sales['Almacen'].unique()
    selected_almacen = st.selectbox("Selecciona un Almacén", options=almacenes)

    df_almacen = almacen_sales[almacen_sales['Almacen'] == selected_almacen]
    fig_almacen_sales = px.line(
        df_almacen,
        x='Mes',
        y='VentaBruta',
        color='Año',  # Diferenciar por año en la misma gráfica
        title=f'Venta Bruta Mensual para {selected_almacen}',
        labels={'Mes': 'Mes', 'VentaBruta': 'Venta Bruta'},
        template='plotly_white'
    )
    fig_almacen_sales.update_layout(
        xaxis=dict(
            tickvals=list(month_mapping.values()),
            ticktext=ordered_months
        ),
        yaxis_title='Venta Bruta'
    )

    st.subheader(f"Venta Bruta Mensual para {selected_almacen}")
    st.plotly_chart(fig_almacen_sales, use_container_width=True)



if __name__ == "__main__":
    show()
