# Libraries
# ============================================
import pandas as pd
import requests
from io import BytesIO
import wbgapi as wb
import matplotlib.pyplot as plt
import seaborn as sns

# Extraction Data MACROHISTORY
# ============================================
# URL file
url = "https://www.macrohistory.net/app/download/9834512469/JSTdatasetR6.dta?t=1720600177"

# Headers to simulate agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.100 Safari/537.36"
}
# Downdload file
response = requests.get(url, headers=headers)

# File to dataframe
dfm = pd.read_stata(BytesIO(response.content))

# Extraction Data PENN WORLD DATA 10.0
# ============================================
# URL file
url = "https://dataverse.nl/api/access/datafile/354098"

# Headers to simulate agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.100 Safari/537.36"
}
# Downdload file
response = requests.get(url, headers=headers)

# File to dataframe
dfp = pd.read_stata(BytesIO(response.content))

# Extraction Data COUNTRIES
# =====================================================================
# Extract JSON and bring data to a dataframe
url = 'https://raw.githubusercontent.com/guillemmaya92/world_map/main/Dim_Country.json'
response = requests.get(url)
data = response.json()
dfc = pd.DataFrame(data)
dfc = pd.DataFrame.from_dict(data, orient='index').reset_index()
df_countries = dfc.rename(columns={'index': 'ISO3'})

# Extraction Data WORLDBANK
# ========================================================
# To use the built-in plotting method
indicator = ['NY.GDP.MKTP.CD', 'NE.EXP.GNFS.CD', 'NE.IMP.GNFS.CD']
countries = df_countries['ISO3'].tolist()
data_range = range(1970, 2024)
data = wb.data.DataFrame(indicator, 'WLD', data_range, numericTimeKeys=True, labels=False, columns='series').reset_index()
dfw = data.rename(columns={
    'time': 'year',
    'economy': 'iso',
    'NY.GDP.MKTP.CD': 'gdp',
    'NE.EXP.GNFS.CD': 'exports',
    'NE.IMP.GNFS.CD': 'imports'
})

# Manipulation Data
# ============================================
# First dfm
dfm = dfm[dfm['year'] < 1950]
dfm = dfm[['year', 'iso', 'gdp', 'imports', 'exports', 'xrusd']]
dfm['imports'] = dfm['imports'] / dfm['xrusd']
dfm['exports'] = dfm['exports'] / dfm['xrusd']
dfm['gdp'] = dfm['gdp'] / dfm['xrusd']
dfm['comerce'] = dfm['imports'] + dfm['exports']
dfm = dfm[['year', 'gdp', 'comerce']].groupby('year', as_index=False).sum()
dfm['comerce_per'] = dfm['comerce'] / dfm['gdp']

# Second dfm
dfp = dfp[(dfp['year'] >= 1950) & (dfp['year'] < 1970)]
dfp = dfp[['countrycode', 'year', 'rgdpe', 'csh_x', 'csh_m']]
dfp = dfp.dropna()
dfp['comerce'] = dfp['rgdpe'] * dfp['csh_x'] + dfp['rgdpe'] * dfp['csh_m'].abs()
dfp = dfp.groupby('year')[['rgdpe', 'comerce']].sum().reset_index()
dfp['comerce_per'] = dfp['comerce'] / dfp['rgdpe']
dfp = dfp.rename(columns={'rgdpe': 'gdp'})

# third dfm
dfw['comerce'] = dfw['imports'] + dfw['exports']
dfw = dfw[['year', 'gdp', 'comerce']].groupby('year', as_index=False).sum()
dfw['comerce_per'] = dfw['comerce'] / dfw['gdp']

# concat dataframes
df = pd.concat([dfm, dfp, dfw], ignore_index=True)

df['comerce_per'] = df['comerce_per'].rolling(window=2, center=True).mean()

print(df)

# Visualization Data
# ============================================
# Definir colores y otros parámetros
sns.set(style="white", palette="muted")

# Dividir los datos en varios rangos
df_1870_1914 = df[(df['year'] >= 1870) & (df['year'] <= 1915)]
df_1915_1945 = df[(df['year'] >= 1915) & (df['year'] <= 1945)]
df_1945_2008 = df[(df['year'] >= 1945) & (df['year'] <= 2008)]
df_2008_2023 = df[(df['year'] >= 2008) & (df['year'] <= 2023)]

# Crear el gráfico con stackplot
plt.figure(figsize=(10, 6))

# Stackplot para los años 1870-1914 (azul)
plt.stackplot(df_1870_1914['year'], df_1870_1914['comerce_per'], color='#084d95', alpha=0.9)
plt.stackplot(df_1915_1945['year'], df_1915_1945['comerce_per'], color='#d92724', alpha=0.9)
plt.stackplot(df_1945_2008['year'], df_1945_2008['comerce_per'], color='#084d95', alpha=0.9)
plt.stackplot(df_2008_2023['year'], df_2008_2023['comerce_per'], color='#d92724', alpha=0.9)

# Añadir líneas verticales en los años 1915, 1945 y 2008
plt.axvline(x=1915, color='white', linestyle='--', linewidth=1)
plt.axvline(x=1945, color='white', linestyle='--', linewidth=1)
plt.axvline(x=2008, color='white', linestyle='--', linewidth=1)

plt.xlim(1871, 2023)

# Agregar etiquetas y título
plt.title("Gráfico de Área Apilada - Comercio per GDP")
plt.xlabel("Año")
plt.ylabel("Comercio per GDP")

# Agregar leyenda
plt.legend(loc='upper left')

# Mostrar el gráfico
plt.show()