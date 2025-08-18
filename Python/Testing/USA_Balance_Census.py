# Libraries
# ============================================
import requests
import pandas as pd
import os

# Parameters
# ============================================
key = '4b7bc64c1dfa7faca1c0b68a73e815c5eae94123'
base = 'https://api.census.gov/data/timeseries/intltrade/'
flows = {
    'exports': 'CTY_CODE,CTY_NAME,ALL_VAL_MO',
    'imports': 'CTY_CODE,CTY_NAME,GEN_VAL_MO'
}
endpoint = 'hs'
param = 'CTY_CODE,CTY_NAME,ALL_VAL_MO'
start = '2000-01'
end = '2025-12' 

# Data Countries
# ============================================
# URL countries
url = "https://www.census.gov/foreign-trade/schedules/c/country.txt"

# Read and clean the country data
dfc = (
    pd.read_csv(url, sep='|', header=None, skiprows=6, engine='python')
      .dropna(axis=1, how='all')
      .rename(columns={0: 'code', 1: 'name', 2: 'iso'})
)

# Select columns
dfc = dfc.astype(str).map(lambda x: x.strip())
dfc = dfc[['code', 'iso']]

# Data Countries (Custom)
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
dfgh = pd.DataFrame(data)
dfgh = pd.DataFrame.from_dict(data, orient='index').reset_index()
dfgh = dfgh.rename(columns={'index': 'iso3'})

# Data Extraction
# ============================================
# List to hold dataframes
dfs = []

# Iterate over each month and year
for flow, param in flows.items():
            url = f'{base}{flow}/{endpoint}?get={param}&key={key}&time=from+{start}+to+{end}'
        
            # Make the request
            r = requests.get(url)
            data = r.json()
                
            # Convert to dataframe
            df = pd.DataFrame(data[1:], columns=data[0])
            df = df.rename(columns={'CTY_CODE': 'code', 'CTY_NAME': 'name', 'ALL_VAL_MO': 'value', 'GEN_VAL_MO': 'value'})
            df['flow'] = flow
            dfs.append(df)

# Concatenate all dataframes
df = pd.concat(dfs, ignore_index=True)

# Data Manipulation
# ============================================
# Merge with country data
df = df.merge(dfc, on='code', how='left')
df = df[['code', 'iso', 'flow', 'time', 'value']]

# Filters countries and pivot table
df = df[df['iso'].notna()]
df['value'] = pd.to_numeric(df['value'], errors='coerce')
df = df.pivot_table(index=['code', 'iso', 'time'], columns='flow', values='value').reset_index()
df['balance'] = df['exports'].fillna(0) - df['imports'].fillna(0)

# Path to save the CSV file
downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
output_file = os.path.join(downloads_path, "census_trade_data.csv")

# Save to CSV
df.to_csv(output_file, index=False)

print(df)