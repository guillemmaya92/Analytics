# Data processing
# ==============================================================================
import requests
import pandas as pd
import io
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table, Column, String, Float, Date


# Building URL
# ==============================================================================
# Building blocks for the URL
entrypoint = 'https://sdw-wsrest.ecb.europa.eu/service/' # Using protocol 'https'
resource = 'data'           # The resource for data queries is always'data'
flowRef ='EXR'              # Dataflow describing the data that needs to be returned, exchange rates in this case
key = 'D..EUR.SP00.A'       # Defining the dimension values to get all currencies against EUR

# Define the parameters
parameters = {
    'startPeriod': '1970-01-01',  # Start date of the time series
    'endPeriod': '2024-07-25'     # End of the time series
}

# Construct the URL: https://sdw-wsrest.ecb.europa.eu/service/data/EXR/D..EUR.SP00.A
request_url = entrypoint + resource + '/' + flowRef + '/' + key

# API Data Extraction
# ==============================================================================

response = requests.get(request_url, params=parameters, headers={'Accept': 'text/csv'})
df = pd.read_csv(io.StringIO(response.text))
df = df.filter(['CURRENCY', 'TIME_PERIOD', 'OBS_VALUE'], axis=1)
df.columns = ['Symbol', 'Date', 'Close']

# SQL Server connection
# ==============================================================================
# SQL Server connection details
server = '10.0.0.1'
database = 'informes'
table_name = 'H_BCE'
    
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
    Column('Close', Float)
)

# Create the table if it doesn't exist
metadata.create_all(engine)

# Insert DataFrame to SQL Server
with engine.connect() as connection:
    df.to_sql(table_name, con=connection, if_exists='replace', index=False)

# Show result
print(df)
