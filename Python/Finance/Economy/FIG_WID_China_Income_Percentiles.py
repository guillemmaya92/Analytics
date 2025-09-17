# Libraries
# ===================================================
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.lines import Line2D
import matplotlib.dates as mdates
from matplotlib.ticker import PercentFormatter

# Data Extraction
# ===================================================
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

# Filter dataframes
country = ['CN'] # iso3
variable = ['sdiincj992'] # sdiincj992 / shwealj992
percentile = ['p99p100', 'p90p100', 'p50p90', 'p0p50']
year = range(1978, 2023)
df = df[(df['country'].isin(country)) & df['variable'].isin(variable) & df['percentile'].isin(percentile) & df['year'].isin(year)]
df = df[['country', 'percentile', 'year', 'value']]

# Interpolate monthly data (cubic)
dfs = []

for percentile in df['percentile'].unique():
    temp_df = df[df['percentile'] == percentile].copy()
    temp_df['date'] = pd.to_datetime(temp_df['year'], format='%Y')
    temp_df = temp_df[['date', 'value']]
    temp_df = temp_df.set_index('date').resample('D').mean().interpolate(method='cubic').reset_index()
    temp_df['percentile'] = percentile
    temp_df['year'] = temp_df['date'].dt.year 
    dfs.append(temp_df)

df = pd.concat(dfs, ignore_index=True)

# Formatting date
df['date'] = pd.to_datetime(df['date'])

# Replace percentile values
replace_dict = {
    'p99p100': 'Top 1',
    'p90p100': 'Top 10',
    'p50p90': 'Middle 40',
    'p0p50': 'Bottom 50'
}

df['percentile'] = df['percentile'].replace(replace_dict)

print(df)

# Data Visualization
# ===================================================
# Font and style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Franklin Gothic'], 'font.size': 9})
sns.set(style="white", palette="muted")

# Create figure
fig, ax = plt.subplots(figsize=(8, 6))

# Define custom color palette
palette = {
    "Bottom 50": "#F15B4C",   # naranja
    "Middle 40": "#537C78",  # verde
    "Top 10": "#FAA41B",     # azul
    "Top 1": "#FFD45B"      # rojo
}

# Line plot
sns.lineplot(data=df, x='date', y='value', hue='percentile', palette=palette, legend=False, ax=ax)

# Add title and subtitle
fig.add_artist(plt.Line2D([0.1, 0.1], [0.86, 0.96], linewidth=6, color='#203764', solid_capstyle='butt'))
plt.text(0.02, 1.15, f'Share of Income in China', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.1, f'Distribution across percentiles from 1980 to 2022', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.06, f'(percentage of total income held by percentile groups)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)

# Axis x-axis limits and labels
ax.set_xlim(pd.to_datetime("1980-01-01"), pd.to_datetime("2022-12-31"))
ax.xaxis.set_major_locator(mdates.YearLocator(10))  
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y")) 
ax.tick_params(axis="x", labelsize=9) 
ax.set_xlabel('') 

# Set y-axis limits and labels
ax.set_ylabel('Share of National Income (%)', fontsize=10)
ax.tick_params(axis='y', labelsize=9)
ax.grid(axis='y', linestyle=':', color='gray', alpha=0.7, linewidth=0.25)
ax.yaxis.set_major_formatter(PercentFormatter(xmax=1, decimals=0))

# Remove spines and legend
ax = plt.gca()
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_linewidth(0.5)
ax.spines['left'].set_linewidth(0.5)

# Add percentages for each line at the end of the plot
for percentile in df['percentile'].unique():
    # Filter the last value for each percentile
    subset = df[df['percentile'] == percentile]
    last_value = subset.iloc[-1]
    
    # Create the text with bold percentage
    texto = f"{last_value['percentile']}: " + r"$\bf{" + f"{last_value['value']*100:.2f}" + r"\%}$"
    
    # Add annotation
    plt.annotate(texto, 
                 xy=(last_value['date'], last_value['value']), 
                 xytext=(5, 0),
                 textcoords='offset points', 
                 color='black', 
                 fontsize=8, 
                 weight='normal',
                 va='center',
                 ha='left')

for key, color in palette.items():
    ax.plot([], [], color=color, label=key, linestyle='-', linewidth=2)

ax.legend(
    loc='lower center',
    bbox_to_anchor=(0.5, -0.12),
    ncol=len(palette),
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
plt.text(0, -0.18, space + 'Post-tax national income is the sum of primary incomes over all sectors (private and public), minus taxes.',
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')
      
# Adjust layout
plt.tight_layout()

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_WID_China_Income_Percentiles")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Mostrar el gráfico
plt.show()