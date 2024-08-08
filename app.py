from PIL import Image
import streamlit as st
from VistaGeneral import show as show_VistaGeneral
from InformeGeneral import show as show_InformeGeneral
from HardDiscount import show as show_HardDiscount
from ProductoMaquiladoTerminado import show as show_ProductoMaquiladoTerminado
from AnalisisDeVentasAnualesYMensuales import show as show_AnalisisAnualMensual

# Clave de acceso
ACCESS_KEY = 'Servipan2024'

# Función para cargar y redimensionar la imagen
def load_and_resize_image(image_path, width):
    img = Image.open(image_path)
    height = int((width / img.width) * img.height)
    return img.resize((width, height))

# Función para autenticar al usuario
def authenticate():
    
    st.title('Autenticación')
    # Aplicar estilos CSS para el campo de entrada de texto
    st.markdown(
        """
        <style>
        .stTextInput input[type="password"] {
            background-color: #333333;  /* Color de fondo más oscuro */
            color: #FFFFFF;  /* Color del texto en blanco */
            border: 1px solid #555555;  /* Color del borde del campo */
            border-radius: 4px;  /* Bordes redondeados */
            padding: 10px;  /* Espaciado interno */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    key = st.text_input('Introduce la clave de acceso:', type='password')
    
    if key == ACCESS_KEY:
        st.session_state.authenticated = True
        st.success('Clave correcta. Acceso concedido.')
    else:
        st.session_state.authenticated = False
        st.error('Clave incorrecta. Intenta de nuevo.')

def main():
    # Verificar el estado de autenticación
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    # Autenticación
    if not st.session_state.authenticated:
        authenticate()
        return
    
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
        'Analisis Mensual-Anual'
    ])

    # Mostrar el contenido correspondiente según la pestaña seleccionada
    if pagina == 'Vista General':
        show_VistaGeneral()
    elif pagina == 'Hard Discount':
        show_HardDiscount()
    elif pagina == 'Producto Maquilado-Terminado':
        show_ProductoMaquiladoTerminado()
    elif pagina == 'Analisis Mensual-Anual':
        show_AnalisisAnualMensual()
    elif pagina == 'Informe General':
        show_InformeGeneral()

if __name__ == "__main__":
    # Configura la página al principio
    st.set_page_config(layout="wide")
    main()
