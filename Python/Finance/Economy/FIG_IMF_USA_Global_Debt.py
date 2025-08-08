# Libraries
# ================================================
import pandas as pd
import numpy as np
import comtradeapicall
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import matplotlib.image as mpimg
import os
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
import matplotlib.ticker as mticker
import pathlib


# Data Extraction (Countries)
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = df.rename(columns={'index': 'iso3'})

# Data Extraction - IMF (1980-2030)
# =====================================================================
#Parametro
parameters = ['NGDPD', 'CG_DEBT_GDP']

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
df_imf = df_imf.merge(df_countries['iso3'], on='iso3', how='inner')

# Pivot Parameter to columns and filter nulls
df_imf = df_imf.pivot(index=['iso3', 'year'], columns='parameter', values='value').reset_index()
df_imf = df_imf[(df_imf['year'] >= 1980) & (df_imf['year'] <= 2023)]
df_imf['CG_DEBT_GDP'] = df_imf['CG_DEBT_GDP'] / 100 * df_imf['NGDPD']

# Filter for USA and Global
df_usa = df_imf[df_imf['iso3'] == 'USA']
df_usa = df_usa.rename(columns={'CG_DEBT_GDP': 'debt_usa', 'NGDPD': 'gdp_usa'})

df_total = df_imf.groupby('year', as_index=False)[['CG_DEBT_GDP', 'NGDPD']].sum()
df_total = df_total.rename(columns={'CG_DEBT_GDP': 'debt_total', 'NGDPD': 'gdp_total'})

# Merge USA and Global Data
df = df_total.merge(df_usa[['year', 'debt_usa', 'gdp_usa']], on='year', how='left')

# Calculate ratios
df['debt_usa_ratio'] = df['debt_usa'] / df['gdp_usa']
df['gdp_usa_global'] = df['gdp_usa'] / df['gdp_total']
df['debt_usa_global'] = df['debt_usa'] / df['debt_total']

print(df)

# Visualization
# =====================================================================
# Font and style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Franklin Gothic'], 'font.size': 9})
sns.set(style="white", palette="muted")

# Create figure
fig, ax = plt.subplots(figsize=(8, 6))

# Palette
palette = [
    "#003468",  # USA National Debt Ratio
    "#125a2e",  # USA Share of Global GDP
    "#b80000",  # USA Share of Global Debt
]

# Plot data
ax.fill_between(df['year'], df['debt_usa_ratio'], color=palette[0], alpha=0.4)
ax2 = ax.twinx()
ax2.plot(df['year'], df['gdp_usa_global'], linewidth=2, color=palette[1])
ax2.plot(df['year'], df['debt_usa_global'], linewidth=2, color=palette[2])

# Add title and labels
fig.add_artist(plt.Line2D([0.08, 0.08], [0.87, 0.97], linewidth=6, color='#203764', solid_capstyle='butt'))
plt.text(0.02, 1.12, f'U.S. Debt Ratio and Global Economic Share', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.08, f'While debt expands, global dominance contracts', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.04, f'(indicators as percent of GDP)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)

# Adjust ticks and grid
plt.xlim(1980, 2023)
ax.set_ylim(0, 1.2)
ax2.set_ylim(0, 1.2)
formatter = mticker.FuncFormatter(lambda x, pos: f'{int(x*100):,}%'.replace(",", "."))
ax.yaxis.set_major_formatter(formatter)
ax2.yaxis.set_major_formatter(formatter)
ax2.yaxis.set_ticks([])
ax2.yaxis.set_ticklabels([])   
ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
ax2.xaxis.set_major_locator(ticker.MultipleLocator(10))
plt.gca().set_xlabel('')
ax.tick_params(axis='x', labelsize=9, rotation=0)
ax.tick_params(axis='y', labelsize=9, colors='#282828')
ax2.tick_params(axis='y', labelsize=9, colors='#282828')
ax.grid(axis='y', linestyle='--', color='gray', linewidth=0.5, alpha=0.3)

# Custom legend values
handles = [
    mpatches.Patch(color=palette[0], label="USA National Debt Ratio", linewidth=2),
    mpatches.Patch(color=palette[1], label="USA Share of Global GDP", linewidth=2),
    mpatches.Patch(color=palette[2], label="USA Share of Global Debt", linewidth=2)
]

# Legend
plt.legend(
    handles=handles,
    loc='lower center', 
    bbox_to_anchor=(0.5, -0.12),
    ncol=3,
    fontsize=8,
    frameon=False,
    handlelength=0.5,
    handleheight=0.5,
    borderpad=0.2,
    columnspacing=0.4
)

# Add Data Source
plt.text(0, -0.15, 'Data Source:', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')
space = " " * 23
plt.text(0, -0.15, space + 'IMF World Economic Outlook Database (2025)', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Remove spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)

# Adjust layout
plt.tight_layout()

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_IMF_USA_Global_Debt.png")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Show it :)
plt.show()