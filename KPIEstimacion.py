import streamlit as st
import pandas as pd

# Mapeo de números de meses a nombres en español
month_mapping = {
    1: 'ENERO', 2: 'FEBRERO', 3: 'MARZO', 4: 'ABRIL', 5: 'MAYO', 6: 'JUNIO',
    7: 'JULIO', 8: 'AGOSTO', 9: 'SEPTIEMBRE', 10: 'OCTUBRE', 11: 'NOVIEMBRE', 12: 'DICIEMBRE'
}

def load_all_data():
    try:
        file_path = "archivo_excelSS.xlsx"
        current_year_data = pd.read_excel(file_path, sheet_name="Sheet1")
        
        file_path_historical = "Historico.xlsx"
        sheets = pd.read_excel(file_path_historical, sheet_name=None)
        df_list = [sheets[year].assign(Año=year) for year in sheets]
        historical_data = pd.concat(df_list, ignore_index=True)
        
        return current_year_data, historical_data
    except Exception as e:
        st.error(f"Error al cargar los archivos de datos: {e}")
        return pd.DataFrame(), pd.DataFrame()

def calculate_kpis(current_year_data, historical_data):
    # Preparar datos
    current_year_data['Almacen'] = current_year_data['Almacen'].str.strip()
    current_year_data['VentaBruta'] = current_year_data[['ProductoTerminado', 'ProductoMaquilado']].sum(axis=1)
    current_year_data['Mes'] = current_year_data['Mes'].map(month_mapping)
    current_year_data['Mes'] = current_year_data['Mes'].str.upper()
    current_year_data['Año'] = 2024
    
    historical_data = historical_data.melt(id_vars=['Almacen', 'Año'], var_name='Mes', value_name='VentaBruta')
    historical_data['Almacen'] = historical_data['Almacen'].str.strip()
    historical_data['Mes'] = historical_data['Mes'].str.upper()
    historical_data['VentaBruta'] = historical_data['VentaBruta'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    
    # Unir datos históricos y actuales
    all_data = pd.concat([historical_data, current_year_data[['Almacen', 'Año', 'Mes', 'VentaBruta']]], ignore_index=True)
    
    # Convertir la columna 'Mes' a categoría con un conjunto fijo de valores
    ordered_months = [month_mapping[i] for i in range(1, 13)]
    all_data['Mes'] = pd.Categorical(all_data['Mes'], categories=ordered_months, ordered=True)
    
    # Asegurarse de que el año 2024 esté al final
    all_data['Año'] = all_data['Año'].astype(str)
    all_data['Año'] = all_data['Año'].apply(lambda x: '9999' if x == '2024' else x)
    all_data['Año'] = all_data['Año'].astype(int)
    all_data.sort_values(by=['Año', 'Mes'], inplace=True)
    
    # Restaurar el año 2024 a su valor original
    all_data['Año'] = all_data['Año'].apply(lambda x: '2024' if x == 9999 else str(x))
    
    # Calcular KPI 1: Comparación con el año anterior
    yearly_sales = all_data.groupby(['Año', 'Mes'])['VentaBruta'].sum().reset_index()
    yearly_sales['VentaBruta_Ant'] = yearly_sales.groupby('Mes')['VentaBruta'].shift(1)
    yearly_sales['KPI_1'] = ((yearly_sales['VentaBruta'] - yearly_sales['VentaBruta_Ant']) / yearly_sales['VentaBruta_Ant']) * 100
    
    # Calcular KPI 2: Incremento de ventas por Trimestre
    all_data['Trimestre'] = all_data['Mes'].apply(lambda x: (ordered_months.index(x) // 3) + 1)
    quarterly_sales = all_data.groupby(['Año', 'Trimestre'])['VentaBruta'].sum().reset_index()
    
    # Ordenar por Año y Trimestre para asegurar la correcta comparación
    quarterly_sales = quarterly_sales.sort_values(by=['Año', 'Trimestre'])
    
    # Convertir 'Año' a entero para el cálculo
    quarterly_sales['Año'] = quarterly_sales['Año'].astype(int)
    
    # Calcular las ventas del trimestre anterior
    quarterly_sales['VentaBruta_Ant'] = quarterly_sales.groupby('Año')['VentaBruta'].shift(1)
    
    # Calcular el KPI 2: Incremento porcentual
    quarterly_sales['Incremento'] = ((quarterly_sales['VentaBruta'] - quarterly_sales['VentaBruta_Ant']) / quarterly_sales['VentaBruta_Ant']) * 100
    
    # Ajustar el cálculo para el primer trimestre de cada año comparado con el último trimestre del año anterior
    first_trimestre_indices = quarterly_sales['Trimestre'] == 1
    if not quarterly_sales[first_trimestre_indices].empty:
        # Obtener datos del último trimestre del año anterior
        last_trimestre_data = quarterly_sales[quarterly_sales['Trimestre'] == 4].copy()
        last_trimestre_data['Año'] = last_trimestre_data['Año'] + 1
        last_trimestre_data = last_trimestre_data.rename(columns={'VentaBruta': 'VentaBruta_Ant_PrevYear'})
        
        # Convertir 'Año' a entero antes de hacer el merge
        quarterly_sales['Año'] = quarterly_sales['Año'].astype(int)
        last_trimestre_data['Año'] = last_trimestre_data['Año'].astype(int)
        
        # Merge para añadir la venta del trimestre anterior del año previo
        quarterly_sales = pd.merge(quarterly_sales, last_trimestre_data[['Año', 'VentaBruta_Ant_PrevYear']],
                                   how='left', on='Año', suffixes=('', '_PrevYear'))
        
        # Actualizar el KPI para el primer trimestre del año
        quarterly_sales.loc[first_trimestre_indices, 'VentaBruta_Ant'] = quarterly_sales.loc[first_trimestre_indices, 'VentaBruta_Ant_PrevYear']
        quarterly_sales['Incremento'] = ((quarterly_sales['VentaBruta'] - quarterly_sales['VentaBruta_Ant']) / quarterly_sales['VentaBruta_Ant']) * 100
    
    return yearly_sales, quarterly_sales

def format_currency(value):
    return "${:,.2f}".format(value)

def show():
    st.title("Estimación de KPIs de Ventas")

    # Cargar datos
    current_year_data, historical_data = load_all_data()
    
    if current_year_data.empty or historical_data.empty:
        return

    yearly_sales, quarterly_sales = calculate_kpis(current_year_data, historical_data)
    
    # Filtros para KPI 1 (Año y Mes)
    years = yearly_sales['Año'].unique()
    selected_year = st.selectbox('Selecciona el Año para KPI 1', sorted(years))

    months = yearly_sales['Mes'].unique()
    selected_month = st.selectbox('Selecciona el Mes para KPI 1', sorted(months))
    
    # Filtrar datos para KPI 1
    filtered_yearly_sales = yearly_sales[
        (yearly_sales['Año'] == selected_year) & (yearly_sales['Mes'] == selected_month)
    ]
    
    # Mostrar KPI 1
    if not filtered_yearly_sales.empty:
        latest_month = filtered_yearly_sales.iloc[0]
        st.subheader(f"KPI 1: Incremento de Ventas para el Mes {selected_month} del Año {selected_year}")
        st.metric(
            "Ventas Brutas Mensuales",
            format_currency(latest_month['VentaBruta']),
            delta=f"{latest_month['KPI_1']:.2f}%"
        )
    else:
        st.warning("No hay datos para el mes seleccionado en el año seleccionado.")
    
    # Filtros para KPI 2 (Año y Trimestre)
    selected_year_for_kpi2 = st.selectbox('Selecciona el Año para KPI 2', sorted(years))
    trimesters = [1, 2, 3, 4]
    selected_trimestre = (st.selectbox('Selecciona el Trimestre para KPI 2', trimesters))
    
    # Filtrar datos para KPI 2 usando query()
    filtered_quarterly_sales = quarterly_sales[
    (quarterly_sales['Año'] == int(selected_year_for_kpi2)) & 
    (quarterly_sales['Trimestre'] == int(selected_trimestre))]
    
    # Mostrar KPI 2
    if not filtered_quarterly_sales.empty:
        latest_quarter = filtered_quarterly_sales.iloc[0]
        st.subheader(f"KPI 2: Incremento de Ventas para el Trimestre {int(selected_trimestre)} del Año {int(selected_year_for_kpi2)}")
        st.metric(
            "Ventas Brutas Trimestrales",
            format_currency(latest_quarter['VentaBruta']),
            delta=f"{latest_quarter['Incremento']:.2f}%"
        )
    else:
        st.warning("No hay datos para el trimestre seleccionado en el año seleccionado.")
    

if __name__ == "__main__":
    show()
