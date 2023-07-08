#imports
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
import datetime
import pickle
from pathlib import Path
import streamlit_authenticator as stauth

#User authentication
names = ["Bongo", "Joe", "Mohamed"]
usernames = ["bongo", "joe","mohamed"]
passwords = ['xxx', 'xxx', 'xxx']

# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

credentials = {
    "usernames": {
        usernames[0]: {
            "name": names[0],
            "password": hashed_passwords[0]
        },
        usernames[1]: {
            "name": names[1],
            "password": hashed_passwords[1]
        },
        usernames[2]: {
            "name": names[2],
            "password": hashed_passwords[2]
        }
    }
}


authenticator = stauth.Authenticate(credentials, "SRP", "auth", cookie_expiry_days=30)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status == True:

    # css connection
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    #google sheet connection
    SERVICE_ACCOUNT_FILE = 'keys.json'
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    credentials= None

    credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # The ID and range of a sample spreadsheet.
    SAMPLE_SPREADSHEET_ID = '1mPpKMXAfYssoe5Zo-Ckz9XbBeb9r3gUq4FgqylH-ujk'

    service = build('sheets', 'v4', credentials=credentials)

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                                range="A1:L2000").execute()
    values = result.get('values', [])

    # Convert the array of arrays to a pandas DataFrame
    df = pd.DataFrame(values, columns=['Date','Time','Channel','Branch','Phone number','first name','Last name','email','Address','Sales','Items','Item Category'])

    # Convert the 'Date' column to datetime data type
    df['Date'] = pd.to_datetime(df['Date'])

    # Branch selection
    customer_select = df['Phone number'].unique()
    p_id = st.sidebar.selectbox("Choose customer Phone number", customer_select)


    # Filter rows based on dates using .query() method
    fil_df = df[(df['Phone number'].isin([p_id]))]

    # Convert the 'Price' column to numeric data type
    fil_df['Sales'] = pd.to_numeric(fil_df['Sales'])

    # current date for days since last order
    current_date = pd.Timestamp.today()
    last_order_date = fil_df['Date'].max()

    # Select the items by index
    name = fil_df['first name'].max() + " " + fil_df['Last name'].max()
    phone = fil_df['Phone number'].max()
    email = fil_df['email'].max()
    last_od = str(last_order_date)[:10]
    days_since_last_order = str(current_date - last_order_date)[:8]
    mon_v = fil_df['Sales'].sum()
    tcs = fil_df['Sales'].count()
    avc = mon_v / tcs

    #page contents
    st.title(f"{name}'s Profile")

    # Use columns layout manager
    col1, col2 = st.columns(2)

    #Display the selected items

    col1.metric(label="Name",value= name)
    col2.metric(label="Lifetime value",value= "{:,.1f}".format(mon_v))
    col1.metric(label="Days since last order", value=days_since_last_order)
    col2.metric(label="Email",value= email)
    col2.metric(label="Phone number",value= phone)
    col1.metric(label="Transactions", value=tcs)
    col2.metric(label="Last order date", value=last_od)
    col1.metric(label="Average order value", value= "{:,.1f}".format(avc))

    # Customer behaviour section
    with st.container():
        st.write(f'''
            ## {name}'s Behaviour
    ''')
        # Use columns layout manager
        col1, col2 = st.columns(2)

        #Display a channel breakdown of sales in a pie chart
        # Calculate the total sales for each branch
        channel_sales = fil_df.groupby('Channel')['Sales'].sum()
        # Define a custom color palette with shades of purple
        colors2 = ['#663399', '#8A63B2', '#B28AC7', '#D1A2DC', '#EBC6F2', '#F9ECFF']
        # Create a pie chart
        fig2, ax = plt.subplots(facecolor='none')
        wedges, labels, _ = ax.pie(channel_sales, labels=channel_sales.index, autopct='%1.1f%%', colors=colors2)
        for label in labels:
            label.set_color('white')
        # Set title color to white
        title = ax.set_title('Customer transactions by Channel', fontsize=16, color='white')


        # Display the pie chart in Streamlit
        col1.pyplot(fig2)

        # Display a branch breakdown of sales in a pie chart
        # Calculate the total sales for each branch
        branch_sales = fil_df.groupby('Branch')['Sales'].sum()

        # Define a custom color palette
        colors = ['#004BA8', '#0084FF', '#33A1FF', '#66B2FF', '#99C3FF', '#CCE5FF']
        # Create a pie chart
        fig, ax = plt.subplots(facecolor='none')
        wedges, labels, _ = ax.pie(branch_sales, labels=branch_sales.index, autopct='%1.1f%%', colors=colors)
        for label in labels:
            label.set_color('white')
        # Set title color to white
        title = ax.set_title('Customer Transactions by Branch', fontsize=16, color='white')

        # Display the pie chart in Streamlit
        col2.pyplot(fig)

        # show the items the customer likes
        st.text('Ordered items with Revenue')
        # Calculate the total sales for each item
        Sales_mix = fil_df.groupby('Items')['Sales'].sum()
        sort_sm = Sales_mix
        st.dataframe(sort_sm)

    # Recorded Transactions section
    st.text('Recorded Transactions')

    # Assume 'df' is your DataFrame
    for index, row in fil_df.iterrows():
        # Access row data using column names or indices
        #Acess the date
        date = row['Date']
        channel = row['Channel']
        branch = row['Branch']
        items = row['Items']
        # Create the callout message
        callout_message = f"Date: {date}\n\nItems:\n\n{items}\n\nChannel: {channel}\n\nBranch: {branch}"


        # Display the callout using st.info()
        st.info(callout_message)



