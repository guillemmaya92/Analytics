# Data processing
# ==============================================================================
import requests
import pandas as pd
import json
import re
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, Date

# Currency List
#=============================================================================================
# API Key
apikey = "079d4119ea5bb192bbe45afc8233a1b4"

# API URL exchange currencies
url_list = f"http://api.exchangerate.host/list?access_key={apikey}"
response_list = requests.get(url_list)
data_list = response_list.json()

# Extract currencies from JSON
currencies = data_list.get('currencies', {})
currency_codes = list(currencies.keys())
currency_string = ','.join(currency_codes)

# Currency Rates
#=============================================================================================
# Parameter years
start_year = 1999
end_year = 2024

# API URL exchange currency rates
url_timeframe = f"http://api.exchangerate.host/timeframe?access_key={apikey}"

# List to save data
rows = []

# Iterate over each year
for year in range(start_year, end_year +1):

    params = {
            'start_date': f"{year}-01-01",
            'end_date': f"{year}-12-31",
            'source': 'EUR',
            'currencies': currency_string
        }

    # Request API data
    response_timeframe = requests.get(url_timeframe, params=params)
    response_text = response_timeframe.text
    json_match = re.search(r'\{.*\}', response_text)
    json_text = json_match.group(0)
    data = json.loads(json_text)

    # Iterate over each date and currency
    for date, rates in data.get('quotes', {}).items():
        if isinstance(rates, dict):
            for symbol, rate in rates.items():
                rows.append({
                    'symbol': symbol,
                    'date': date,
                    'rate': rate
                })

df = pd.DataFrame(rows)

# Filtering outliers
#=============================================================================================
# Format Date
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values(['symbol', 'date'])

# Iterate each symbol
for _ in range(3):
    df['changepercent'] = df.groupby('symbol')['rate'].transform(lambda x: x.pct_change() +1)
    df = df.loc[((df['changepercent'] > 0.8) & (df['changepercent'] < 1.25)) | (df['changepercent'].isna())]
    
df = df[['symbol', 'date', 'rate']]

# Getting a daily frequency
#=============================================================================================
# Create an empty dataframe
df = df.set_index('date')
df = df.groupby('symbol').resample('D').ffill().reset_index(level=0, drop=True)
df = df.reset_index()

# Transformation data
#=============================================================================================
# Get variations
df['change'] = df.groupby('symbol')['rate'].diff()
df['changepercent'] = df.groupby('symbol')['rate'].transform(lambda x: x.pct_change())
df['changesign'] = df['change'].apply(lambda x: '+' if x > 0 else '-' if x < 0 else '=')

# Add moving average columns
df['ma10'] = df.groupby('symbol')['rate'].transform(lambda x: x.rolling(window=10, min_periods=1).mean())
df['ma20'] = df.groupby('symbol')['rate'].transform(lambda x: x.rolling(window=20, min_periods=1).mean())
df['ma50'] = df.groupby('symbol')['rate'].transform(lambda x: x.rolling(window=50, min_periods=1).mean())
df['ma100'] = df.groupby('symbol')['rate'].transform(lambda x: x.rolling(window=100, min_periods=1).mean())
df['ma200'] = df.groupby('symbol')['rate'].transform(lambda x: x.rolling(window=200, min_periods=1).mean())
df['ma300'] = df.groupby('symbol')['rate'].transform(lambda x: x.rolling(window=300, min_periods=1).mean())

# Formatting data
df['date'] = pd.to_datetime(df['date']).dt.date
df['change'] = df['change'].astype(float).round(5)
df['changepercent'] = df['changepercent'].astype(float).round(5)
df['ma10'] = df['ma10'].astype(float).round(5)
df['ma20'] = df['ma20'].astype(float).round(5)
df['ma50'] = df['ma50'].astype(float).round(5)
df['ma100'] = df['ma100'].astype(float).round(5)
df['ma200'] = df['ma200'].astype(float).round(5)
df['ma300'] = df['ma300'].astype(float).round(5)

# Selection columns
df = df[['symbol', 'date', 'rate', 'change', 'changepercent', 'changesign', 'ma10', 'ma20', 'ma50', 'ma100', 'ma200', 'ma300']]
df.columns = ['Symbol', 'Date', 'Rate', 'Change', 'Changepercent', 'Changesign', 'MA10', 'MA20', 'MA50', 'MA100', 'MA200', 'MA300']

# SQL Server connection
# ==============================================================================
# SQL Server connection details
server = '10.0.0.1'
database = 'informes'
table_name = 'H_Currencies_EXH'
    
# Create a connection string using username and password
engine_url = f'mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
engine = create_engine(engine_url)
metadata = MetaData()

# SQL Server Dumping Data
# ==============================================================================
# Define the table structure
exchange_table = Table(
    table_name, metadata,
    Column('Symbol', String(10)),
    Column('Date', Date),
    Column('Rate', Float),
    Column('Change', Float),
    Column('Changepercent', Float),
    Column('Changesign', Float),
    Column('MA10', Float),
    Column('MA20', Float),
    Column('MA50', Float),
    Column('MA100', Float),
    Column('MA200', Float),
    Column('MA300', Float)
)

# Create the table if it doesn't exist
metadata.create_all(engine)

# Insert DataFrame to SQL Server
with engine.connect() as connection:
    df.to_sql(table_name, con=connection, if_exists='replace', index=False)

# Show result
print(df)