import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import altair as alt
from datetime import datetime
import pytz

# 1. Page Configuration
st.set_page_config(page_title="Agri-Intel Dashboard", layout="wide")

# Force Verdana via simple Markdown (Safer than complex CSS for now)
st.markdown("""<style> html, body, * { font-family: 'Verdana', sans-serif !important; } </style>""", unsafe_allow_html=True)

# 2. Data Fetcher (10 Days History + 7 Days Forecast)
@st.cache_data(ttl=3600)
def get_weather_data(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max&past_days=10&forecast_days=7&timezone=auto"
        res = requests.get(url).json()
        df = pd.DataFrame({
            'Date': pd.to_datetime(res['daily']['time']),
            'Temp': res['daily']['temperature_2m_max'],
            'Type': ['Historical']*10 + ['Forecast']*7
        })
        return df
    except Exception as e:
        return None

# 3. Session State for 18 Cities
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
        {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Ludhiana", "lat": 30.90, "lon": 75.85},
        {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Bikaner", "lat": 28.03, "lon": 73.31},
        {"name": "Nagpur", "lat": 21.15, "lon": 79.09}, {"name": "Indore", "lat": 22.72, "lon": 75.86}
    ]

st.title("🌾 Agri-Intelligence: Predictive Trend Map")

# 4. Map Initialization
# We use a standard dark tile set for stability
m = folium.Map(
    location=[22.5, 78], 
    zoom_start=5, 
    tiles='CartoDB dark_matter', # Native dark theme, no CSS hacks needed
    zoom_control=False
)

for hub in st.session_state.city_list:
    df_trend = get_weather_data(hub['lat'], hub['lon'])
    
    if df_trend is not None:
        # Create Altair Trend Chart
        chart = alt.Chart(df_trend).mark_line(point=True).encode(
            x=alt.X('Date:T', title=None),
            y=alt.Y('Temp:Q', title='Max Temp (°C)', scale=alt.Scale(zero=False)),
            strokeDash=alt.condition(alt.datum.Type == 'Forecast', alt.value([5, 5]), alt.value([0, 0])),
            color=alt.condition(alt.datum.Type == 'Forecast', alt.value('#FF4B4B'), alt.value('#3b82f6')),
            tooltip=['Date', 'Temp', 'Type']
        ).properties(width=280, height=180, title=f"{hub['name']} Forecast").configure_title(font='Verdana')

        # Convert to Popup
        vega_chart = folium.VegaLite(chart, width='100%', height='100%')
        popup = folium.Popup(max_width=320)
        vega_chart.add_to(popup)
        
        # Add Dot
        folium.CircleMarker(
            location=[hub['lat'], hub['lon']],
            radius=10, color='#FF4B4B', fill=True, fill_color='#FF4B4B',
            popup=popup, tooltip=f"Click for {hub['name']} Trends"
        ).add_to(m)

# 5. Render Map
st_folium(m, width=1400, height=750)

st.dataframe(pd.DataFrame(st.session_state.city_list)[['name']], use_container_width=True)
