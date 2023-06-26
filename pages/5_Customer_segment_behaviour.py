#imports
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import matplotlib.pyplot as plt
import datetime

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

# Pick the channels for the segment
channel_select = df['Channel'].unique()
channel = st.sidebar.multiselect('Choose the channels', channel_select)

# Pick the channels for the segment
branch_select = df['Branch'].unique()
branch = st.sidebar.multiselect('Choose the branches', branch_select)

# Pick the Items for the segment
item_select = df['Items'].unique()
item = st.sidebar.multiselect('Choose the items', item_select)

#convert start and end dates to variable dates for overview
sd = pd.to_datetime(st.sidebar.date_input('Start Date'))
ed = pd.to_datetime(st.sidebar.date_input('End Date'))

# Filter rows based on dates using .query() method
fil_dfi = df[(df['Date'] >= sd) & (df['Date'] <= ed)]

# Check if 'item', 'channel', and 'branch' variables have values
# Assuming you have a DataFrame called 'fil_df'

# Assuming you have a DataFrame called 'fil_df'
if item and channel and branch:
    fil_df = fil_dfi[
        (fil_dfi['Items'].isin(item)) &
        (fil_dfi['Channel'].isin(channel)) &
        (fil_dfi['Branch'].isin(branch))
    ]
elif item and channel:
    fil_df = fil_dfi[
        (fil_dfi['Items'].isin(item)) &
        (fil_dfi['Channel'].isin(channel))
    ]
elif item and branch:
    fil_df = fil_dfi[
        (fil_dfi['Items'].isin(item)) &
        (fil_dfi['Branch'].isin(branch))
    ]
elif channel and branch:
    fil_df = fil_dfi[
        (fil_dfi['Channel'].isin(channel)) &
        (fil_dfi['Branch'].isin(branch))
    ]
elif item:
    fil_df = fil_dfi[fil_dfi['Items'].isin(item)]
elif channel:
    fil_df = fil_dfi[fil_dfi['Channel'].isin(channel)]
elif branch:
    fil_df = fil_dfi[fil_dfi['Branch'].isin(branch)]
else:
    fil_df = fil_dfi  # No filters applied


# Returning vs New customer
customer_counts = fil_df.groupby('Phone number')['Sales'].nunique().reset_index()
customer_counts.columns = ['CustomerID', 'TransactionCount']

customer_counts['CustomerType'] = customer_counts['TransactionCount'].apply(lambda x: 'Returning' if x > 1 else 'New')

customer_counts_pie = customer_counts.groupby('CustomerType')['TransactionCount'].count()


# comparison date section
st.sidebar.write('''Pick Comparison Dates''')
sd_c = pd.to_datetime(st.sidebar.date_input('Start comparison Date'))
ed_c = pd.to_datetime(st.sidebar.date_input('End comparison Date'))

#Filter the datafrane based on the comparison
fil_df_c = df[(df['Date'] >= sd_c) & (df['Date'] <= ed_c)]

#page contents
st.title("Customer Segment Analysis")
# Revenue metric
# Convert the 'Price' column to numeric data type
fil_df['Sales'] = pd.to_numeric(fil_df['Sales'])

# Sum the numbers in the 'Price' column
total_price = fil_df['Sales'].sum()

# Format the revenue metric
formatted_revenue = "{:.1f}".format(total_price)
if total_price >= 1000:
    formatted_revenue = "{:,.1f}k".format(total_price)

# Transaction metric
# Convert the 'Price' column to numeric data type
fil_df['Sales'] = pd.to_numeric(fil_df['Sales'])

# Sum the numbers in the 'Price' column
total_tcs = fil_df['Sales'].count()
formatted_tc = total_tcs

# Format the tcs metric
if total_tcs >= 1000:
    formatted_tc = "{:,.1f}k".format(total_tcs)

# the comparison metrics are here boi
# Comparison Revenue metric
# Convert the 'Price' column to numeric data type
fil_df_c['Sales'] = pd.to_numeric(fil_df_c['Sales'])

# Sum the numbers in the 'Price' column
total_price_c = fil_df_c['Sales'].sum()

revenue_c = total_price - total_price_c
# Comparison Transaction metric
# Convert the 'Price' column to numeric data type
fil_df_c['Sales'] = pd.to_numeric(fil_df_c['Sales'])

# Sum the numbers in the 'Price' column
total_tc_c = fil_df_c['Sales'].count()

tc_c = total_tcs - total_tc_c
# Use columns layout manager
col1, col2 = st.columns(2)

# Display the metrics in separate columns
col1.metric(label="Revenue",value= formatted_revenue, delta= "{:,.1f}".format(revenue_c))
col2.metric(label="Transactions", value=formatted_tc, delta= "{:,.1f}".format(tc_c))
col1.metric(label="Average order value", value="{:,.1f}".format(total_price/ total_tcs))

#container for pie charts
with st.container():
    # Use columns layout manager
    col1, col2 = st.columns(2)
    # new vs returning customers
    # New vs returning customers pie chart
    colors3 = ['#FF8400', '#F0CBA8']
    fig3, ax = plt.subplots(facecolor='none')
    wedges, labels, _ = ax.pie(customer_counts_pie, labels=customer_counts_pie.index, autopct='%1.1f%%',colors=colors3)
    ax.axis('equal')
    # Set title color to white
    for label in labels:
        label.set_color('white')
    title = ax.set_title('New vs returning Customers', fontsize=16, color='white')
    col1.pyplot(fig3)
# Calculate the total sales for each item
Sales_mix= fil_df.groupby('Items')['Sales'].sum()
# Plot the bar chart
st.write('''
### Sales by items
''')
st.bar_chart(Sales_mix)

# Calculate the total sales for each branch
branch_mix= fil_df.groupby('Branch')['Sales'].sum()
# Plot the bar chart
st.write('''
### Sales by Branches
''')
st.bar_chart(branch_mix)

# Calculate the total sales for each channel
channel_mix= fil_df.groupby('Channel')['Sales'].sum()
# Plot the bar chart
st.write('''
### Sales by channel
''')
st.bar_chart(channel_mix)
# Recorded Transactions section
st.text('Recorded Transactions')
st.dataframe(fil_df)