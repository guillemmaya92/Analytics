# Libraries
# ======================================
import eurostat
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches

# EUROSTAT Data
# ======================================
# Get Data from Eurostat
dataset = eurostat.get_data_df('TGS00005')
df = pd.DataFrame(dataset)

# Select and rename columns
df = df[['geo\TIME_PERIOD', '2019']]
df = df.rename(columns={'geo\\TIME_PERIOD': 'geo'})

# GEOPANDAS Data
# ======================================
# Read GEOJSON file
geojson_url = "https://gisco-services.ec.europa.eu/distribution/v2/nuts/geojson/NUTS_RG_60M_2021_4326_LEVL_2.geojson"
gdf = gpd.read_file(geojson_url)

# Merge dataframes
gdf = gdf.merge(df, left_on='NUTS_ID', right_on='geo')

# Filter french islands
gdf = gdf[~gdf['NUTS_ID'].str.startswith('FRY')]
gdf = gdf[~gdf['NUTS_ID'].str.startswith('ES70')]
gdf = gdf[~gdf['NUTS_ID'].str.startswith('PT20')]
gdf = gdf[~gdf['NUTS_ID'].str.startswith('PT30')]

# STATIC Map
# ======================================
# Font Style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Open Sans'], 'font.size': 10})

# Create figure
fig, ax = plt.subplots(1, 1, figsize=(12, 12))

# Define palette range
ranges = [7000, 16000, 22000, 27000, 32000, 38000, 80000]
colors = ['#d66d35', '#e5a53e', '#efcd94', '#d5dcef', '#88a0d0', '#4b6cb0']  # Colores específicos para cada rango
labels = [
    '≥ 5 700 to 12 800',
    '≥ 12 800 to 17 600',
    '≥ 17 600 to 22 000',
    '≥ 22 000 to 27 000',
    '≥ 27 000 to 32 200',
    '≥ 32 200 to 70 400'
]

# Plot Map
gdf.plot(
    column='2019', 
    ax=ax, 
    legend=False,
    cmap=mcolors.ListedColormap(colors), 
    linewidth=0.15, 
    edgecolor='black', 
    norm=mcolors.BoundaryNorm(boundaries=ranges, ncolors=len(colors))
)

# Custom Legend
patches = [mpatches.Patch(color=color, label=label) for color, label in zip(colors, labels)]
legend = ax.legend(
    handles=patches, 
    loc='upper left', 
    fontsize=8, 
    title="GDP per capita", 
    title_fontsize=9, 
    labelspacing=0.5, 
    borderpad=0.3
)
legend.get_title().set_fontweight('bold')
plt.subplots_adjust(right=0.8)

# Configuration
plt.text(0, 1.05, 'Regional GDP per capita', fontsize=13, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0, 1.02, 'By NUTS 2 Region (Europe)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)
ax.set_axis_off()

 # Add Year label
formatted_date = 2019 
ax.text(1, 1.06, f'{formatted_date}',
    transform=ax.transAxes,
    fontsize=22, ha='right', va='top',
    fontweight='bold', color='#D3D3D3')

# Add Data Source
plt.text(0, -0.1, 'Data Source: Eurostat (2024), GDP and main components (output, expenditure and income)', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight = 'bold',
    color='gray')

# Add Notes
plt.text(0, -0.12, 'Notes: Gross domestic product (GDP) at current market prices by NUTS 2 region', 
    transform=plt.gca().transAxes,
    fontsize=8, 
    color='gray')

# Add author
plt.text(1, -0.1, '@guillemmaya.com', 
    transform=plt.gca().transAxes, 
    fontsize=8, 
    color='#212121', 
    ha='right')

# Save it!
plt.savefig('C:/Users/guill/Downloads/FIG_EUROSTAT_Map_GDP.png', format='png', bbox_inches='tight')

# Plot it!
plt.show()
