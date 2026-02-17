import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import altair as alt
import json
from datetime import datetime

# 1. Page & Theme Configuration
st.set_page_config(page_title="Agri-Intelligence Map", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Verdana&display=swap');
    html, body, [class*="css"] { font-family: 'Verdana', sans-serif !important; }
    .main { background-color: #0a0e1a; }
    h1 { color: #f8fafc; font-family: 'Verdana'; font-size: 24px; padding-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

# 2. Data Engine (Past 10d + Future 7d)
@st.cache_data(ttl=3600)
def get_weather_trend(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&past_days=10&forecast_days=7&timezone=auto"
    res = requests.get(url).json()
    dates = res['daily']['time']
    temps = res['daily']['temperature_2m_max']
    
    df = pd.DataFrame({
        'Date': pd.to_datetime(dates),
        'Temp': temps,
        'Type': ['Historical']*10 + ['Forecast']*7
    })
    return df

# 3. List of Hubs
hubs = [
    {"name": "Amritsar", "lat": 31.63, "lon": 74.87},
    {"name": "Bikaner", "lat": 28.02, "lon": 73.31},
    {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
    {"name": "Nagpur", "lat": 21.14, "lon": 79.08},
    {"name": "Indore", "lat": 22.72, "lon": 75.86}
]

# 4. Dashboard Title
st.title("🌾 Wheat Intelligence: Predictive Trend Map")

# 5. Map Creation (Folium for Chart-in-Popup support)
# Using a custom Dark-Blue Tile look
m = folium.Map(
    location=[22.5937, 78.9629], 
    zoom_start=5, 
    tiles='cartodbpositron', # Clean base
    zoom_control=False,
    scrollWheelZoom=False,
    dragging=True
)

# Apply a CSS filter to the map tiles to get that Midnight Blue tone
folium.header.Element("""
    <style>
    .leaflet-container { background: #0a0e1a !important; }
    .leaflet-tile-pane { filter: brightness(0.6) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.5); }
    </style>
    """).add_to(m)

for hub in hubs:
    df_trend = get_weather_trend(hub['lat'], hub['lon'])
    
    # Create Altair Chart for the Popup
    base = alt.Chart(df_trend).encode(
        x=alt.X('Date:T', axis=alt.Axis(title=None, format='%d %b')),
        y=alt.Y('Temp:Q', axis=alt.Axis(title='Max Temp (°C)')),
    ).properties(width=250, height=150, title=f"{hub['name']} Trend")

    # Solid line for Historical
    line_hist = base.transform_filter(alt.datum.Type == 'Historical').mark_line(color='#3b82f6', strokeWidth=3)
    
    # Dotted line for Forecast
    line_fore = base.transform_filter(alt.datum.Type == 'Forecast').mark_line(color='#ef4444', strokeWidth=3, strokeDash=[5,5])

    chart = (line_hist + line_fore).configure_view(strokeOpacity=0).configure_title(font='Verdana', fontSize=14, color='white')
    
    # Convert Altair to JSON for Folium
    vega_chart = folium.VegaLite(chart, width='100%', height='100%')
    
    # Add Dot and Popup
    popup = folium.Popup(max_width=300)
    vega_chart.add_to(popup)
    
    folium.CircleMarker(
        location=[hub['lat'], hub['lon']],
        radius=8,
        color='#FF4B4B',
        fill=True,
        fill_color='#FF4B4B',
        fill_opacity=0.7,
        popup=popup,
        tooltip=f"<b>{hub['name']}</b><br>Click for Trends"
    ).add_to(m)

# 6. Render Map
st_folium(m, width=1400, height=750, returned_objects=[])

st.markdown("<p style='color: #94a3b8; font-size: 12px;'>Data Source: Open-Meteo Agri-Forecast Engine | Solid: Last 10 Days | Dotted: Next 7 Days</p>", unsafe_allow_html=True)
