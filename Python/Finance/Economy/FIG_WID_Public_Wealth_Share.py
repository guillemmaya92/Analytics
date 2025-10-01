# Libraries
# ==============================================
import requests
import pandas as pd
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.ticker import PercentFormatter
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from io import BytesIO
import os

# Data Extraction
# ==============================================
# Define CSV path
path = r'C:\Users\guillem.maya\Downloads\wid_all_data\analyze'

# List to save dataframe
list = []

# Iterate over each file
for archivo in os.listdir(path):
    if archivo.startswith("WID_data_") and archivo.endswith(".csv"):
        df = pd.read_csv(os.path.join(path, archivo), delimiter=';')
        list.append(df)

# Combine all dataframes and create a copy
df = pd.concat(list, ignore_index=True)

# Filter years and measures
df = df[(df['year'] >= 1980) & (df['year'] <= 2023) &
        (df['variable'].isin(["wpweali999", "wgweali999", "mpweali999", "mgweali999", "xlcusxi999"])) &
        (df['country'].isin(["JP", "US", "CN", "DE", "RU"]))]

# Pivotar to columns
df = df.pivot_table(index=['country', 'year'], 
                    columns='variable', 
                    values='value').reset_index()

# Create columns
df['private_wealth_ratio'] = df['wpweali999']
df['public_wealth_ratio'] = df['wgweali999']
df['public_wealth_usd'] = df['mgweali999'] / df['xlcusxi999']
df['private_wealth_usd'] = df['mpweali999'] / df['xlcusxi999']
df['public_wealth_percent'] = df['mgweali999'] / (df['mgweali999'] + df['mpweali999'])
df['total_wealth_usd'] = (df['mgweali999'] + df['mpweali999']) / df['xlcusxi999']

# Select columns
df = df[['country', 'year', 'public_wealth_percent']]

# Add country names
country_names = {
    "CN": "China",
    "US": "United States",
    "DE": "Germany",
    "JP": "Japan",
    "RU": "Russia",
}

# Añadir la columna 'name'
df["name"] = df["country"].map(country_names)

# Interpolate monthly
dfs = []
for country in df["country"].unique():
    temp_df = df[df["country"] == country].copy()
    temp_df["date"] = pd.to_datetime(temp_df["year"], format="%Y")
    temp_df = temp_df.set_index("date")
    temp_df = temp_df.resample("M").mean(numeric_only=True).interpolate(method="cubic")
    temp_df = temp_df.reset_index()
    temp_df["country"] = country
    temp_df["year"] = temp_df["date"].dt.year
    dfs.append(temp_df)
df = pd.concat(dfs, ignore_index=True)

# Formatting date
df['date'] = pd.to_datetime(df['date'])

# Specific order countries
df = df.sort_values(
    ["country", "date"],
    key=lambda col: col.map({c: i for i, c in enumerate(["RU","JP","DE","US","CN"])}) 
                   if col.name=="country" else col
)

# Show df
print(df)

# Data Visualization
# ==============================================
# Font and style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Franklin Gothic'], 'font.size': 9})
sns.set(style="white", palette="muted")

# Create figure
fig, ax = plt.subplots(figsize=(8, 6))

# Define custom color palette
palette = {
    "CN": "#C00000", # "#C00000",
    "US": "#203764", # "#203764",
    "DE": "#DFF7D0", # "#548235",
    "JP": "#F5DCB4", # "#FAA41B",
    "RU": "#F3E1F5", # "#A0A5BB"
}

# Line plot
sns.lineplot(data=df, x='date', y='public_wealth_percent', hue='country', palette=palette, legend=False, ax=ax)

# Add title and subtitle
fig.add_artist(plt.Line2D([0.095, 0.095], [0.865, 0.965], linewidth=6, color='#203764', solid_capstyle='butt'))
plt.text(0.02, 1.12, f'Declining of Public Property', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.07, f'Capitalization phase toward a mostly privatized economy', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.03, f'(net public wealth as percent of net national)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)

# Axis x-axis limits and labels
ax.set_xlim(pd.to_datetime("1980-01-01"), pd.to_datetime("2023-01-31"))
ax.xaxis.set_major_locator(mdates.YearLocator(10))  
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y")) 
ax.tick_params(axis="x", labelsize=9) 
ax.set_xlabel('') 

# Set y-axis limits and labels
ax.set_ylabel('Share of Public Wealth (%)', fontsize=10)
ax.tick_params(axis='y', labelsize=9)
ax.grid(axis='y', linestyle=':', color='gray', alpha=0.7, linewidth=0.25)
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))

# Remove spines and legend
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(0.5)
ax.spines['left'].set_linewidth(0.5)

# URLs flags
flag_urls = {
    'CN': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/CN.png',
    'US': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/US.png',
    'JP': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/JP.png',
    'DE': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/DE.png',
    'RU': 'https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/RU.png'
}

# Download and read flags
flags = {country: mpimg.imread(BytesIO(requests.get(url).content)) for country, url in flag_urls.items()}

# Add percentage and flag
for country in df['country'].unique():
    subset = df[df['country'] == country]
    last_value = subset.iloc[-1]

    # Texto con el porcentaje
    texto = f"{last_value['country']}: " + r"$\bf{" + f"{last_value['public_wealth_percent']*100:.2f}" + r"\%}$"

    # Color del texto: gris si no es CN ni US
    text_color = 'black' if country in ["CN", "US"] else 'gray'
    
    # Añadir texto
    plt.annotate(
        texto,
        xy=(last_value['date'], last_value['public_wealth_percent']),
        xytext=(20, 0),
        textcoords='offset points',
        color=text_color,
        fontsize=8,
        weight='normal',
        va='center',
        ha='left'
    )

    # Imagen de la bandera
    flag_img = flags[country]

    # Aplicar transparencia si el país no es CN
    if country not in ["CN", "US"]:
        imagebox = OffsetImage(flag_img, zoom=0.021, alpha=0.4)  # con transparencia
    else:
        imagebox = OffsetImage(flag_img, zoom=0.021)  # sin transparencia

    ab = AnnotationBbox(
        imagebox,
        (last_value['date'], last_value['public_wealth_percent']),
        frameon=False,
        box_alignment=(0, 0.5),
        xybox=(5, 0),
        xycoords='data',
        boxcoords="offset points"
    )

    plt.gca().add_artist(ab)

# Add Legend
legend = {
    "China": "#C00000",
    "Russia": "#D4D6E0",
    "Japan": "#F0D19F",
    "Germany": "#CDECB9", 
    "US": "#B2C0DD"
}

# Create custom legend
for key, color in legend.items():
    ax.plot([], [], color=color, label=key, linestyle='-', linewidth=2)

ax.legend(
    loc='lower center',
    bbox_to_anchor=(0.5, -0.12),
    ncol=len(legend),
    fontsize=8,
    frameon=False,
    handlelength=1.5,
    handleheight=1,
    borderpad=0.2,
    columnspacing=0.8
)

# Add Data Source
plt.text(0, -0.15, 'Data Source:', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')
space = " " * 23
plt.text(0, -0.15, space + 'World Inequality Database (WID)', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Add Note
plt.text(0, -0.18, 'Notes:', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')
space = " " * 12
plt.text(0, -0.18, space + 'Net public wealth is the total value of assets owned by the government sector, minus its debts',
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')
      
# Adjust layout
plt.tight_layout()

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_WID_Public_Wealth_Share")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Mostrar el gráfico
plt.show()