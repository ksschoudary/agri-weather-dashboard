import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

# 1. Page Config - Defaulting to collapsed sidebar as requested
st.set_page_config(page_title="Wheat Intelligence Hub", layout="wide", initial_sidebar_state="collapsed")

# 2. Session State for Data Persistence
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
        {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
        {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Bikaner", "lat": 28.03, "lon": 73.31},
        {"name": "Patna", "lat": 25.59, "lon": 85.14}, {"name": "Nagpur", "lat": 21.15, "lon": 79.09},
        {"name": "Indore", "lat": 22.72, "lon": 75.86}, {"name": "Hyderabad", "lat": 17.39, "lon": 78.49},
        {"name": "Bangalore", "lat": 12.97, "lon": 77.59}, {"name": "Chennai", "lat": 13.08, "lon": 80.27}
    ]

# 3. Location Manager (Sidebar)
with st.sidebar:
    st.title("📍 Location Manager")
    
    # Unified Add Section
    with st.expander("➕ Add New Location", expanded=False):
        new_city = st.text_input("City Name", placeholder="e.g. Jaipur")
        if st.button("Confirm Add"):
            url = f"https://geocoding-api.open-meteo.com/v1/search?name={new_city}&count=1&language=en&format=json"
            res = requests.get(url).json()
            if "results" in res:
                r = res["results"][0]
                st.session_state.city_list.append({"name": new_city, "lat": r["latitude"], "lon": r["longitude"]})
                st.rerun()
            else: st.error("City not found.")

    # Unified Remove Section
    with st.expander("❌ Remove Locations", expanded=False):
        current_names = [c['name'] for c in st.session_state.city_list]
        to_del = st.multiselect("Select to Remove", options=current_names)
        if st.button("Confirm Delete"):
            st.session_state.city_list = [c for c in st.session_state.city_list if c['name'] not in to_del]
            st.rerun()

# 4. Weather Data Engine
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
    return pd.DataFrame(data)

# 5. The Locked India Map
st.title("🌾 Agri-Intelligence Dashboard")
df = fetch_weather(st.session_state.city_list)

fig = go.Figure(go.Scattergeo(
    lat = df['Lat'], lon = df['Lon'], text = df['City'],
    mode = 'markers+text',
    textposition = "top center",
    marker = dict(size=14, color=df['Cur'], colorscale='RdYlGn_r', 
                  line=dict(width=2, color='white'), opacity=0.9),
    # Only showing Temperature Metrics on hover as requested
    hovertemplate = "<b>%{text}</b><br>Cur: %{customdata[0]}°C<br>Max: %{customdata[1]}°C<br>Min: %{customdata[2]}°C<extra></extra>",
    customdata = df[['Cur', 'Max', 'Min']]
))

fig.update_geos(
    visible=False, resolution=50,
    showcountries=True, countrycolor="Black",
    showsubunits=True, subunitcolor="Gray", 
    showland=True, landcolor="white",
    lataxis_range=[6, 38], lonaxis_range=[68, 98],
    projection_type="mercator"
)

# DISABLING ZOOM AND PAN
fig.update_layout(
    height=800, margin={"r":0,"t":0,"l":0,"b":0},
    dragmode=False # Disables panning/dragging
)

# Final config to remove the "Zoom" icons and disable scroll-zoom
st.plotly_chart(fig, use_container_width=True, config={
    'displayModeBar': False, # Hides the entire top toolbar
    'scrollZoom': False,     # Disables mouse-wheel zoom
    'staticPlot': False      # Keeps hover interaction active
})

st.dataframe(df[['City', 'Cur', 'Max', 'Min']], use_container_width=True, hide_index=True)
