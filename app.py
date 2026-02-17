import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import altair as alt

# 1. Page Config
st.set_page_config(page_title="Agri-Trend Command", layout="wide")

# Global Verdana Styling
st.markdown("<style> * { font-family: 'Verdana' !important; } .main { background-color: #0a0e1a; } </style>", unsafe_allow_html=True)

# 2. Simplified Data Engine (7d Past + 7d Future)
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
    except:
        return None

# 3. India Map with Hover-Popups
st.title("🌾 Wheat Hubs: 14-Day Max Temp Trends")

# Native Dark Tiles for professional look
m = folium.Map(location=[22.5, 78], zoom_start=5, tiles='CartoDB dark_matter', zoom_control=False)

hubs = st.session_state.get('city_list', [
    {"name": "Amritsar", "lat": 31.63, "lon": 74.87},
    {"name": "Bikaner", "lat": 28.02, "lon": 73.31},
    {"name": "Nagpur", "lat": 21.15, "lon": 79.09}
])

for hub in hubs:
    df_trend = get_trend_data(hub['lat'], hub['lon'])
    
    if df_trend is not None:
        # Create Minimalist Altair Sparkline
        chart = alt.Chart(df_trend).mark_line().encode(
            x=alt.X('Day:O', axis=None), # Hide X axis
            y=alt.Y('Temp:Q', axis=None, scale=alt.Scale(zero=False)), # Hide Y axis
            strokeDash=alt.condition(alt.datum.Type == 'Forecast', alt.value([5, 5]), alt.value([0, 0])),
            color=alt.value('#3b82f6') # Professional Blue
        ).properties(width=200, height=80, title=f"{hub['name']} Trend (14d)")

        # Convert to Popup
        vega_chart = folium.VegaLite(chart, width='100%', height='100%')
        popup = folium.Popup(max_width=220)
        vega_chart.add_to(popup)
        
        # Add Hub Dot
        folium.CircleMarker(
            location=[hub['lat'], hub['lon']],
            radius=10, color='#FF4B4B', fill=True, fill_color='#FF4B4B',
            popup=popup, tooltip=f"<b>{hub['name']}</b>"
        ).add_to(m)

# 4. Render
st_folium(m, width=1400, height=720)
