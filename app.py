import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Agri-Weather India", layout="portrait")

st.title("🌾 Agri-Weather Command Center")

# Your 18 Cities Data (Simplified for this example)
cities = [
    {"name": "Bikaner", "lat": 28.02, "lon": 73.31, "temp": 32},
    {"name": "Nagpur", "lat": 21.14, "lon": 79.08, "temp": 34},
    # ... add the rest here
]

# 1. The Map
m = folium.Map(location=[22.0, 78.0], zoom_start=5, tiles="CartoDB positron")

# 2. Add the Dots
for city in cities:
    folium.CircleMarker(
        location=[city["lat"], city["lon"]],
        radius=8,
        popup=f"{city['name']}: {city['temp']}°C",
        color="red" if city["temp"] > 33 else "green",
        fill=True
    ).add_to(m)

# 3. Display in Streamlit
st_folium(m, width=700, height=500)

if st.button('🔄 Refresh Live IMD Data'):
    st.experimental_rerun()
