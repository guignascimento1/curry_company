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

df1 = df.copy()

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

st.header("Marketplace Visão Entregadores", divider=True)

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
                            
#st.header( date_slider )
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
#Layout no Streamlit
#===========================================



tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
  with st.container():
    st.title('Overall Metrics')
    col1, col2, col3, col4 = st.columns(4, gap='large')
    with col1:
           #Maior idade dos Entregadores
      maior_idade = df1.loc[: ,['Delivery_person_Age']].max()
      col1.metric('Maior Idade', maior_idade )
    
    with col2:
          
          #Menor idade dos Entregadores
      menor_idade = df1.loc[: ,['Delivery_person_Age']].min()
      col2.metric( 'Menor Idade', menor_idade )

    
    with col3:
          
      melhor_condicao = df1.loc[: ,['Vehicle_condition']].max()
      col3.metric('Melhor Condição', melhor_condicao )

    with col4:
          
      pior_condicao = df1.loc[: ,['Vehicle_condition']].min()
      col4.metric('Pior Condição', pior_condicao )


  with st.container():
    st.markdown("""---""")
    st.title( 'Avaliações')
    
    col1, col2 = st.columns(2)
    with col1:
      st.markdown('#### Avaliação Média por Entregadores')
      df2 = df1.loc[: , ['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
      st.dataframe(df2)
      
    with col2:
          st.markdown( '#### Avaliação Média por Trânsito' )
          df_avg_std_rating_by_traffic = (df1.loc[:, ['Delivery_person_Ratings' , 'Road_traffic_density']]
                                             .groupby('Road_traffic_density')
                                             .agg({'Delivery_person_Ratings' : ['mean' , 'std']}))

          df_avg_std_rating_by_traffic.columns = ['delivery_mean' ,'delivery_std']

          #reset index
          df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
          st.dataframe(df_avg_std_rating_by_traffic)
      
          st.markdown( '#### Avaliacão Média por Clima' )
          df_aux = (df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions' ]]
                        .groupby('Weatherconditions')
                        .agg({'Delivery_person_Ratings' : ['mean', 'std']})
                        .reset_index())
          df_aux.columns = ['Weatherconditions', 'delivery_mean', 'delivery_std']
          st.dataframe(df_aux)                                                           
                                                                                                                                             



  with st.container():
    st.markdown("""---""")
    st.title('Velocidade de Entrega')
    
    col1, col2 = st.columns( 2 )
    
    with col1:
      st.markdown('##### Top Entregadores mais Rápidos')
      df3 = (df1.loc[:, ['Delivery_person_ID', 'City' , 'Time_taken(min)' ]]
                .groupby(['City','Delivery_person_ID'])
                .mean()
                .sort_values(['City', 'Time_taken(min)'], ascending =True)
                .reset_index())

      df_aux01 = df3.loc[df3['City'] == 'Metropolitian', :].head(10)
      df_aux02 = df3.loc[df3['City'] == 'Urban', :].head(10)
      df_aux03 = df3.loc[df3['City'] == 'Semi-Urban', :].head(10)

      df4 = pd.concat([ df_aux01, df_aux02, df_aux03 ]).reset_index(drop=True)
      st.dataframe( df4 )
    
    with col2:
      st.markdown('##### Top Entregadores Mais Lentos')
      df3 = (df1.loc[:, ['Delivery_person_ID', 'City' , 'Time_taken(min)' ]]
                .groupby(['City','Delivery_person_ID'])
                .mean()
                .sort_values(['City', 'Time_taken(min)'], ascending =False)
                .reset_index())

      df_aux01 = df3.loc[df3['City'] == 'Metropolitian', :].head(10)
      df_aux02 = df3.loc[df3['City'] == 'Urban', :].head(10)
      df_aux03 = df3.loc[df3['City'] == 'Semi-Urban', :].head(10)

      df4 = pd.concat([ df_aux01, df_aux02, df_aux03 ]).reset_index(drop=True)
      st.dataframe( df4 )

























