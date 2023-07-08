#imports
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
from streamlit_extras.switch_page_button import switch_page

# page system set up
st.set_page_config(
    page_title="Overview",
)

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




    # css connection
    with open('style.css') as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

    # Convert the array of arrays to a pandas DataFrame
    df = pd.DataFrame(values, columns=['Date','Time','Channel','Branch','Phone number','first name','Last name','email','Address','Price','Ordered items','Item Category'])

    #convert start and end dates to variable dates for overview
    sd = pd.to_datetime(st.sidebar.date_input('Start Date'))
    ed = pd.to_datetime(st.sidebar.date_input('End Date'))


    # Convert the 'Date' column to datetime data type
    df['Date'] = pd.to_datetime(df['Date'])

    # Filter rows based on dates using .query() method
    fil_df = df[(df['Date'] >= sd) & (df['Date'] <= ed)]

    # Returning vs New customer
    customer_counts = fil_df.groupby('Phone number')['Price'].nunique().reset_index()
    customer_counts.columns = ['CustomerID', 'TransactionCount']

    customer_counts['CustomerType'] = customer_counts['TransactionCount'].apply(lambda x: 'Returning' if x > 1 else 'New')

    customer_counts_pie = customer_counts.groupby('CustomerType')['TransactionCount'].count()


    #page contents
    st.title(f"Hey {name}")

    st.subheader('Here is an overview of your business')
    # Display the value in the subheader using Markdown formatting
    st.write(f"For dates between {sd.date()} and {ed.date()}.")

    # Revenue metric
    # Convert the 'Price' column to numeric data type
    fil_df['Price'] = pd.to_numeric(fil_df['Price'])

    # Sum the numbers in the 'Price' column
    total_price = fil_df['Price'].sum()

    # Format the revenue metric
    formatted_revenue = "{:.1f}".format(total_price)
    if total_price >= 1000:
        formatted_revenue = "{:,.1f}k".format(total_price)

    # Transaction metric
    # Convert the 'Price' column to numeric data type
    fil_df['Price'] = pd.to_numeric(fil_df['Price'])

    # Sum the numbers in the 'Price' column
    total_tcs = fil_df['Price'].count()
    formatted_tc = total_tcs

    # Format the tcs metric
    if total_tcs >= 1000:
        formatted_tc = "{:,.1f}k".format(total_tcs)

    #AOV metric
    aov = total_price/total_tcs
    # Format the AOV metric
    formatted_aov = "{:.1f}".format(aov)
    if aov >= 1000:
        formatted_aov = "{:,.1f}k".format(aov)

    # Use columns layout manager
    col1, col2 = st.columns(2)

    # Display the metrics in separate columns
    col1.metric(label="Revenue",value= formatted_revenue)
    col2.metric(label="Transactions", value=formatted_tc)
    col1.metric(label="Average order value", value=formatted_aov)

    #Display a branch breakdown of sales in a pie chart
    # Calculate the total sales for each branch
    branch_sales = fil_df.groupby('Branch')['Price'].sum()

    #container for pie charts
    with st.expander("Further Overview"):
        # Use columns layout manager
        col1, col2 = st.columns(2)

        # Define a custom color palette
        colors = ['#004BA8', '#0084FF', '#33A1FF', '#66B2FF', '#99C3FF', '#CCE5FF']
        # Create a pie chart
        fig, ax = plt.subplots(facecolor='none')
        wedges, labels, _ = ax.pie(branch_sales, labels=branch_sales.index, autopct='%1.1f%%', colors=colors)
        for label in labels:
            label.set_color('white')
        # Set title color to white
        title = ax.set_title('Sales Breakdown by Branch', fontsize=16, color='white')


        # Display the pie chart in Streamlit
        col1.pyplot(fig)

        #Display a channel breakdown of sales in a pie chart
        # Calculate the total sales for each branch
        channel_sales = fil_df.groupby('Channel')['Price'].sum()
        # Define a custom color palette with shades of purple
        colors2 = ['#663399', '#8A63B2', '#B28AC7', '#D1A2DC', '#EBC6F2', '#F9ECFF']
        # Create a pie chart
        fig2, ax = plt.subplots(facecolor='none')
        wedges, labels, _ = ax.pie(channel_sales, labels=channel_sales.index, autopct='%1.1f%%', colors=colors2)
        for label in labels:
            label.set_color('white')
        # Set title color to white
        title = ax.set_title('Sales Breakdown by Channel', fontsize=16, color='white')


        # Display the pie chart in Streamlit
        col2.pyplot(fig2)

        # New vs returning customers pie chart
        colors3 = ['#FF8400', '#F0CBA8']
        fig3, ax = plt.subplots(facecolor='none')
        wedges, labels, _ = ax.pie(customer_counts_pie, labels=customer_counts_pie.index, autopct='%1.1f%%', colors=colors3)
        ax.axis('equal')
        # Set title color to white
        for label in labels:
            label.set_color('white')
        title = ax.set_title('New vs returning Customers', fontsize=17, color='white')
        col1.pyplot(fig3)

    # container for Understand your customers and explore your business
    with st.container():
        # Explore your business
        st.subheader('Explore your business')
        # Display the value in the subheader using Markdown formatting
        st.write("Understand the performance and trends of your branches, items and channels.")
        # Use columns layout manager
        col1, col2 = st.columns(2)
        Branches = col1.button("Branches")
        if Branches:
            switch_page("Branch performance")

        Items = col2.button("Items")
        if Items:
            switch_page("Item performance")
        Channels = col1.button("Channels")
        if Channels:
            switch_page("channel performance")
        # Explore your business
        st.subheader('Understand your customers')
        # Display the value in the subheader using Markdown formatting
        st.write("Understand and segment your customers, view customer profiles and send sms campaigns.")
        # Use columns layout manager
        col1, col2 = st.columns(2)
        Saved = col1.button("Saved Segments")
        if Saved:
            switch_page("Saved segments")

        Customers_b = col2.button("Customer segment behaviour")
        if Customers_b:
            switch_page("Customer segment behaviour")

        Customer_b = col1.button("customer profiles")
        if Customer_b:
            switch_page("Customer_behaviour")







