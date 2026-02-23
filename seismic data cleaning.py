import requests
import pandas as pd
import os

BASE_URL = "https://earthquake.usgs.gov/fdsnws/event/1/query"

records = []

# Create data folder if it doesn't exist
os.makedirs("data", exist_ok=True)

# Collect data for last 5 years (month-wise)
for year in range(2020, 2025):
    for month in range(1, 13):
        start = f"{year}-{month:02d}-01"
        end = f"{year}-{month:02d}-28"

        params = {
            "format": "geojson",
            "starttime": start,
            "endtime": end,
            "minmagnitude": 2.5
        }

        response = requests.get(BASE_URL, params=params)

        if response.status_code == 200:
            data = response.json()

            for feature in data.get("features", []):
                prop = feature.get("properties", {})
                geo = feature.get("geometry", {})
                coords = geo.get("coordinates", [None, None, None])

                records.append({
                    "id": feature.get("id"),
                    "time": prop.get("time"),
                    "updated": prop.get("updated"),
                    "mag": prop.get("mag"),
                    "magType": prop.get("magType"),
                    "place": prop.get("place"),
                    "status": prop.get("status"),
                    "tsunami": prop.get("tsunami"),
                    "sig": prop.get("sig"),
                    "net": prop.get("net"),
                    "nst": prop.get("nst"),
                    "dmin": prop.get("dmin"),
                    "rms": prop.get("rms"),
                    "gap": prop.get("gap"),
                    "magError": prop.get("magError"),
                    "depthError": prop.get("depthError"),
                    "magNst": prop.get("magNst"),
                    "locationSource": prop.get("locationSource"),
                    "magSource": prop.get("magSource"),
                    "types": prop.get("types"),
                    "ids": prop.get("ids"),
                    "sources": prop.get("sources"),
                    "type": prop.get("type"),
                    "longitude": coords[0],
                    "latitude": coords[1],
                    "depth_km": coords[2]
                })

df = pd.DataFrame(records)
df.to_csv("data/earthquakes.csv", index=False)

print("✅ Data fetched and saved successfully")
print("Rows:", df.shape[0], "Columns:", df.shape[1])


import pandas as pd
import re

df = pd.read_csv("data/earthquakes.csv")

# Convert timestamps
df["time"] = pd.to_datetime(df["time"], unit="ms", errors="coerce")
df["updated"] = pd.to_datetime(df["updated"], unit="ms", errors="coerce")

# Extract country
def extract_country(place):
    if pd.isna(place):
        return "Unknown"
    match = re.search(r",\s*(.*)", place)
    return match.group(1) if match else "Unknown"

df["country"] = df["place"].apply(extract_country)

# Fill numeric nulls
numeric_cols = [
    "mag","depth_km","nst","dmin","rms","gap",
    "magError","depthError","magNst","sig"
]
df[numeric_cols] = df[numeric_cols].fillna(0)

# Time features
df["year"] = df["time"].dt.year
df["month"] = df["time"].dt.month
df["day"] = df["time"].dt.day
df["day_of_week"] = df["time"].dt.day_name()
df["hour"] = df["time"].dt.hour

df.to_csv("data/earthquakes_cleaned.csv", index=False)
print("✅ STEP 2 COMPLETE")

