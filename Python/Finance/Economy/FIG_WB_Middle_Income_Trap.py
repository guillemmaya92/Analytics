# Libraries
# =====================================================================
import os
import requests
import wbgapi as wb
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Data Extraction (Countries)
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = df.rename(columns={'index': 'cod_country'})

# Data Extraction - WBD (1960-1980)
# ========================================================
# To use the built-in plotting method
indicator = ['NY.GDP.PCAP.CD', 'SP.POP.TOTL']
countries = df_countries['cod_country'].tolist()
data_range = ['1960', '2023']
data = wb.data.DataFrame(indicator, countries, data_range, numericTimeKeys=True, labels=False, columns='series').reset_index()
df_wb = data.rename(columns={
    'economy': 'cod_country',
    'time': 'year',
    'NY.GDP.PCAP.CD': 'gdpc',
    'SP.POP.TOTL': 'pop'
})

# Data Manipulation
# ========================================================
# Filter nulls and both years
df_wb = df_wb[~df_wb['gdpc'].isna()]
df_unique = df_wb.groupby('cod_country')['year'].nunique()
country_ok = df_unique[df_unique == 2].index
df_wb = df_wb[df_wb['cod_country'].isin(country_ok)]

# Add gdpc_usa
usa_gdpc = df_wb[df_wb['cod_country'] == 'USA'][['year', 'gdpc']].rename(columns={'gdpc': 'gdpc_usa'})
df_wb = df_wb.merge(usa_gdpc, on='year', how='left')
df_wb['gdpc_usa_rel'] = df_wb['gdpc'] / df_wb['gdpc_usa'] * 100
df_wb['ln_gdpc_usa_rel'] = np.log(df_wb['gdpc_usa_rel'])

# Select columns
df_wb = df_wb[['cod_country', 'year', 'pop', 'gdpc', 'gdpc_usa_rel', 'ln_gdpc_usa_rel']]

# Rename year row values
df_wb['year'] = df_wb['year'].replace({1960: 'start', 2023: 'end'})

# Unpivot to columns
df_wb = df_wb.pivot_table(index='cod_country', columns='year', values=['pop', 'gdpc', 'gdpc_usa_rel', 'ln_gdpc_usa_rel'])
df_wb.columns = [f'{var}_{year}' for var, year in df_wb.columns]
df_wb = df_wb.reset_index()
df_wb = df_wb.rename(columns={'ln_gdpc_usa_rel_start': 'start', 'ln_gdpc_usa_rel_end': 'end'})

# Merge queries
df = df_wb.merge(df_countries, how='left', left_on='cod_country', right_on='cod_country')
df = df[['Region', 'Country_Abr', 'cod_country', 'pop_end', 'gdpc_start', 'gdpc_end', 'gdpc_usa_rel_start', 'gdpc_usa_rel_end', 'start', 'end']]
df = df.rename(columns={'Region': 'region', 'Country_Abr': 'country'})
df = df[df['region'].notna()]

# Population Log
df['pop_end_log'] = np.log(df_wb['pop_end'])

# Palette dot
color_map_dot = {
    'Oceania': "#AFEBFF",
    'Europe':  "#C0FFD8",
    'Africa':  "#FFC1A9",
    'Americas': "#FFBEBE",
    'Asia':    '#FFFFE0'
}

# Palette dot line
color_map_dot_line = {
    'Oceania': "#001CB9",
    'Europe': "#00AA3E",
    'Africa': "#D16500",
    'Americas': "#BB0000",
    'Asia': "#D6D600"
}

# Add columns with colors
df['color_line'] = df['region'].map(color_map_dot_line)
df['color_dot'] = df['region'].map(color_map_dot)

print(df)

# Data Visualization
# ========================================================
# Figure
fig = go.Figure()

labels = df['cod_country'].apply(lambda x: x.upper() if x.lower() in ['usa', 'chn'] else "")

# Obtener los valores únicos de color y su región asociada (asumimos que la relación es uno a uno)
for color in df['color_dot'].unique():
    df_color = df[df['color_dot'] == color]
    region_name = df_color['region'].iloc[0]
    
    fig.add_trace(go.Scatter(
        x=df_color['start'],
        y=df_color['end'],
        mode='markers+text',
        name=region_name,
        marker=dict(
            size=df_color['pop_end'],
            color=color,
            line=dict(color=df_color['color_line'].iloc[0], width=2),
            sizemode='area',
            sizeref=2 * max(df['pop_end']) / (60. ** 2),
            sizemin=2
        ),
        text=labels[df_color.index],  # Asegúrate que labels está indexado correctamente
        textposition='top center',
        showlegend=True,
        customdata=df_color[['country', 'gdpc_start', 'gdpc_usa_rel_start', 'gdpc_end', 'gdpc_usa_rel_end']],
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "GDP Capita (1960): %{customdata[1]:,.0f} (%{customdata[2]:,.2f}%)<br>"
            "GDP Capita (2023): %{customdata[3]:,.0f} (%{customdata[4]:,.2f}%)<extra></extra>"
        )
    ))

# Axis Labels
fig.update_layout(
    xaxis=dict(
        tickmode='array',
        tickvals=[0.9, 1.8, 2.7, 3.6, 4.6052],
        ticktext=['2%', '6%', '15%', '36%', '100%']
    ),
    yaxis=dict(
        tickmode='array',
        tickvals=[0.9, 1.8, 2.7, 3.6, 4.6052],
        ticktext=['2%', '6%', '15%', '36%', '100%']
    )
)

# Font Type
fig.update_layout(
    font=dict(
        family="sans-serif",
        size=12,
        color="black"
    )
)

# Configuration
fig.update_layout(
    xaxis=dict(range=[0, 5.4], title='Start', showgrid=False),
    yaxis=dict(range=[0, 5.4], title='End', showgrid=False),
    title=dict(
        text=(
            "<b style='font-size:22px;'>The Middle Income Trap</b>"
            "<span style='font-size:2px;'> </span><br>"
            "<span style='font-size:14px; color:gray;'>Income per person relative to United States, 1960 vs 2023</span>"
        ),
        font=dict(size=24, color="black"),
        x=0.1,
        xanchor='left',
        yanchor='top'
    ),    
    width=700,
    height=600,
    plot_bgcolor='white',
    paper_bgcolor='white'
)

# Label Axis
fig.update_layout(
    xaxis_title=dict(
        text="<b>Income per person relative to US, 1960</b>",
        font=dict(size=12, color="black", family="sans-serif")
    ),
    yaxis_title=dict(
        text="<b>Income per person relative to US, 2023</b>",
        font=dict(size=12, color="black", family="sans-serif")
    )
)

# Annotations
fig.update_layout(
    annotations=[
        dict(
            text="<b>Data Source:</b> World Bank, World Development Indicators (2024)",
            xref="paper",
            yref="paper",
            x=0,
            y=-0.15,
            showarrow=False,
            font=dict(size=10, color="black"),
            align="left"
        ),
        dict(
            text=f"<b>Size:</b> The size of each bubble represents the population size, scaled proportionally to ensure visual comparability.",
            xref="paper",
            yref="paper",
            x=0,
            y=-0.18,
            showarrow=False,
            font=dict(size=10, color="black"),
            align="left"
        )
    ],
    shapes=[
        dict(
            type="rect",
            xref="paper", yref="paper",
            x0=-0.06, y0=1.03,
            x1=-0.04, y1=1.17, 
            fillcolor="darkblue",
            line=dict(width=0),
            layer="above"
        )
    ]
)

# Low Text
fig.add_annotation(
    x=0.2,
    y=1.7,
    text="<b>Low</b>",
    showarrow=False,
    textangle=0,
    font=dict(size=11, color="red"),
    xref="x",
    yref="y"
)

# Middle Text
fig.add_annotation(
    x=2,
    y=3.5,
    text="<b>Middle</b>",
    showarrow=False,
    textangle=0,
    font=dict(size=11, color="orange"),
    xref="x",
    yref="y"
)

# High Text
fig.add_annotation(
    x=3.8,
    y=5.3,
    text="<b>High</b>",
    showarrow=False,
    textangle=0,
    font=dict(size=11, color="green"),
    xref="x",
    yref="y"
)

# Box Middle-Income Trap
fig.add_shape(
    type="rect",
    x0=0, y0=0,
    x1=1.8, y1=1.8,
    line=dict(color="red", width=1),
    fillcolor="#E6ADAD",
    opacity=0.3,
    layer="below"
)

# Box Middle-Income Trap
fig.add_shape(
    type="rect",
    x0=1.8, y0=1.8,
    x1=3.6, y1=3.6,
    line=dict(color="yellow", width=1),
    fillcolor="#E6E2AD",
    opacity=0.3,
    layer="below"
)

# Box High-Income Trap
fig.add_shape(
    type="rect",
    x0=3.6, y0=3.6,
    x1=5.4, y1=5.4,
    line=dict(color="green", width=1),
    fillcolor="#B2E6AD",
    opacity=0.3,
    layer="below"
)

# Grid Vertical Lines
fig.add_shape(type="line", x0=1.8, y0=0, x1=1.8, y1=5.4,
              line=dict(color="gray", width=0.25, dash="solid"))
fig.add_shape(type="line", x0=3.6, y0=0, x1=3.6, y1=5.4,
              line=dict(color="gray", width=0.25, dash="solid"))

# Grid Horizontal lines
fig.add_shape(type="line", x0=0, y0=1.8, x1=5.4, y1=1.8,
              line=dict(color="gray", width=0.25, dash="solid"))
fig.add_shape(type="line", x0=0, y0=3.6, x1=5.4, y1=3.6,
              line=dict(color="gray", width=0.25, dash="solid"))

# Diagonal = 1
fig.add_shape(type="line", x0=0, y0=0, x1=5.4, y1=5.4,
              line=dict(color="red", width=1, dash="solid")
)

# USA Lines
fig.add_shape(
    type="line",
    x0=4.6,
    x1=4.6,
    y0=0,
    y1=4.6,
    line=dict(color="red", width=0.5, dash="dot"),
    xref="x",
    yref="y"
)
fig.add_shape(
    type="line",
    x0=0,
    x1=4.6,
    y0=4.6,
    y1=4.6,
    line=dict(color="red", width=0.5, dash="dot"),
    xref="x",
    yref="y"
)

# Save it...
download_folder = os.path.join(os.path.expanduser("~"), "Downloads")
filename = os.path.join(download_folder, f"FIG_WB_Middle_Income_Trap")
fig.write_html(filename + ".html")