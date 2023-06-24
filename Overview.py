#imports
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
import matplotlib.pyplot as plt


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
                            range="A1:L100").execute()
values = result.get('values', [])




#page system set up
st.set_page_config(
    page_title="Overview",
)
# Convert the array of arrays to a pandas DataFrame
df = pd.DataFrame(values, columns=['Date','Time','Channel','Branch','Phone number','first name','Last name','email','Address','Price','Ordered items','Item Category'])

#convert start and end dates to variable dates for overview
sd = pd.to_datetime(st.sidebar.date_input('Start Date'))
ed = pd.to_datetime(st.sidebar.date_input('End Date'))

# Convert the 'Date' column to datetime data type
df['Date'] = pd.to_datetime(df['Date'])

# Filter rows based on dates using .query() method
fil_df = df[(df['Date'] >= sd) & (df['Date'] <= ed)]

#page contents
st.title("Overview")
# Display the value in the subheader using Markdown formatting
st.write(f" This is the overview for the dates between {sd} and {ed}.")

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

# Display the DataFrame using Streamlit
st.text('Recorded Transactions')
st.dataframe(fil_df)











