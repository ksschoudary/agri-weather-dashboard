import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime
import pytz

# 1. Page Config
st.set_page_config(page_title="Wheat Intelligence Hub", layout="wide", initial_sidebar_state="expanded")

# 2. Session State for Locations
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
        {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
        {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Bikaner", "lat": 28.03, "lon": 73.31},
        {"name": "Nagpur", "lat": 21.15, "lon": 79.09}, {"name": "Indore", "lat": 22.72, "lon": 75.86}
    ]

# 3. ENHANCED LOCATION MANAGER (SIDEBAR)
with st.sidebar:
    st.title("📍 Location Manager")
    st.markdown("---")
    
    # --- SECTION 1: ADD ---
    st.subheader("➕ Add New Hub")
    new_city = st.text_input("Search City Name", placeholder="e.g. Jaipur, Kota", key="add_input")
    
    if st.button("Add to Map", use_container_width=True, type="primary"):
        if new_city:
            with st.spinner('Locating...'):
                url = f"https://geocoding-api.open-meteo.com/v1/search?name={new_city}&count=1&language=en&format=json"
                res = requests.get(url).json()
                if "results" in res:
                    r = res["results"][0]
                    st.session_state.city_list.append({"name": new_city, "lat": r["latitude"], "lon": r["longitude"]})
                    st.success(f"✅ {new_city} added!")
                    st.rerun()
                else:
                    st.error("City not found. Try another name.")
    
    st.markdown("---")
    
    # --- SECTION 2: MANAGE/DELETE ---
    st.subheader("🗑️ Manage Hubs")
    if len(st.session_state.city_list) > 0:
        # Create a clean list for the selection
        city_names = [c['name'] for c in st.session_state.city_list]
        
        # Multiselect for bulk deletion is much faster for the user
        to_del = st.multiselect("Select cities to remove:", options=city_names)
        
        if st.button("Remove Selected", use_container_width=True):
            if to_del:
                st.session_state.city_list = [c for c in st.session_state.city_list if c['name'] not in to_del]
                st.toast(f"Removed {len(to_del)} locations")
                st.rerun()
            else:
                st.warning("Please select at least one city.")
    else:
        st.info("No cities added yet.")

# 4. Data Engine (Fetch Weather)
@st.cache_data(ttl=3600)
def fetch_weather(cities):
    data = []
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

# 5. Dashboard Layout
st.title("🌾 Agri-Intelligence Dashboard")
df, last_sync = fetch_weather(st.session_state.city_list)

# Top Bar with Sync Info
c1, c2 = st.columns([3, 1])
with c1: st.markdown(f"🕒 **Last Updated:** `{last_sync} IST`")
with c2:
    if st.button("🔄 Refresh Now", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Map and Data Display
if not df.empty:
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

    fig.update_layout(height=750, margin={"r":0,"t":10,"l":0,"b":0}, paper_bgcolor="#0e1117", plot_bgcolor="#0e1117", dragmode=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    st.dataframe(df[['City', 'Cur', 'Max', 'Min']], use_container_width=True, hide_index=True)
else:
    st.warning("Add a location from the sidebar to view weather data.")
