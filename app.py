import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

# 1. Page Configuration (Wide allows for better map visibility)
st.set_page_config(page_title="Wheat Intelligence Hub", layout="wide", initial_sidebar_state="collapsed")

# 2. Session State for Persistent Locations
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
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

# 3. Sidebar: Add/Remove Locations
with st.sidebar:
    st.title("🗺️ Map Controls")
    
    # ADD SECTION
    st.subheader("Add Location")
    new_city = st.text_input("Enter City Name", key="new_city_input")
    if st.button("Add City"):
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={new_city}&count=1&language=en&format=json"
        res = requests.get(url).json()
        if "results" in res:
            res_data = res["results"][0]
            st.session_state.city_list.append({"name": new_city, "lat": res_data["latitude"], "lon": res_data["longitude"]})
            st.rerun()
        else:
            st.error("City not found.")

    # REMOVE SECTION
    st.subheader("Manage Locations")
    city_names = [c['name'] for c in st.session_state.city_list]
    to_remove = st.multiselect("Select Cities to Remove", options=city_names)
    if st.button("Remove Selected"):
        st.session_state.city_list = [c for c in st.session_state.city_list if c['name'] not in to_remove]
        st.rerun()

# 4. Data Engine (Fetch Weather)
@st.cache_data(ttl=3600)
def fetch_weather(cities):
    results = []
    for c in cities:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={c['lat']}&longitude={c['lon']}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
        res = requests.get(url).json()
        results.append({
            "City": c['name'], "Lat": c['lat'], "Lon": c['lon'],
            "Cur": res["current_weather"]["temperature"],
            "Max": res["daily"]["temperature_2m_max"][0],
            "Min": res["daily"]["temperature_2m_min"][0]
        })
    return pd.DataFrame(results)

# 5. Visualization
st.title("🌾 Agri-Intelligence Command Center")
df = fetch_weather(st.session_state.city_list)

fig = go.Figure(go.Scattergeo(
    lat = df['Lat'], lon = df['Lon'], text = df['City'],
    mode = 'markers+text',
    textposition = "top center",
    marker = dict(size=14, color=df['Cur'], colorscale='RdYlGn_r', 
                  line=dict(width=2, color='white'), opacity=0.9),
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

fig.update_layout(height=800, margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)

# Footer Table
st.dataframe(df[['City', 'Cur', 'Max', 'Min']], use_container_width=True, hide_index=True)
