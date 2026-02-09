# Libraries
# =====================================================================
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import requests
import os

# Data (China) 
# =====================================================================
# Read wikipedia data
url = "https://en.wikipedia.org/wiki/List_of_prefecture-level_divisions_of_China_by_GDP"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}
html = requests.get(url, headers=headers).text
tables = pd.read_html(html)
df = tables[0]
df.columns = ['region', '1', '2', '3', 'gdp', '4', 'gdpc', '5']
df['population'] = df['gdp'] / df['gdpc'] * 1000
df = df[['region', 'gdpc', 'population']]
df['region'] = df['region'].str.replace('*', '', regex=False)

data = pd.DataFrame({
    'region': ['Beijing', 'Shangai', 'Chongqing', 'Tianjin', 'Hong Kong', 'Macao', 'Taiwan'],
    'gdpc': [28294, 26747, 12350, 17727, 48800, 36909, 32756],
    'population': [21.8, 24.7, 32.0, 13.9, 7.5, 0.68, 23.3],
})

df = pd.concat([df, data], ignore_index=True)

# Data Manipulation
# =====================================================================
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

# Calculate gini and median
gini_index = gini(df['gdpc'].values, df['population'].values)

# Calculate weighted median
df.sort_values('gdpc', inplace=True)
cumsum = df['population'].cumsum()
cutoff = df['population'].sum() / 2.0
median = df.loc[cumsum >= cutoff, 'gdpc'].iloc[0]

# Show dataframe, gini and median
print(df)
print(gini_index)
print(median)

# Data Visualization
# =====================================================================
# Seaborn figure style
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(12, 8))

# Create a palette
norm = plt.Normalize(df["gdpc"].min(), 25000)
colors = plt.cm.coolwarm_r(norm(df["gdpc"]))

# Create a Matplotlib plot
bars = plt.bar(df['left'], df['gdpc'], width=df['population'], 
        color=colors, alpha=1, align='edge', edgecolor='grey', linewidth=0.1)

# Title
fig.add_artist(plt.Line2D([0.085, 0.085], [0.90, 0.985], linewidth=6, color='#203764', solid_capstyle='butt'))
ax.text(0.02, 1.09, f'Regional GDP Distribution of China', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
ax.text(0.02, 1.06, f'From rural to urban, the role of location in income inequality', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
ax.text(0.02, 1.03, f'(GDP per capita in $US)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)

# Configuration grid and labels
ax.set_xlim(0, df['population_cum'].max()) 
ax.set_ylim(0, df['gdpc'].max() * 1.093)
ax.set_xlabel('Cumulative Population (M)', fontsize=10, fontweight='bold')
ax.set_ylabel('GDP per capita ($USD)', fontsize=10, fontweight='bold')
ax.grid(axis='x')
ax.grid(axis='y', linestyle='--', linewidth=0.5, color='lightgray')
ax.tick_params(axis='x', labelsize=9)
ax.tick_params(axis='y', labelsize=9) 
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax.xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.axhline(y=median, color='red', linestyle='--', linewidth=0.5, zorder=0, alpha=0.4)
ax.text(75, median + 100, f"Median: {median:,.0f}$", color='darkred', fontweight='bold', fontsize=9, ha='center', va='bottom', zorder=2)

# Add text each region except Ávila and Segovia
for i, bar in enumerate(bars):
    region_name = df['region'].iloc[i]
    
    top_cities = [
        'Beijing', 'Shangai', 'Chongqing', 'Tianjin', 'Hong Kong',
        'Ordos', 'Suzhou, Jiangsu', 'Zhenjiang', 'Jieyang', 'Kashgar', 'Shangrao', 'Qujing',
        'Shenzhen', 'Guangzhou', 'Suzhou', 'Chengdu', 'Wuhan', 'Hangzhou', 'Nanjing',
        'Ningbo', 'Qingdao', 'Wuxi', 'Changsha', 'Zhengzhou', 'Fuzhou', 'Quanzhou',
        'Jinan', 'Dongguan', 'Foshan', "Xi'an", 'Dalian', 'Wenzhou', 'Shenyang',
        'Kunming', 'Baoding', 'Shijiazhuang', 'Linyi', 'Harbin', 'Nanyang',
        'Weifang', 'Handan', 'Changchun', 'Xuzhou', 'Ganzhou', 'Zhoukou', 'Nanning',
        'Heze', 'Fujian', 'Jining', 'Shaoyang', 'Hefei', 'Nantong', 'Shangqiu',
        'Tangshan', 'Hengyang', 'Cangzhou', 'Jinhua', 'Luoyang', 'Xingtai',
        'Zhanjiang', 'Zhumadian', 'Bijie', 'Taiwan', 'Macao'
    ]
    
    # Add labels
    if region_name in top_cities:
        x = bar.get_x() + bar.get_width() / 2
        y = bar.get_height()
        
        # Special position
        if region_name == "Macao":
            x += -8
            y += 1000
        elif region_name == "Ordos":
            x += -2
            y += 3500
        elif region_name in ["Jinan", "Foshan", "Qingdao"]:
            x -= 5
            y += 1000
        else:
            y += 1000

        ax.text(
            x, y,
            region_name,
            ha='center', va='bottom', color='#363636', fontsize=7, rotation=90,
        )

# Add Year label 
ax.text(1, 1.12, f'2022',
             transform=plt.gca().transAxes,
             fontsize=22, ha='right', va='top',
             fontweight='bold', color='#D3D3D3')
    
# Add Data Source
ax.text(0, -0.1, 'Data Source: National Bureau of Statistics of China', 
            transform=plt.gca().transAxes, 
            fontsize=8, 
            color='gray')

# Show GINI Index
ax.text(
    0.09, 0.97, f"Gini Index: {gini_index:.2f}", 
    transform=ax.transAxes,
    fontsize=8.5,
    color='black',
    ha='right',
    va='top', 
    bbox=dict(boxstyle="round,pad=0.3", edgecolor='gray', facecolor='white')
)

# Add Gini Index
ax.text(0, -0.12, 'Notes: The Gini coefficient has been calculated using population weights for each region.', 
            transform=plt.gca().transAxes, 
            fontsize=8, 
            color='gray')

# Add label "poorest" and "richest"
ax.text(0, -0.065, 'Low Income',
             transform=ax.transAxes,
             fontsize=11, fontweight='bold', color='darkred', ha='left', va='center')
ax.text(0.915, -0.065, 'High Income',
             transform=ax.transAxes,
             fontsize=11, fontweight='bold', color='darkblue', va='center')

# Adjust layout
plt.tight_layout()

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_BUREAU_Region_Distribution_China_Prefecture.png")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Show :)
plt.show()