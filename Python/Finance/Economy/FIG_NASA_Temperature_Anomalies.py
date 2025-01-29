# Libraries
# =========================================
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Data Extraction
# =========================================
# URL NASA GISS global temperature
url = "https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv"

# Read csv
df = pd.read_csv(url, skiprows=1)

# Data Manipulation
# =========================================
# Select columns
df = df[["Year", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "J-D"]]

# Rename columns
df.columns = df.columns.str.lower()
df = df.rename(columns=lambda x: x.lower())

# Unpivot columns
df = df.melt(id_vars=["year"], var_name="month", value_name="value")
df = df[df["month"] == "j-d"]

# Data Visualization
# =========================================
# Font and style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Open Sans'], 'font.size': 9})
sns.set(style="white", palette="muted")

# Define a color map
cmap = plt.get_cmap('coolwarm')
norm = plt.Normalize(-0.5, 1)

# Create figure and plot
plt.figure(figsize=(10, 5))
bars =plt.bar(df['year'], df['value'], color=cmap(norm(df['value'])), width=1, edgecolor='none')

# Add title and labels
plt.text(0, 1.08, f'Global Temperature Anomaly', fontsize=16, fontweight='bold', ha='left', transform=plt.gca().transAxes)
plt.text(0, 1.03, 'Compared with mid -20th century (°C)', fontsize=11, color='#262626', ha='left', transform=plt.gca().transAxes)
plt.xlim(1879, 2025)
plt.axhline(y=0, color='black', linestyle='-', linewidth=0.75)
yticks = [-0.5, -0.25, 0, 0.25, 0.5, 0.75, 1, 1.25]
ytick_labels = [f'{y:+.2f}' if y != 0 else '0' for y in yticks]
plt.yticks(yticks, ytick_labels, fontsize=9)
plt.xticks([1880, 1890, 1900, 1910, 1920, 1930, 1940, 1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020], fontsize=9)
plt.tight_layout()

# Add column labels
for i, year in enumerate(df['year']):
    if year in [1973, 1990, 1998, 2010, 2016, 2024]:
        # Check positive and negative values
        symbol = "+" if df['value'].iloc[i] >= 0 else "-"
        value_text = f"{symbol}{abs(df['value'].iloc[i]):,.2f}"
        
        # Recent value bold
        fontweight = 'bold' if year == df['year'].max() else 'normal'

        # Add label
        plt.text(year, df['value'].iloc[i] + 0.05, value_text,
                 ha='center', va='bottom', fontsize=7, color='#363636', fontweight=fontweight)

# Remove spines
for spine in ["top", "bottom", "right"]:
    plt.gca().spines[spine].set_visible(False)

# Add Data Source
plt.text(0, -0.12, 'Data Source: NASA Goddard Institute for Spaces Studies', 
    transform=plt.gca().transAxes, 
    fontsize=8, 
    color='gray')

 # Add Year label
formatted_date = 2024 
plt.text(1, 1.12, f'{formatted_date}',
    transform=plt.gca().transAxes, 
    fontsize=18, ha='right', va='top',
    fontweight='bold', color='#D3D3D3')

# Save it..
plt.savefig('C:/Users/guillem.maya/Downloads/FIG_NASA_Temperature_Anomalies.png', format='png', bbox_inches='tight')

# Show the plot!
plt.show()

