# Libraries
# ================================================
import pandas as pd
import comtradeapicall
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import matplotlib.image as mpimg
import os
from io import BytesIO
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import pathlib

# Countries
# ================================================
# URL to get the list of countries
url = "https://comtradeapi.un.org/files/v1/app/reference/Reporters.json"
response = requests.get(url)
data = response.json()

# Manipulate the DataFrame
df = pd.DataFrame(data['results'])
df = df[['text', 'reporterCode', 'reporterCodeIsoAlpha3']]
df = df.rename(columns={'text': 'name', 'reporterCode': 'code','reporterCodeIsoAlpha3': 'iso3'})

# Filter and convert to list
df = df[df['iso3'].isin(['USA'])]
reporter_codes = df['code'].tolist()

print(reporter_codes)

# Data Extraction
# ================================================
# Lista de typeCode a iterar
type_codes = [
    {'typeCode': 'C', 'clCode': 'HS', 'cmdCode': 'TOTAL'},
    {'typeCode': 'S', 'clCode': 'EB', 'cmdCode': '200'}
]

flow_codes = ['X', 'M']

# Lista para guardar los DataFrames
df_list = []

# Iterar por cada typeCode
for fcode in flow_codes:
    for tcode in type_codes:
        for rcode in reporter_codes:
            df = comtradeapicall.previewFinalData(
                typeCode=tcode['typeCode'],       # Goods (C) or Services (S)
                freqCode='A',                     # Annual (A) or Monthly (M)
                clCode=tcode['clCode'],           # Indicates the product classification used and which version (HS, SITC)
                period='2022',                    # Period
                reporterCode=rcode,               # Country origin (reporter)
                cmdCode=tcode['cmdCode'],          # Product code in conjunction with classification code (7108 Gold)
                flowCode=fcode,                   # Exportaciones (X) imports (M)
                partnerCode=None,                 # Country destination (partner)
                partner2Code=None,                # The primary partner country or geographic area for the respective trade flow
                customsCode=None,                 # A secondary partner country or geographic area for the respective trade flow
                motCode=None,                     # The mode of transport used when goods enter or leave the economic territory of a country
                maxRecords=500,                   # Limit number of returned records
                format_output='JSON',             # The output format. CSV or JSON
                aggregateBy=None,                 # Option for aggregating the query
                breakdownMode='classic',          # Option to select the classic (trade by partner/product) or plus (extended breakdown) mode
                countOnly=None,                   # Return the actual number of records if set to True
                includeDesc=True                  # Option to include the description or not
            )
            df_list.append(df)

df = pd.concat(df_list, ignore_index=True)

# Obtener ruta a la carpeta Descargas del usuario actual
download_path = str(pathlib.Path.home() / "Downloads")

# Nombre del archivo
file_name = "comtrade_export_USA_2023.csv"

# Guardar como CSV
csv_path = os.path.join(download_path, file_name)
df.to_csv(csv_path, index=False)


print(df)