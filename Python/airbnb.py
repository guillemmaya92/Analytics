# Libraries
# ==========================================
import pandas as pd

# Data Extraction (insideairbnb)
# ==========================================
url1 = 'https://data.insideairbnb.com/spain/catalonia/girona/2024-09-29/visualisations/listings.csv'
url2 = 'https://data.insideairbnb.com/spain/catalonia/barcelona/2024-09-06/visualisations/listings.csv'
df1=pd.read_csv(url1)
df2=pd.read_csv(url2)
df = pd.concat([df1, df2], axis=0)

# Data Manipulation
# ==========================================
# Group and category data
host_count = df.groupby(['host_id']).size().reset_index(name='count')
bins = [0, 1, 2, 5, 10, 100, float('inf')]
labels = ['1', '2', '+2', '+5', '+10', '+100']
host_count['host_category'] = pd.cut(host_count['count'], bins=bins, labels=labels, right=True)

# Join and select columns
df = pd.merge(df, host_count, on='host_id', how='left')
df = df[['id', 'host_id', 'host_name', 'host_category', 'count', 'license']]

# Check if have license
df['license_category'] = df['license'].apply(lambda x: 0 if pd.isna(x) or x == 'Exempt' else 1)

# Grouping by host category
df = df.groupby('host_category').agg(
    {'id': 'count', 'license_category': 'sum'}).reset_index()

# Rename columns
df = df.rename(columns={'id': 'property', 'license_category': 'license'})

# Calculate percents
df['property_percent'] = df['property'] / df['property'].sum()
df['license_percent'] = df['license'] / df['property']

print(df)