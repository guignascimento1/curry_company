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


#===========================================
#Barra Lateral no Streamlit
#===========================================

st.header("Marketplace Visão Empresa", divider=True)

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
        min_value=datetime(2022, 2,11),
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


#st.dataframe(df1)

#print ( 'Estou Aqui' )


# Filtros de Datas
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]


# Filtros de Transitos

linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]


st.dataframe(df1.head())


#===========================================
#Layout no Streamlit
#===========================================



tab1, tab2, tab3 = st.tabs(['Visão Gerancial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
  with st.container():
          #Order Matric
            st.markdown('# Orders by Day')
            cols = ['ID', 'Order_Date']
      
          #seleção de linhas
      
            df_aux = df1.loc[: , cols].groupby('Order_Date').count().reset_index()
      
          # Desenhar Gráfico de linhas
            
            fig = px.bar(df_aux, x='Order_Date', y='ID' )
            st.plotly_chart(fig, use_container_width=True)
          
            col1, col2 = st.columns(2)
            with col1:
              st.header('Traffic Order Share')
              df_aux = df1.loc[: , ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
              df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
              df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'] .sum()

              # grafico de pie
              
              fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
              st.plotly_chart( fig, use_container_width=True )

    
            with col2:
              st.header('Traffic Order City')
              df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()

              # Removendo Caracter 'NaN'
              
              df_aux = df_aux.loc[df_aux['City'] != "NaN", :]
              df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
              
              # Criar um Gráfico de Bolhas
              
              fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='ID', hover_name='City')
              st.plotly_chart( fig, use_container_width=True )



with tab2:
    with st.container():
        st.markdown("# Order By Week")
        # Criar a coluna de semana
    
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        
        # Agrupar Colunas
        
        df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        
        # Desenhar Gráfico de Linhas
        
        fig = px.line(df_aux, x='week_of_year', y='ID')
        st.plotly_chart(fig, use_container_width=True )
    
    with st.container():
      st.markdown("# Order Shere By Week")
      df_aux01 = df1.loc[: , ['ID','week_of_year' ]].groupby( ['week_of_year'] ).count().reset_index()

      df_aux02 = df1.loc[: , ['Delivery_person_ID', 'week_of_year']].groupby( ['week_of_year'] ).nunique().reset_index()
      
      
      #juntar dois DataFrame
      
      df_aux = pd.merge(df_aux01, df_aux02, how='inner')
      
      # Realizar a divisão entre dois DataFrames
      
      df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
      
      df_aux
      # Desenhar Gráfico de Linhas
      
      fig = px.line(df_aux, x='week_of_year', y='order_by_delivery')
      st.plotly_chart( fig, use_container_width=True )
      
with tab3:
    st.markdown("# Country Maps")
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude' ]].groupby(['City', 'Road_traffic_density']).median().reset_index()

    df_aux = df_aux.loc[df_aux['City'] != "NaN", :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
    map = folium.Map( zoom_start=11 )

    for index, location_info in df_aux.iterrows():
      folium.Marker( [location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
                     popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )
       
    folium_static(map, width= 1024, height=600)

































