# Bibliotecas
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
import folium 
from haversine import haversine
from datetime import datetime
from PIL import Image
from streamlit_folium import folium_static
import plotly.graph_objects as go
import numpy as np

#==============================================
# Import Data Set 
#==============================================

df = pd.read_csv('dataset/train.csv')

# =============================================
#Limpeza do Data Set
#==============================================

df1 = clean_code( df )

# Função para limpar valores 'NaN ', espaços e garantir apenas números
def limpar_coluna_numerica(df, coluna):
    # Garante que tudo é texto e tira espaços
    df[coluna] = df[coluna].astype(str).str.strip()
    # Mantém só as linhas com números válidos (exclui 'NaN ', 'nan', etc)
    return df[df[coluna].str.isnumeric()].copy()

# Limpeza das colunas numéricas
df1 = limpar_coluna_numerica(df1, 'Delivery_person_Age')
df1 = limpar_coluna_numerica(df1, 'multiple_deliveries')

# Limpeza das colunas categóricas que podem ter 'NaN ' como string
colunas_categoricas = ['Road_traffic_density', 'Festival', 'City']
for coluna in colunas_categoricas:
    df1[coluna] = df1[coluna].astype(str).str.strip()      # tira espaços
    df1 = df1[df1[coluna].str.lower() != 'Nan '].copy()     # remove 'NaN', 'nan', 'NaN ', etc

# Conversões de tipo
df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

# Removendo espaços das principais colunas de texto
colunas_texto = ['ID', 'Festival', 'City', 'Road_traffic_density', 'Type_of_order', 'Type_of_vehicle']
for coluna in colunas_texto:
    df1[coluna] = df1[coluna].astype(str).str.strip()

# Limpando 'Time_taken(min)' com segurança
def limpar_tempo(x):
    if isinstance(x, str) and '(min) ' in x:
        return x.split('(min) ')[1]
    return x

df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(limpar_tempo)
df1 = df1[df1['Time_taken(min)'].notna()].copy()
df1 = df1[df1['Time_taken(min)'].astype(str).str.isnumeric()].copy()
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)


linhas_selecionadas = (df1['City'] != 'NaN')
df1 = df1.loc[linhas_selecionadas, : ].copy()


#===========================================
#Barra Lateral no Streamlit
#===========================================

st.header("Marketplace Visão Restaurantes", divider=True)

image_pach = 'Fast_Delivery.png'
image = Image.open('Fast_Delivery.png')
st.sidebar.image(image, width=160)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown( """---""" )

st.sidebar.markdown('## Selecione Uma Data Limite')
date_slider = st.sidebar.slider(
        'Até qual Valor?',
        value=datetime(2022, 4, 13),
        min_value=datetime(2022, 2,12),
        max_value=datetime(2022, 4, 6),
        format='DD-MM-YYYY')
                            
st.header( date_slider )
st.sidebar.markdown( """---""" )

traffic_options = st.sidebar.multiselect(
                    'Quais as condições do Trânsito',
                     ['Low', 'Medium', 'High', 'Jam'],
                     default= ['Low', 'Medium' , 'High', 'Jam' ])


st.sidebar.markdown( """---""" )
st.sidebar.markdown('### Developed by Guilherme Gomes')

# Filtros de Datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]


# Filtros de Transitos

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]



#===========================================
#Layout Streamlit
#===========================================



tab1, tab2, tab3 = st.tabs( [ 'Visão Gerencial', '__' , '__' ] )
  
with tab1:
  with st.container():
    st.title("Overal Metrics")

    col1, col2, col3, col4, col5, col6 = st.columns ( 6 )
    with col1:
      delivery_unique = len( df1.loc[: , 'Delivery_person_ID'].unique())
      col1.metric('Entregadores Únicos' , delivery_unique )
      
    with col2:
      cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
      df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                               haversine(
                                                        (x['Restaurant_latitude'] , x['Restaurant_longitude'] ),
                                                        (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )), axis=1 )
      avg_distance = np.round( df1['distance'].mean(), 2)
      col2.metric('A distância média das Entregas', avg_distance)
      
    with col3:
      cols = [ 'Time_taken(min)' , 'Festival']

      df_aux = df1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)' : ['mean' , 'std']})
      
      df_aux.columns = ['delivery_mean' , 'delivery_std']
      
      df_aux = df_aux.reset_index()
          
      df_aux = np.round (df_aux.loc[df_aux['Festival'] == 'Yes', 'delivery_mean'], 2)

      col3.metric('Tempo médio de Entrega com Festival', df_aux)
      
    with col4:
      cols = [ 'Time_taken(min)' , 'Festival']

      df_aux = df1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)' : ['mean' , 'std']})
      
      df_aux.columns = ['delivery_mean' , 'delivery_std']
      
      df_aux = df_aux.reset_index()
          
      df_aux = np.round (df_aux.loc[df_aux['Festival'] == 'Yes', 'delivery_std'], 2)

      col4.metric('Desvio Padrão de Entrega com Festival', df_aux)


    
    with col5:
      cols = [ 'Time_taken(min)' , 'Festival']

      df_aux = df1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)' : ['mean' , 'std']})
      
      df_aux.columns = ['delivery_mean' , 'delivery_std']
      
      df_aux = df_aux.reset_index()
          
      df_aux = np.round (df_aux.loc[df_aux['Festival'] == 'No', 'delivery_mean'], 2)

      col5.metric('Tempo médio de Entrega com Festival', df_aux)
      
    with col6:
      cols = [ 'Time_taken(min)' , 'Festival']

      df_aux = df1.loc[:, cols].groupby(['Festival']).agg({'Time_taken(min)' : ['mean' , 'std']})
      
      df_aux.columns = ['delivery_mean' , 'delivery_std']
      
      df_aux = df_aux.reset_index()
          
      df_aux = np.round (df_aux.loc[df_aux['Festival'] == 'No', 'delivery_std'], 2)

      col6.metric('Desvio Padrão de Entrega com Festival', df_aux)

  with st.container():
    st.markdown( """---""" )
    

    col1, col2  = st.columns ( 2 )     
    with col1:
      cols = ['City', 'Time_taken(min)']
      df_aux = df1.loc[:, cols].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
      df_aux.columns = ['avg_time', 'delivery_std']      
      df_aux = df_aux.reset_index()      
      fig = go.Figure()
      fig.add_trace( go.Bar( name = 'Control',
                               x=df_aux['City'],
                               y=df_aux['avg_time'],
                               error_y=dict(type='data', array=df_aux['delivery_std'])))
      st.plotly_chart( fig )
    
    with col2:
      cols = ['City' , 'Type_of_order', 'Time_taken(min)']
  
      df_aux = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)' : ['mean', 'std']})
      
      df_aux.columns = ['delivery_mean', 'delivery_std']
      
      df_aux = df_aux.reset_index()
      
      st.dataframe(df_aux)
      
  with st.container():
    st.markdown( """---""" )
    st.title("Distribuição do Tempo")

    col1, col2  = st.columns ( 2 )
    with col1:
      st.markdown( '#### Distância Média' )
      cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
      df1['distance'] = df1.loc[:, cols].apply(lambda x:
                                               haversine( (x['Restaurant_latitude'] , x['Restaurant_longitude'] ),
                                                          (x['Delivery_location_latitude'], x['Delivery_location_longitude'] )), axis=1 )
    
      avg_distance = df1.loc[:, ['City' , 'distance']].groupby('City').mean().reset_index()
      fig = go.Figure( data=[ go.Pie(labels=avg_distance['City'], values= avg_distance['distance'], pull = [0, 0.1, 0])])
      st.plotly_chart( fig )
      
      
    with col2:
      st.markdown( '#### Tempo Médio e Desvio Padrão' )
      cols = ['City', 'Road_traffic_density' , 'Time_taken(min)']

      df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)' : ['mean', 'std']})
      
      df_aux.columns = ['avg_time', 'delivery_std']
      
      df_aux = df_aux.reset_index()
      
      fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                        color='delivery_std', color_continuous_scale='RdBu',
                        color_continuous_midpoint = np.average(df_aux['delivery_std']))
      st.plotly_chart( fig )
     
 





























