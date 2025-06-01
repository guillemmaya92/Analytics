# Data processing
# ==============================================================================
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine, MetaData, Table, Column, String, Integer, Unicode

# Currency List
#=============================================================================================
url = "https://raw.githubusercontent.com/guillemmaya92/Analytics/refs/heads/master/Data/DIM_Country.json"
data = pd.read_json(url)
df = pd.DataFrame(data).T.reset_index().rename(columns={"index": "cod_iso3", "iso2": "cod_iso2"})

# SQL Server connection
# ==============================================================================
# SQL Server connection details
server = 'DESKTOP-FUOV4IE\MSSQLSERVER_TAB2'
database = 'master'
table_name = 'D_Country'
    
# Create a connection string using username and password
engine_url = f'mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
engine = create_engine(engine_url)
metadata = MetaData()

# SQL Server Dumping Data
# ==============================================================================
# Define the table structure
country_table = Table(
    "D_Country", metadata,
    Column('ISO3', String(3), primary_key=True),
    Column('ISO2', String(2)),
    Column('Cod_Country', Integer),
    Column('Country', String(100)),
    Column('Country_Abr', String(100)),
    Column('Capital', String(100)),
    Column('Region', String(50)),
    Column('Sub_Region', String(100)),
    Column('Class', String(50)),
    Column('Sub_Class', String(50)),
    Column('Category', String(50)),
    Column('Analytical', String(100)),
    Column('Analytical2', String(100)),
    Column('Cod_Currency', String(3)),
    Column('Currency', String(50)),
    Column('Symbol', Unicode(10)),
    Column('Format', Unicode(100)),
    Column('Latitude', String(20)),
    Column('Longitude', String(20)),
    Column('Flag', String(200))
)

# Create the table if it doesn't exist
metadata.create_all(engine)

# Insert DataFrame to SQL Server
with engine.connect() as connection:
    df.to_sql(table_name, con=connection, if_exists='replace', index=False)

# Show result
print(df)
