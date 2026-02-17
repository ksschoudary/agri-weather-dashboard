import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import altair as alt

# 1. Page Configuration (Using valid layout)
st.set_page_config(page_title="Agri-Trend Command", layout="wide")

# Force Verdana Styling
st.markdown("<style> * { font-family: 'Verdana' !important; } .main { background-color: #0a0e1a; } </style>", unsafe_allow_html=True)

# 2. Stable Data Fetcher (7d Past + 7d Future)
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

# 3. Default Hubs
hubs = [
    {"name": "Amritsar", "lat": 31.63, "lon": 74.87},
    {"name": "Bikaner", "lat": 28.02, "lon": 73.31},
    {"name": "Nagpur", "lat": 21.15, "lon": 79.09},
    {"name": "Indore", "lat": 22.72, "lon": 75.86}
]

st.title("🌾 Wheat Hub Intelligence")

# 4. Map Initialization (Using a built-in dark theme for stability)
m = folium.Map(
    location=[22.5, 78], 
    zoom_start=5, 
    tiles='CartoDB dark_matter', # Native professional dark look
    zoom_control=False
)

for hub in hubs:
    df_trend = get_trend_data(hub['lat'], hub['lon'])
    
    if df_trend is not None:
        # Create Minimalist Altair Trendline
        chart = alt.Chart(df_trend).mark_line(strokeWidth=3).encode(
            x=alt.X('Day:O', axis=None), 
            y=alt.Y('Temp:Q', axis=None, scale=alt.Scale(zero=False)),
            strokeDash=alt.condition(alt.datum.Type == 'Forecast', alt.value([5, 5]), alt.value([0, 0])),
            color=alt.value('#3b82f6') # Professional Blue
        ).properties(width=200, height=80, title=f"{hub['name']} 14d Trend")

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

# 5. Safe Render
try:
    st_folium(m, width=1400, height=720)
except Exception as e:
    st.error(f"Render Error: {e}. Check if streamlit-folium is in requirements.txt")
