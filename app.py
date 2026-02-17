import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from PIL import Image
import os

# 1. Setup Page - "centered" works best for mobile portrait stacking
st.set_page_config(page_title="Wheat Intelligence Hub", layout="centered")

# 2. Define your 18 Wheat Hubs
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

# 3. Fetch Live Data from Open-Meteo (Free)
@st.cache_data(ttl=3600)  # Caches data for 1 hour to stay fast
def get_live_weather(city_list):
    results = []
    for city in city_list:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={city['lat']}&longitude={city['lon']}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
            data = requests.get(url).json()
            results.append({
                "City": city['name'],
                "Lat": city['lat'],
                "Lon": city['lon'],
                "Temp": data['current_weather']['temperature'],
                "Max": data['daily']['temperature_2m_max'][0],
                "Min": data['daily']['temperature_2m_min'][0]
            })
        except:
            continue
    return pd.DataFrame(results)

# 4. Load the Background Map
try:
    base_path = os.path.dirname(__file__)
    img = Image.open(os.path.join(base_path, "india_map.png"))
except FileNotFoundError:
    st.error("Error: 'india_map.png' not found. Please upload it to your GitHub repo.")
    st.stop()

# 5. Build Visualization
st.title("🌾 Wheat Intelligence Command Center")
df = get_live_weather(CITIES)

# We use Latitude/Longitude as X/Y directly for the scatter overlay
fig = px.scatter(df, x="Lon", y="Lat", text="City", 
                 hover_data={"Temp": True, "Max": True, "Min": True, "Lat": False, "Lon": False},
                 color="Temp", color_continuous_scale="RdYlGn_r") # Red for hot, Green for cool

# Overlay the image
fig.add_layout_image(
    dict(source=img, xref="x", yref="y", 
         x=68, y=38, # Bottom-left anchor (approx India coords)
         sizex=30, sizey=32, # Width/Height in degrees
         sizing="stretch", opacity=1, layer="below")
)

# Hide axes for a clean "Command Center" look
fig.update_xaxes(showgrid=False, visible=False, range=[68, 98])
fig.update_yaxes(showgrid=False, visible=False, range=[6, 38])
fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=700)

st.plotly_chart(fig, use_container_width=True)

# 6. Summary Table below the Map
st.subheader("📊 Region Summary")
st.dataframe(df[['City', 'Temp', 'Max', 'Min']], use_container_width=True, hide_index=True)

if st.button('🔄 Refresh Data'):
    st.cache_data.clear()
    st.rerun()
