import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import altair as alt
from datetime import datetime

st.set_page_config(page_title="Agri-Intelligence Map", layout="wide")

# Global Verdana Styling
st.markdown("<style>body { font-family: 'Verdana'; }</style>", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def get_weather_trend(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&past_days=10&forecast_days=7&timezone=auto"
    res = requests.get(url).json()
    df = pd.DataFrame({
        'Date': pd.to_datetime(res['daily']['time']),
        'Temp': res['daily']['temperature_2m_max'],
        'Type': ['Historical']*10 + ['Forecast']*7
    })
    return df

hubs = st.session_state.get('city_list', [
    {"name": "Amritsar", "lat": 31.63, "lon": 74.87},
    {"name": "Bikaner", "lat": 28.02, "lon": 73.31},
    {"name": "Nagpur", "lat": 21.14, "lon": 79.08}
])

st.title("🌾 Wheat Intelligence: Predictive Trend Map")

# Initialize Map
m = folium.Map(location=[22.5, 78], zoom_start=5, tiles='cartodbpositron', zoom_control=False)

# Add Dark Theme CSS
dark_css = """
<style>
    .leaflet-container { background: #0a0e1a !important; }
    .leaflet-tile-pane { filter: brightness(0.6) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.5); }
</style>
"""
m.get_root().header.add_child(folium.Element(dark_css))

for hub in hubs:
    df_trend = get_weather_trend(hub['lat'], hub['lon'])
    
    # Altair Chart Configuration
    chart = alt.Chart(df_trend).mark_line().encode(
        x=alt.X('Date:T', title=None),
        y=alt.Y('Temp:Q', title='Max Temp (°C)'),
        strokeDash=alt.condition(alt.datum.Type == 'Forecast', alt.value([5, 5]), alt.value([0, 0])),
        color=alt.condition(alt.datum.Type == 'Forecast', alt.value('#ef4444'), alt.value('#3b82f6'))
    ).properties(width=250, height=150, title=f"{hub['name']} Trend").configure_title(font='Verdana')

    # Add to Map
    vega_chart = folium.VegaLite(chart, width='100%', height='100%')
    popup = folium.Popup(max_width=300)
    vega_chart.add_to(popup)
    
    folium.CircleMarker(
        location=[hub['lat'], hub['lon']],
        radius=10, color='#FF4B4B', fill=True, fill_color='#FF4B4B', popup=popup
    ).add_to(m)

st_folium(m, width=1400, height=750)
