from PIL import Image
import streamlit as st
from VistaGeneral import show as show_VistaGeneral
from InformeGeneral import show as show_InformeGeneral
from HardDiscount import show as show_HardDiscount
from ProductoMaquiladoTerminado import show as show_ProductoMaquiladoTerminado
from ComisionesVendedoras import show as show_ComisionesVendedoras

# Cargar y redimensionar la imagen
def load_and_resize_image(image_path, width):
    img = Image.open(image_path)
    height = int((width / img.width) * img.height)
    return img.resize((width, height))

def main():
    # Muestra la imagen redimensionada
    img_resized = load_and_resize_image('servipan logo.png', 200)
    st.image(img_resized, caption='', use_column_width=False)

    # Crear las pestañas en Streamlit
    st.sidebar.title('Panel de Navegación')
    pagina = st.sidebar.radio('Selecciona la pestaña', [
        'Vista General',
        'Informe General',
        'Hard Discount',
        'Producto Maquilado-Terminado',
        'Comisiones Vendedoras'
    ])

    # Mostrar el contenido correspondiente según la pestaña seleccionada
    if pagina == 'Vista General':
        show_VistaGeneral()
    elif pagina == 'Hard Discount':
        show_HardDiscount()
    elif pagina == 'Producto Maquilado-Terminado':
        show_ProductoMaquiladoTerminado()
    elif pagina == 'Comisiones Vendedoras':
        show_ComisionesVendedoras()
    elif pagina == 'Informe General':
        show_InformeGeneral()

if __name__ == "__main__":
    # Configura la página al principio
    st.set_page_config(layout="wide")
    main()



