import streamlit as st
from PIL import Image

st.set_page_config(
  page_title= "Home",
  page_icon= "🎲" )


#image_path = 'C:/Users/finan/OneDrive/Desktop/Gui/Comunidade DS/Repos/FTC_Python/' 
image = Image.open ( 'Fast_Delivery.png' )
st.sidebar.image( image, width = 120)



#======================
# Barra Lateral
#======================


st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown( """---""" )


st.write("# Curry Company Growth Dashboard")

st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as metricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visão Empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de Crescimento.
        - Visão Geográfica: Insights de Geolocalização.
    - Visão Entregadores: 
        - Acompanhamento dos indicadores Semanais de crescimento
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Meu Linkedin: www.linkedin.com/in/guilherme-gomes-nascimento-04614b188
      
    """)
