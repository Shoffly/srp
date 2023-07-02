#imports
import streamlit as st
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build
from email.message import EmailMessage
import ssl
import smtplib



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
fil_df = df[(df['Date'] >= sd) & (df['Date'] <= ed)]

# Check if 'item', 'channel', and 'branch' variables have values
# Assuming you have a DataFrame called 'fil_df'

# Assuming you have a DataFrame called 'fil_df'
if item and channel and branch:
    filtered_df = fil_df[
        (fil_df['Items'].isin(item)) &
        (fil_df['Channel'].isin(channel)) &
        (fil_df['Branch'].isin(branch))
    ]
elif item and channel:
    filtered_df = fil_df[
        (fil_df['Items'].isin(item)) &
        (fil_df['Channel'].isin(channel))
    ]
elif item and branch:
    filtered_df = fil_df[
        (fil_df['Items'].isin(item)) &
        (fil_df['Branch'].isin(branch))
    ]
elif channel and branch:
    filtered_df = fil_df[
        (fil_df['Channel'].isin(channel)) &
        (fil_df['Branch'].isin(branch))
    ]
elif item:
    filtered_df = fil_df[fil_df['Items'].isin(item)]
elif channel:
    filtered_df = fil_df[fil_df['Channel'].isin(channel)]
elif branch:
    filtered_df = fil_df[fil_df['Branch'].isin(branch)]
else:
    filtered_df = fil_df  # No filters applied


# Returning vs New customer
customer_counts = fil_df.groupby('Phone number')['Sales'].nunique().reset_index()
customer_counts.columns = ['CustomerID', 'TransactionCount']

customer_counts['CustomerType'] = customer_counts['TransactionCount'].apply(lambda x: 'Returning' if x > 1 else 'New')

customer_counts_pie = customer_counts.groupby('CustomerType')['TransactionCount'].count()

#page contents
st.title("SMS Campaign Tool")

# Use columns layout manager
col1, col2 = st.columns(2)
# sms audience size
total_size = filtered_df['Sales'].count()
# Display the metrics in separate columns
col1.metric(label="Audience size",value= total_size)
col2.metric(label='Cost of sms campaign', value = "{:,.1f}".format(total_size*0.15))

# Define the function to count characters
@st.cache_data(show_spinner=False)
def count_characters(text):
    return len(text)

# Get input values
sms_input = st.text_area('What message do you want to send?')
# Call the function to get the character count
character_count = count_characters(sms_input)

# Display the character count
st.write("Number of characters:", character_count)
st.info('Your message should be not more than 150 characters')
sms_date = st.date_input('What Day?')
sms_time = st.time_input('What time')

# Perform actions on button click
# For example, display a success message and clear the text areas
if st.button("Submit"):


    # email sender code start
    email_sender = 'sunnymoh44@gmail.com'
    email_p = 'qywokurzqrfpcufp'
    email_to = 'mohammed09ahmed@gmail.com'

    # email variables
    subject = 'SMS Request'
    # These tables will be sent in the email
    form_mdf = filtered_df.to_html()
    body = f'''<p>{sms_input}</p>
            <p>{sms_date}</p>
            <p>{sms_time}</p>
                    {form_mdf}'''

    # email instance creation
    em = EmailMessage()
    em['From'] = email_sender
    em['To'] = email_to
    em['Subject'] = subject
    em.add_alternative(body, subtype='html')  # Set the content type to HTML

    # email ssl and sending
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(email_sender, email_p)
        smtp.sendmail(email_sender, email_to, em.as_string())

    # Display success message and clear text areas
    st.success("SMS request sent successfully!")
    sms_input = "Message sent!"
    sms_date = None
    sms_time = None

# Recorded Transactions section
st.text('SMS Audience')
st.dataframe(filtered_df)




