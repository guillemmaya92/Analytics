# Libraries
# =====================================================================
import requests
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

# Data Extraction (Countries)
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = df.rename(columns={'index': 'ISO3'})

# Data Extraction (IMF)
# =====================================================================
#Parametro
parameters = ['BCA']

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
                'Parameter': parameter,
                'ISO3': country,
                'Year': int(year),
                'Value': float(value)
            })
    
# Create dataframe
df_imf = pd.DataFrame(records)

# Data Manipulation
# =====================================================================
# Pivot Parameter to columns and filter nulls
df = df_imf.pivot(index=['ISO3', 'Year'], columns='Parameter', values='Value').reset_index()
df = df.dropna(subset=['BCA'], how='any')

# Merge queries
df = df.merge(df_countries, how='left', left_on='ISO3', right_on='ISO3')
df = df[['ISO3', 'Country', 'Year', 'BCA', 'Analytical', 'Region', 'Cod_Currency']]
df = df[df['Region'].notna()]

# Custom region
conditions = [
    df['ISO3'] == 'USA',
    df['ISO3'] == 'CHN',
    df['Cod_Currency'] == 'EUR',
    df['BCA'] >= 0,
    df['BCA'] < 0
]
result = ['USA', 'China', 'Europe', 'Positive', 'Negative']

df['Region'] = np.select(conditions, result)

# Groupping region and year
df = df.groupby(["Region", "Year"], as_index=False)["BCA"].sum()

# Pivot Regions
df = df.pivot_table(index="Year", columns="Region", values="BCA", aggfunc="sum")
    
# Reorder columns
df = df[["USA", "Europe", "China", "Positive", "Negative"]]

# Filter period
df = df.loc[df.index <= 2024]

# Values
usa_percent = df.loc[2024, 'USA'] / (df.loc[2024, 'USA'] + df.loc[2024, 'Negative'])
eur_percent = df.loc[2024, 'Europe'] / (df.loc[2024, 'Europe'] + df.loc[2024, 'China'] + df.loc[2024, 'Positive'])
chn_percent = df.loc[2024, 'China'] / (df.loc[2024, 'Europe'] + df.loc[2024, 'China'] + df.loc[2024, 'Positive'])

print(df)

# Data Visualization
# =====================================================================
# Font and style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Franklin Gothic'], 'font.size': 9})
sns.set(style="white", palette="muted")

# Palette
palette = ["#003366", "#068a41", "#FF0000", "#cfcfcf", "#cfcfcf"]

# Crear figure and plot
ax = df.plot(kind="bar", stacked=True, figsize=(10, 6), width=0.7, color=palette, legend=False)

# Add title and labels
plt.text(0, 1.12, f'Who Absorbs the World’s Savings?', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0, 1.07, f'Global imbalance in the current account', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)

# Adjust ticks and grid
plt.ylim(-2000, 2000)
ax.set_xticks(range(0, len(df) + 1, len(df) // 10))  # Ajustar el rango con len(df)+1
ax.set_xticklabels(df.index[::len(df) // 10], fontsize=9, rotation=0)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, pos: f'{int(x):,}'.replace(",", ".")))
plt.gca().set_xlabel('')
plt.yticks(fontsize=9, color='#282828')
plt.grid(axis='x', linestyle='--', color='gray', linewidth=0.5, alpha=0.3)

# Custom legend values
handles = [
    mpatches.Patch(color=palette[0], label="USA", linewidth=2),
    mpatches.Patch(color=palette[1], label="Eurozone", linewidth=2),
    mpatches.Patch(color=palette[2], label="China", linewidth=2),
    mpatches.Patch(color=palette[3], label="Rest of countries", linewidth=2)
]

# Legend
plt.legend(
    handles=handles,
    loc='lower center', 
    bbox_to_anchor=(0.5, -0.12),
    ncol=4,
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
plt.text(0, -0.15, space + 'IMF World Economic Outlook Database, 2024', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Add text
plt.text(45, -500, f"← {usa_percent:.0%}", fontsize=7, ha='left', va='bottom')
plt.text(45, 250, f"← {eur_percent:.0%}", fontsize=7, ha='left', va='bottom')
plt.text(45, 675, f"← {chn_percent:.0%}", fontsize=7, ha='left', va='bottom')

plt.text(45, 1900, f"World\ndeficit", fontsize=7, fontweight = 'bold', ha='left', va='top')
plt.text(45, -1500, f"World\nsuperavit", fontsize=7, fontweight = 'bold', ha='left', va='bottom')

# Remove spines
for spine in plt.gca().spines.values():
    spine.set_visible(False)

# Save figure...
plt.savefig(r'C:\Users\guillem.maya\Downloads\FIG_IMF_Current_Account.png', format='png', dpi=300)

plt.show()