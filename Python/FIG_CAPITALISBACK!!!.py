# Libraries
# ===================================================
import requests
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# Extract Data (Countries)
# ===================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
df = pd.DataFrame(data)
df = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = df.rename(columns={'index': 'ISO3'})

# Extract Data (WID)
# ===================================================
# URL del archivo Parquet en GitHub
url = "https://raw.githubusercontent.com/guillemmaya92/Analytics/master/Data/WID_Values.parquet"
df = pd.read_parquet(url, engine="pyarrow")

# Transform Data
# ===================================================
df['gdpinc'] = (df['gdptotal'] / df.groupby('country')['gdptotal'].shift(1) -1) * 100
df['gdptotal'] = df['gdptotal'] / df['xusd']
df = df[df['year'] == 2023]
df = df[df['wiratio'].notna() & df['gdpinc'].notna()]
df = pd.merge(df, df_countries, left_on='country', right_on='ISO2', how='inner')
df = df[['country', 'Country_Abr', 'gdptotal', 'wiratio', 'gdpinc']]
df = df[(df['gdpinc'] >= 0) & (df['gdpinc'] <= 10)]
df = df.sort_values(by='gdptotal', ascending=True)

df = df.rename(
        columns={
            'Country_Abr': 'country_name',
            'gdptotal': 'total_income', 
            'wiratio': 'betaCY', 
            'gdpinc': 'incomeCY'}
    )
print(df)

# Data Visualization
# ===================================================
# Ordena el DataFrame por total_income de menor a mayor
df = df.sort_values(by='total_income', ascending=True)

# Crea la figura
fig = go.Figure()

# Marker size y line width calculados
marker_size = np.sqrt(df["total_income"] / df["total_income"].max()) * 100 + 3
line_width  = np.sqrt(df["total_income"] / df["total_income"].max()) * 4 + 0.5

# Primero agregamos los puntos del scatter
fig.add_trace(go.Scatter(
    x=df["betaCY"],
    y=df["incomeCY"],
    mode='markers',
    text=df["country_name"],
    marker=dict(
        size=marker_size,
        color="rgba(0,0,0,0)",
        line=dict(
            width=line_width,
            color='black'
        )
    ),
    hovertemplate="<b>Country:</b> %{text}<br>" +
                  "<b>Income Avg (€):</b> %{y:.0f}k | <b>Var. 1995:</b> %{customdata[2]:.2f}%<br>" + 
                  "<b>Wealth Avg (€):</b> %{customdata[1]:.0f}k | <b>Var. 1995:</b> %{customdata[3]:.2f}%<br>" +
                  "<b>Ratio:</b> %{customdata[4]:.2f} | <b>Var. 1995:</b> %{customdata[5]:.2f}pp<extra></extra>",
    showlegend=False
))

# Ahora agregamos las imágenes de las banderas
for i, row in df.iterrows():
    country_iso = row["country"]
    
    # Calcular tamaño de la imagen
    image_size = marker_size[i] * 0.021

    # Añadir la imagen de la bandera, asegurándose de que el orden es correcto
    fig.add_layout_image(
        dict(
            source=f"https://raw.githubusercontent.com/matahombres/CSS-Country-Flags-Rounded/master/flags/{country_iso}.png",
            xref="x",
            yref="y",
            xanchor="center",
            yanchor="middle",
            x=row["betaCY"],
            y=row["incomeCY"],
            sizex=image_size,
            sizey=image_size,
            sizing="contain",
            opacity=0.8,
            layer="above"
        )
    )

# Add red and green shapes
fig.add_shape(
    type="rect",
    xref="x", yref="paper",
    x0=0, x1=6,
    y0=0, y1=1,
    fillcolor="green",
    opacity=0.04,
    layer="below",
    line_width=0
)
fig.add_shape(
    type="rect",
    xref="x", yref="paper",
    x0=6, x1=12,
    y0=0, y1=1,
    fillcolor="red",
    opacity=0.04,
    layer="below",
    line_width=0
)

# Configuration plot
fig.update_layout(
    title="<b>Capital is Back</b>",
    title_x=0.11,
    title_font=dict(size=16),
    annotations=[
        dict(
            text="Income and Wealth Ratio by Country",
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
            text="<b>Currency:</b> Official exchange rate 2023 of the local currency to EUR.",
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
        title="<b>Income-Wealth Ratio</b>",
        range=[0, 12],
        tickvals=[i *  4 / 2 for i in range(7)],
        ticktext=[f"{int(i * 4 / 2)}" for i in range(7)],
        showline=True,
        linewidth=1,
        linecolor="black",
        gridcolor="#ebebeb"
    ),
    yaxis=dict(
        title="<b>Income Average (€)</b>",
        range=[0, 12],
        tickvals=[i * 12 / 6 for i in range(7)],
        ticktext=[f"{int(i * 12 / 6)}k" for i in range(7)],
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
fig.write_html("C:/Users/guill/Desktop/FIG_WID_CapitalisBack_Flag.html")
fig.write_image("C:/Users/guill/Desktop/FIG_WID_CapitalisBack_Flag.png")

# Show the plot!
fig.show()