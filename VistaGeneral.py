import streamlit as st

def show():
    st.title('Vista General')

    st.write('## Introducción')
    st.write('Bienvenido a la aplicación de análisis de datos. Esta aplicación está diseñada para proporcionar una visión detallada de los datos en diferentes áreas. A continuación se detalla el contenido de cada pestaña disponible en el panel de navegación.')

    st.write('## Pestañas disponibles')

    st.write('### Vista General')
    st.write('En esta pestaña, encontrarás una visión general de la aplicación, incluyendo una descripción de las funcionalidades y una guía rápida para navegar por el sistema.')

    st.write('### Hard Discount')
    st.write('Esta pestaña proporciona un análisis detallado de las estrategias de descuento y su impacto en las ventas. Aquí encontrarás gráficos y datos relevantes para evaluar las promociones y descuentos aplicados.')

    st.write('### Producto Maquilado-Terminado')
    st.write('Aquí se presenta un análisis detallado del proceso de producción, desde los productos maquilados hasta los productos terminados. Esta pestaña incluye datos de producción, eficiencia, y calidad.')

    st.write('### Comisiones Vendedoras')
    st.write('En esta sección se muestra un análisis de las comisiones asignadas a los vendedores, incluyendo un desglose de comisiones por vendedor y análisis de desempeño.')

    st.write('## Información Adicional')
    st.write('Para más detalles sobre el uso de esta aplicación o para resolver dudas, por favor contacta al equipo de soporte o consulta la documentación adicional que se encuentra en el siguiente enlace:')
    st.markdown('[Documentación Adicional](https://www.ejemplo.com)')  # Reemplaza con el enlace a tu documentación si es aplicable

    st.write('Gracias por usar la aplicación.')
