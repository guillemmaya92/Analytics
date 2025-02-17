# Libraries
# =====================================================================
import requests
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import numpy as np

# Data Extraction (Countries)
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = df.rename(columns={'index': 'ISO3'})

# Data Extraction - IMF (1980-2030)
# =====================================================================
#Parametro
parameters = ['NGDPD', 'PPPGDP', 'LP']

# Create an empty list
records = []

# Iterar sobre cada parámetro
for parameter in parameters:
    # Request URL
    url = f"https://www.imf.org/external/datamapper/api/v1/{parameter}"
    response = requests.get(url)
    data = response.json()
    values = data.get('values', {})

    # Iterate over each country and year
    for country, years in values.get(parameter, {}).items():
        for year, value in years.items():
            records.append({
                'Parameter': parameter,
                'ISO3': country,
                'Year': int(year),
                'Value': float(value)
            })
    
# Create dataframe
df_imf = pd.DataFrame(records)

# Pivot Parameter to columns and filter nulls
df_imf = df_imf.pivot(index=['ISO3', 'Year'], columns='Parameter', values='Value').reset_index()

# Filter after 2024
df_imf = df_imf[df_imf['Year'] == 2024]

# Data Manipulation
# =====================================================================
# Concat and filter dataframes
df = df_imf.dropna(subset=['NGDPD', 'PPPGDP', 'LP'], how='any')

# Merge queries
df = df.merge(df_countries, how='left', left_on='ISO3', right_on='ISO3')
df = df[['Region', 'ISO2', 'Country', 'Cod_Currency', 'Year', 'NGDPD', 'PPPGDP', 'LP']]
df = df[df['Cod_Currency'].notna()]

# Calculate PPP
df = df.groupby(['Region', 'ISO2', 'Country', 'Cod_Currency', 'Year'])[['NGDPD', 'PPPGDP', 'LP']].sum()
df = df.reset_index()
df['PPP'] = df['NGDPD'] / df['PPPGDP']
df['NGDPDPC'] = df['NGDPD'] / df['LP']
df['PPPPC'] = df['PPPGDP'] / df['LP']

# Calculate Average Weight and Percent
df['AVG_Weight'] = df.groupby('Year')['NGDPDPC'].transform(lambda x: np.average(x, weights=df.loc[x.index, 'LP']))
df['Percent'] = df['NGDPD'] / df.groupby('Year')['NGDPD'].transform('sum')

# Filtering
df = df[df['NGDPDPC'] < 115 ]
df = df[df['PPP'] < 1.25]
df = df[~df['ISO2'].isin(['SZ', 'VA', 'NC', 'CI', 'MW', 'SS', 'MY'])]

print(df)

# Data Visualization
# =====================================================================
fig = go.Figure()

# Tamaño de los marcadores
marker_size = np.sqrt(df["NGDPD"] / df["NGDPD"].max()) * 100 + 3
line_width  = np.sqrt(df["NGDPD"] / df["NGDPD"].max()) * 4 + 0.5

# Add scatter plot
fig.add_trace(go.Scatter(
    x=df["PPP"],
    y=df["NGDPDPC"],
    mode='markers',
    text=df["Country"],
    marker=dict(
        size=marker_size,
        color="rgba(0,0,0,0)",
        line=dict(
            width=line_width,
            color='black'
        )
    ),
    hovertemplate="<b>Country:</b> %{text}<br>" +
                  "<b>GDP per Capita:</b> $%{y:.2f}<br>" + 
                  "<b>PPP:</b> $%{x:.2f}<extra></extra>",
    showlegend=False
))

# Add flag images to scatterplot
for i, row in df.iterrows():
    country_iso = row["ISO2"]
    
    # Calculate image size
    image_size = marker_size[i] * 0.21

    # Add the flag image
    fig.add_layout_image(
        dict(
            source=f"https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/{country_iso}.png",
            xref="x",
            yref="y",
            xanchor="center",
            yanchor="middle",
            x=row["PPP"],
            y=row["NGDPDPC"],
            sizex=image_size,
            sizey=image_size,
            sizing="contain",
            opacity=0.8,
            layer="above"
        )
    )
    
# Modeling a line trend
z = np.polyfit(df['PPP'], df['NGDPDPC'], 2, w=df['NGDPD'])
p = np.poly1d(z)
x_range = np.linspace(df['PPP'].min(), df['PPP'].max(), 100)
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

# Add red and green shapes
fig.add_shape(
    type="rect",
    xref="x", yref="paper",
    x0=0, x1=1,
    y0=0, y1=1,
    fillcolor="red",
    opacity=0.04,
    layer="below",
    line_width=0
)
fig.add_shape(
    type="rect",
    xref="x", yref="paper",
    x0=1, x1=1.2,
    y0=0, y1=1,
    fillcolor="green",
    opacity=0.04,
    layer="below",
    line_width=0
)

# Configuration plot
fig.update_layout(
    title="<b>Global Inequalities in GDP per Capita</b>",
    title_x=0.11,
    title_font=dict(size=16),
    annotations=[
        dict(
            text="Exploring Discrepancies between Market Exchanges Rates and Purchasing Power Parity",
            xref="paper",
            yref="paper",
            x=0,
            y=1.07,
            showarrow=False,
            font=dict(size=11)
        ),
        dict(
            text="<b>Data Source:</b> IMF World Economic Outlook Database, 2024",
            xref="paper",
            yref="paper",
            x=0,
            y=-0.13,
            showarrow=False,
            font=dict(size=10),
            align="left"
        ),
        dict(
            text=f"2024",
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
        title="<b>GAP Between PPP and Market Exchange Rate</b>",
        range=[0, 1.2],
        tickvals=[i * 1.2 / 6 for i in range(7)],
        showline=True,
        linewidth=1,
        linecolor="black",
        gridcolor="#ebebeb"
    ),
    yaxis=dict(
        title="<b>GDP per Capita (US$)</b>",
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
        title=dict(text='<b>   GDP Scale</b>'), 
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
fig.write_html("C:/Users/guill/Desktop/FIG_PPP_Inequalities_Flag.html")
fig.write_image("C:/Users/guill/Desktop/FIG_PPP_Inequalities_Flag.png")

# Show the plot!
fig.show()
