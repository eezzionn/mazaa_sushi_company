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

st.set_page_config( page_title='Visão Empresa', layout='wide')

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

# --------- gera gráfico order metric --------------
def order_metric(df1):
    # recebe ascolunas
    cols = ['ID', 'Order_Date']
    # seleção de linhas
    df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
    #desenhar o gráfico de barras
    fig = px.bar( df_aux, x='Order_Date', y='ID' )
    return fig

# --------- gera gráfico traffic order share --------------
def traffic_order_share( df1 ):
    # colunas
    df_aux = (df1.loc[:,['ID','Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count().reset_index())
    # seleção de linhas
    df_aux['entrega_perc'] = df_aux['ID'] / df_aux['ID'].sum() 
    fig2 = px.pie( df_aux, values='entrega_perc', names='Road_traffic_density' )
    return fig2

# --------- gera gráfico traffic order city --------------
def traffic_order_city( df1 ):
    df_aux = (df1.loc[:, ['ID', 'Type_of_vehicle', 'City']]
                 .groupby('City')
                 .count().reset_index())
    fig3 = px.scatter(df_aux, x='City', y='Type_of_vehicle', size='ID', color='City')
    return fig3
    
# --------- gera gráfico order by week --------------    
def order_by_week( df1 ):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = (df1.loc[:, ['ID', 'week_of_year']]
                 .groupby('week_of_year')
                 .count().reset_index())
    fig4 = px.line(df_aux, x='week_of_year', y='ID')
    return fig4    
 
# --------- gera gráfico order share week -------------- 
def order_share_week( df1 ):
    df_aux1 = (df1.loc[:, ['ID', 'week_of_year']]
                  .groupby('week_of_year')
                  .count().reset_index())
    df_aux2 = (df1.loc[:, ['Delivery_person_ID', 'week_of_year']]
                  .groupby('week_of_year')
                  .nunique().reset_index())

    # unificando tabelas
    df_aux = pd.merge(df_aux1, df_aux2, how="inner", on='week_of_year')
    df_aux['order_by_delivery'] = df_aux['ID']/df_aux['Delivery_person_ID']

    fig5 = px.line(df_aux, x='week_of_year', y='order_by_delivery')
    return fig5
 
# --------- gera contry map --------------     
def country_maps( df1 ):
    cols = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df_aux = (df1.loc[:, cols]
                 .groupby(['City', 'Road_traffic_density'])
                 .median().reset_index())

    map = folium.Map( location=[21.92, 77.9], zoom_start=5 )    
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']], 
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to(map)
       
    st_folium( map, width=1024, height=600 )
    
# --------- gera contry map 2 de clusters--------------     
def country_maps2( df1 ):
    df2 = ( df1.loc[ (df1['Delivery_location_latitude'] < 33.0 ) & 
                    (df1['Delivery_location_latitude'] > 7.0 ) & 
                    (df1['Delivery_location_longitude'] > 67.0 ) & 
                    (df1['Delivery_location_longitude'] < 89.0 ), :] )

    linhas_selecionadas = df2['Festival'] == 'Yes'
    cols = ['City','Festival','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    df_aux = (df2.loc[linhas_selecionadas, cols]).reset_index()

    map2 = folium.Map( location=[21.92, 77.9], zoom_start=5 )
    mc = MarkerCluster()

    for index, location_info in df_aux.iterrows():
      mc.add_child(folium.Marker( [location_info['Delivery_location_latitude'],
                                   location_info['Delivery_location_longitude']], 
                                  popup=str(location_info[['City', 'Road_traffic_density']]),
                                   icon=folium.Icon(icon='book'))).add_to(map2)
       
    st_folium( map2, width=1024, height=600 )    
    

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
st.header('Marketplace - Visão Cliente')

#image_path = '/Users/esiomds/documents/repos/FTC/ciclo5/exer/logo.png'
image = Image.open('logo.png')
st.sidebar.image(image, width=200 )

st.sidebar.markdown('# Mazáá Sushi Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual data ?',
    value= dt.datetime( 2022, 4, 13),
    min_value= dt.datetime(2022, 2, 11),
    max_value= dt.datetime(2022, 4, 6),
    format='DD-MM-YYYY'  )

st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito ?',
    ['Low','Medium','High','Jam'],
    default=['Low','Medium','High','Jam'] )

st.sidebar.markdown("""___""")
st.sidebar.markdown('### Powered by Comunidade DS')

#filtro de data do dashboard

linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

#filtro de transito do dashboard
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# ==========================================
# Layout do dashboard no Streamlit      
# ==========================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        # Order Metric para criação do gráfico
        fig = order_metric( df1 )
        st.markdown('# Orders by Day')
        # desenho do gráfico no streamlit
        st.plotly_chart( fig, use_container_width=True)
    
    #criando 2(dois) gráficos lado a lado
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            # traffic order share para criação de gráfico
            fig2 = traffic_order_share( df1 )
            st.markdown('##### Traffic Order Share')            
            # desenho do gráfico no streamlit
            st.plotly_chart( fig2, use_container_width=True)

        with col2:
            # traffic order city para criação de gráfico
            fig3 = traffic_order_city( df1 )
            st.markdown('##### Traffic Order City')
            #desenho do gráfico no streamlit
            st.plotly_chart( fig3, use_container_width=True)
            
# ====================================================    
with tab2:
    with st.container():
        # order by week para criação de gráfico
        fig4 = order_by_week( df1 )
        st.markdown(' Order by Week')
        # desenho do gráfico no streamlit
        st.plotly_chart( fig4, use_container_width=True)
        
    with st.container():
        # order share week para criação de gráfico
        fig5 = order_share_week( df1 )
        st.markdown(' Order Share by week')
        # desenho do gráfico no streamlit
        st.plotly_chart( fig5, use_container_width=True)
    
#=====================================================    
with tab3:
    with st.container():
        st.markdown('### Mapa de distância média dos clientes')
        # criação do Contry map
        country_maps( df1 )
        
    with st.container():
        st.sidebar.markdown("""___""")
        st.markdown('### Mapa de clusters no Festival')
        st.markdown('### Número de vendas por região')
        # criação do Contry map
        country_maps2( df1 ) 
