# Libraries
# ===================================================
import requests
import os
import pandas as pd
import numpy as np

# Data Extraction (Countries)
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = df.rename(columns={'index': 'ISO3'})

# Data Extraction
# ===================================================
# Define CSV path
path = r'C:\Users\guill\Downloads\wid_all_data'

# List to save dataframe
list = []

# Iterate over each file
for archivo in os.listdir(path):
    if archivo.startswith("WID_data_") and archivo.endswith(".csv"):
        df = pd.read_csv(os.path.join(path, archivo), delimiter=';')
        list.append(df)

# Combine all dataframe
dfx = pd.concat(list, ignore_index=True)

# Data Manipulation
# ===================================================
# Filter dataframe
variable = ['mgdproi999', 'gdiincj992', 'ghwealj992', 'adiincj992', 'anninci992', 'ahweali992', 'anweali992', 'npopuli999', 'xlceuxi999', 'xlcusxi999', 'wwealni999']
percentile = ['p0p100']
df = dfx[dfx['variable'].isin(variable) & dfx['percentile'].isin(percentile)].copy()

# Rename variable
df['variable'] = df['variable'].replace({
    'mgdproi999': 'gdptotal',
    'gdiincj992': 'gincome', 
    'ghwealj992': 'gwealth', 
    'adiincj992': 'tincome',
    'anninci992': 'tincome2',
    'ahweali992': 'twealth',
    'anweali992': 'twealth2',
    'npopuli999': 'population',
    'xlceuxi999': 'xeur',
    'xlcusxi999': 'xusd',
    'wwealni999': 'wiratio'}) 
df = df[['variable', 'country', 'year', 'value']]

# Unpivot to columns
df = df.pivot_table(index=['country', 'year'], columns='variable', values='value')
df = df.reset_index()

# Select and order columns
df = df[['country', 'year', 'gdptotal', 'tincome', 'tincome2', 'twealth', 'twealth2', 'gincome', 'gwealth', 'population', 'xeur', 'xusd', 'wiratio']]

# Save to parquet
df.to_parquet(r'C:\Users\guill\Downloads\WID_Values.parquet', engine='pyarrow')

print(df)