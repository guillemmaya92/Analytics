# Libraries
# ==========================================
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import re
from io import StringIO

# Data Extraction (insideairbnb)
# ==========================================
# Extract url pages in a dataframe
url = "https://insideairbnb.com/get-the-data/"
response = requests.get(url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')

# Get unique URLs that contain 'listings.csv'
listings_urls = set(a['href'] for a in soup.find_all('a', href=True) if a['href'].endswith('listings.csv'))

# Convert the set back to a DataFrame
df_urls = pd.DataFrame(list(listings_urls), columns=["url"])

# Add city, province and country
df_urls['city'] = df_urls['url'].apply(lambda x: x.strip('/').split('/')[-4].title() if len(x.strip('/').split('/')) >= 4 else None)
df_urls['province'] = df_urls['url'].apply(lambda x: x.strip('/').split('/')[-5].title() if len(x.strip('/').split('/')) >= 5 else None)
df_urls['country'] = df_urls['url'].apply(lambda x: x.strip('/').split('/')[-6].title() if len(x.strip('/').split('/')) >= 6 else None)

# Solve empty values 
df_urls['country'] = df_urls.apply(lambda row: row['city'] if row['province'] == "Data.Insideairbnb.Com" else row['country'], axis=1)
df_urls['country'] = df_urls.apply(lambda row: row['province'] if row['country'] == "Data.Insideairbnb.Com" else row['country'], axis=1)
df_urls['province'] = df_urls.apply(lambda row: row['city'] if row['province'] == "Data.Insideairbnb.Com" else row['province'], axis=1)

# Filter cities and convert to list
urls = df_urls.to_dict(orient='records')

# Create empty list
dfs = []

# Iterate over each url and city in the list of dictionaries
for entry in urls:
    url = entry['url']
    city = entry['city']
    province = entry['province']
    country = entry['country']
    response = requests.get(url)
    df = pd.read_csv(StringIO(response.text), encoding='utf-8')
    df['city'] = city
    df['province'] = province
    df['country'] = country
    dfs.append(df)

# Concatenate dataframes
df = pd.concat(dfs, axis=0, ignore_index=True)

# Data Manipulation
# ==========================================
# Group and category data
host_count = df.groupby(['host_id']).size().reset_index(name='count')
bins = [0, 1, 2, 5, 10, 100, float('inf')]
labels = ['1', '2', '+2', '+5', '+10', '+100']
host_count['host_category'] = pd.cut(host_count['count'], bins=bins, labels=labels, right=True)

# Join and select columns
df = pd.merge(df, host_count, on='host_id', how='left')
df = df[['city', 'id', 'host_id', 'host_name', 'host_category', 'count', 'license']]

# Check if have license
df['license_category'] = df['license'].apply(lambda x: 0 if pd.isna(x) or x == 'Exempt' else 1)

# Grouping by host category
df = df.groupby(['city', 'host_category']).agg(
    {'id': 'count', 'license_category': 'sum'}).reset_index()

# Rename columns
df = df.rename(columns={'id': 'property', 'license_category': 'license'})

# Calculate percents
df['side'] = np.where(df['host_category'].isin(['1', '2']), 'left', 'right')
df['property_percent'] = df['property'] / df.groupby('city')['property'].transform('sum') * 100
df['property_percent'] *= df['side'].eq('left').map({True: -1, False: 1})

# Pivot columns
df_pivot = df.pivot(index="city", columns="host_category", values="property_percent").fillna(0)

# Define column with values for individuals and professionals
df_pivot['total_left'] = df_pivot['1'] + df_pivot['2']
df_pivot['total_right'] = df_pivot['+2'] + df_pivot['+5'] + df_pivot['+10'] + df_pivot['+100']
df_pivot = df_pivot.sort_values(by='total_left', ascending=True)

# Select and order columns
order = ["2", "1", "+2", "+5", "+10", "+100"]
dfplot = df_pivot[order]

print(dfplot)
