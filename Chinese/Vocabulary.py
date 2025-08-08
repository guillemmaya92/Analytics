# Libraries
# ==============================================================================
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, String, Unicode

# Data Manipulation
# ==============================================================================
# Excel file path
rls_file = r"C:\Users\guillem.maya\Desktop\Guillem\Chinese\Vocabulary.xlsx"

# Vocabulary DataFrame
df = pd.read_excel(rls_file, sheet_name="Vocabulary")

# Rename columns
df = df.rename(columns={
    'Group': 'group',
    'Topic': 'topic',
    'English': 'english',
    'Pinyin': 'pinyin',
    'Hànzì': 'hanzi',
    'Phrase English': 'phrase_english',
    'Phrase Pinyin': 'phrase_pinyin'
})

# Select relevant columns
df = df[['group', 'topic', 'english', 'pinyin', 'hanzi', 'phrase_english', 'phrase_pinyin']]

print(df)

# SQL Server connection
# ==============================================================================
# SQL Server connection details
server = '10.0.0.1'
database = 'informes'
table_name = 'H_Vocabulary'
    
# Create a connection string using username and password
engine_url = f'mssql+pyodbc://@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'
engine = create_engine(engine_url)
metadata = MetaData()

# SQL Server Dumping Data
# ==============================================================================
# Define the table structure
RLS_table = Table(
    table_name, metadata,
    Column('group', String(255)),
    Column('topic', String(255)),
    Column('english', String(255)),
    Column('pinyin', String(255)),
    Column('hanzi', Unicode(50)),
    Column('phrase_english', String(255)),
    Column('phrase_pinyin', String(255)),
)

# Create the table if it doesn't exist
metadata.create_all(engine)

# Insert DataFrame to SQL Server
with engine.connect() as connection:
    df.to_sql(
        table_name, 
        con=connection, 
        if_exists='replace', 
        index=False,
                dtype={
            'hanzi': Unicode(50)
        }
    )

# Show result
print(df)