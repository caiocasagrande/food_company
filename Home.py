# Home Page

import streamlit as st

from PIL import Image

st.set_page_config(
    page_title='Home',
    page_icon='🎲'
)

image = Image.open('logo.png')

st.sidebar.image(image, width=300)

st.sidebar.markdown('# Food Delivery Company')
st.sidebar.markdown("""---""")
st.sidebar.markdown('##### Powered by [Caio Casagrande](https://www.linkedin.com/in/caiopc/)')

st.write('# Food Delivery Company')

st.markdown(
    """
    This Growth Dashboard Page was developed to monitor the growth metrics between the company, the deliverymen and the restaurants.
    
    ### How to use the Growth Dashboard Page?

    - Company View:
        - Quantity of orders per day and per week;
        - How the orders behave in different traffic and city type conditions;
        - Geolocation for the median points of traffic in each city.
    
    - Delivery View:
        - General information about the deliverymen;
        - Average rating by vehicle condition, traffic density, type of order and weather conditions;
        - The fastest and slowest deliverymen by type of city.
    
    - Restaurants View:
        - General information about delivery time;
        - Average distance and time by type of city;
        - Average time by city and type of order;
        - Delivery time by city and traffic.

    - Observations:
        - There are filter options in three views above, like date interval, traffic conditions and city type to select. 
    ### Contato:
    """
)

st.write('Check out my [LinkedIn](https://www.linkedin.com/in/caiopc/) profile or my [GitHub](https://github.com/caiocasagrande) page to get in contact with me.')
