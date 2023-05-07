# Restaurants View

# Libraries

import pandas               as pd
import numpy                as np
import plotly.express       as px
import plotly.graph_objects as go
import streamlit            as st
import folium
import haversine 

from PIL                    import  Image
from haversine              import  haversine
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

def time(df, decision, parameter):
    """
    Description.

    decision = 'Yes' or 'No'
    parameter = 'avg_time' or 'std_time'
    """
    df_aux = df[['Time_taken(min)', 'Festival']].groupby(['Festival']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = np.round(df_aux.reset_index(), 2)
    results = df_aux.loc[df_aux['Festival'] == decision, parameter]

    return results

def distance(df):
    """
    This function generates a distance result between the restaurantes 
    and the delivery location point and then display a bar chart with the average result.
    """

    df['distance'] = (df.apply( lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude'] ), 
                                                    (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1))
    avg_distance = (df.loc[:, ['City', 'distance']]
                    .groupby(['City']).mean().reset_index())
        
    fig = go.Figure()
    fig.add_trace(go.Bar(x = avg_distance['City'],
                         y = avg_distance['distance']
                         ))
        
    fig.update_layout(width=500)
    st.plotly_chart(fig)

    return fig

def time_taken(df):
    """
    This function generates a bar chart for the average and std time taken for each type of city.
    """

    df_aux = df[['Time_taken(min)', 'City']].groupby(['City']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()  

    fig = go.Figure()
    fig.add_trace(go.Bar(name = 'Control',
                        x = df_aux['City'],
                        y = df_aux['avg_time'],
                        error_y = dict(
        type='data', array = df_aux['std_time']
                        )))

    fig.update_layout(barmode='group', width=500)
    st.plotly_chart(fig)
    
    return fig

def time_city_order(df):
    """
    This function generates a dataframe with the time taken for each type of order for each type of city.
    """
    df_aux = (df[['City', 'Time_taken(min)', 'Type_of_order']]
              .groupby(['City', 'Type_of_order'])
              .agg({'Time_taken(min)': ['mean', 'std']}))
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    st.dataframe(df_aux)
    
    return df_aux

def sunburst_chart(df):
    """
    This function creates a sunburst chart for the time taken.
    """

    df_aux = (df[['City', 'Time_taken(min)', 'Road_traffic_density']]
              .groupby(['City', 'Road_traffic_density'])
              .agg({'Time_taken(min)': ['mean', 'std']}))
    
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values = 'avg_time', 
                      color = 'std_time', color_continuous_scale='RdBu', 
                      color_continuous_midpoint=np.average(df_aux['std_time']))
    
    fig.update_layout(width=500)
    
    st.plotly_chart(fig)
    
    return fig

# ----------------------
# Load 
# ----------------------

# Import dataset

df_raw      = pd.read_csv('train.csv')
df_clean    = clean_code(df_raw)
df          = df_clean.copy()

# ----------------------
# Streamlit

st.set_page_config(page_title='Restaurants View', layout="wide", initial_sidebar_state='expanded')

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

st.markdown('# Restaurants View')
st.markdown("""---""")

with st.container():
        
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        number_deliverymen = len(df['Delivery_person_ID'].unique())
        col1.metric('Number of deliverymen', number_deliverymen)

    with col2:
        results = time(df, 'No', 'avg_time')
        col2.metric('Usual average time', results)

    with col3:
        results = time(df, 'No', 'std_time')
        col3.metric('Usual std. time', results)

    with col4:
        results = time(df, 'Yes', 'avg_time')
        col4.metric('Average time during festival', results)

    with col5:
        results = time(df, 'Yes', 'std_time')
        col5.metric('Std. time during festival', results)

with st.container():
    st.markdown("""---""")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown('### Average distance by city (km)')
        st.write('The average distance is measured between the restaurants and the delivery points.')
        
        distance(df)
    
    with col2:
        st.markdown('### Time delivery by city (min)')
        st.write('The chart displays the average time taken for the deliveries with the standard deviation indicator at the top of each bar.')
        
        time_taken(df)

with st.container():
    st.markdown("""---""")

    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('### Average time and standard deviation by city and type of order')
        
        time_city_order(df)


    with col2:
        st.markdown('### Delivery time by city and traffic')
        st.write('The average time are displayed as the values and the standard deviation as the colors.')
        
        sunburst_chart(df)
        

