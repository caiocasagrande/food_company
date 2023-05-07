# Company View

# Importing libraries

import pandas               as pd
import numpy                as np
import plotly.express       as px
import streamlit            as st

import folium

from PIL                    import  Image
from streamlit_folium       import  folium_static

# ----------------------
# Functions
# ----------------------

def clean_code(df_raw):
    """
    The purpose of this function is cleaning the Dataframe

    Types of cleaning:
     1. Removal of 'NaN ' string data and its removal from Dataframe
     2. Conversion of text columns to number
     3. Conversion of text columns to datetime
     4. Time_taken(min) column split and text to number conversion
     5. Removing spaces inside strings/text/object
    
    Input: Dataframe
    Output: Dataframe
    """

    # 1. Removal of 'NaN ' string data and its removal from Dataframe

    df_clean = df_raw.replace('NaN ', np.nan).dropna()

    # 2. Conversion of text columns to number

    df_clean['Delivery_person_Age']         = df_clean['Delivery_person_Age'].astype(int)
    df_clean['Delivery_person_Ratings']     = df_clean['Delivery_person_Ratings'].astype(float)
    df_clean['multiple_deliveries']         = df_clean['multiple_deliveries'].astype(int)

    # 3. Conversion of text columns to datetime

    df_clean['Order_Date'] = pd.to_datetime(df_clean['Order_Date'], format = '%d-%m-%Y')

    # 4. Time_taken(min) column split and text to number conversion
    
    df_clean['Time_taken(min)'] = df_clean['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df_clean['Time_taken(min)'] = df_clean['Time_taken(min)'].astype(int)
    
    # 5. Removing spaces inside strings/text/object

    df_clean.loc[:, 'ID']                   = df_clean.loc[:, 'ID'].str.strip()
    df_clean.loc[:, 'Road_traffic_density'] = df_clean.loc[:, 'Road_traffic_density'].str.strip()
    df_clean.loc[:, 'Type_of_order']        = df_clean.loc[:, 'Type_of_order'].str.strip()
    df_clean.loc[:, 'Type_of_vehicle']      = df_clean.loc[:, 'Type_of_vehicle'].str.strip()
    df_clean.loc[:, 'City']                 = df_clean.loc[:, 'City'].str.strip()
    df_clean.loc[:, 'Festival']             = df_clean.loc[:, 'Festival'].str.strip()
  
    return df_clean

def orders_per_day(df):
    """ 
    This function creates a bar chart to analyse the number of orders in each day of the dataset.
    """

    df_aux = df[['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()
    fig = px.bar(df_aux, x='Order_Date', y='ID', 
                 labels={'Order_Date':'Date', 'ID': 'Quantity'})

    st.plotly_chart(fig, use_container_width=True)

    return fig

def orders_by_traffic(df):
    """ 
    This function creates a bar chart to analyse how the orders are distributed 
    according to the traffic density.
    """

    df_aux = (df.loc[:, ['ID', 'Road_traffic_density']].groupby( 'Road_traffic_density' )
                                                        .count()
                                                        .reset_index())
    df_aux['perc_ID'] = 100 * ( df_aux['ID'] / df_aux['ID'].sum() )
    fig = px.bar(df_aux, x = 'Road_traffic_density', y = 'perc_ID', 
                 labels={'Road_traffic_density':'Traffic Density', 'perc_ID': 'Percentage'})

    st.plotly_chart(fig, use_container_width=True)

    return fig

def orders_city_traffic(df):
    """ 
    This function creates a bar chart to analyse how the orders are distributed 
    according to the traffic density in each city of the dataset.
    """

    df_aux = (df[['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density'])
                                                        .count()
                                                        .reset_index())
    fig = px.scatter(df_aux, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City', 
                     labels={'City':'City', 'Road_traffic_density': 'Traffic Density'})

    st.plotly_chart(fig, use_container_width=True)

    return fig

def orders_per_week(df):
    """ 
    This function creates a column named Week_of_year to analyse how the 
    number of orders change from week to week.
    """
    
    df['Week_of_year'] = df['Order_Date'].dt.strftime('%U')
    df_aux = df[['ID', 'Week_of_year']].groupby(['Week_of_year']).count().reset_index()
    fig = px.line(df_aux, x = 'Week_of_year', y = 'ID',
                  labels={'Week_of_year': 'Week of Year', 'ID': 'Quantity'})

    st.plotly_chart(fig, use_container_width=True)

    return fig

def location_map(df):
    """ 
    This function creates a map to visualize the median point of traffic density in each city.
    """

    df_aux = (df[['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']]
              .groupby(['City', 'Road_traffic_density'])
              .median()
              .reset_index())

    map = folium.Map( location=[18.546947,75.898497], zoom_start=5.5 )

    for index, df_aux in df_aux.iterrows():
        folium.Marker( [df_aux['Delivery_location_latitude'], 
                        df_aux['Delivery_location_longitude']], 
                        popup=df_aux[['City', 'Road_traffic_density']] ).add_to( map )
        
    folium_static(map, width=800, height=500)

    return None

# ----------------------
# Load 
# ----------------------

# Import dataset

df_raw      = pd.read_csv('train.csv')
df_clean    = clean_code(df_raw)
df          = df_clean.copy()

# ----------------------
# Streamlit

st.set_page_config(page_title='Company View', layout="wide", initial_sidebar_state='expanded')

# ----------------------
# Sidebar

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width=300)

st.sidebar.markdown( '# Food Delivery Company')
st.sidebar.markdown("""---""")

st.sidebar.markdown('# Filters')
st.sidebar.markdown('## Select dates')

date_slider = st.sidebar.slider(
    'Time interval',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022,2,11),
    max_value=pd.datetime(2022,4,6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown('## Select traffic conditions')

traffic_options = st.sidebar.multiselect(
    'Traffic density',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown('## Select the city type')

city_options = st.sidebar.multiselect(
    'City type',
    ['Metropolitian','Urban','Semi-Urban'],
    default=['Metropolitian','Urban','Semi-Urban']
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('##### Powered by [Caio Casagrande](https://www.linkedin.com/in/caiopc/)')

# ----------------------
# Adapting dataset to filters

# Date filter
df = df.loc[df['Order_Date'] <= date_slider, :]

# Traffic filter
df = df.loc[df['Road_traffic_density'].isin(traffic_options), :]

# City Filter
df=df.loc[df['City'].isin(city_options),:]

# ----------------------
# Streamlit main page layout

st.markdown('# Company View')
st.markdown("""---""")

# First Section - 1 chart

with st.container():
    # 1. Quantity of orders per day
    st.markdown('## Quantity of orders per day')

    orders_per_day(df)

# Second Section - 2 charts in 2 columns

with st.container():
    
    col1, col2 = st.columns(2)

    with col1:
        # 2. Distribution of orders by type of traffic
        st.markdown('## Orders by type of traffic')

        orders_by_traffic(df)
        
    with col2:
        # 3. Comparison of order volume by city and type of traffic
        st.markdown('## Order volume by city and type of traffic')
        
        orders_city_traffic(df)

# Third Section - 1 chart

with st.container():
   
    # 4. Quantity of orders per week
    st.markdown('## Quantity of orders per week')

    orders_per_week(df)

# Fourth Section - 1 map

with st.container():
    
    st.markdown("""---""")
    st.markdown('# Geolocation')
    
    # 5. The central location of each city by type of traffic
    st.markdown('## The central location of each city by type of traffic')
    
    location_map(df)




















