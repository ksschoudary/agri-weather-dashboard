import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from PIL import Image
import os
from io import BytesIO

# 1. Page Configuration
st.set_page_config(page_title="Agri-Weather Command Center", layout="centered")

# 2. 18 Cities Data (Verified coordinates)
CITIES = [
    {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
    {"name": "Delhi", "lat": 28.61, "lon": 77.20}, {"name": "Mathura", "lat": 27.49, "lon": 77.67},
    {"name": "Rudrapur", "lat": 28.98, "lon": 79.41}, {"name": "Shahjahanpur", "lat": 27.88, "lon": 79.91},
    {"name": "Bikaner", "lat": 28.02, "lon": 73.31}, {"name": "Kota", "lat": 25.21, "lon": 75.86},
    {"name": "Patna", "lat": 25.59, "lon": 85.13}, {"name": "Begusarai", "lat": 25.41, "lon": 86.13},
    {"name": "Lalitpur", "lat": 24.68, "lon": 78.41}, {"name": "Bhopal", "lat": 23.25, "lon": 77.41},
    {"name": "Indore", "lat": 22.71, "lon": 75.85}, {"name": "Rajkot", "lat": 22.30, "lon": 70.80},
    {"name": "Nadiad", "lat": 22.69, "lon": 72.86}, {"name": "Nagpur", "lat": 21.14, "lon": 79.08},
    {"name": "Hyderabad", "lat": 17.38, "lon": 78.48}, {"name": "Bangalore", "lat": 12.97, "lon": 77.59}
]

# 3. Sidebar Calibration (Use these to align the dots to your image)
st.sidebar.header("🗺️ Map Alignment")
x_nudge = st.sidebar.slider("Left/Right Nudge", 60.0, 75.0, 68.0, 0.1)
y_nudge = st.sidebar.slider("Up/Down Nudge", 30.0, 45.0, 38.0, 0.1)
map_size = st.sidebar.slider("Map Scale", 25.0, 40.0, 31.0, 0.1)

# 4. Fetch Weather Data (Open-Meteo Free)
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

# 5. Load Image
try:
    img = Image.open("india_map.png")
except:
    st.error("Missing 'india_map.png' in GitHub root.")
    st.stop()

# 6. Build Visualization
st.title("🌾 Wheat Weather Hub")
df = get_weather()

fig = px.scatter(df, x="Lon", y="Lat", text="City",
                 color="Temp", color_continuous_scale="RdYlGn_r",
                 hover_data={"Temp":True, "Max":True, "Min":True, "Lat":False, "Lon":False})

# Correct visibility: Mode 'markers+text' ensures names stay on screen
fig.update_traces(
    mode='markers+text',
    textposition='top center',
    marker=dict(size=14, line=dict(width=2, color='white'), opacity=0.9),
    textfont=dict(family="Arial Black", size=10, color="black"),
    hovertemplate="<b>%{text}</b><br>Now: %{customdata[0]}°C<br>Max: %{customdata[1]}°C<br>Min: %{customdata[2]}°C<extra></extra>",
    customdata=df[['Temp', 'Max', 'Min']]
)

# Overlay Image using Sidebar Nudge Values
fig.add_layout_image(
    dict(source=img, xref="x", yref="y", x=x_nudge, y=y_nudge,
         sizex=map_size, sizey=map_size, sizing="stretch", opacity=1, layer="below")
)

# Fixed viewing window for India
fig.update_xaxes(showgrid=False, visible=False, range=[66, 99])
fig.update_yaxes(showgrid=False, visible=False, range=[6, 40])
fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=750, showlegend=False)

st.plotly_chart(fig, use_container_width=True)

# 7. Summary Table (Mobile Friendly)
st.dataframe(df[['City', 'Temp', 'Max', 'Min']], use_container_width=True, hide_index=True)

if st.button('🔄 Refresh'):
    st.cache_data.clear()
    st.rerun()
