# Libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt

# bibliotecas necessárias
import folium
import pandas as pd
import numpy as np
import streamlit as st

from streamlit_folium import folium_static
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
from PIL import Image
from datetime import datetime 
from itertools import count

st.set_page_config( page_title='Visão Restaurante', page_icon=':)', layout='wide')


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

# --------- gera tabela de tempo médio --------------
def time_mean(df1):
    df2 = (df1.loc[:, ['City','Time_taken(min)', 'Type_of_order']]
               .groupby(['City', 'Type_of_order'])
               .agg({'Time_taken(min)':['mean', 'std']}))

    df2.columns = ['Time mean', 'Time std']
    df8 = df2.reset_index()
    return df8

# --------- gera calculo da distancia --------------
def distance(df1, fig):    
    # calculo das distancias
    cols2 = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    
    df1['distance'] = (df1.loc[:, cols2]
                          .apply( lambda x: haversine
                                 ((x['Restaurant_latitude'],x['Restaurant_longitude']),
                                  (x['Delivery_location_latitude'],x['Delivery_location_longitude'])), axis=1 ))  
        
    # ----------- gera cálculo distânca média total -----------------
    if fig == False:
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance

    # ---------- gera gráfico das distancias médias --------------
    else:
        avg_distance3 = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig7 = go.Figure(data=[ go.Pie(labels=avg_distance3['City'], values=avg_distance3['distance'], pull=[0, 0.05, 0] )])    
        return fig7

# --------- gera calculo do tempo médio no festival -------------
def festival(df1, festival, col):
    """ Esta função cálcula o tempo médio e o desvio padrão do tempo de entrega.
        Parâmetros: 
            Input: - df: Dataframe com dados necessários para o cálculo;
                   - festival: parâmetro para saida de cálculo ;
                               'Yes' : seleciona linha que houve Festival;
                               'No'  : seleciona linha que não houve Festival;
                   - col: Tipo de operação que precisa ser calculado;
                           'avg_time': cálcula o tempo médio;
                           'std_time': cálcula o desvio padrão;
           Output: - df: Dataframe com 2 colunas e 1 linha.
    
    """
    df_calc3 = (df1.loc[:, ['Festival','Time_taken(min)']]
                   .groupby('Festival')
                   .agg({'Time_taken(min)':['mean', 'std']}))

    df_calc3.columns = ['avg_time', 'std_time']
    df_calc3 = df_calc3.reset_index()
    df_calc3 = np.round(df_calc3.loc[df_calc3['Festival'] == festival, col], 2)

    return df_calc3

# --------- gera gráfico tempo médio e desvio padrão cidade -------------
def avg_std_time_graf(df1):
    df_calc8 = (df1.loc[:, ['City','Time_taken(min)']] 
                   .groupby('City')
                   .agg({'Time_taken(min)':['mean', 'std']}))

    df_calc8.columns = ['avg_time', 'std_time']

    df_calc8 = df_calc8.reset_index()

    fig8 = go.Figure()
    fig8.add_trace( go.Bar( name='Control', 
                           x=df_calc8['City'], 
                           y=df_calc8['avg_time'], 
                           error_y=dict( type='data', array=df_calc8['std_time'])))

    fig8.update_layout(barmode='group')  
    return fig8

# --------- gera gráfico tempo médio e desvio padrão do tráfego da cidade -------------
def avg_std_time_on_traffic(df1):
    df_calc9 = (df1.loc[:, ['City','Time_taken(min)', 'Road_traffic_density']]
                   .groupby(['City', 'Road_traffic_density'])
                   .agg({'Time_taken(min)':['mean', 'std']}))

    df_calc9.columns = ['avg_time', 'std_time']

    df_calc9 = df_calc9.reset_index()

    fig9 = (px.sunburst(df_calc9, path=['City', 'Road_traffic_density'],
                                  values='avg_time', color='std_time', 
                                  color_continuous_scale='RdBu',                                  color_continuous_midpoint=np.average(df_calc9['std_time']))) 
    return fig9



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
st.header('Marketplace - Visão Restaurantes')
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
        st.title('Overal Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        
        with col1:
            # calculo dos entregadores
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique() )
            col1.metric('Nº Entregadores', delivery_unique)
            
        with col2:
            distancia = distance(df1, False)            
            col2.metric('Distância média', distancia)
            
        with col3:
            med_festival = festival(df1, 'Yes', 'avg_time')           
            col3.metric('Tempo médio de entrega Festival', med_festival)
            
        with col4:
            med_festival = festival(df1, 'Yes', 'std_time')            
            col4.metric('Desvio Padrão do tempo entrega Festival', med_festival)            
            
        with col5: 
            med_festival = festival(df1, 'No', 'avg_time')           
            col5.metric('Tempo médio sem Festival', med_festival)
            
        with col6: 
            med_festival = festival(df1, 'No', 'std_time')            
            col6.metric('Desvio Padrão do tempo entrega sem Festival', med_festival) 
    st.markdown("""___""") 
        
    with st.container():
        st.markdown('###### Distribução do tempo')
        fig8 = avg_std_time_graf(df1)
        st.plotly_chart(fig8, use_container_width=True) 


    st.markdown("""___""")    
    
    with st.container():
        st.markdown("""___""")
        st.title("Distribuição do tempo")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Tempo médio entrega por cidade em %')
            # calculo das distancias
            fig7 = distance(df1, True)
            st.plotly_chart(fig7, use_container_width=True)               
                        
            
        with col2:            
            st.markdown('##### Std entrega por cidade')
            fig9 = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig9, use_container_width=True)
        
    
    
    with st.container():
        st.markdown("""___""")
        st.markdown('##### Tabela do tempo médio e desvio padrão do tráfego da cidade')
        df8 = time_mean( df1 )        
        st.dataframe(df8, use_container_width=True)
