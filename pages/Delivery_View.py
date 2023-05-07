# Delivery View

# Libraries

import pandas               as pd
import numpy                as np
import plotly.graph_objects as go
import streamlit            as st

from PIL                    import  Image

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

def rating_average_std(df, column):
    """
    Description
    """
        
    df_aux = (df[['Delivery_person_Ratings', column]]
              .groupby([column])
              .agg({'Delivery_person_Ratings': ['mean', 'std']}))
        
    df_aux.columns = ['avg_rating', 'std_rating']
    df_aux = df_aux.reset_index()

    fig = go.Figure()

    fig.add_trace(go.Bar(x = df_aux[column],
                         y = df_aux['avg_rating'],
                         error_y = dict(type='data', array = df_aux['std_rating'])
                         ))
    
    fig.update_layout(barmode='group', width=500)
    st.plotly_chart(fig)

    return fig

def delivery_speed(df, boolean):
    """
    Description
    """
    
    df_aux = (df[['Delivery_person_ID', 'Time_taken(min)', 'City']]
                        .groupby(['City', 'Delivery_person_ID']).mean()
                        .sort_values(by=['City','Time_taken(min)'], ascending = boolean).reset_index())
        
    df_aux1 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux2 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    df_aux3 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)
    df_aux = pd.concat([df_aux1, df_aux2, df_aux3])
        
    st.dataframe(df_aux)

    return df_aux


# ----------------------
# Load  
# ----------------------

# Import dataset

df_raw      = pd.read_csv('train.csv')
df_clean    = clean_code(df_raw)
df          = df_clean.copy()

# ----------------------
# Streamlit

st.set_page_config(page_title='Delivery View', layout="wide", initial_sidebar_state='expanded')

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

st.markdown('# Delivery View')
st.markdown("""---""")

# First Section

with st.container():
    st.title('General Information')

    col1, col2, col3, col4 = st.columns(4, gap='large')

    with col1:
        # st.subheader('Coluna 1')
        oldest_deliveryman = df['Delivery_person_Age'].max()
        col1.metric('Oldest Deliveryman', oldest_deliveryman)

    with col2:
        # st.subheader('Coluna 2')
        youngest_deliveryman = df['Delivery_person_Age'].min()
        col2.metric('Youngest Deliveryman', youngest_deliveryman)

    with col3:
        # st.subheader('Coluna 3')
        best_condition = df['Vehicle_condition'].max()
        col3.metric('Best Vehicle Condition', best_condition)

    with col4:
        # st.subheader('Coluna 4')
        worst_condition = df['Vehicle_condition'].min()
        col4.metric('Worst Vehicle Condition', worst_condition)

# Second Section

st.markdown("""---""")

with st.container():
    
    st.title('Average Rating')

    st.write(
        """
        Bar Charts were developed in order to figure out which of the main topics might influence the average rating.
        Along with the averages, standard errors sticks are displayed at the top of the bars. \n
        As a result of the following, we are able to affirm that there is not much discrepancy in the same chart between its conditions.
        """
        )

    col1, col2 = st.columns(2, gap='large')

    with col1:
        st.markdown('### By vehicle condition')
        
        rating_average_std(df, 'Vehicle_condition')

        st.markdown('### By type of order')

        rating_average_std(df, 'Type_of_order')

    with col2:
        st.markdown('### By traffic density')
        
        rating_average_std(df, 'Road_traffic_density')

        st.markdown('### By weather condition')
        
        rating_average_std(df, 'Weatherconditions')
    

# Third Section

st.markdown("""---""")

with st.container():
      
     st.title('Delivery Speed')
     
     col1, col2 = st.columns(2, gap='large')

     with col1:
        st.subheader('Fastest Delivery Person')
        st.markdown('##### on average by city')

        delivery_speed(df, True)

    
     with col2:
        st.subheader('Slowest Delivery Person')
        st.markdown('##### on average by city ')

        delivery_speed(df, False)
        
