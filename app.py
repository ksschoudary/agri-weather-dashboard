import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime
import pytz # Standard library for handling timezones

# 1. Page Config
st.set_page_config(page_title="Wheat Intelligence Hub", layout="wide", initial_sidebar_state="collapsed")

# 2. Session State for Locations
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
        {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
        {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Bikaner", "lat": 28.03, "lon": 73.31},
        {"name": "Patna", "lat": 25.59, "lon": 85.14}, {"name": "Nagpur", "lat": 21.15, "lon": 79.09},
        {"name": "Indore", "lat": 22.72, "lon": 75.86}, {"name": "Hyderabad", "lat": 17.39, "lon": 78.49},
        {"name": "Bangalore", "lat": 12.97, "lon": 77.59}, {"name": "Chennai", "lat": 13.08, "lon": 80.27}
    ]

# 3. Weather Data Engine with Timestamp
@st.cache_data(ttl=3600)
def fetch_weather(cities):
    data = []
    # Fetching Current Time in IST
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist).strftime("%d %b %Y | %I:%M %p")
    
    for c in cities:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={c['lat']}&longitude={c['lon']}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
            res = requests.get(url).json()
            data.append({
                "City": c['name'], "Lat": c['lat'], "Lon": c['lon'],
                "Cur": res["current_weather"]["temperature"],
                "Max": res["daily"]["temperature_2m_max"][0],
                "Min": res["daily"]["temperature_2m_min"][0]
            })
        except: continue
    return pd.DataFrame(data), current_time

# 4. Header Section: Refresh & Timestamp
st.title("🌾 Agri-Intelligence Dashboard")

df, last_sync = fetch_weather(st.session_state.city_list)

col_time, col_refresh = st.columns([3, 1])

with col_time:
    # Clean, professional timestamp
    st.markdown(f"🕒 **Last Updated:** `{last_sync} IST`")

with col_refresh:
    # Small, high-speed refresh button
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 5. The Locked Dark Map
fig = go.Figure(go.Scattergeo(
    lat = df['Lat'], lon = df['Lon'], text = df['City'],
    mode = 'markers+text',
    textposition = "top center",
    marker = dict(size=14, color='#FF4B4B', line=dict(width=2, color='white'), opacity=1),
    textfont=dict(family="Verdana", size=10, color="white"),
    hovertemplate = "<b>%{text}</b><br>Cur: %{customdata[0]}°C<br>Max: %{customdata[1]}°C<br>Min: %{customdata[2]}°C<extra></extra>",
    customdata = df[['Cur', 'Max', 'Min']]
))

fig.update_geos(
    visible=False, resolution=50,
    showcountries=True, countrycolor="#444",
    showsubunits=True, subunitcolor="#222", 
    showland=True, landcolor="#111",
    lataxis_range=[6, 38], lonaxis_range=[68, 98],
    projection_type="mercator"
)

fig.update_layout(
    height=750, margin={"r":0,"t":10,"l":0,"b":0},
    paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
    dragmode=False
)

st
