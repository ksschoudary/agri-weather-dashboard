import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests

st.set_page_config(page_title="Agri-Weather Command Center", layout="wide")

# 1. Location Manager in Sidebar
st.sidebar.title("📍 Location Manager")
manual_city = st.sidebar.text_input("Add City Manually (e.g., 'Jaipur')")
add_btn = st.sidebar.button("Add to Map")

# Initialize city list in session state if not present
if 'my_cities' not in st.session_state:
    st.session_state.my_cities = [
        {"name": "Bikaner", "lat": 28.02, "lon": 73.31},
        {"name": "Nagpur", "lat": 21.14, "lon": 79.08},
        {"name": "Indore", "lat": 22.71, "lon": 75.85}
    ]

# 2. Geocoding Function (Finds Lat/Lon for your manual city)
def get_coords(city_name):
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
    res = requests.get(url).json()
    if "results" in res:
        return res["results"][0]["latitude"], res["results"][0]["longitude"]
    return None, None

if add_btn and manual_city:
    lat, lon = get_coords(manual_city)
    if lat:
        st.session_state.my_cities.append({"name": manual_city, "lat": lat, "lon": lon})
        st.sidebar.success(f"Added {manual_city}!")
    else:
        st.sidebar.error("City not found. Check spelling.")

# 3. Fetch Weather Data (Min/Max/Current)
@st.cache_data(ttl=3600)
def fetch_weather(city_list):
    data = []
    for c in city_list:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={c['lat']}&longitude={c['lon']}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&timezone=auto"
        res = requests.get(url).json()
        data.append({
            "City": c['name'], "Lat": c['lat'], "Lon": c['lon'],
            "Current": res["current_weather"]["temperature"],
            "Max": res["daily"]["temperature_2m_max"][0],
            "Min": res["daily"]["temperature_2m_min"][0]
        })
    return pd.DataFrame(data)

# 4. Create the "India Only" Visual
st.title("🌾 Agri-Intelligence Dashboard")
df = fetch_weather(st.session_state.my_cities)

fig = go.Figure(go.Scattergeo(
    lat = df['Lat'], lon = df['Lon'], text = df['City'],
    mode = 'markers+text',
    textposition = "top center",
    marker = dict(size=14, color=df['Current'], colorscale='RdYlGn_r', 
                  line=dict(width=2, color='white'), opacity=0.9),
    # THIS BOX SHOWS ON HOVER
    hovertemplate = (
        "<b>%{text}</b><br>" +
        "Current: %{customdata[0]}°C<br>" +
        "Max: %{customdata[1]}°C<br>" +
        "Min: %{customdata[2]}°C<extra></extra>"
    ),
    customdata = df[['Current', 'Max', 'Min']]
))

fig.update_geos(
    visible=False, 
    showcountries=True, countrycolor="Black",
    showsubunits=True, subunitcolor="Gray", 
    lataxis_range=[6, 38], lonaxis_range=[68, 98],
    projection_type="mercator"
)

fig.update_layout(height=800, margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(fig, use_container_width=True)
