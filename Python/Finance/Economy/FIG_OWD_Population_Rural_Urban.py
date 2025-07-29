# Libraries
# ========================================================
import pandas as pd
import numpy as np
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm

# Parameters
# ========================================================
code_iso = 'CHN'
name_iso = 'China'
max_urban = 0.82
year_pred = 1980 

# Data Extraction (urban and rural)
# ========================================================
# OWD Urban and Rural Population Data
df = pd.read_csv("https://ourworldindata.org/grapher/share-of-population-urban.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
df = df[df['Code'] == code_iso]
df = df[(df['Year'] >= 1960) & (df['Year'] <= 2023)]
df['Urban'] = df['sp_urb_totl_in_zs'] / 100
df = df[['Code', 'Year', 'Urban']]

# Variables
dfx = df[df['Year'] >= year_pred]
X = dfx[['Year']]
y = dfx['Urban']

# Transformar to polynomial
poly = PolynomialFeatures(degree=3)
X_poly = poly.fit_transform(X)

# Training model
model = LinearRegression()
model.fit(X_poly, y)

# Future year range
future_years = pd.DataFrame({'Year': range(2024, 2051)})
future_X_poly = poly.transform(future_years)

# Prediction
future_preds = model.predict(future_X_poly)

# Limit prediction to max_urban
future_preds = np.clip(future_preds, None, max_urban)

# Dataframe prediction
future_df = pd.DataFrame({
    'Code': code_iso,
    'Year': future_years['Year'],
    'Urban': future_preds
})

# Concatenate future predictions with original dataframe
df = pd.concat([df, future_df], ignore_index=True)

# Add rural percentage
df['Rural'] = 1 - df['Urban']

# Data Extraction (population)
# ========================================================
# OWD Population Data
dfp = pd.read_csv("https://ourworldindata.org/grapher/population-long-run-with-projections.csv?v=1&csvType=full&useColumnShortNames=true", storage_options = {'User-Agent': 'Our World In Data data fetch/1.0'})
dfp = dfp[dfp['Code'] == code_iso]
dfp = dfp[dfp['Year'] >= 1960]
dfp['Total'] = dfp['population_projection'].fillna(0) + dfp['population_historical'].fillna(0)
dfp = dfp[['Code', 'Year', 'Total']]

# Merge urban and rural data with population data
df = df.merge(dfp, on=['Code', 'Year'], how='left')
df['Urban_Per'] = df['Urban']
df['Urban'] = df['Urban'] * df['Total']
df['Rural'] = df['Rural'] * df['Total']
df = df[['Code', 'Year', 'Urban', 'Rural', 'Urban_Per']]

print(df)

# Data Visualization
# ========================================================
# Seaborn figure style
sns.set(style="whitegrid")
fig, ax = plt.subplots(figsize=(12, 8))

# Create a palette
palette1 = ["#D32F2F", "#FBC02D"]  # 1960–2023

# Separar periods (actual and forecast)
df1 = df[df['Year'] <= 2023].copy()
df2 = df[df['Year'] >= 2023].copy()

# Create stacked area plot
df1.set_index('Year')[['Urban', 'Rural']].plot(
    kind="area", stacked=True, color=palette1, ax=ax, linewidth=0
)
df2.set_index('Year')[['Urban', 'Rural']].plot(
    kind="area", stacked=True, color=palette1, ax=ax, linewidth=0, alpha=0.7, legend=False
)

# Title
fig.add_artist(plt.Line2D([0.073, 0.073], [0.90, 0.99], linewidth=6, color='#203764', solid_capstyle='butt'))
ax.text(0.02, 1.09, f'The Urbanization of {name_iso}', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
ax.text(0.02, 1.06, f'A demographic shift from rural to urban centers', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
ax.text(0.02, 1.03, f'(Includes projections through 2050)', fontsize=9, color='#262626', ha='left', transform=plt.gca().transAxes)

# Configuration
ax.set_xlim(1960, 2050)
ax.set_xlabel('')
ax.set_ylabel('Population', fontsize=10, fontweight='bold')
ax.grid(axis='x')
ax.grid(axis='y', linestyle='--', linewidth=0.5, color='lightgray')
ax.tick_params(axis='x', labelsize=9)
ax.tick_params(axis='y', labelsize=9) 
ax.yaxis.set_major_formatter(plt.FuncFormatter(
    lambda x, _: f'{x/1e9:.1f}B' if x >= 1e9 else f'{x/1e6:.0f}M'
))
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

max_total = (df["Urban"] + df["Rural"]).max()

# Establecer el límite del eje y
ax.set_ylim(top=max_total)

# White vertical line at 2023
ax.axvline(x=2023, color='white', linestyle='--', linewidth=1)

# Add text labels for urban percentages
y_offset = df['Urban'].max() * 0.04
for i, year in enumerate(df['Year']):
    if year % 10 == 0 and year not in [1960, 2050] or year in [1962, 2048]:
        urban_value = df.loc[i, 'Urban']
        urban_per = df.loc[i, 'Urban_Per']
        ax.text(
            year,
            urban_value + y_offset,
            f'{urban_per:.0%}',
            ha='center',
            va='bottom',
            fontsize=8,
            color='black',
            weight='bold',
            bbox=dict(facecolor='white', alpha=0.4, edgecolor='none', boxstyle='round,pad=0.3')
        )

# Legend configuration
handles, labels = ax.get_legend_handles_labels()
title_font = fm.FontProperties(weight='bold', size=11)
ax.legend(
    handles[:2], labels[:2],
    title="Zone",
    title_fontproperties=title_font,
    fontsize=10,
    loc='upper left'
)

# Actual text
y_max = ax.get_ylim()[1]
plt.text(
    x=(2023-1960)/2 + 1960,
    y=y_max*0.035,
    s="1960-2023",
    fontsize=9, 
    color='white',
    ha='center',
    va='bottom'
)
plt.text(
    x=(2023-1960)/2 + 1960,
    y=y_max*0.01,
    s="Actual",
    fontsize=9, 
    fontweight='bold',
    color='white',
    ha='center',
    va='bottom'
)

# Forecast text
plt.text(
    x=(2050-2023)/2 + 2023,
    y=y_max*0.035,
    s="2024-2050",
    fontsize=9, 
    color='white',
    ha='center',
    va='bottom'
)
plt.text(
    x=(2050-2023)/2 + 2023,
    y=y_max*0.01,
    s="Forecast",
    fontsize=9, 
    fontweight='bold',
    color='white',
    ha='center',
    va='bottom'
)

# Add Data Source
plt.text(0, -0.1, 'Data Source:', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')
space = " " * 23
plt.text(0, -0.1, space + 'World Bank based on data from the UN Population Division (2025)', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Add Notes
plt.text(0, -0.12, 'Forecast:', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    fontweight='bold',
    color='gray')
space = " " * 17
plt.text(0, -0.12, space + 'Urban and rural population percentages were estimated using a polynomial linear regression model.', 
    transform=plt.gca().transAxes, 
    fontsize=8,
    color='gray')

# Adjust layout
plt.tight_layout()

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_OWD_Population_Rural_Urban_{code_iso}.png")
plt.savefig(filename, dpi=300, bbox_inches='tight')

# Show :)
plt.show()