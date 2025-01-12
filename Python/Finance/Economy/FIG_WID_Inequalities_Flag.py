# Libraries
# ===================================================
import os
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go

# Data Extraction (Countries)
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df = df.rename(columns={'index': 'ISO3'})
df = df[['ISO2', 'Country']]
df_countries = df.rename(columns={'ISO2': 'country', 'Country': 'country_name'})

# Data Extraction
# ===================================================
# Define CSV path
path = r'C:\Users\guillem.maya\Downloads\data\X'

# List to save dataframe
list = []

# Iterate over each file
for archivo in os.listdir(path):
    if archivo.startswith("WID_data_") and archivo.endswith(".csv"):
        df = pd.read_csv(os.path.join(path, archivo), delimiter=';')
        list.append(df)

# Combine all dataframes and create a copy
df = pd.concat(list, ignore_index=True)
dfr = df.copy()
dfp = df.copy()

# Filter dataframes
variable = ['adiincj992', 'ahwealj992']
variabler = ['xlceuxi999']
variablep = ['npopuli999']
percentile = ['p0p100']
year = [2002, 2022]
df = df[df['variable'].isin(variable) & df['percentile'].isin(percentile) & df['year'].isin(year)]
dfr = dfr[dfr['variable'].isin(variabler) & dfr['percentile'].isin(percentile) & dfr['year'].isin(year)]
dfp = dfp[dfp['variable'].isin(variablep) & dfp['percentile'].isin(percentile) & dfp['year'].isin([max(year)])]

# Data Manipulation
# ===================================================
# Selection Columns DF
df = df[['country', 'variable', 'year', 'value']]
df['variable'] = df['variable'].replace({'adiincj992': 'income', 'ahwealj992': 'wealth'})

# Selection Columns DFR
dfr = dfr[['country', 'year', 'value']]
dfr = dfr.rename(columns={'value': 'exchange'})

# Selection Columns DFP
dfp = dfp[['country', 'value']]
dfp = dfp.rename(columns={'value': 'population'})

# Join Currencies DFR
df = pd.merge(df, dfr, on=['country', 'year'], how='left')
df['value_eur'] = df['value'] / df['exchange']

# Join Countries
df = pd.merge(df, df_countries, on=['country'], how='left')
df = df[df['country_name'].notna()]

# Replace year values
max_value = df['year'].max()
df['year'] = df['year'].apply(lambda x: 'CY' if x == max_value else 'PY')
df['variable_year'] = df['variable'].astype(str) + df['year'].astype(str)

# Pivot variable
df = df.pivot_table(index=['country', 'country_name'], columns='variable_year', values='value_eur')
df = df.reset_index()
df = df[df['incomeCY'].notna() & df['incomePY'].notna() & df['wealthCY'].notna() & df['wealthPY'].notna()]
df = df[~df['country'].isin(['SL', 'CU', 'LU'])]
df = df[~df['country'].isin(['SZ', 'VA', 'NC', 'CI', 'MW', 'SS', 'MY'])]

# Join Population
df = pd.merge(df, dfp, on=['country'], how='left')

# Ordering
df['incomeCY'] = df['incomeCY'] / 1000
df['incomePY'] = df['incomePY'] / 1000
df['wealthCY'] = df['wealthCY'] / 1000
df['wealthPY'] = df['wealthPY'] / 1000
df['population'] = df['population'] / 1000000
df['total_income'] = df['incomeCY'] * df['population'] / 1000

# Variations
df['betaCY'] = df['wealthCY'] / df['incomeCY']
df['betaPY'] = df['wealthPY'] / df['incomePY']
df['incomeVAR'] = (df['incomeCY'] - df['incomePY']) / df['incomePY'] * 100
df['wealthVAR'] = (df['wealthCY'] - df['wealthPY']) / df['wealthPY'] * 100
df['betaVAR'] = (df['betaCY'] - df['betaPY'])

# Data Visualization
# ===================================================
fig = go.Figure()

# Marker size
marker_size = np.sqrt(df["total_income"] / df["total_income"].max()) * 100 + 3
line_width  = np.sqrt(df["total_income"] / df["total_income"].max()) * 4 + 0.5

# Add scatter plot
fig.add_trace(go.Scatter(
    x=df["wealthCY"],
    y=df["incomeCY"],
    mode='markers',
    text=df["country_name"],
    customdata=np.vstack((df["incomeVAR"], df["wealthVAR"], df["betaCY"], df["betaVAR"])).T,
    marker=dict(
        size=marker_size,
        color="rgba(0,0,0,0)",
        line=dict(
            width=line_width,
            color='black'
        )
    ),
    hovertemplate="<b>Country:</b> %{text}<br>" +
                  "<b>Income Avg (€):</b> %{y:.0f}k | <b>Var. 2002:</b> %{customdata[0]:.2f}%<br>" + 
                  "<b>Wealth Avg (€):</b> %{x:.0f}k | <b>Var. 2002:</b> %{customdata[1]:.2f}%<br>" +
                  "<b>Ratio:</b> %{customdata[2]:.2f} | <b>Var. 2002:</b> %{customdata[3]:.2f}pp<extra></extra>",
    showlegend=False
))

# Add flag images to scatterplot
for i, row in df.iterrows():
    country_iso = row["country"]
    
    # Calculate image size
    image_size = marker_size[i] * 1.12

    # Add the flag image
    fig.add_layout_image(
        dict(
            source=f"https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/{country_iso}.png",
            xref="x",
            yref="y",
            xanchor="center",
            yanchor="middle",
            x=row["wealthCY"],
            y=row["incomeCY"],
            sizex=image_size,
            sizey=image_size,
            sizing="contain",
            opacity=0.8,
            layer="above"
        )
    )
    
# Modeling a line trend
z = np.polyfit(df['wealthCY'], df['incomeCY'], 2, w=df['total_income'])
p = np.poly1d(z)
x_range = np.linspace(df['wealthCY'].min(), df['wealthCY'].max(), 100)
y_range = p(x_range)

# Add the line trend
fig.add_trace(go.Scatter(
    x=x_range,
    y=y_range,
    mode='lines',
    name='Trend Line',
    line=dict(color='darkred', width=0.5),
    showlegend=False
))

# Configuration plot
fig.update_layout(
    title="<b>World Inequality</b>",
    title_x=0.11,
    title_font=dict(size=16),
    annotations=[
        dict(
            text="Exploring Discrepancies between Income and Wealth Averages",
            xref="paper",
            yref="paper",
            x=0,
            y=1.07,
            showarrow=False,
            font=dict(size=11)
        ),
        dict(
            text="<b>Data Source:</b> World Inequality Database (WID)",
            xref="paper",
            yref="paper",
            x=0,
            y=-0.12,
            showarrow=False,
            font=dict(size=10),
            align="left"
        ),
        dict(
            text="<b>Currency:</b> Official exchange rate of the local currency to EUR.",
            xref="paper",
            yref="paper",
            x=0,
            y=-0.14,
            showarrow=False,
            font=dict(size=10),
            align="left"
        ),
        dict(
            text=f"2022",
            xref="paper", 
            yref="paper",
            x=1, 
            y=1.1,
            showarrow=False,
            font=dict(size=22, color='lightgray', weight='bold'),
            align="right"
        )
    ],
    xaxis=dict(
        title="<b>Wealth Average (€)</b>",
        range=[0, 675],
        tickvals=[i * 675 / 6 for i in range(7)],
        ticktext=[f"{int(i * 675 / 6)}k" for i in range(7)],
        showline=True,
        linewidth=1,
        linecolor="black",
        gridcolor="#ebebeb"
    ),
    yaxis=dict(
        title="<b>Income Average (€)</b>",
        range=[0, 120],
        tickvals=[i * 120 / 6 for i in range(7)],
        ticktext=[f"{int(i * 120 / 6)}k" for i in range(7)],
        showline=True,
        linewidth=1,
        linecolor="black",
        gridcolor="#ebebeb"
    ),
    height=750,
    width=750,
    plot_bgcolor="white",   
    paper_bgcolor="white"
)

# Add a custom legend
size_legend = ['Smaller', 'Middle', 'Bigger']
size_values = [5, 10, 20]

for label, size in zip(size_legend, size_values):
    fig.add_trace(go.Scatter(
        x=[None],
        y=[None],
        mode='markers',
        marker=dict(
            size=size,
            color="rgba(0,0,0,0)",
            line=dict(
                width=1,
                color='black'
            )
        ),
        legendgroup='size',
        showlegend=True,
        name=f'{label}'
    ))

fig.update_layout(
    legend=dict(
        title=dict(text='<b>  Total Income</b>'), 
        font=dict(size=11),
        x=0.025,
        y=0.95,
        xanchor='left',
        bgcolor='white',
        bordercolor='black',
        borderwidth=1
    )
)

# Save as HTML file!
fig.write_html("C:/Users/guillem.maya/Desktop/FIG_WID_Inequalities_Flag.html")
fig.write_image("C:/Users/guillem.maya/Desktop/FIG_WID_Inequalities_Flag.png")

# Show the plot!
fig.show()

