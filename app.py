import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

st.set_page_config(page_title="Agri-Weather Hub", layout="centered")

# 1. Precise Data for your 18 Hubs
CITIES = [
    {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
    {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Mathura", "lat": 27.49, "lon": 77.67},
    {"name": "Rudrapur", "lat": 28.98, "lon": 79.41}, {"name": "Shahjahanpur", "lat": 27.88, "lon": 79.91},
    {"name": "Bikaner", "lat": 28.02, "lon": 73.31}, {"name": "Kota", "lat": 25.21, "lon": 75.86},
    {"name": "Patna", "lat": 25.59, "lon": 85.14}, {"name": "Begusarai", "lat": 25.42, "lon": 86.13},
    {"name": "Bhopal", "lat": 23.26, "lon": 77.41}, {"name": "Indore", "lat": 22.72, "lon": 75.86},
    {"name": "Rajkot", "lat": 22.30, "lon": 70.80}, {"name": "Nadiad", "lat": 22.69, "lon": 72.86},
    {"name": "Nagpur", "lat": 21.15, "lon": 79.09}, {"name": "Hyderabad", "lat": 17.39, "lon": 78.49},
    {"name": "Bangalore", "lat": 12.97, "lon": 77.59}, {"name": "Chennai", "lat": 13.08, "lon": 80.27}
]

# 2. Fetch Live Weather
@st.cache_data(ttl=3600)
def get_weather():
    results = []
    for city in CITIES:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
            d = requests.get(url).json()
            results.append({
                "City": city['name'], "Lat": city['lat'], "Lon": city['lon'],
                "Temp": d['current_weather']['temperature'],
                "Max": d['daily']['temperature_2m_max'][0],
                "Min": d['daily']['temperature_2m_min'][0]
            })
        except: continue
    return pd.DataFrame(results)

st.title("🌾 Wheat Intelligence Command Center")
df = get_weather()

# 3. Create a Professional Geo Map (Ensures Perfect Alignment)
fig = go.Figure()

# Add City Dots & Text
fig.add_trace(go.Scattergeo(
    lon = df['Lon'], lat = df['Lat'],
    text = df['City'],
    mode = 'markers+text',
    textposition = "top center",
    marker = dict(size = 10, color = df['Temp'], colorscale = 'RdYlGn_r', 
                  line=dict(width=1, color='white'), opacity=0.8),
    hovertemplate = "<b>%{text}</b><br>Now: %{customdata[0]}°C<br>Max: %{customdata[1]}°C<br>Min: %{customdata[2]}°C<extra></extra>",
    customdata = df[['Temp', 'Max', 'Min']]
))

# 4. Map Layout (Locked to India / Portrait feel)
fig.update_geos(
    visible=False, resolution=50,
    showcountries=True, countrycolor="Black",
    showsubunits=True, subunitcolor="Gray", # This shows State Outlines
    projection_type="mercator",
    lataxis_range=[6, 38], lonaxis_range=[68, 98] # Focus on India
)

fig.update_layout(height=800, margin={"r":0,"t":30,"l":0,"b":0})

st.plotly_chart(fig, use_container_width=True)

# 5. Data Summary
st.dataframe(df[['City', 'Temp', 'Max', 'Min']], use_container_width=True, hide_index=True)
