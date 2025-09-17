# Libraries
# ===================================================
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from matplotlib.lines import Line2D

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
country = ['CN']
variable = ['wwealhi999', 'wwealgi999', 'wwealni999']
percentile = ['p0p100']
year = range(1978, 2023)
df = df[(df['country'].isin(country)) & df['variable'].isin(variable) & df['percentile'].isin(percentile) & df['year'].isin(year)]
df = df[['country', 'variable', 'year', 'value']]

# Replace values
df['variable'] = df['variable'].replace({
    'wwealhi999': 'private',
    'wwealgi999': 'public',
    'wwealni999': 'total'
})

df['variable'] = df['variable'] + df['country']

# Interpolate monthly data (cubic)
dfs = []

for variable in df['variable'].unique():
    temp_df = df[df['variable'] == variable].copy()
    temp_df['date'] = pd.to_datetime(temp_df['year'], format='%Y')
    temp_df = temp_df[['date', 'value']]
    temp_df = temp_df.set_index('date').resample('D').mean().interpolate(method='cubic').reset_index()
    temp_df['variable'] = variable
    temp_df['year'] = temp_df['date'].dt.year 
    dfs.append(temp_df)

df = pd.concat(dfs, ignore_index=True)

# Formatting date
df['date'] = pd.to_datetime(df['date'])

# Separate detail and total
dfdetail = df[df['variable'] != 'totalCN'].copy()
dftotal = df[df['variable'] == 'totalCN'].copy()

print(df)

# Data Visualization
# ===================================================
# Font and style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Franklin Gothic'], 'font.size': 9})
sns.set(style="white", palette="muted")

# Create figure
fig, ax = plt.subplots(figsize=(8, 6))

# Plot lines
sns.lineplot(data=dftotal, x='date', y='value', hue='variable', legend=False, palette=["#0D0D0D"], linewidth=2)
sns.lineplot(data=dfdetail, x='date', y='value', hue='variable', legend=False, palette=["#153D64", "#C00000"], linewidth=1.25)

# Add title and subtitle
fig.add_artist(plt.Line2D([0.08, 0.08], [0.87, 0.97], linewidth=6, color='#203764', solid_capstyle='butt'))
plt.text(0.02, 1.09, f'Wealth Property in China', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.045, f'Evolution of public and private wealth-income ratio', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
plt.text(0.02, 1.01, f'(wealth divided by annual income)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)

# Axis configuration
plt.grid(axis='y', linewidth=0.5, color='lightgray')
ax.set_xlim(pd.to_datetime("1978-01-01"), pd.to_datetime("2023-12-31"))
plt.xlabel('')
plt.ylabel('')
plt.tick_params(axis='both', which='major', labelsize=9)

# Modify spines
for spine in ['top', 'right', 'left']:
    plt.gca().spines[spine].set_visible(False)
plt.gca().spines['bottom'].set_color('#404040')
plt.gca().spines['bottom'].set_linewidth(0.75)
plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1))

# Create custom legend
legend_elements = [
    Line2D([0], [0], color='#0D0D0D', lw=2, label='Total'),
    Line2D([0], [0], color='#153D64', lw=2, label='Private'),
    Line2D([0], [0], color='#C00000', lw=2, label='Public')
]

plt.legend(
    handles=legend_elements, 
    loc='upper center', 
    bbox_to_anchor=(0.5, -0.065), 
    ncol=3,
    fontsize=8,
    frameon=False
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
plt.text(0, -0.18, space + 'Net private wealth, Net Public Wealth and Net national wealth to net annual national income.',
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Add Total text
lastyear = dftotal['date'].max()
lastvalue = dftotal.loc[dftotal['date'] == lastyear, 'value'].values[0]
plt.text(lastyear + pd.Timedelta(days=180), lastvalue, 'Total', fontweight='bold', va='center', ha='left', fontsize=9, color="#0D0D0D")

# Add Private and Public text
for var, color in zip(dfdetail['variable'].unique(), ["#153D64", "#C00000"]):
    df_var = dfdetail[dfdetail['variable'] == var]
    lastyear = df_var['date'].max()
    lastvalue = df_var.loc[df_var['date'] == lastyear, 'value'].values[0]
    texto = "Public" if color == "#153D64" else "Private"
    plt.text(lastyear + pd.Timedelta(days=180), lastvalue, texto, va='center', ha='left', 
             fontsize=9, color=color)
    
# Adjust layout
plt.tight_layout()

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_WID_China_Wealth_Property")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Show :)
plt.show()