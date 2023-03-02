import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon=":)"
)

# image_path = '/Users/esiomds/documents/repos/FTC/ciclo5/exer/'
image = Image.open('logo.png')
st.sidebar.image(image, width=200)

st.sidebar.markdown('# Mazáá Sushi Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.write("# Mazáá Sushi Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as métricas de crescimento do Entregadores e Restaurantes.
    ### Como utilizar ess Graowth Dashboard ?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregador:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanis de crescimento dos restaurantes.
        
    ### Ask for Help
    - Time de Data Science no Discord
        - @meigarom
    
    """

)




