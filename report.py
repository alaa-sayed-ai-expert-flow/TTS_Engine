# import sqlite3
# import pandas as pd
# import streamlit as st
# from fpdf import FPDF
# import requests
#
#
# # Get Client IP
# def get_client_ip():
#     try:
#         # Use httpbin to fetch client IP (you can replace this with a reverse proxy solution)
#         response = requests.get('https://httpbin.org/ip')
#         ip = response.json()['origin']
#         return ip
#     except:
#         return 'Unknown'
#
#
# client_ip = get_client_ip()
#
# # Connect to the SQLite database
# conn = sqlite3.connect('api_logs.db')
#
# # Query to filter by the current IP
# query = f"""
#     SELECT
#         date_time,
#         client_ip,
#         method,
#         url,
#         duration,
#         status,
#         request_content,
#         error_message,
#         LENGTH(request_content) AS characters_count
#     FROM logs
#     WHERE client_ip = '{client_ip}';  -- Filter by current client IP
# """
# # Read the data into a pandas DataFrame
# df = pd.read_sql_query(query, conn)
#
# # Display the DataFrame in Streamlit
# st.title(f"API Logs Report for IP: {client_ip}")
# st.dataframe(df)
#
#
# # Function to generate PDF
# def generate_pdf(dataframe):
#     pdf = FPDF()
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#
#     # Set column headers
#     headers = ['Date Time', 'Client IP', 'Method', 'URL', 'Duration', 'Status', 'Request Content', 'Error Message',
#                'Characters Count']
#     col_width = 3 * (pdf.w / len(headers) ) # Column width
#
#     for header in headers:
#         pdf.cell(col_width, 10, header, border=1)
#     pdf.ln()
#
#     # Add data rows
#     for row in dataframe.itertuples(index=False):
#         for item in row:
#             pdf.cell(col_width, 10, str(item), border=1)
#         pdf.ln()
#
#     return pdf
#
#
# # Button to download as PDF
# if st.button("Download Report as PDF"):
#     pdf = generate_pdf(df)
#     pdf_output = pdf.output(dest='S').encode('latin1')  # Output to string
#     st.download_button("Download PDF", data=pdf_output, file_name="api_logs_report.pdf", mime="application/pdf")
#
# # Close the database connection
# conn.close()

# import sqlite3
# import pandas as pd
# import streamlit as st
# from fpdf import FPDF
# import requests
#
#
# # Get Client IP
# def get_client_ip():
#     try:
#         # Use httpbin to fetch client IP (you can replace this with a reverse proxy solution)
#         response = requests.get('https://httpbin.org/ip')
#         ip = response.json()['origin']
#         return ip
#     except:
#         return 'Unknown'
#
#
# client_ip = get_client_ip()
#
# # Connect to the SQLite database
# conn = sqlite3.connect('api_logs.db')
#
# # Query to filter by the current IP
# query = f"""
#     SELECT
#         date_time,
#         client_ip,
#         method,
#         url,
#         duration,
#         status,
#         request_content,
#         error_message,
#         LENGTH(request_content) AS characters_count
#     FROM logs
#     WHERE client_ip = '{client_ip}';  -- Filter by current client IP
# """
# # Read the data into a pandas DataFrame
# df = pd.read_sql_query(query, conn)
#
# # Display the DataFrame in Streamlit
# st.title(f"API Logs Report for IP: {client_ip}")
# st.dataframe(df)
#
#
# # Function to generate PDF with a wider page
# def generate_pdf(dataframe):
#     # Define a custom page width and height (e.g., 420mm wide and 297mm tall for a wider page)
#     pdf = FPDF('L', 'mm', (297, 420))  # Landscape mode, with custom width
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#
#     # Set column headers
#     headers = ['Date Time', 'Client IP', 'Method', 'URL', 'Duration', 'Status', 'Request Content', 'Error Message',
#                'Characters Count']
#     col_width = (pdf.w / len(headers))  # Adjust column width for larger page size
#
#     # Add headers
#     for header in headers:
#         pdf.cell(col_width, 10, header, border=1)
#     pdf.ln()
#
#     # Add data rows
#     for row in dataframe.itertuples(index=False):
#         for item in row:
#             pdf.cell(col_width, 10, str(item), border=1)
#         pdf.ln()
#
#     return pdf
#
#
# # Button to download as PDF
# if st.button("Download Report as PDF"):
#     pdf = generate_pdf(df)
#     pdf_output = pdf.output(dest='S').encode('latin1')  # Output to string
#     st.download_button("Download PDF", data=pdf_output, file_name="api_logs_report.pdf", mime="application/pdf")
#
# # Close the database connection
# conn.close()


# import sqlite3
# import pandas as pd
# import streamlit as st
# from fpdf import FPDF
# import requests
#
#
# # Get Client IP
# def get_client_ip():
#     try:
#         # Use httpbin to fetch client IP (you can replace this with a reverse proxy solution)
#         response = requests.get('https://httpbin.org/ip')
#         ip = response.json()['origin']
#         return ip
#     except:
#         return 'Unknown'
#
#
# client_ip = get_client_ip()
#
# # Connect to the SQLite database
# conn = sqlite3.connect('api_logs.db')
#
# # Query to filter by the current IP
# query = f"""
#     SELECT
#         date_time,
#         client_ip,
#         method,
#         url,
#         duration,
#         status,
#         request_content,
#         error_message,
#         LENGTH(request_content) AS characters_count
#     FROM logs
#     WHERE client_ip = '{client_ip}';  -- Filter by current client IP
# """
# # Read the data into a pandas DataFrame
# df = pd.read_sql_query(query, conn)
#
# # Display the DataFrame in Streamlit
# st.title(f"API Logs Report for IP: {client_ip}")
# st.dataframe(df)
#
#
# # Function to generate PDF with proper handling of wide columns
# def generate_pdf(dataframe):
#     # Define a custom page width and height (e.g., 420mm wide and 297mm tall for a wider page)
#     pdf = FPDF('L', 'mm', (297, 420))  # Landscape mode, with custom width
#     pdf.add_page()
#     pdf.set_font("Arial", size=8)
#
#     # Set column headers
#     headers = ['Date Time', 'Client IP', 'Method', 'URL', 'Duration', 'Status', 'Request Content', 'Error Message',
#                'Characters Count']
#
#     # Adjust column widths (customize these widths as necessary)
#     col_widths = {
#         'Date Time': 40,
#         'Client IP': 30,
#         'Method': 20,
#         'URL': 30,
#         'Duration': 75,
#         'Status': 20,
#         'Request Content': 80,  # Adjust for potentially long content
#         'Error Message': 80,  # Adjust for potentially long content
#         'Characters Count': 20
#     }
#
#     # Add headers to the PDF
#     for header in headers:
#         pdf.cell(col_widths[header], 10, header, border=1)
#     pdf.ln()
#
#     # Add data rows, using multi_cell for long text columns
#     for row in dataframe.itertuples(index=False):
#         pdf.cell(col_widths['Date Time'], 10, str(row.date_time), border=1)
#         pdf.cell(col_widths['Client IP'], 10, str(row.client_ip), border=1)
#         pdf.cell(col_widths['Method'], 10, str(row.method), border=1)
#         pdf.cell(col_widths['URL'], 10, str(row.url), border=1)
#         pdf.cell(col_widths['Duration'], 10, str(row.duration), border=1)
#         pdf.cell(col_widths['Status'], 10, str(row.status), border=1)
#
#         # Use multi_cell for Request Content and Error Message
#         x_before_request_content = pdf.get_x()  # Save current x-position
#         y_before_request_content = pdf.get_y()  # Save current y-position
#
#         pdf.multi_cell(col_widths['Request Content'], 10, str(row.request_content), border=1)
#
#         # Move back to the saved x-position before 'Request Content' column, and align to the same y
#         pdf.set_xy(x_before_request_content + col_widths['Request Content'], y_before_request_content)
#
#         pdf.multi_cell(col_widths['Error Message'], 10, str(row.error_message), border=1)
#
#         # Move back for the remaining columns after multi_cell usage
#         pdf.set_xy(x_before_request_content + col_widths['Request Content'] + col_widths['Error Message'],
#                    y_before_request_content)
#         pdf.cell(col_widths['Characters Count'], 10, str(row.characters_count), border=1)
#
#         pdf.ln()
#
#     return pdf
#
#
# # Button to download as PDF
# if st.button("Download Report as PDF"):
#     pdf = generate_pdf(df)
#     pdf_output = pdf.output(dest='S').encode('latin1')  # Output to string
#     st.download_button("Download PDF", data=pdf_output, file_name="api_logs_report.pdf", mime="application/pdf")
#
# # Close the database connection
# conn.close()


# import sqlite3
# import pandas as pd
# import streamlit as st
# from fpdf import FPDF
# import requests
#
# # Connect to the SQLite database
# conn = sqlite3.connect('api_logs.db')
#
# # Query to filter by the current IP
# query = f"""
#     SELECT
#         date_time,
#         client_ip,
#         method,
#         url,
#         duration,
#         status,
#         request_content,
#         error_message,
#         LENGTH(request_content) AS characters_count
#     FROM logs
#
# """
# # WHERE client_ip = '{client_ip}';  -- Filter by current client IP
# # Read the data into a pandas DataFrame
# df = pd.read_sql_query(query, conn)
#
# # Display the DataFrame in Streamlit
# st.title(f"API Logs Report for IP: {client_ip}")
# st.dataframe(df)
#
#
# # Function to generate PDF with no multi_cell for Request Content
# def generate_pdf(dataframe):
#     # Define a custom page width and height (e.g., 420mm wide and 297mm tall for a wider page)
#     pdf = FPDF('L', 'mm', (297, 420))  # Landscape mode, with custom width
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#
#     # Set column headers
#     headers = ['Date Time', 'Client IP', 'Method', 'URL', 'Duration', 'Status', 'Error Message',  # 'Request Content'
#                'Characters Count']
#
#     # Adjust column widths (customize these widths as necessary)
#     col_widths = {
#         'Date Time': 45,
#         'Client IP': 30,
#         'Method': 20,
#         'URL': 32,
#         'Duration': 75,
#         'Status': 20,
#         # 'Request Content': 80,  # Adjust for potentially long content
#         'Error Message': 90,  # Adjust for potentially long content
#         'Characters Count': 40
#     }
#
#     # Add headers to the PDF
#     for header in headers:
#         pdf.cell(col_widths[header], 10, header, border=1)
#     pdf.ln()
#
#     # Add data rows, using multi_cell only for Error Message
#     for row in dataframe.itertuples(index=False):
#         pdf.cell(col_widths['Date Time'], 10, str(row.date_time), border=1)
#         pdf.cell(col_widths['Client IP'], 10, str(row.client_ip), border=1)
#         pdf.cell(col_widths['Method'], 10, str(row.method), border=1)
#         pdf.cell(col_widths['URL'], 10, str(row.url), border=1)
#         pdf.cell(col_widths['Duration'], 10, str(row.duration), border=1)
#         pdf.cell(col_widths['Status'], 10, str(row.status), border=1)
#
#         # For Request Content: Keep it in one line (no multi_cell)
#         # pdf.cell(col_widths['Request Content'], 10, str(row.request_content), border=1)
#
#         # Use multi_cell for Error Message
#         x_before_error_message = pdf.get_x()  # Save current x-position
#         y_before_error_message = pdf.get_y()  # Save current y-position
#
#         pdf.multi_cell(col_widths['Error Message'], 10, str(row.error_message), border=1)
#
#         # Move back for the remaining column after multi_cell usage
#         pdf.set_xy(x_before_error_message + col_widths['Error Message'], y_before_error_message)
#         pdf.cell(col_widths['Characters Count'], 10, str(row.characters_count), border=1)
#
#         pdf.ln()
#
#     return pdf
#
#
# # Button to download as PDF
# if st.button("Download Report as PDF"):
#     pdf = generate_pdf(df)
#     pdf_output = pdf.output(dest='S').encode('latin1')  # Output to string
#     st.download_button("Download PDF", data=pdf_output, file_name="api_logs_report.pdf", mime="application/pdf")
#
# # Close the database connection
# conn.close()


import sqlite3
import pandas as pd
import streamlit as st
from fpdf import FPDF
import requests
from datetime import datetime

# Connect to the SQLite database
conn = sqlite3.connect('api_logs.db')

# User inputs for filtering
st.title("API Logs Report")

# Date range filter using calendar
start_date = st.date_input('From', value=datetime(2023, 1, 1))  # Set a default date
end_date = st.date_input('To', value=datetime.now())  # Default to today

# Dropdown for filtering by Client IP
client_ip_list = pd.read_sql_query("SELECT DISTINCT client_ip FROM logs", conn)['client_ip'].tolist()
client_ip = st.selectbox("Filter by Client IP", ['All'] + client_ip_list)

# Dropdown for filtering by Status
status_list = pd.read_sql_query("SELECT DISTINCT status FROM logs", conn)['status'].tolist()
status = st.selectbox("Filter by Status", ['All'] + status_list)

# Query modification with filtering
query = f"""
    SELECT 
        date_time, 
        client_ip, 
        duration, 
        status, 
        request_content, 
        error_message, 
        LENGTH(request_content) AS characters_count 
    FROM logs
    WHERE date(date_time) BETWEEN '{start_date}' AND '{end_date}'
"""

# Apply filters
if client_ip != 'All':
    query += f" AND client_ip = '{client_ip}'"
if status != 'All':
    query += f" AND status = '{status}'"

# Sort by date_time (newer to older)
query += " ORDER BY date_time DESC"

# Read the data into a pandas DataFrame
df = pd.read_sql_query(query, conn)

# Display the DataFrame in Streamlit
st.dataframe(df)

# Function to generate PDF with the filtered data
def generate_pdf(dataframe):
    # Define a custom page width and height (e.g., 420mm wide and 297mm tall for a wider page)
    pdf = FPDF('L', 'mm', (297, 420))  # Landscape mode, with custom width
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Set column headers
    headers = ['Date Time', 'Client IP', 'Duration', 'Status', 'Error Message', 'Characters Count']

    # Adjust column widths (customize these widths as necessary)
    col_widths = {
            'Date Time': 45,
            'Client IP': 30,
            'Duration': 75,
            'Status': 20,
            'Error Message': 150,  # Adjust for potentially long content
            'Characters Count': 40
        }

    # Add headers to the PDF
    for header in headers:
        pdf.cell(col_widths[header], 10, header, border=1)
    pdf.ln()

    # Add data rows, using multi_cell only for Error Message
    for row in dataframe.itertuples(index=False):
        pdf.cell(col_widths['Date Time'], 10, str(row.date_time), border=1)
        pdf.cell(col_widths['Client IP'], 10, str(row.client_ip), border=1)
        pdf.cell(col_widths['Duration'], 10, str(row.duration), border=1)
        pdf.cell(col_widths['Status'], 10, str(row.status), border=1)

        # Use multi_cell for Error Message
        x_before_error_message = pdf.get_x()  # Save current x-position
        y_before_error_message = pdf.get_y()  # Save current y-position

        pdf.multi_cell(col_widths['Error Message'], 10, str(row.error_message), border=1)

        # Move back for the remaining column after multi_cell usage
        pdf.set_xy(x_before_error_message + col_widths['Error Message'], y_before_error_message)
        pdf.cell(col_widths['Characters Count'], 10, str(row.characters_count), border=1)

        pdf.ln()

    return pdf

# Button to download as PDF
if st.button("Download Report as PDF"):
    # Generate PDF using the filtered DataFrame (df)
    pdf = generate_pdf(df)
    pdf_output = pdf.output(dest='S').encode('latin1')  # Output to string
    st.download_button("Download PDF", data=pdf_output, file_name="api_logs_report.pdf", mime="application/pdf")

# Close the database connection
conn.close()
# # Function to generate PDF without URL and Method columns
# def generate_pdf(dataframe):
#     # Define a custom page width and height (e.g., 420mm wide and 297mm tall for a wider page)
#     pdf = FPDF('L', 'mm', (297, 420))  # Landscape mode, with custom width
#     pdf.add_page()
#     pdf.set_font("Arial", size=12)
#
#     # Set column headers
#     headers = ['Date Time', 'Client IP', 'Duration', 'Status', 'Error Message', 'Characters Count']
#
#     # Adjust column widths (customize these widths as necessary)
#     col_widths = {
#         'Date Time': 45,
#         'Client IP': 30,
#         'Duration': 75,
#         'Status': 20,
#         'Error Message': 120,  # Adjust for potentially long content
#         'Characters Count': 40
#     }
#
#     # Add headers to the PDF
#     for header in headers:
#         pdf.cell(col_widths[header], 10, header, border=1)
#     pdf.ln()
#
#     # Add data rows, using multi_cell only for Error Message
#     for row in dataframe.itertuples(index=False):
#         pdf.cell(col_widths['Date Time'], 10, str(row.date_time), border=1)
#         pdf.cell(col_widths['Client IP'], 10, str(row.client_ip), border=1)
#         pdf.cell(col_widths['Duration'], 10, str(row.duration), border=1)
#         pdf.cell(col_widths['Status'], 10, str(row.status), border=1)
#
#         # Use multi_cell for Error Message
#         x_before_error_message = pdf.get_x()  # Save current x-position
#         y_before_error_message = pdf.get_y()  # Save current y-position
#
#         pdf.multi_cell(col_widths['Error Message'], 10, str(row.error_message), border=1)
#
#         # Move back for the remaining column after multi_cell usage
#         pdf.set_xy(x_before_error_message + col_widths['Error Message'], y_before_error_message)
#         pdf.cell(col_widths['Characters Count'], 10, str(row.characters_count), border=1)
#
#         pdf.ln()
#
#     return pdf

# Button to download as PDF
# if st.button("Download Report as PDF"):
#     pdf = generate_pdf(df)
#     pdf_output = pdf.output(dest='S').encode('latin1')  # Output to string
#     st.download_button("Download PDF", data=pdf_output, file_name="api_logs_report.pdf", mime="application/pdf")
#
# # Close the database connection
# conn.close()
