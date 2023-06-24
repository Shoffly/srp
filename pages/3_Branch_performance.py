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
df = pd.DataFrame(values, columns=['Date','Time','Channel','Branch','Phone number','first name','Last name','email','Address','Sales','Items','Item Category'])

# Convert the 'Date' column to datetime data type
df['Date'] = pd.to_datetime(df['Date'])

# Branch selection
branch_select = df['Branch'].unique()
store = st.sidebar.selectbox("Pick the branch", branch_select)
#convert start and end dates to variable dates for overview
sd = pd.to_datetime(st.sidebar.date_input('Start Date'))
ed = pd.to_datetime(st.sidebar.date_input('End Date'))


# Filter rows based on dates using .query() method
fil_df = df[(df['Date'] >= sd) & (df['Date'] <= ed) & (df['Branch'].isin([store]))]
# Convert the 'Price' column to numeric data type
fil_df['Sales'] = pd.to_numeric(fil_df['Sales'])

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
fil_df_c = df[(df['Date'] >= sd_c) & (df['Date'] <= ed_c) & (df['Branch'].isin([store]))]

#page contents
st.title(f"{store} Analysis")
# Display the value in the subheader using Markdown formatting
st.write(f" This is a deep dive in {store} for the dates between {sd} and {ed}.")

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

# Calculate the total sales for each item and channel
Sales_mix= fil_df.groupby('Items')['Sales'].sum()
Channel_mix= fil_df.groupby('Channel')['Sales'].sum()

# Plot the bar chart
#st.write('''
#Sales by items
#''')
#st.bar_chart(Sales_mix)

# new vs returning customers
# New vs returning customers pie chart
fig3, ax = plt.subplots(facecolor='none')
wedges, labels, _ = ax.pie(customer_counts_pie, labels=customer_counts_pie.index, autopct='%1.1f%%')
ax.axis('equal')
# Set title color to white
for label in labels:
    label.set_color('white')
title = ax.set_title('New vs returning Customers', fontsize=16, color='white')
col1.pyplot(fig3)

# Diagnostic section
st.write('''
## Diagnostic Section
''')
# Calculate the total sales for each item
Sales_mix_c= fil_df_c.groupby('Items')['Sales'].sum()

# Merge the DataFrames based on the 'ID' column
merged_Salesmix = pd.merge(Sales_mix, Sales_mix_c, on='Items', how='outer')

# Replace None values in 'ColumnA' with zero
merged_Salesmix['Sales_x'].fillna(0, inplace=True)
merged_Salesmix['Sales_y'].fillna(0, inplace=True)

#Calculate variance
merged_Salesmix['Variance'] = merged_Salesmix['Sales_x'] - merged_Salesmix['Sales_y']
tv_sort = merged_Salesmix.sort_values(by='Sales_x', ascending=False)
# Rename a column
tv_f = tv_sort.rename(columns={'Sales_x': 'This week', 'Sales_y': 'Last week'})
#Display the diagnostic Dataframe
st.write('''
### Items:
''')
st.write('''
Overview
''')
st.dataframe(tv_f)

# Create a new DataFrame with only positive variance items
negative_variance_df = merged_Salesmix[merged_Salesmix['Variance'] < 0]
nv_sort = negative_variance_df.sort_values(by='Sales_y', ascending=False)
# Rename a column
nv_f = nv_sort.rename(columns={'Sales_x': 'This week', 'Sales_y': 'Last week'})
st.write('''
This store's sales dropped in the following items
''')
st.dataframe(nv_f)

# Create a new DataFrame with only negative revenue stores
positive_variance_df = merged_Salesmix[merged_Salesmix['Variance'] >= 0]
pv_sort = positive_variance_df.sort_values(by='Sales_x', ascending=False)
# Rename a column
pv_f = pv_sort.rename(columns={'Sales_x': 'This week', 'Sales_y': 'Last week'})
st.write('''
This store's sales increased or remained stable in the following items
''')
st.dataframe(pv_f)

#Display the diagnostic Dataframe
st.write('''
### Channels:
''')
# Calculate the total sales for each item
Channel_mix_c= fil_df_c.groupby('Channel')['Sales'].sum()

# Merge the DataFrames based on the 'ID' column
merged_channelmix = pd.merge(Channel_mix, Channel_mix_c, on='Channel', how='outer')

# Replace None values in 'ColumnA' with zero
merged_channelmix['Sales_x'].fillna(0, inplace=True)
merged_channelmix['Sales_y'].fillna(0, inplace=True)

#Calculate variance
merged_channelmix['Variance'] = merged_channelmix['Sales_x'] - merged_channelmix['Sales_y']
cv_sort = merged_channelmix.sort_values(by='Sales_x', ascending=False)
# Rename a column
cv_f = cv_sort.rename(columns={'Sales_x': 'This week', 'Sales_y': 'Last week'})
st.write('''
Overview
''')
st.dataframe(cv_f)

# Create a new DataFrame with only positive variance items
negative_variance_dfc = merged_channelmix[merged_channelmix['Variance'] < 0]
ncv_sort = negative_variance_dfc.sort_values(by='Sales_y', ascending=False)
# Rename a column
ncv_f = ncv_sort.rename(columns={'Sales_x': 'This week', 'Sales_y': 'Last week'})
st.write('''
This store's sales dropped in the following channels
''')
st.dataframe(ncv_f)

# Create a new DataFrame with only negative revenue stores
positive_variance_dfc = merged_channelmix[merged_channelmix['Variance'] >= 0]
pcv_sort = positive_variance_dfc.sort_values(by='Sales_x', ascending=False)
# Rename a column
pvc_f = pcv_sort.rename(columns={'Sales_x': 'This week', 'Sales_y': 'Last week'})
st.write('''
This store's sales increased or remained stable in the following channels
''')
st.dataframe(pvc_f)