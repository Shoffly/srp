#imports
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import numpy as np
import matplotlib.pyplot as plt
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
    df['Sales'] = pd.to_numeric(df['Sales'])

    # Cohort selection
    cohort_options = ['30 Day Active Users', 'High Value Customers', 'Active Repeats']
    selected_cohort = st.sidebar.selectbox("Select a Cohort", cohort_options)

    # Cohort calculations
    # Get the current date
    current_date = pd.to_datetime('today').normalize()

    # Determine which cohort was selected and calculate the corresponding metrics
    if selected_cohort == '30 Day Active Users':
        active_users_last_30_days = df[df['Date'] >= (current_date - pd.DateOffset(days=30))]
        num_users = active_users_last_30_days['Phone number'].nunique()

        # Calculate the metrics for the previous 30 days
        previous_active_users = df[(df['Date'] >= (current_date - pd.DateOffset(days=60))) & (
                    df['Date'] < (current_date - pd.DateOffset(days=30)))]
        num_previous_users = previous_active_users['Phone number'].nunique()

        # Display metrics for 30 Day Active Users cohort
        st.title("30 Day Active Users")
        st.sidebar.info('The users who have made 1 or more purchases within the last 30 Days.')
        # Use columns layout manager
        col1, col2 = st.columns(2)

        # Display the metrics in separate columns
        col1.metric(label="Total Users", value=num_users, delta=num_users - num_previous_users)

        # Returning vs New customer analysis
        customer_counts = active_users_last_30_days.groupby('Phone number')['Sales'].nunique().reset_index()
        customer_counts.columns = ['CustomerID', 'TransactionCount']
        customer_counts['CustomerType'] = customer_counts['TransactionCount'].apply(
            lambda x: 'Returning' if x > 1 else 'New')
        customer_counts_pie = customer_counts.groupby('CustomerType')['TransactionCount'].count()

        # Revenue metric
        active_users_last_30_days['Sales'] = pd.to_numeric(active_users_last_30_days['Sales'])
        total_price = active_users_last_30_days['Sales'].sum()
        formatted_revenue = "{:.1f}".format(total_price)
        if total_price >= 1000:
            formatted_revenue = "{:,.1f}k".format(total_price)

        # Transaction metric
        total_tcs = active_users_last_30_days['Sales'].count()
        formatted_tc = total_tcs
        if total_tcs >= 1000:
            formatted_tc = "{:,.1f}k".format(total_tcs)


        # Display the metrics in separate columns
        col2.metric(label="Revenue", value=formatted_revenue)
        col2.metric(label="Transactions", value=formatted_tc)
        col1.metric(label="Average order value", value="{:,.1f}".format(total_price / total_tcs))

        # New vs returning customers
        colors3 = ['#FF8400', '#F0CBA8']
        fig3, ax = plt.subplots(facecolor='none')
        wedges, labels, _ = ax.pie(customer_counts_pie, labels=customer_counts_pie.index, autopct='%1.1f%%',
                                   colors=colors3)
        ax.axis('equal')
        for label in labels:
            label.set_color('white')
        title = ax.set_title('New vs returning Customers', fontsize=16, color='white')
        col1.pyplot(fig3)

        # Sales by items
        Sales_mix = active_users_last_30_days.groupby('Items')['Sales'].sum()
        st.write('''
           ### Sales by items
           ''')
        st.bar_chart(Sales_mix)

        # Sales by branches
        branch_mix = active_users_last_30_days.groupby('Branch')['Sales'].sum()
        st.write('''
           ### Sales by Branches
           ''')
        st.bar_chart(branch_mix)

        # Sales by channels
        channel_mix = active_users_last_30_days.groupby('Channel')['Sales'].sum()
        st.write('''
           ### Sales by Channel
           ''')
        st.bar_chart(channel_mix)

        # Additional analysis or visualizations specific to this cohort can be added here

        # Recorded Transactions section
        st.write('Recorded Transactions')
        st.dataframe(active_users_last_30_days)

        # Additional analysis or visualization specific to this cohort can be added here

    elif selected_cohort == 'High Value Customers':
        # Sidebar date range selector
        st.sidebar.info('The top 25% spending customers between 2 dates.')
        st.sidebar.write("Select Date Range")
        start_date_hv = pd.to_datetime(st.sidebar.date_input("Start Date"))
        end_date_hv = pd.to_datetime(st.sidebar.date_input("End Date"))

        df['Sales'] = pd.to_numeric(df['Sales'])
        t_fil = df[(df['Date'] >= start_date_hv) & (df['Date'] <= end_date_hv)]
        high_value_customers = t_fil.groupby('Phone number')['Sales'].sum()
        num_customers = high_value_customers.shape[0]

        # Filter the original DataFrame based on high value customer phone numbers
        filtered_df = df[df['Phone number'].isin(high_value_customers.index)]

        # Display metrics for High Value Customers cohort
        st.title("High Value Customers")

        st.metric(label="Users", value=num_customers)
        # Revenue metric
        total_price = high_value_customers.sum()
        formatted_revenue = "{:.1f}".format(total_price)
        if total_price >= 1000:
            formatted_revenue = "{:,.1f}k".format(total_price)

        # Transaction metric
        total_tcs = filtered_df['Sales'].count()
        formatted_tc = total_tcs
        if total_tcs >= 1000:
            formatted_tc = "{:,.1f}k".format(total_tcs)

        # Average order value
        average_order_value = total_price / total_tcs

        # Use columns layout manager
        col1, col2, col3 = st.columns(3)

        # Display the metrics in separate columns
        col1.metric(label="Revenue", value=formatted_revenue)
        col2.metric(label="Transactions", value=formatted_tc)
        col3.metric(label="Average Order Value", value="{:,.1f}".format(average_order_value))

        # Sales by items
        Sales_mix = filtered_df.groupby('Items')['Sales'].sum()
        st.write('''
           ### Sales by Items
           ''')
        st.bar_chart(Sales_mix)

        # Channel mix
        channel_mix = filtered_df.groupby('Channel')['Sales'].sum()
        st.write('''
        ### Channel Mix
        ''')
        st.bar_chart(channel_mix)

        # Sales by branches
        branch_mix = filtered_df.groupby('Branch')['Sales'].sum()
        st.write('''
           ### Sales by Branches
           ''')
        st.bar_chart(branch_mix)
        # Recorded Transactions section
        st.write('Recorded Transactions')
        st.dataframe(filtered_df)



        # Additional analysis or visualization specific to this cohort can be added here

    elif selected_cohort == 'Active Repeats':
        st.sidebar.info(
            'Customers with 2 or more purchases within the last 60 days and likely to convert again.')
        # Calculate the start and end dates for the last 60 days
        start_date_ar = current_date - pd.DateOffset(days=60)
        end_date_ar = current_date

        # Step 1: Filter the DataFrame based on the last 60 days
        filtered_df = df[
            (df['Date'] >= start_date_ar) & (df['Date'] <= end_date_ar)
            ]

        # Step 2: Filter the DataFrame to include only active repeats
        active_repeats = filtered_df.groupby('Phone number')['Sales'].count()
        active_repeats = active_repeats[active_repeats >= 2]
        active_repeats_df = filtered_df[filtered_df['Phone number'].isin(active_repeats.index)]

        # Step 3: Calculate the metrics
        revenue = active_repeats_df['Sales'].sum()
        users = active_repeats.shape[0]
        transactions = active_repeats_df['Sales'].count()
        average_order_value = revenue / transactions

        # Step 4: Calculate the sales mix by items
        sales_mix = active_repeats_df.groupby('Items')['Sales'].sum()

        # Step 5: Calculate the branch mix
        branch_mix = active_repeats_df.groupby('Branch')['Sales'].sum()

        # Step 6: Calculate the channel mix
        channel_mix = active_repeats_df.groupby('Channel')['Sales'].sum()

        # Display metrics for Active Repeats cohort
        st.title("Active Repeats")
        # Use columns layout manager
        col1, col2= st.columns(2)
        col1.metric(label="Users", value= users)
        col2.metric(label="Revenue", value="{:.1f}".format(revenue))
        col1.metric(label="Transactions", value=transactions)
        col2.metric(label="Average Order Value", value="{:.1f}".format(average_order_value))

        # Display the sales mix by items
        st.write('''### Sales Mix''')
        st.bar_chart(sales_mix)


        # Display the branch mix
        st.write('''### Branch Mix''')
        st.bar_chart(branch_mix)


        # Display the channel mix
        st.write('''### Channel Mix''')
        st.bar_chart(channel_mix)


        # Display the filtered DataFrame
        st.write('Active Repeats Data:')
        st.dataframe(active_repeats_df)


    elif selected_cohort == 'At-risk Repeats':
        # Calculate the start and end dates for the last 30 days
        end_date = current_date - pd.DateOffset(days=1)
        start_date = end_date - pd.DateOffset(days=30)

        # Step 1: Filter the DataFrame based on the last 30 days
        filtered_df = df[
            (df['Date'] >= start_date) & (df['Date'] <= end_date)
            ]

        # Step 2: Filter the DataFrame to include only customers with 2 or more orders before the last 30 days
        customer_counts = filtered_df.groupby('Phone number')['Sales'].count()
        at_risk_repeats = customer_counts[customer_counts >= 2].index

        at_risk_repeats_df = df[
            (df['Phone number'].isin(at_risk_repeats)) &
            (df['Date'] < start_date)
            ]

        # Step 3: Calculate the metrics
        revenue = at_risk_repeats_df['Sales'].sum()
        transactions = at_risk_repeats_df.shape[0]
        average_order_value = revenue / transactions

        # Step 4: Calculate the sales mix by items
        sales_mix = at_risk_repeats_df.groupby('Items')['Sales'].sum()

        # Step 5: Calculate the branch mix
        branch_mix = at_risk_repeats_df.groupby('Branch')['Sales'].sum()

        # Step 6: Calculate the channel mix
        channel_mix = at_risk_repeats_df.groupby('Channel')['Sales'].sum()

        # Display metrics for At-risk Repeats cohort
        st.title("At-risk Repeats")
        st.write("Metrics:")
        st.metric(label="Revenue", value="{:.1f}".format(revenue))
        st.metric(label="Transactions", value=transactions)
        st.metric(label="Average Order Value", value="{:.1f}".format(average_order_value))

        # Display the sales mix by items
        st.write('Sales Mix by Items:')
        st.bar_chart(sales_mix)
        st.write('')

        # Display the branch mix
        st.write('Branch Mix:')
        st.bar_chart(branch_mix)
        st.write('')

        # Display the channel mix
        st.write('Channel Mix:')
        st.bar_chart(channel_mix)
        st.write('')

        # Display the filtered DataFrame
        st.write('At-risk Repeats Data:')
        st.dataframe(at_risk_repeats_df)

        # Display metrics for At-risk Repeats cohort
        st.sidebar.info('Customers with 2 or more purchases and at risk of churning (not made a purchase within the last 30 to 60 days).')


        # Additional analysis or visualization specific to this cohort can be added here

    # ...

