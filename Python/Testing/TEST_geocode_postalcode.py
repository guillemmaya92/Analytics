# Libraries
# ===================================================
import pandas as pd
from geopy.geocoders import Nominatim
import time

# Extract Data
# ===================================================
# Read the csv and create dataframe
file_path = r'C:\Users\guill\Downloads\SCRAPERIUM\Catalunya.csv'
df = pd.read_csv(file_path, sep=';')

# Create a geolocate instance
geolocator = Nominatim(user_agent="http")

# Function to get postal code
def get_postal_code(lat, lon):
    lat = float(lat.replace(',', '.'))
    lon = float(lon.replace(',', '.'))

    location = geolocator.reverse((lat, lon), language='es')
    if location and 'address' in location.raw:
        return location.raw['address'].get('postcode', None)
    return None

# Add column with the postal code
df['postal_code'] = df.apply(lambda row: get_postal_code(row['latitude'], row['longitude']), axis=1)

# Save as csv! 
df.to_csv(r'C:\Users\guill\Downloads\SCRAPERIUM\Catalunya_CP.csv', index=False, encoding='utf-8')

