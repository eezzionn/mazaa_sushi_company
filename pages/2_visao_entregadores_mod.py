# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

# bibliotecas necessárias
import pandas as pd
import numpy as np
import streamlit as st
import folium

from streamlit_folium import st_folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster
from PIL import Image
from datetime import datetime 
from itertools import count


st.set_page_config( page_title='Visão Entregadores', page_icon=':)', layout='wide')


# ==========================================
# Funções        
# ==========================================

# --------- limpeza dos dados --------------
def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe
        
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudanção do tipo de coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)    
        
        Input: Dataframe
        Output: Dataframe    
    """
    # 1. Remoção dos dados NaN
    # Remove as linhas que tenham o conteudo igual a 'NaN '
    linhas_vazias = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :].copy()

    linhas_vazias = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :].copy()

    linhas_vazias = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :].copy()

    linhas_vazias = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :].copy()

    linhas_vazias = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_vazias, :].copy()

    # 2. Mudanção do tipo de coluna de dados
    # Conversao de texto/categoria/string (object) para numeros inteiros (int)
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    # Conversao de texto/categoria/string (object) para numeros decimais (float)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    # Conversao de texto/categoria/string (object) para data (datetime)
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    # Conversao de texto/categoria/string (object) para numeros inteiros (int)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    # 3. Remoção dos espaços das variáveis de texto
    # Remover spaco da string com método .str
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()

    
    # 5. Limpeza da coluna de tempo (remoção do texto da variável numérica)    
    df1['Time_taken(min)']  = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1] )
    # 4. Formatação da coluna de datas
    df1['Time_taken(min)']  = df1['Time_taken(min)'].astype(int)

    return df1

# --------- gera matriz dos top mais lentos / rápidos --------------
def top_delivers(df1, top_asc):
    df6 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
               .groupby(['City', 'Delivery_person_ID'])
               .max().sort_values(['City', 'Time_taken(min)'], ascending=top_asc)
               .reset_index() )

    df_aux01 = df6.loc[ df6['City'] == 'Metropolitian', :].head()
    df_aux02 = df6.loc[ df6['City'] == 'Urban', :].head()
    df_aux03 = df6.loc[ df6['City'] == 'Semi-Urban', :].head()

    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index( drop=True)
    return df3

# --------- gera tabela da média de trafego --------------
def avg_traffic(df1):    
    avg_traffic = (df1.loc[:, ['Road_traffic_density', 'Delivery_person_Ratings']]
                  .groupby('Road_traffic_density')
                  .agg({'Delivery_person_Ratings':['mean', 'std']}))

    avg_traffic.columns = ['delivery mean', 'delivery std']
    avg_traffic = avg_traffic.reset_index()

    return avg_traffic

# --------- gera tabela da média e desvio padrão do tipo de clima --------------
def avg_std_weather(df1):
    avg_std_weather = (df1.loc[:, ['Delivery_person_Ratings','Weatherconditions', ]]
                  .groupby('Weatherconditions')
                  .agg({'Delivery_person_Ratings':['mean', 'std']}))

    avg_std_weather.columns = ['delivery mean', 'delivery std']
    avg_std_weather = avg_std_weather.reset_index()

    return avg_std_weather











# -------------------------- Início da Estrutura Lógica de código ---------------------------

# ----------------------------------------
# Import dataset
# ----------------------------------------
df = pd.read_csv('dataset/train.csv')

# ----------------------------------------
# Limpando os dados
# ----------------------------------------
df1 = clean_code(df)

# ==========================================
# Barra Lateral         
# ==========================================
st.header('Marketplace - Visão Entregadores')

#image_path = '/Users/esiomds/documents/repos/FTC/ciclo5/exer/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=200 )

st.sidebar.markdown('# Mazáá Sushi Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Arraste o botão',
    value= dt.datetime( 2022, 4, 13),
    min_value= dt.datetime(2022, 2, 11),
    max_value= dt.datetime(2022, 4, 6),
    format='DD-MM-YYYY'  )

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Selecione as condições do trânsito',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'] )

weather_options = st.sidebar.multiselect(
    'Selecione as condições climáticas',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'] )

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

#filtro de data do dashboard

linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito do dashboard
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#filtro de clima do dashboard
linhas_selecionadas = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selecionadas, :]

# ==========================================
# Layout do dashboard no Streamlit      
# ==========================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1: 
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # maior idade do entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)
            
        with col2:
            # menor idade do entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)
            
        with col3:
            # melhor condição dos veiculos
            melhor = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor Condição Veiculo', melhor)
            
        with col4:
            # Pior condição dos veiculos
            pior = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior Condição Veiculo', pior)
            
    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Avaliações médias por entregador')
            df_avg_per_deliver = ( df1.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                               .groupby('Delivery_person_ID').mean()
                                                .reset_index() )           
            # tabela
            st.dataframe(df_avg_per_deliver)
            
        with col2:    
            # primeira tabela
            st.markdown('##### Avaliação por tipo de transito')
            tabela1 = avg_traffic(df1)            
            # exibição da tabela
            st.dataframe(tabela1)
            
            # segunda tabela
            st.markdown('##### Avaliação por tipo de  clima')
            tabela2 =avg_std_weather(df1)
            # exibição da tabela
            st.dataframe(tabela2)
            
    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            tabela3 = top_delivers(df1, top_asc=True)
            # exibição da tabela
            st.dataframe(tabela3, use_container_width=True)
            
            
        with col2:    
            st.markdown('##### Top Entregadores mais lentos')
            tabela4 = top_delivers(df1, top_asc=False)
            # exibição da tabela
            st.dataframe(tabela4, use_container_width=True)


            

    
                