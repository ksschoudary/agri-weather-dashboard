import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="Agri-Weather Command Center", layout="centered")

# 1. Precise City Data
cities = [
    {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
    {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Mathura", "lat": 27.49, "lon": 77.67},
    {"name": "Rudrapur", "lat": 28.98, "lon": 79.41}, {"name": "Shahjahanpur", "lat": 27.88, "lon": 79.91},
    {"name": "Bikaner", "lat": 28.03, "lon": 73.31}, {"name": "Kota", "lat": 25.21, "lon": 75.86},
    {"name": "Patna", "lat": 25.59, "lon": 85.14}, {"name": "Begusarai", "lat": 25.42, "lon": 86.13},
    {"name": "Bhopal", "lat": 23.26, "lon": 77.41}, {"name": "Indore", "lat": 22.72, "lon": 75.86},
    {"name": "Rajkot", "lat": 22.30, "lon": 70.80}, {"name": "Nadiad", "lat": 22.69, "lon": 72.86},
    {"name": "Nagpur", "lat": 21.15, "lon": 79.09}, {"name": "Hyderabad", "lat": 17.39, "lon": 78.49},
    {"name": "Bangalore", "lat": 12.97, "lon": 77.59}, {"name": "Chennai", "lat": 13.08, "lon": 80.27}
]
df = pd.DataFrame(cities)

st.title("🌾 India Agri-Intelligence Map")

# 2. Build the Visual
fig = go.Figure(go.Scattergeo(
    lat = df['lat'], lon = df['lon'], text = df['name'],
    mode = 'markers+text',
    textposition = "top center",
    marker = dict(size=12, color='red', line=dict(width=2, color='white')),
    textfont = dict(family="Arial Black", size=10, color="black"),
    hovertemplate = "<b>%{text}</b><br>Lat: %{lat}<br>Lon: %{lon}<extra></extra>"
))

# 3. THE "INDIA ONLY" CROP
fig.update_geos(
    visible=False, # Hides the entire world map
    showcountries=True, countrycolor="Black",
    showsubunits=True, subunitcolor="Gray", # Shows state lines
    showland=True, landcolor="white", # Keeps land visible
    lataxis_range=[6, 38], # Crops view to India's latitude
    lonaxis_range=[68, 98], # Crops view to India's longitude
    projection_type="mercator"
)

fig.update_layout(height=800, margin={"r":0,"t":0,"l":0,"b":0})

st.plotly_chart(fig, use_container_width=True)
