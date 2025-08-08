# Libraries
# =====================================================================
import requests
import wbgapi as wb
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
from matplotlib.ticker import FuncFormatter
import seaborn as sns
import matplotlib.image as mpimg
import os
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Data Extraction (Countries)
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = df.rename(columns={'index': 'ISO3'})

# Data Extraction - WBD (1960-1980)
# =====================================================================
# To use the built-in plotting method
indicator = ['NY.GDP.PCAP.CD']
countries = df_countries['ISO3'].tolist()
data_range = range(1960, 2024)
data = wb.data.DataFrame(indicator, countries, data_range, numericTimeKeys=True, labels=False, columns='series').reset_index()
df_wb = data.rename(columns={
    'economy': 'iso3',
    'time': 'year',
    'NY.GDP.PCAP.CD': 'NGDPDPC'
})

# Adjust LP and filter before 1980
df_wb = df_wb[df_wb['year'] < 1980]

# Data Extraction - IMF (1980-2030)
# =====================================================================
#Parametro
parameters = ['NGDPDPC']

# Create an empty list
records = []

# Iterar sobre cada parámetro
for parameter in parameters:
    # Request URL
    url = f"https://www.imf.org/external/datamapper/api/v1/{parameter}"
    response = requests.get(url)
    data = response.json()
    values = data.get('values', {})

    # Iterate over each country and year
    for country, years in values.get(parameter, {}).items():
        for year, value in years.items():
            records.append({
                'parameter': parameter,
                'iso3': country,
                'year': int(year),
                'value': float(value)
            })
    
# Create dataframe
df_imf = pd.DataFrame(records)

# Pivot Parameter to columns and filter nulls
df_imf = df_imf.pivot(index=['iso3', 'year'], columns='parameter', values='value').reset_index()

# Data Manipulation
# =====================================================================
# Concat and filter dataframes
df = pd.concat([df_wb, df_imf], ignore_index=True)
df = df[df['NGDPDPC'].notnull()]

# USA Dataframe
df_usa = df[df['iso3'] == 'USA']
df_usa = df_usa.rename(columns={'NGDPDPC': 'NGDPDPC_USA'})
df = df.merge(df_usa[['year', 'NGDPDPC_USA']], on='year', how='left')

# Calculate relative to USA
df['relative_usa'] = df['NGDPDPC'] / df['NGDPDPC_USA'] * 100
df['relative_usa_log'] = np.log(df['relative_usa'])
df = df[['iso3', 'year', 'relative_usa', 'relative_usa_log']]

# Filter for specific countries
df = df[df['iso3'].isin(['USA', 'DEU', 'JPN', 'KOR', 'CHN', 'IND', 'IDN', 'VNM'])]
df = df[
    (df['iso3'] != 'VNM') |
    ((df['iso3'] == 'VNM') & (df['year'] > 1990))
]

print(df)

# Data Visualization
# =====================================================================
# Font and style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Franklin Gothic'], 'font.size': 9})
sns.set(style="white", palette="muted")

# Palette
palette = {
    'USA': "#093e64",
    'DEU': "#21aa4e",
    'JPN': "#9a9c1c",
    'CHN': "#a02c2c",
    'KOR': "#58afbe",
    'IDN': "#883F88",
    'VNM': "#5d3b7c",
    'IND': "#2a282c",
}

# Plotting
fig, ax = plt.subplots(figsize=(8, 6))
lines = sns.lineplot(data=df, x='year', y='relative_usa_log', hue='iso3', palette=palette)
ax.legend_.remove()
ax.grid(False)

# Add title and labels
fig.add_artist(plt.Line2D([0.1, 0.1], [0.87, 0.97], linewidth=6, color='#203764', solid_capstyle='butt'))
plt.text(0.02, 1.13, f'The Midle Income Trap', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.09, 'Highlighting economic growth challenges across emerging markets', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.05, f'(GDP per capita relative to USA)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)    

# Configuration of axes
ax.set_yticks([0.9, 1.8, 2.7, 3.6, 4.6052, 5.52])
ax.set_ylim(0, np.log(250))
ax.set_xlim(1960, 2035)
ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f'{np.exp(y):.0f}%'))
ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax.set_ylabel("GDP per capita (relative to USA)", fontsize=9, fontweight='bold')
plt.gca().set_xlabel('')
plt.yticks(fontsize=9, color='#282828')
plt.xticks(fontsize=9, rotation=0)
plt.grid(axis='y', linestyle='--', color='gray', linewidth=0.5, alpha=0.3)

# Color rectangles
ymin, ymax = ax.get_ylim()
ax.axvspan(1960, 2035, ymin=0 / ymax, ymax=1.8 / ymax, color='#E6ADAD', alpha=0.3)
ax.axvspan(1960, 2035, ymin=1.8 / ymax, ymax=3.6 / ymax, color='#E6E2AD', alpha=0.3)
ax.axvspan(1960, 2035, ymin=3.6 / ymax, ymax=5.52 / ymax, color='#B2E6AD', alpha=0.3)

# Define flags
flag_urls = {
    'USA': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/US.png',
    'DEU': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/DE.png',
    'JPN': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/JP.png',
    'CHN': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/CN.png',
    'KOR': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/KR.png',
    'IND': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/IN.png',
    'IDN': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/ID.png',
    'VNM': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/VN.png',
}

# Load flags
flags = {country: mpimg.imread(BytesIO(requests.get(url).content)) for country, url in flag_urls.items()}

# Add flags
flag_offsets = {
    'USA': {'dx': 0.8, 'dy': 0},
    'DEU': {'dx': 0.8, 'dy': 0},
    'JPN': {'dx': 0.8, 'dy': 0.15},
    'CHN': {'dx': 0.8, 'dy': 0},
    'KOR': {'dx': 0.8, 'dy': -0.15},
    'IDN': {'dx': 0.8, 'dy': 0.11},
    'VNM': {'dx': 0.8, 'dy': -0.11},
    'IND': {'dx': 0.8, 'dy': -0.06},
}

for iso3 in df['iso3'].unique():
    if iso3 in flags:
        df_country = df[df['iso3'] == iso3]
        last_year = df_country['year'].max()
        last_value = df_country[df_country['year'] == last_year]['relative_usa_log'].values[0]
        img = flags[iso3]
        imagebox = OffsetImage(img, zoom=0.025)

        # Add offsets
        dx = flag_offsets.get(iso3, {}).get('dx', 0.5)
        dy = flag_offsets.get(iso3, {}).get('dy', 0.0)

        ab = AnnotationBbox(
            imagebox,
            (last_year + dx, last_value + dy),
            frameon=False,
            box_alignment=(0, 0.5)
        )
        ax.add_artist(ab)

# Custom legend values
handles = [
    mpatches.Patch(color=palette['USA'], label="USA", linewidth=2),
    mpatches.Patch(color=palette['DEU'], label="Germany", linewidth=2),
    mpatches.Patch(color=palette['JPN'], label="Japan", linewidth=2),
    mpatches.Patch(color=palette['KOR'], label="South Korea", linewidth=2),
    mpatches.Patch(color=palette['CHN'], label="China", linewidth=2),
    mpatches.Patch(color=palette['IDN'], label="Indonesia", linewidth=2),
    mpatches.Patch(color=palette['VNM'], label="Vietnam", linewidth=2),
    mpatches.Patch(color=palette['IND'], label="India", linewidth=2),
]


# Legend
legend = plt.legend(
    handles=handles,
    loc='lower center', #center
    bbox_to_anchor=(0.5, -0.15),
    ncol=9,
    fontsize=8,
    frameon=False,
    handlelength=0.5,
    handleheight=0.5,
    borderpad=0.2,
    columnspacing=0.4
)

# Add Data Source
plt.text(0, -0.18, 'Data Source:', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')
space = " " * 23
plt.text(0, -0.18, space + 'IMF World Economic Outlook Database, World Bank Data', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Remove spines
for spine in plt.gca().spines.values():
    spine.set_visible(False)


# Adjust layout
plt.tight_layout()

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_IMF_Middle_Income_Evolution.png")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Show :)
plt.show()