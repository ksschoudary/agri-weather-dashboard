import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime

# 1. Page Config - Professional Dark Theme Setup
st.set_page_config(page_title="Agri-Intel Command", layout="wide", initial_sidebar_state="collapsed")

# Custom CSS for a truly dark dashboard
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State for Locations
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
        {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
        {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Bikaner", "lat": 28.03, "lon": 73.31},
        {"name": "Patna", "lat": 25.59, "lon": 85.14}, {"name": "Nagpur", "lat": 21.15, "lon": 79.09},
        {"name": "Indore", "lat": 22.72, "lon": 75.86}, {"name": "Hyderabad", "lat": 17.39, "lon": 78.49},
        {"name": "Bangalore", "lat": 12.97, "lon": 77.59}, {"name": "Chennai", "lat": 13.08, "lon": 80.27}
    ]

# 3. Location Manager Sidebar
with st.sidebar:
    st.header("📍 Location Manager")
    with st.expander("➕ Add Location"):
        new_city = st.text_input("City Name")
        if st.button("Add"):
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={new_city}&count=1&language=en&format=json"
            res = requests.get(url).json()
            if "results" in res:
                r = res["results"][0]
                st.session_state.city_list.append({"name": new_city, "lat": r["latitude"], "lon": r["longitude"]})
                st.rerun()
    with st.expander("❌ Remove"):
        names = [c['name'] for c in st.session_state.city_list]
        to_del = st.multiselect("Select Cities", options=names)
        if st.button("Delete"):
            st.session_state.city_list = [c for c in st.session_state.city_list if c['name'] not in to_del]
            st.rerun()

# 4. Fetch Weather Data
@st.cache_data(ttl=3600)
def fetch_weather(cities):
    data = []
    for c in cities:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={c['lat']}&longitude={c['lon']}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
        res = requests.get(url).json()
        data.append({
            "City": c['name'], "Lat": c['lat'], "Lon": c['lon'],
            "Cur": res["current_weather"]["temperature"],
            "Max": res["daily"]["temperature_2m_max"][0],
            "Min": res["daily"]["temperature_2m_min"][0]
        })
    return pd.DataFrame(data), datetime.now().strftime("%Y-%m-%d %H:%M")

# 5. Visual Dashboard
df, last_updated = fetch_weather(st.session_state.city_list)

st.title("🌾 Agri-Intelligence Dashboard")
st.info(f"🕒 Last Updated: {last_updated}")

# Build the Glowing India Map
fig = go.Figure()

# Add the Map Trace
fig.add_trace(go.Scattergeo(
    lat = df['Lat'], lon = df['Lon'], text = df['City'],
    mode = 'markers+text',
    textposition = "top center",
    # ATTRACTIVE DOTS: Glowing orange center with white ring
    marker = dict(
        size=14, color='#FF4B4B', 
        line=dict(width=2, color='white'),
        opacity=1
    ),
    textfont=dict(family="Verdana", size=10, color="white"),
    hovertemplate = "<b>%{text}</b><br>Cur: %{customdata[0]}°C<br>Max: %{customdata[1]}°C<br>Min: %{customdata[2]}°C<extra></extra>",
    customdata = df[['Cur', 'Max', 'Min']]
))

# CUSTOM DARK THEME & CLEAN CROP
fig.update_geos(
    visible=False, resolution=50,
    showcountries=True, countrycolor="#444", # Subtle dark borders
    showsubunits=True, subunitcolor="#222", # Very subtle state lines
    showland=True, landcolor="#111", # Deep black land
    showocean=True, oceancolor="#0e1117", # Background matching ocean
    lataxis_range=[6, 38], lonaxis_range=[68, 98],
    projection_type="mercator"
)

fig.update_layout(
    height=800, margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor="#0e1117", plot_bgcolor="#0e1117",
    dragmode=False
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

# Summary Table
st.dataframe(df[['City', 'Cur', 'Max', 'Min']], use_container_width=True, hide_index=True)
