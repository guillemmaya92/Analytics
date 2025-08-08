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

'''
# Data Extraction (Countries)
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = df.rename(columns={'index': 'iso3', 'Cod_Currency': 'cod_currency'})

# Data Extraction - IMF (1980-2030)
# =====================================================================
#Parametro
parameters = ['NGDPD']

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
df_imf = (
    df_imf[df_imf['iso3'].isin(['CHN', 'HKG'])]
    .groupby('year', as_index=False)['NGDPD']
    .sum()
)

# Countries
# ================================================
# URL to get the list of countries
url = "https://comtradeapi.un.org/files/v1/app/reference/Reporters.json"
response = requests.get(url)
data = response.json()

# Manipulate the DataFrame
df = pd.DataFrame(data['results'])
df = df[['text', 'reporterCode', 'reporterCodeIsoAlpha3']]
df = df.rename(columns={'text': 'name', 'reporterCode': 'code','reporterCodeIsoAlpha3': 'iso3'})

# Filter and convert to list
df = df[df['iso3'].isin(['CHN', 'HKG'])]
reporter_codes = df['code'].tolist()

print(reporter_codes)

# Data Extraction
# ================================================
# Lista de typeCode a iterar
type_codes = [
    {'typeCode': 'C', 'clCode': 'HS', 'cmdCode': 'TOTAL'},
    {'typeCode': 'S', 'clCode': 'EB', 'cmdCode': '200'}
]

flow_codes = ['X', 'M']

years = range(1999, 2025)

# Lista para guardar los DataFrames
df_list = []

# Iterar por cada typeCode
for year in years:
    for fcode in flow_codes:
        for tcode in type_codes:
            for rcode in reporter_codes:
                df = comtradeapicall.previewFinalData(
                    typeCode=tcode['typeCode'],       # Goods (C) or Services (S)
                    freqCode='A',                     # Annual (A) or Monthly (M)
                    clCode=tcode['clCode'],           # Indicates the product classification used and which version (HS, SITC)
                    period=str(year),                 # Period
                    reporterCode=rcode,               # Country origin (reporter)
                    cmdCode=tcode['cmdCode'],         # Product code in conjunction with classification code (7108 Gold)
                    flowCode=fcode,                   # Exportaciones (X) imports (M)
                    partnerCode=None,                 # Country destination (partner)
                    partner2Code=None,                # The primary partner country or geographic area for the respective trade flow
                    customsCode=None,                 # A secondary partner country or geographic area for the respective trade flow
                    motCode=None,                     # The mode of transport used when goods enter or leave the economic territory of a country
                    maxRecords=500,                   # Limit number of returned records
                    format_output='JSON',             # The output format. CSV or JSON
                    aggregateBy=None,                 # Option for aggregating the query
                    breakdownMode='classic',          # Option to select the classic (trade by partner/product) or plus (extended breakdown) mode
                    countOnly=None,                   # Return the actual number of records if set to True
                    includeDesc=True                  # Option to include the description or not
                )
                df_list.append(df)

df = pd.concat(df_list, ignore_index=True)

# Data Manipulation
# ================================================
# Select and rename columns
df = df[['flowCode', 'typeCode', 'reporterISO', 'reporterDesc', 'partnerISO', 'partnerDesc', 'period', 'primaryValue']]
df.columns = ['flow', 'type', 'reporter_iso', 'reporter_name', 'partner_iso', 'partner_name', 'year', 'value']

# Filter total world trade
df = df[df['partner_iso'] != 'W00']

# Pivot flow to columns
df = df.pivot(
    index=['type', 'reporter_iso', 'reporter_name', 'partner_iso', 'partner_name', 'year'],
    columns='flow',
    values='value'
).reset_index()

# Calculate trade balance
df['T'] = df['X'] - df['M']

# Merge with country data
df = df.merge(df_countries[['iso3', 'cod_currency']], left_on='partner_iso', right_on='iso3', how='left')

# Region Classification
conditions = [
    df['partner_iso'] == 'USA',
    df['partner_iso'].isin(['BRN', 'KHM', 'IDN', 'LAO', 'MYS', 'MMR', 'PHL', 'SGP', 'THA', 'VNM']),
    df['partner_iso'] == 'IND',
    df['partner_iso'] == 'GBR',
    df['partner_iso'] == 'KOR',
    df['partner_iso'] == 'JPN',
    df['partner_iso'] == 'AUS',
    df['cod_currency'] == 'EUR',
    df['T'] >= 0,
    df['T'] < 0
]
choices = ['USA', 'ASEAN', 'India', 'UK', 'South Korea', 'Japan', 'Australia', 'Eurozone', 'Surplus', 'Deficit']
df['region'] = np.select(conditions, choices, default='Others')

# Filter partner not in CHN or HKG
df = df[~df['partner_iso'].isin(['CHN', 'HKG'])]
df = df.groupby(['region', 'year'], as_index=False)['T'].sum()

# Join with IMF data
df['year'] = df['year'].astype(int)
df_imf['year'] = df_imf['year'].astype(int)
df = df.merge(df_imf, on='year', how='left')

# Obtener ruta a la carpeta Descargas del usuario actual
download_path = str(pathlib.Path.home() / "Downloads")

# Nombre del archivo
file_name = "comtrade_export_chn.csv"
full_path = os.path.join(download_path, file_name)
df.to_csv(full_path, index=False)

print(df)
'''

# Ruta al archivo
ruta = r"C:\Users\guillem.maya\Downloads\comtrade_export_chn.csv"

# Leer CSV en un DataFrame
df = pd.read_csv(ruta)

# Adjust data expression
df['NGDPD'] = df['NGDPD'] * 10**9
df['T_Per'] = df['T'] / df['NGDPD'] * 100
df = df[['region', 'year', 'T_Per']]

# Region Classification
conditions = [
    df['region'] == 'USA',
    df['region'] == 'Eurozone',
    df['region'] == 'UK',
    df['region'] == 'ASEAN',
    df['region'] == 'India',
    df['region'] == 'Japan',
    df['region'] == 'South Korea',
    df['region'] == 'Australia',
    df['region'] == 'Surplus',
    df['region'] == 'Deficit',
]
choices = ['USA', 'Eurozone + UK', 'Eurozone + UK', 'ASEAN + India', 'ASEAN + India', 'Japan + South Korea + Australia', 'Japan + South Korea + Australia', 'Japan + South Korea + Australia', 'Surplus', 'Deficit']
df['region'] = np.select(conditions, choices, default='Others')
df = df.groupby(['region', 'year'], as_index=False)['T_Per'].sum()

# Pivot and order columns
df = df.pivot(index='year', columns='region', values='T_Per')
order = ["USA", "Eurozone + UK", "ASEAN + India", "Japan + South Korea + Australia", "Surplus", "Deficit"]
df = df.reindex(columns=order)

print(df)

# Data Visualization
# ================================================
# Font and style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Franklin Gothic'], 'font.size': 9})
sns.set(style="white", palette="muted")

# Custom Palettete
palette = ["#0D0C55", "#2A8F6D", "#bbb123", "#6869b1", "#DFF7DF","#F7DFDF"]

# Create figure
fig, ax = plt.subplots(figsize=(8, 6))

# Plot columnas apiladas
df.plot(kind='bar', stacked=True, width=0.9, color=palette, legend=False, ax=ax)

# Add title and labels
fig.add_artist(plt.Line2D([0.08, 0.08], [0.87, 0.97], linewidth=6, color='#203764', solid_capstyle='butt'))
plt.text(0.02, 1.13, f'China and Hong Kong Trade Balance', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.09, f'Breakdown by trading partners', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.05, f'(trade balance as percent of GDP)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)

# Adjust ticks and grid
plt.ylim(-15, 15)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{int(x):,}%'.replace(",", ".")))
ax.xaxis.set_major_locator(ticker.MultipleLocator(5))
plt.gca().set_xlabel('')
plt.yticks(fontsize=9, color='#282828')
plt.xticks(fontsize=9, rotation=0)
plt.grid(axis='y', linestyle='--', color='gray', linewidth=0.5, alpha=0.3)

# Custom legend values
handles = [
    mpatches.Patch(color=palette[0], label="USA", linewidth=2),
    mpatches.Patch(color=palette[1], label="Eurozone + UK", linewidth=2),
    mpatches.Patch(color=palette[2], label="ASEAN + India", linewidth=2),
    mpatches.Patch(color=palette[3], label="Japan + South Korea + Australia", linewidth=2),
    mpatches.Patch(color=palette[4], label="Surplus", linewidth=2),
    mpatches.Patch(color=palette[5], label="Deficit", linewidth=2)
]

# Legend
plt.legend(
    handles=handles,
    loc='lower center', 
    bbox_to_anchor=(0.5, -0.12),
    ncol=6,
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
plt.text(0, -0.15, space + 'United Nations. (2025). UN Comtrade Database.', 
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
filename = os.path.join(download_folder, f"FIG_CHN_Trade_Balance.png")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Show it :)
plt.show()