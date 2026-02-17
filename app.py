import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime
import pytz

# 1. Page Config & Custom Midnight Theme
st.set_page_config(page_title="Agri-Intelligence Command", layout="wide", initial_sidebar_state="collapsed")

# Injecting the Midnight Blue background tone
st.markdown("""
    <style>
    .main { background-color: #0a0e1a; }
    div.block-container { padding-top: 1rem; }
    [data-testid="stSidebar"] { background-color: #111827; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State with all 18 Wheat-Growing Hubs
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
        {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
        {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Mathura", "lat": 27.49, "lon": 77.67},
        {"name": "Rudrapur", "lat": 28.98, "lon": 79.41}, {"name": "Shahjahanpur", "lat": 27.88, "lon": 79.91},
        {"name": "Bikaner", "lat": 28.02, "lon": 73.31}, {"name": "Kota", "lat": 25.21, "lon": 75.86},
        {"name": "Rajkot", "lat": 22.30, "lon": 70.80}, {"name": "Nadiad", "lat": 22.69, "lon": 72.86},
        {"name": "Bhopal", "lat": 23.26, "lon": 77.41}, {"name": "Indore", "lat": 22.72, "lon": 75.86},
        {"name": "Nagpur", "lat": 21.15, "lon": 79.09}, {"name": "Patna", "lat": 25.59, "lon": 85.14},
        {"name": "Begusarai", "lat": 25.42, "lon": 86.13}, {"name": "Lalitpur", "lat": 24.69, "lon": 78.41},
        {"name": "Hyderabad", "lat": 17.39, "lon": 78.49}, {"name": "Bangalore", "lat": 12.97, "lon": 77.59}
    ]

# 3. Location Manager (Sidebar)
with st.sidebar:
    st.title("📍 Location Manager")
    with st.expander("➕ Add Location", expanded=False):
        new_city = st.text_input("City Name")
        if st.button("Add Hub", use_container_width=True):
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={new_city}&count=1&language=en&format=json"
            res = requests.get(url).json()
            if "results" in res:
                r = res["results"][0]
                st.session_state.city_list.append({"name": new_city, "lat": r["latitude"], "lon": r["longitude"]})
                st.rerun()
    with st.expander("❌ Remove Locations", expanded=False):
        to_del = st.multiselect("Select Hubs", [c['name'] for c in st.session_state.city_list])
        if st.button("Delete Selected", use_container_width=True):
            st.session_state.city_list = [c for c in st.session_state.city_list if c['name'] not in to_del]
            st.rerun()

# 4. Data Engine
@st.cache_data(ttl=3600)
def fetch_weather(cities):
    data = []
    ist = pytz.timezone('Asia/Kolkata')
    ts = datetime.now(ist).strftime("%d %b %Y | %I:%M %p")
    for c in cities:
        try:
            url = f"https://api.open-meteo.com/v1/forecast?latitude={c['lat']}&longitude={c['lon']}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
            res = requests.get(url).json()
            data.append({"City": c['name'], "Lat": c['lat'], "Lon": c['lon'], "Cur": res["current_weather"]["temperature"], "Max": res["daily"]["temperature_2m_max"][0], "Min": res["daily"]["temperature_2m_min"][0]})
        except: continue
    return pd.DataFrame(data), ts

# 5. Dashboard Execution
df, last_sync = fetch_weather(st.session_state.city_list)

st.title("🌾 Agri-Intelligence Command Center")
c1, c2 = st.columns([3, 1])
with c1: st.markdown(f"🕒 **Last Sync:** `{last_sync} IST`")
with c2: 
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# MAP VISUALIZATION - PROFESSIONAL CROP
fig = go.Figure()

# Background Glow for Markers
fig.add_trace(go.Scattergeo(
    lat=df['Lat'], lon=df['Lon'], mode='markers',
    marker=dict(size=22, color='#FF4B4B', opacity=0.15),
    hoverinfo='skip'
))

# Main Active Markers
fig.add_trace(go.Scattergeo(
    lat=df['Lat'], lon=df['Lon'], text=df['City'],
    mode='markers+text', textposition="top center",
    marker=dict(size=12, color='#FF4B4B', line=dict(width=1.5, color='white')),
    textfont=dict(family="Verdana", size=9, color="#94a3b8"),
    hovertemplate="<b>%{text}</b><br>Cur: %{customdata[0]}°C<br>Max: %{customdata[1]}°C<extra></extra>",
    customdata=df[['Cur', 'Max']]
))

fig.update_geos(
    visible=False, resolution=50,
    showland=True, landcolor="#1e293b", # Dark Blue-Grey Land
    showocean=True, oceancolor="#0a0e1a", # Matches background exactly
    showcountries=True, countrycolor="#334155", # Professional subtle borders
    showsubunits=True, subunitcolor="#1e293b",
    lataxis_range=[6, 38], lonaxis_range=[68, 98],
    projection_type="mercator"
)

fig.update_layout(
    height=800, margin={"r":0,"t":0,"l":0,"b":0},
    paper_bgcolor="#0a0e1a", plot_bgcolor="#0a0e1a",
    dragmode=False
)

st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
st.dataframe(df[['City', 'Cur', 'Max', 'Min']], use_container_width=True, hide_index=True)
