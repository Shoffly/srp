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

# Convert the array of arrays to a pandas DataFrame
df = pd.DataFrame(values, columns=['Date','Time','Channel','Branch','Phone number','first name','Last name','email','Address','Sales','Ordered items','Item Category'])

# Convert the 'Date' column to datetime data type
df['Date'] = pd.to_datetime(df['Date'])
#convert start and end dates to variable dates for overview
sd = pd.to_datetime(st.sidebar.date_input('Start Date'))
ed = pd.to_datetime(st.sidebar.date_input('End Date'))

# Filter rows based on dates using .query() method
fil_df = df[(df['Date'] >= sd) & (df['Date'] <= ed)]
# Convert the 'Price' column to numeric data type
fil_df['Sales'] = pd.to_numeric(fil_df['Sales'])
#page contents
st.title("Channel Performance")

# Display the value in the subheader using Markdown formatting
st.write(f" This is the performance broken down by channel for the dates between {sd} and {ed}.")



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
title = ax.set_title('Sales Breakdown by Channel', fontsize=16, color='white')


# Display the pie chart in Streamlit
col1.pyplot(fig2)

# Calculate the total sales for each branch
channel_sales = fil_df.groupby('Channel')['Sales'].sum().apply(lambda x: f"{x:,.0f}" if x >= 1000 else x)
col2.table(channel_sales)

tab1, tab2, tab3 = st.tabs(["Talabat", "Instore", "El menus"])

with tab1:
   st.header("Talabat Performance")
   # Set the specific channel to filter
   channel_to_filter = 'Talabat'
   # Use columns layout manager
   col1, col2 = st.columns(2)
   # Filter the DataFrame based on the channel
   filtered_df_t = fil_df[fil_df['Channel'] == channel_to_filter]

   # Revenue metric
   # Convert the 'Price' column to numeric data type
   filtered_df_t['Sales'] = pd.to_numeric(filtered_df_t['Sales'])

   # Sum the numbers in the 'Price' column
   total_price_t = filtered_df_t['Sales'].sum()

   # Format the revenue metric
   formatted_revenue_t = "{:.1f}".format(total_price_t)
   if total_price_t >= 1000:
       formatted_revenue_t = "{:,.1f}k".format(total_price_t)



   # Transaction metric
   # count the numbers in the 'Price' column
   total_tcs_t = filtered_df_t['Sales'].count()
   formatted_tc_t = total_tcs_t

   # Format the tcs metric
   if total_tcs_t >= 1000:
    formatted_tc_t = "{:,.1f}k".format(total_tcs_t)

   #Display the metrics in separate columns
   col1.metric(label="Revenue", value=formatted_revenue_t)
   col2.metric(label="Transactions", value=formatted_tc_t)
   col2.metric(label="Top item", value=formatted_tc_t)
   col1.metric(label="Average order value", value="{:,.1f}".format(total_price_t / total_tcs_t))

   #Group the filtered DataFrame by branches and calculate the total sales for each branch
   branch_sales_t = filtered_df_t.groupby('Branch')['Sales'].sum()
   # Define a custom color palette with shades of purple
   colors2 = ['#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500']
   # Create a pie chart
   fig, ax = plt.subplots(facecolor='none')
   wedges, labels, _ = ax.pie(branch_sales_t, labels=branch_sales_t.index, autopct='%1.1f%%', colors=colors2)
   for label in labels:
       label.set_color('white')
   # Set title color to white
   title = ax.set_title('Talabat Sales by branch', fontsize=16, color='white')

   # Display the pie chart in Streamlit
   col1.pyplot(fig)

   # Group the filtered DataFrame by items for a salesmix and calculate the total sales for each branch
   branch_sales_t2 = filtered_df_t.groupby('Ordered items')['Sales'].sum()
   # Define a custom color palette with shades of purple
   colors2 = ['#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500']
   # Create a pie chart
   fig2, ax = plt.subplots(facecolor='none')
   wedges, labels, _ = ax.pie(branch_sales_t2, labels=branch_sales_t2.index, autopct='%1.1f%%', colors=colors2)
   for label in labels:
       label.set_color('white')
   # Set title color to white
   title2 = ax.set_title('Talabat Salesmix', fontsize=16, color='white')

   # Display the pie chart in Streamlit
   col2.pyplot(fig2)

   # Group the filtered DataFrame by branches and calculate the total sales for each branch
   branch_sales_t = filtered_df_t.groupby('Item Category')['Sales'].sum()
   # Define a custom color palette with shades of purple
   colors2 = ['#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500']
   # Create a pie chart
   fig, ax = plt.subplots(facecolor='none')
   wedges, labels, _ = ax.pie(branch_sales_t, labels=branch_sales_t.index, autopct='%1.1f%%', colors=colors2)
   for label in labels:
       label.set_color('white')
   # Set title color to white
   title = ax.set_title('Talabat Category Salesmix', fontsize=16, color='white')

   # Display the pie chart in Streamlit
   col1.pyplot(fig)
   # Display the DataFrame using Streamlit
   st.text('Recorded Transactions')
   st.dataframe(filtered_df_t)



with tab2:
   st.header("Instore Performance")
   # Set the specific channel to filter
   channel_to_filter = 'In store'
   # Use columns layout manager
   col1, col2 = st.columns(2)
   # Filter the DataFrame based on the channel
   filtered_df_t = fil_df[fil_df['Channel'] == channel_to_filter]

   # Revenue metric
   # Convert the 'Price' column to numeric data type
   filtered_df_t['Sales'] = pd.to_numeric(filtered_df_t['Sales'])

   # Sum the numbers in the 'Price' column
   total_price_t = filtered_df_t['Sales'].sum()

   # Format the revenue metric
   formatted_revenue_t = "{:.1f}".format(total_price_t)
   if total_price_t >= 1000:
       formatted_revenue_t = "{:,.1f}k".format(total_price_t)

   # Transaction metric
   # count the numbers in the 'Price' column
   total_tcs_t = filtered_df_t['Sales'].count()
   formatted_tc_t = total_tcs_t

   # Format the tcs metric
   if total_tcs_t >= 1000:
       formatted_tc_t = "{:,.1f}k".format(total_tcs_t)

   # Display the metrics in separate columns
   col1.metric(label="Revenue", value=formatted_revenue_t)
   col2.metric(label="Transactions", value=formatted_tc_t)
   col2.metric(label="Top item", value=formatted_tc_t)
   col1.metric(label="Average order value", value="{:,.1f}".format(total_price_t / total_tcs_t))

   # Group the filtered DataFrame by branches and calculate the total sales for each branch
   branch_sales_t = filtered_df_t.groupby('Branch')['Sales'].sum()
   # Define a custom color palette with shades of purple
   colors2 = ['#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500']
   # Create a pie chart
   fig, ax = plt.subplots(facecolor='none')
   wedges, labels, _ = ax.pie(branch_sales_t, labels=branch_sales_t.index, autopct='%1.1f%%', colors=colors2)
   for label in labels:
       label.set_color('white')
   # Set title color to white
   title = ax.set_title('In store Sales by branch', fontsize=16, color='white')

   # Display the pie chart in Streamlit
   col1.pyplot(fig)

   # Group the filtered DataFrame by items for a salesmix and calculate the total sales for each branch
   branch_sales_t2 = filtered_df_t.groupby('Ordered items')['Sales'].sum()
   # Define a custom color palette with shades of purple
   colors2 = ['#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500']
   # Create a pie chart
   fig2, ax = plt.subplots(facecolor='none')
   wedges, labels, _ = ax.pie(branch_sales_t2, labels=branch_sales_t2.index, autopct='%1.1f%%', colors=colors2)
   for label in labels:
       label.set_color('white')
   # Set title color to white
   title2 = ax.set_title('Instore Salesmix', fontsize=16, color='white')

   # Display the pie chart in Streamlit
   col2.pyplot(fig2)
   # Group the filtered DataFrame by branches and calculate the total sales for each branch
   branch_sales_t = filtered_df_t.groupby('Item Category')['Sales'].sum()
   # Define a custom color palette with shades of purple
   colors2 = ['#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500']
   # Create a pie chart
   fig, ax = plt.subplots(facecolor='none')
   wedges, labels, _ = ax.pie(branch_sales_t, labels=branch_sales_t.index, autopct='%1.1f%%', colors=colors2)
   for label in labels:
       label.set_color('white')
   # Set title color to white
   title = ax.set_title('Instore Category Salesmix', fontsize=16, color='white')

   # Display the pie chart in Streamlit
   col1.pyplot(fig)
   # Display the DataFrame using Streamlit
   st.text('Recorded Transactions')
   st.dataframe(filtered_df_t)

with tab3:
   st.header("El menus Performance")
# Set the specific channel to filter
   channel_to_filter = 'El menus'
   # Use columns layout manager
   col1, col2 = st.columns(2)
   # Filter the DataFrame based on the channel
   filtered_df_t = fil_df[fil_df['Channel'] == channel_to_filter]

   # Revenue metric
   # Convert the 'Price' column to numeric data type
   filtered_df_t['Sales'] = pd.to_numeric(filtered_df_t['Sales'])

   # Sum the numbers in the 'Price' column
   total_price_t = filtered_df_t['Sales'].sum()

   # Format the revenue metric
   formatted_revenue_t = "{:.1f}".format(total_price_t)
   if total_price_t >= 1000:
       formatted_revenue_t = "{:.1f}k".format(total_price_t)

   # Transaction metric
   # count the numbers in the 'Price' column
   total_tcs_t = filtered_df_t['Sales'].count()
   formatted_tc_t = total_tcs_t

   # Format the tcs metric
   if total_tcs_t >= 1000:
       formatted_tc_t = "{:,.1f}k".format(total_tcs_t)

   # Display the metrics in separate columns
   col1.metric(label="Revenue", value=formatted_revenue_t)
   col2.metric(label="Transactions", value=formatted_tc_t)
   col2.metric(label="Top item", value=formatted_tc_t)
   col1.metric(label="Average order value", value= "{:,.1f}".format(total_price_t / total_tcs_t))

   # Group the filtered DataFrame by branches and calculate the total sales for each branch
   branch_sales_t = filtered_df_t.groupby('Branch')['Sales'].sum()
   # Define a custom color palette with shades of purple
   colors2 = ['#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500']
   # Create a pie chart
   fig, ax = plt.subplots(facecolor='none')
   wedges, labels, _ = ax.pie(branch_sales_t, labels=branch_sales_t.index, autopct='%1.1f%%', colors=colors2)
   for label in labels:
       label.set_color('white')
   # Set title color to white
   title = ax.set_title('In store Sales by branch', fontsize=16, color='white')

   # Display the pie chart in Streamlit
   col1.pyplot(fig)

   # Group the filtered DataFrame by items for a salesmix and calculate the total sales for each branch
   branch_sales_t2 = filtered_df_t.groupby('Ordered items')['Sales'].sum()
   # Define a custom color palette with shades of purple
   colors2 = ['#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500']
   # Create a pie chart
   fig2, ax = plt.subplots(facecolor='none')
   wedges, labels, _ = ax.pie(branch_sales_t2, labels=branch_sales_t2.index, autopct='%1.1f%%', colors=colors2)
   for label in labels:
       label.set_color('white')
   # Set title color to white
   title2 = ax.set_title('Instore Salesmix', fontsize=16, color='white')

   # Display the pie chart in Streamlit
   col2.pyplot(fig2)
   # Group the filtered DataFrame by branches and calculate the total sales for each branch
   branch_sales_t = filtered_df_t.groupby('Item Category')['Sales'].sum()
   # Define a custom color palette with shades of purple
   colors2 = ['#FFA500', '#FF8C00', '#FF7F50', '#FF6347', '#FF4500']
   # Create a pie chart
   fig, ax = plt.subplots(facecolor='none')
   wedges, labels, _ = ax.pie(branch_sales_t, labels=branch_sales_t.index, autopct='%1.1f%%', colors=colors2)
   for label in labels:
       label.set_color('white')
   # Set title color to white
   title = ax.set_title('El menus Category Salesmix', fontsize=16, color='white')

   # Display the pie chart in Streamlit
   col1.pyplot(fig)
   # Display the DataFrame using Streamlit
   st.text('Recorded Transactions')
   st.dataframe(filtered_df_t)


