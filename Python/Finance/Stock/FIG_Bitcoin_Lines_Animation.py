# Libraries
# ==============================================================================
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter, FFMpegWriter
import requests

# Get API Data
# ==============================================================================
# Create a df with final year dates
dp = pd.DataFrame({'date': pd.date_range(start='2010-12-31', end='2024-12-31', freq='Y')})
dp['to_ts'] = dp['date'].apply(lambda x: int(pd.to_datetime(x).timestamp()))

# Create an empty list
dataframes = []

# Iterate API with each date
for to_ts in dp['to_ts']:
    # Build an URL with parameters and transform data
    url = f"https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=365&toTs={to_ts}"
    response = requests.get(url)
    data = response.json().get("Data", {}).get("Data", [])
    df = pd.DataFrame([
        {
            "symbol": "BTCUSD",
            "date": pd.to_datetime(entry["time"], unit="s").date(),
            "open": entry["open"],
            "close": entry["close"],
            "low": entry["low"],
            "high": entry["high"],
            "volume": entry["volumeto"]
        }
        for entry in data
    ])
    dataframes.append(df)
# Combine all df into one
btc = pd.concat(dataframes, ignore_index=True)

# DataSet 0 - Halving
#================================================================================
halving = {'halving': [0 , 1, 2, 3, 4],
           'date': ['2009-01-03', '2012-11-28', '2016-07-09', '2020-05-11', '2024-04-20'] 
           }

halving = pd.DataFrame(halving)
halving['date'] = pd.to_datetime(halving['date'])

# DataSet 1 - BTC Price
# ==============================================================================
# Definir y ordenar dataset
btc = btc.drop_duplicates()
btc = btc[btc['close'] != 0]
btc['date'] = pd.to_datetime(btc['date'])
btc['year_month'] = btc['date'].dt.strftime('%Y-%m')
btc = btc.set_index('date')
btc = btc.asfreq('D').ffill()
btc = btc.reset_index()
btc.sort_values(by=['date'], inplace=True)
btc = pd.merge(btc, halving, on='date', how='left')
btc['halving'] = btc['halving'].ffill().fillna(0).astype(int)
btc['halving'] = btc['halving'].astype(int)
btc['first_close'] = btc.groupby('halving')['close'].transform('first')
btc['increase'] = (btc['close'] - btc['first_close']) / btc['first_close'] * 100
btc['days'] = btc.groupby('halving').cumcount() + 1
btc['closelog'] = np.log10(btc['close'])
btc = btc[btc['halving'] >= 1]
btc['daystotal'] = btc.groupby('symbol').cumcount() + 1

# Graph 2 - SEABORN
# ==============================================================================
# Font Style
plt.rcParams.update({'font.family': 'sans-serif', 'font.sans-serif': ['Open Sans'], 'font.size': 10})

# Colors Background
regions = [
    (0, 500, '#6B8E23'),  # Green
    (500, 1000, '#FF4500'),  # Red
    (1000, 1500, '#FFA500')  # Orange
    ] 

# Colors Palette Lines
lines = {
    0: '#E0E0E0',  # Very Light Grey
    1: '#C0C0C0',  # Light Grey
    2: '#808080',  # Medium Grey
    3: '#404040',  # Dark Grey
    4: '#8B0000'   # Red
}

# Create a figure
sns.set(style="whitegrid", rc={"grid.color": "0.95", "axes.grid.axis": "y"})
fig, ax = plt.subplots(figsize=(16, 9))

# Function to refresh animation
def update(frame):
    # Seaborn to plot a graph
    ax.clear()
    df_filtered = btc[btc['daystotal'] <= frame]
    sns.lineplot(x='days', y='closelog', hue='halving', data=df_filtered, markers=True, palette=lines, linewidth=1, ax=ax)

    # Add region colors in the background
    for start, end, color in regions:
        plt.axvspan(start, end, color=color, alpha=0.05)

    # Title and axis
    ax.set_title('Bitcoin Logarithmic Trends: Analysis Since Each Halving', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Days', fontsize=10, fontweight='bold')
    ax.set_ylabel('Log Price', fontsize=10, fontweight='bold')
    ax.set_xlim(0, 1500)
    ax.set_xticks(range(0, 1501, 125))
    ax.tick_params(axis='both', labelsize=8)
    ax.legend(title="Halving", loc='lower right', fontsize=8, title_fontsize='10')

    # Custom legend
    new_title = 'Dates:'
    legend = ax.get_legend()
    legend.set_title(new_title)
    new_labels = ['1st Halving: 2012-11-28 to 2016-07-09', '2nd Halving: 2016-07-09 to 2020-05-11', '3rd Halving: 2020-05-11 to 2024-04-20', '4th Halving: 2024-04-20 to present']
    for text, new_label in zip(legend.texts, new_labels):
        text.set_text(new_label)

    # Max First 750 days
    btc1 = df_filtered[(df_filtered['days'] >= 0) & (df_filtered['days'] <= 750)]
    for halving, group in btc1.groupby('halving'):
        max_value = group['closelog'].max()
        max_row = group[group['closelog'] == max_value].iloc[0]
        ax.plot(max_row['days'], max_row['closelog'] + 0.05, marker='*', color='darkgoldenrod', markersize=5)
        ax.text(max_row['days'], max_row['closelog'] + 0.1, f'{max_row["close"]:,.0f} ({max_row["increase"]:,.0f})%', fontsize=7, ha='center', color='darkgoldenrod')

    # Min Between 500 and 1000 days
    btc2 = df_filtered[(df_filtered['days'] >= 500) & (df_filtered['days'] <= 1000)]
    for halving, group in btc2.groupby('halving'):
        min_value = group['closelog'].min()
        min_row = group[group['closelog'] == min_value].iloc[0]
        ax.plot(min_row['days'], min_row['closelog'] - 0.05, marker='v', color='darkred', markersize=5)
        ax.text(min_row['days'], min_row['closelog'] - 0.15, f'{min_row["close"]:,.0f} ({min_row["increase"]:,.0f})%', fontsize=7, ha='center', color='darkred')

    # Max After 1000 days 
    btc3 = df_filtered[(df_filtered['days'] >= 1000) & (df_filtered['days'] <= 1500)]
    for halving, group in btc3.groupby('halving'):
        max_value = group['closelog'].max()
        max_row = group[group['closelog'] == max_value].iloc[0]
        ax.plot(max_row['days'], max_row['closelog'] + 0.05, marker='^', color='darkgreen', markersize=5)
        ax.text(max_row['days'], max_row['closelog'] + 0.1, f'{max_row["close"]:,.0f} ({max_row["increase"]:,.0f})%', fontsize=7, ha='center', color='darkgreen')

    # Custom Last Dots
    max_vals = df_filtered.groupby('halving').agg({'closelog': 'last', 'days': 'max'}).reset_index()
    for index, row in max_vals.iterrows():
        ax.plot(row['days'], row['closelog'], 'ro', markersize=2)

    # Custom Line labels
    for halving, group in df_filtered.groupby('halving'):
        last_point = group.iloc[-1]
        x = last_point['days']
        y = last_point['closelog']
        max_days = group['days'].max()
        ax.text(x + 8, y, f'Halving {halving}\n{max_days} days', color=lines[halving], fontsize=8, ha='left', va='center')
    
    # Add Year Label
    current_year_month = df_filtered['year_month'].max() 
    ax.text(1, 1.05, f'{current_year_month}',
            transform=ax.transAxes,
            fontsize=22, ha='right', va='top',
            fontweight='bold', color='#D3D3D3')
    
    # Add Data Source
    ax.text(0, -0.065, 'Data Source: CryptoCompare ', 
            transform=ax.transAxes, 
            fontsize=8, 
            color='gray')

    # Adjust layout
    ylim = ax.get_ylim()
    ax.set_ylim(ylim[0], ylim[1] + 0.25)

# Create animation...
ani = FuncAnimation(fig, update, frames=np.arange(1, btc['daystotal'].max() + 1), interval=1, repeat=False)

# Save the animation :)
ani.save('C:/Users/guill/Downloads/BTC_Good.webp', writer='imagemagick', fps=30)

# Print it!
plt.show()
