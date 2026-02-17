import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import altair as alt

# 1. Page Config & Professional Theme
st.set_page_config(page_title="Agri-Trend Command", layout="wide")

# Global Verdana Styling (Simple & Stable)
st.markdown("""<style> html, body, * { font-family: 'Verdana', sans-serif !important; } </style>""", unsafe_allow_html=True)

# 2. Data Fetcher (7 Days Past + 7 Days Future)
@st.cache_data(ttl=3600)
def get_trend_data(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&past_days=7&forecast_days=7&timezone=auto"
        res = requests.get(url).json()
        df = pd.DataFrame({
            'Day': range(14),
            'Temp': res['daily']['temperature_2m_max'],
            'Type': ['Historical']*7 + ['Forecast']*7
        })
        return df
    except Exception:
        return None

# 3. Hub Locations
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
        {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
        {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Bikaner", "lat": 28.02, "lon": 73.31},
        {"name": "Nagpur", "lat": 21.15, "lon": 79.09}, {"name": "Indore", "lat": 22.72, "lon": 75.86}
    ]

st.title("🌾 Wheat Hubs: 14-Day Max Temp Trends")

# 4. Map Initialization (Native Dark Tiles)
m = folium.Map(
    location=[22.5, 78], 
    zoom_start=5, 
    tiles='CartoDB dark_matter', # Professional dark look without CSS hacks
    zoom_control=False
)

for hub in st.session_state.city_list:
    df_trend = get_trend_data(hub['lat'], hub['lon'])
    
    if df_trend is not None:
        # Create Minimalist Altair Trendline (Simple Blue Line)
        chart = alt.Chart(df_trend).mark_line(strokeWidth=3).encode(
            x=alt.X('Day:O', axis=None), 
            y=alt.Y('Temp:Q', axis=None, scale=alt.Scale(zero=False)),
            strokeDash=alt.condition(alt.datum.Type == 'Forecast', alt.value([5, 5]), alt.value([0, 0])),
            color=alt.value('#3b82f6') # Professional Blue
        ).properties(width=220, height=100, title=f"{hub['name']} Trend (14d)")

        # Convert to Popup
        vega_chart = folium.VegaLite(chart, width='100%', height='100%')
        popup = folium.Popup(max_width=250)
        vega_chart.add_to(popup)
        
        # Add Hub Marker
        folium.CircleMarker(
            location=[hub['lat'], hub['lon']],
            radius=10, color='#FF4B4B', fill=True, fill_color='#FF4B4B',
            popup=popup, tooltip=f"<b>{hub['name']}</b>"
        ).add_to(m)

# 5. Render
try:
    st_folium(m, width=1400, height=720)
except Exception as e:
    st.error(f"Map rendering error: {e}")
