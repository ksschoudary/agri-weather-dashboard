import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
import altair as alt
from datetime import datetime
import pytz

# 1. Page Config
st.set_page_config(page_title="Agri-Intelligence Hub", layout="wide", initial_sidebar_state="collapsed")

# GLOBAL CSS: Verdana & Dark Theme
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Verdana&display=swap');
    html, body, [class*="css"] { font-family: 'Verdana', sans-serif !important; }
    .main { background-color: #0a0e1a; }
    h1 { font-size: 26px !important; color: #f8fafc; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# 2. Intelligence Engine (10d Past + 7d Forecast)
@st.cache_data(ttl=3600)
def fetch_intelligence(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&past_days=10&forecast_days=7&current_weather=true&timezone=auto"
        res = requests.get(url).json()
        df = pd.DataFrame({
            'Date': pd.to_datetime(res['daily']['time']),
            'Max': res['daily']['temperature_2m_max'],
            'Min': res['daily']['temperature_2m_min'],
            'Type': ['Historical']*10 + ['Forecast']*7
        })
        return df, res['current_weather']['temperature']
    except:
        return None, None

# 3. Session State Hubs
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
        {"name": "Amritsar", "lat": 31.63, "lon": 74.87}, {"name": "Bikaner", "lat": 28.02, "lon": 73.31},
        {"name": "Delhi", "lat": 28.61, "lon": 77.21}, {"name": "Nagpur", "lat": 21.15, "lon": 79.09},
        {"name": "Patna", "lat": 25.59, "lon": 85.14}, {"name": "Hyderabad", "lat": 17.39, "lon": 78.49}
    ]

# 4. Header & Filter
st.title("🌾 Agri-Intelligence Command Center")

view_mode = st.radio(
    "Select Map View Data:",
    ["Current/Max Temp", "17-Day Max Average", "17-Day Min Average"],
    horizontal=True
)

# 5. Map Generation (Folium for Chart Support)
m = folium.Map(location=[22.5, 78], zoom_start=5, tiles='CartoDB dark_matter', zoom_control=False)

# CSS for Midnight Blue feel in Folium
m.get_root().header.add_child(folium.Element("""
    <style>.leaflet-container { background: #0a0e1a !important; }</style>
"""))

summary_data = []

for hub in st.session_state.city_list:
    df_trend, cur_temp = fetch_intelligence(hub['lat'], hub['lon'])
    
    if df_trend is not None:
        # Filter logic for chart
        y_col = 'Min' if "Min" in view_mode else 'Max'
        
        # Create Altair Trend Graph
        chart = alt.Chart(df_trend).mark_line(point=True).encode(
            x=alt.X('Date:T', axis=alt.Axis(title=None, format='%d %b')),
            y=alt.Y(f'{y_col}:Q', title=f'{y_col} Temp (°C)', scale=alt.Scale(zero=False)),
            strokeDash=alt.condition(alt.datum.Type == 'Forecast', alt.value([5, 5]), alt.value([0, 0])),
            color=alt.condition(alt.datum.Type == 'Forecast', alt.value('#FF4B4B'), alt.value('#3b82f6'))
        ).properties(width=280, height=180, title=f"{hub['name']} {y_col} Trend").configure_title(font='Verdana')

        # Add to Popup
        vega_chart = folium.VegaLite(chart, width='100%', height='100%')
        popup = folium.Popup(max_width=320)
        vega_chart.add_to(popup)
        
        folium.CircleMarker(
            location=[hub['lat'], hub['lon']],
            radius=10, color='#FF4B4B', fill=True, fill_color='#FF4B4B',
            popup=popup, tooltip=f"<b>{hub['name']}</b> (Click for Trends)"
        ).add_to(m)
        
        summary_data.append({"City": hub['name'], "Cur": cur_temp, "Max Avg": df_trend['Max'].mean(), "Min Avg": df_trend['Min'].mean()})

# 6. Render
st_folium(m, width=1400, height=700)

if summary_data:
    st.dataframe(pd.DataFrame(summary_data), use_container_width=True, hide_index=True)
