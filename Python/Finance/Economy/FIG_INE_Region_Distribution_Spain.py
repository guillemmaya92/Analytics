# Libraries
# =====================================================================
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import os

# Data (Spain) 
# =====================================================================
# Read wikipedia data
url = "https://es.wikipedia.org/wiki/Anexo:Provincias_de_Espa%C3%B1a_por_PIB"
tables = pd.read_html(url)

# population
dfp = tables[2]
dfp.columns = ['number', 'region', '2', '3', '4', '5', '6', '7', 'population', '9']
dfp = dfp.iloc[1:].reset_index(drop=True)
dfp =  dfp[['region', 'population']]
dfp = dfp.iloc[:-1]
dfp['population'] = (
    dfp['population']
    .astype(str)
    .str.replace('.', '', regex=False)
    .str.replace(',', '.', regex=False)
)
dfp['population'] = pd.to_numeric(dfp['population'], errors='coerce') / 1000000

# gdp capita
dfg = tables[3]
dfg.columns = ['number', 'region', '2', '3', '4', '5', '6', '7', 'gdpc', '9']
dfg = dfg.iloc[1:].reset_index(drop=True)
dfg =  dfg[['region', 'gdpc']]
dfg = dfg.iloc[:-1]
dfg['gdpc'] = pd.to_numeric(dfg['gdpc'], errors='coerce') * 1000

# Data (Manipulation) 
# =====================================================================
# Merging dataframes
df = pd.merge(dfp, dfg, on='region', how='left')

# Select columns and solve names
df =  df[['region', 'gdpc', 'population']]

# Order dataframe
df = df.sort_values(by=['gdpc'])

# Calculate 'left accrual widths'
df['population_cum'] = df['population'].cumsum()
df['left'] = df['population'].cumsum() - df['population']

# Pondered Gini Function
def gini(x, weights=None):
    if weights is None:
        weights = np.ones_like(x)
    count = np.multiply.outer(weights, weights)
    mad = np.abs(np.subtract.outer(x, x) * count).sum() / count.sum()
    rmad = mad / np.average(x, weights=weights)
    return 0.5 * rmad

# Calculate gini
gini_index = gini(df['gdpc'].values, df['population'].values)

# Mostrar las primeras filas
print(df)
print(gini_index)

# Data Visualization
# =====================================================================
# Seaborn figure style
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(12, 8))

# Create a palette
norm = plt.Normalize(df["gdpc"].min(), df["gdpc"].max())
colors = plt.cm.coolwarm_r(norm(df["gdpc"]))

# Create a Matplotlib plot
bars = plt.bar(df['left'], df['gdpc'], width=df['population'], 
        color=colors, alpha=1, align='edge', edgecolor='grey', linewidth=0.1)

# Title
fig.add_artist(plt.Line2D([0.08, 0.08], [0.90, 0.99], linewidth=6, color='#203764', solid_capstyle='butt'))
ax.text(0.02, 1.09, f'Distribución regional del PIB en España ', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
ax.text(0.02, 1.06, f'De lo rural a lo urbano: la influencia de la localización en la transformación económica', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
ax.text(0.02, 1.03, f'(PIB Capita en euros €)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)

# Configuration grid and labels
ax.set_xlim(0, df['population_cum'].max()) 
ax.set_ylim(0, 45000)
ax.set_xlabel('Población Acumulada (M)', fontsize=10, fontweight='bold')
ax.set_ylabel('PIB Capita €', fontsize=10, fontweight='bold')
ax.grid(axis='x')
ax.grid(axis='y', linestyle='--', linewidth=0.5, color='lightgray')
ax.tick_params(axis='x', labelsize=9)
ax.tick_params(axis='y', labelsize=9)
ax.set_xticks([0 + (df['population_cum'].max() - 0) * i / 5 for i in range(6)]) 
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.axhline(y=28333, color='red', linestyle='--', linewidth=0.5, zorder=0, alpha=0.4)
ax.text(3, 28333 + 100, "Promedio: 28.333$", color='darkred', fontweight='bold', fontsize=9, ha='center', va='bottom', zorder=2)

# Add text each region except Ávila and Segovia
for i, bar in enumerate(bars):
    region_name = df['region'].iloc[i]
    
    # Excluir las regiones de Ávila y Segovia
    if region_name not in ['Ávila', 'Ceuta', 'Segovia', 'Cuenca', 'Teruel', 'Soria']:
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        
        ax.text(
            x, y + 500,
            region_name,
            ha='center', va='bottom', color='#363636', fontsize=7, rotation=90,
        )

# Add Year label 
ax.text(1, 1.12, f'2022',
             transform=plt.gca().transAxes,
             fontsize=22, ha='right', va='top',
             fontweight='bold', color='#D3D3D3')
    
# Add Data Source
ax.text(0, -0.1, 'Fuente: Instituto Nacional Estadística (INE)', 
            transform=plt.gca().transAxes, 
            fontsize=8, 
            color='gray')

# Show GINI Index
ax.text(
    0.09, 0.97, f"Índice Gini: {gini_index:.2f}", 
    transform=ax.transAxes,
    fontsize=8.5,
    color='black',
    ha='right',
    va='top', 
    bbox=dict(boxstyle="round,pad=0.3", edgecolor='gray', facecolor='white')
)

# Add Gini Index
ax.text(0, -0.12, 'Notes: El coeficiente de Gini ha sido calculado utilizando los pesos de población para cada província.', 
            transform=plt.gca().transAxes, 
            fontsize=8, 
            color='gray')

# Add label "poorest" and "richest"
ax.text(0, -0.065, 'Renta Baja',
             transform=ax.transAxes,
             fontsize=12, fontweight='bold', color='darkred', ha='left', va='center')
ax.text(0.915, -0.065, 'Renta Alta',
             transform=ax.transAxes,
             fontsize=12, fontweight='bold', color='darkblue', va='center')

# Adjust layout
plt.tight_layout()

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_INE_Region_Distribution_Spain.png")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Show :)
plt.show()

