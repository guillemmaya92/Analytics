# Libraries
#================================================================================
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, Date

# SQL Server Connection
#================================================================================
#  SQL Server connection details
server = 'yourserver'
database = 'yourdatabse'
table_name = 'H_Coil_Prices'

# Create a connection string using username and password
engine_url = f'mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
engine = create_engine(engine_url)
metadata = MetaData()

# Read CSV file
#--------------------------------------------------------------------------------
# Define the file path
file_path = r'\STEEL-US\STEEL-US.csv'
df = pd.read_csv(file_path)

# Format columns
df['Date'] = pd.to_datetime(df['Fecha'], format="%d.%m.%Y")
df['Último'] = pd.to_numeric(df['Último'].str.replace('.', '').str.replace(',', '.'))

# Select and rename columns
df = df[["Date", "Último"]]
dfcsv = df.rename(columns={"Date": "date", "Último": "last"})

# Add a priority column
dfcsv = dfcsv.assign(priority=3)

# SQL Query
#--------------------------------------------------------------------------------
# Define a query
query = "SELECT date, last FROM H_Coil_Prices"

# Create a dataframe
try:
    with engine.connect() as connection:
        dfsql = pd.read_sql(query, connection)
except Exception as e:
    dfsql = pd.DataFrame(columns=['date', 'last'])

# Add a priority column
dfsql = dfsql.assign(priority=2)

# Scrapping Investing Website
#--------------------------------------------------------------------------------
# Get HTML content
url = "https://es.investing.com/commodities/us-steel-coil-futures-historical-data"
response = requests.get(url)
html = response.content

# Parsing HTML with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Finding the specific table (assuming the structure of the HTML)
table = soup.find('table', class_='freeze-column-w-1 w-full overflow-x-auto text-xs leading-4')

# Extract data table
rows = table.find_all('tr')
data = []
for row in rows:
    cols = row.find_all('td')
    cols = [col.text.strip() for col in cols]
    data.append(cols)

# Crate a dataframe
df = pd.DataFrame(data, columns=["Fecha", "Último", "Apertura", "Máximo", "Mínimo", "Vol.", "% var."])
df = df[["Fecha", "Último"]]

# Format and rename columns
df['Fecha'] = pd.to_datetime(df['Fecha'], format="%d.%m.%Y")
df['Último'] = pd.to_numeric(df['Último'].str.replace('.', '').str.replace(',', '.'))
df = df.rename(columns={"Fecha": "date", "Último": "last"})

# Filter last price
dfinv = df[df['date'] == df['date'].max()]

# Add a priority column
dfinv = dfinv.assign(priority=1)

# Transform Data
#--------------------------------------------------------------------------------
# Concat Dataframes, order by date/priority and remove duplicates
df = pd.concat([dfcsv, dfinv, dfsql], ignore_index=True).copy()
df.sort_values(by=['date', 'priority'], inplace=True)
df = df.drop_duplicates(subset=['date'], keep='first')
df = df.drop(columns=['priority'])

# Index Date
df = df.set_index('date')
df = df.asfreq('D').ffill()
df = df.reset_index()

# Calculate variations
df['change'] = df['last'] - df['last'].shift(1)
df['changepercent'] = df['change'] / df['last'].shift(1)

# Formatting
df['changepercent'] = df['changepercent'].round(4)

# SQL Server Dumping Data
#================================================================================
# Define the table structure
exchange_table = Table(
    table_name, metadata,
    Column('date', Date),
    Column('last', Float),
    Column('change', Float),
    Column('changepercent', Float)
)

# Create the table if it doesn't exist
metadata.create_all(engine)

# Insert DataFrame to SQL Server
with engine.connect() as connection:
    df.to_sql(table_name, con=connection, if_exists='replace', index=False)

print(df)