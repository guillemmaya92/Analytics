# Libraries
# ===================================================
import requests
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patheffects as patheffects
import matplotlib.font_manager as fm
import matplotlib.image as mpimg
from io import BytesIO

# Extract Data (Countries)
# ===================================================
# Extract JSON to dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = df.rename(columns={'index': 'ISO3'})

# Extract Data (WID)
# ===================================================
# Extract PARQUET to dataframe
url = "https://raw.githubusercontent.com/guillemmaya92/Analytics/master/Data/WID_Values.parquet"
df = pd.read_parquet(url, engine="pyarrow")

# Transform Data
# ===================================================
# Filter nulls and countries
df = df[df['wiratio'].notna()]
df = pd.merge(df, df_countries, left_on='country', right_on='ISO2', how='inner')

# Rename columns
df = df.rename(
        columns={
            'Country_Abr': 'country_name',
            'wiratio': 'beta'
        }
    )

# Filter countries have data post 1980
dfx = df.loc[df['year'] == 1980, 'country']
df = df[df['country'].isin(dfx)]
df = df[df['year'] >= 1980]
df = df[df['Analytical'] == 'Advanced Economies']

# Dataframe countries
dfc = df[df['country'].isin(['CN', 'US', 'FR', 'DE', 'ES'])]

# Select columns and order
df = df[['year', 'country', 'country_name', 'beta']]

print(df)

# Visualization Data
# ===================================================
# Font Style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Open Sans'], 'font.size': 10})

# Create color dictionaire 
palette = {'CN': '#ffc2c2', 'US': '#c2d2ff', 'FR': '#c2ffcb', 'DE': '#e5c2ff', 'ES': '#fffac2'}

# Create line plots
plt.figure(figsize=(12, 8))
sns.lineplot(data=df, x='year', y='beta', hue='country', linewidth=0.3, alpha=0.5, palette=['gray'], legend=False)
sns.lineplot(data=dfc, x='year', y='beta', hue='country', linewidth=2.25, palette=['black'], legend=False)
sns.lineplot(data=dfc, x='year', y='beta', hue='country', linewidth=1.5, palette=palette, legend=False)

# Custom plot
plt.text(0, 1.05, f'Capital is Back', fontsize=13, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0, 1.02, 'Wealth-Income Ratios in Advanced Economies 1980-2023', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)
plt.xlabel('Year', fontsize=10, fontweight='bold')
plt.ylabel(f'Wealth-Income Ratio', fontsize=10, fontweight='bold')
plt.grid(axis='x', alpha=0.8, linestyle='--')
plt.ylim(0, 12)
plt.xlim(1980, 2026)
plt.xticks(range(1980, 2026, 10))
plt.tight_layout()

# Add Data Source
plt.text(0, -0.1, 'Data Source: World Inequality Database (WID)', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')

# Add Notes
plt.text(0, -0.12, 'Notes: Wealth-Income Ratio is the division of national wealth by national income.', 
    transform=plt.gca().transAxes, 
    fontsize=7,
    fontstyle='italic',
    color='gray')

# Add Author
plt.text(0.9, -0.1, '@guillemmaya', 
    transform=plt.gca().transAxes, 
    fontsize=9,
    fontstyle='italic',
    color='#212121')

 # Add Year label
formatted_date = 2023
plt.text(1, 1.06, f'{formatted_date}',
    transform=plt.gca().transAxes,
    fontsize=22, ha='right', va='top',
    fontweight='bold', color='#D3D3D3')

# Legend values
beta_cn = round(df[(df['country'] == 'CN') & (df['year'] == 2023)]['beta'].values[0], 1)
beta_de = round(df[(df['country'] == 'DE') & (df['year'] == 2023)]['beta'].values[0], 1)
beta_es = round(df[(df['country'] == 'ES') & (df['year'] == 2023)]['beta'].values[0], 1)
beta_fr = round(df[(df['country'] == 'FR') & (df['year'] == 2023)]['beta'].values[0], 1)
beta_us = round(df[(df['country'] == 'US') & (df['year'] == 2023)]['beta'].values[0], 1)

# Legend lines
line1 = mlines.Line2D([], [], color=palette['CN'], label=f'China: {beta_cn}', linewidth=2)
line2 = mlines.Line2D([], [], color=palette['DE'], label=f'Germany: {beta_de}', linewidth=2)
line3 = mlines.Line2D([], [], color=palette['ES'], label=f'Spain: {beta_es}', linewidth=2)
line4 = mlines.Line2D([], [], color=palette['FR'], label=f'France: {beta_fr}', linewidth=2)
line5 = mlines.Line2D([], [], color=palette['US'], label=f'USA: {beta_us}', linewidth=2)
line6 = mlines.Line2D([], [], color='grey', label=f'Advanced economies', linewidth=1)
line1.set_path_effects([patheffects.withStroke(linewidth=4, foreground='black')])
line2.set_path_effects([patheffects.withStroke(linewidth=4, foreground='black')])
line3.set_path_effects([patheffects.withStroke(linewidth=4, foreground='black')])
line4.set_path_effects([patheffects.withStroke(linewidth=4, foreground='black')])
line5.set_path_effects([patheffects.withStroke(linewidth=4, foreground='black')])

# Legend plot
plt.legend(handles=[line1, line2, line3, line4, line5, line6], title='Countries', fontsize=8, title_fontproperties=fm.FontProperties(weight='bold'))

# Define flags
flag_urls = {
    'CN': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/CN.png',
    'US': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/US.png',
    'FR': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/FR.png',
    'ES': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/ES.png',
    'DE': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/DE.png'
}

# Load flags
flags = {country: mpimg.imread(BytesIO(requests.get(url).content)) for country, url in flag_urls.items()}

# Add flags
year = 2023
# Adjust flags items
for country, flag in flags.items():
    # Find beta for each country
    beta_value = df[(df['country'] == country) & (df['year'] == year)]['beta'].values[0]
    
    if country == 'CN':
        plt.imshow(flag, aspect='auto', extent=[year+1, year+2, beta_value - 0.2, beta_value + 0.2], alpha=0.7)
    elif country == 'DE':
        plt.imshow(flag, aspect='auto', extent=[year+1, year+2, beta_value - 0.2, beta_value + 0.2], alpha=0.7)
    elif country == 'ES':
        plt.imshow(flag, aspect='auto', extent=[year+1, year+2, beta_value - 0.2, beta_value + 0.2], alpha=0.7)
    elif country == 'FR':
        plt.imshow(flag, aspect='auto', extent=[year+1, year+2, beta_value - 0.4, beta_value + 0], alpha=0.7)
    elif country == 'US':
        plt.imshow(flag, aspect='auto', extent=[year+1, year+2, beta_value - 0.4, beta_value + 0], alpha=0.7)

# Save the animation :)
plt.savefig("C:/Users/guill/Downloads/FIG_WID_Beta_Evolution.png", dpi=300, bbox_inches='tight') 

# Show plot
plt.show()