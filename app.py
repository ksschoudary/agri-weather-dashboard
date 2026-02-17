import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import requests
from datetime import datetime, timedelta
import pytz

# 1. Page & Theme Config
st.set_page_config(page_title="Wheat Predictive Hub", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Verdana&display=swap');
    html, body, [class*="css"], .stMarkdown, .stButton, .stTextInput, .stMultiSelect {
        font-family: 'Verdana', sans-serif !important;
    }
    .main { background-color: #0a0e1a; }
    h1 { font-size: 26px !important; color: #f8fafc; font-weight: 600; }
    div.block-container { padding-top: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# 2. Session State for Locations
if 'city_list' not in st.session_state:
    st.session_state.city_list = [
        {"name": "Bikaner", "lat": 28.02, "lon": 73.31}, {"name": "Amritsar", "lat": 31.63, "lon": 74.87},
        {"name": "Ludhiana", "lat": 30.90, "lon": 75.85}, {"name": "Nagpur", "lat": 21.14, "lon": 79.08}
    ]

# 3. ADVANCED DATA ENGINE: Historical (10d) + Forecast (7d)
@st.cache_data(ttl=3600)
def fetch_comprehensive_weather(lat, lon):
    # Open-Meteo API for 10 days past + 7 days future
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&daily=temperature_2m_max,temperature_2m_min&past_days=10&forecast_days=7&timezone=auto"
    res = requests.get(url).json()
    
    daily = res['daily']
    df_trend = pd.DataFrame({
        'Date': pd.to_datetime(daily['time']),
        'Max': daily['temperature_2m_max'],
        'Min': daily['temperature_2m_min']
    })
    
    # Split into Historical and Forecast
    today = datetime.now().date()
    df_trend['Type'] = df_trend['Date'].apply(lambda x: 'Historical' if x.date() < today else 'Forecast')
    
    current_temp = res['current_weather']['temperature']
    return df_trend, current_temp

# 4. Header & Selection Filter
st.title("🌾 Agri-Predictive Intelligence Hub")

col_filter, col_sync = st.columns([3, 1])
with col_filter:
    view_option = st.segmented_control(
        "📊 Map Intelligence View",
        options=["Real-time (Current/Min/Max)", "Max Temp Trends (10d + 7d)", "Min Temp Trends (10d + 7d)"],
        default="Real-time (Current/Min/Max)"
    )

with col_sync:
    if st.button("🔄 Sync Intelligence", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# 5. Build Map & Interactive Panel
c_map, c_panel = st.columns([3, 1])

# Fetch data for all cities (Map display)
map_data = []
for c in st.session_state.city_list:
    trend, cur = fetch_comprehensive_weather(c['lat'], c['lon'])
    avg_max = trend['Max'].mean()
    avg_min = trend['Min'].mean()
    map_data.append({**c, "Cur": cur, "AvgMax": avg_max, "AvgMin": avg_min, "Trend": trend})

df_map = pd.DataFrame(map_data)

with c_map:
    fig = go.Figure()
    # Logic for Dot Color based on Filter
    color_col = "Cur" if "Real-time" in view_option else ("AvgMax" if "Max" in view_option else "AvgMin")
    
    fig.add_trace(go.Scattergeo(
        lat=df_map['lat'], lon=df_map['lon'], text=df_map['name'],
        mode='markers+text', textposition="top center",
        marker=dict(size=14, color=df_map[color_col], colorscale='RdYlGn_r', line=dict(width=1.5, color='white')),
        textfont=dict(family="Verdana", size=10, color="#94a3b8"),
        hoverinfo="text", # We'll use a sidebar/panel for the complex graph
    ))

    fig.update_geos(
        visible=False, showland=True, landcolor="#1e293b", oceancolor="#0a0e1a",
        showcountries=True, countrycolor="#334155", lataxis_range=[6, 38], lonaxis_range=[68, 98]
    )
    fig.update_layout(height=700, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="#0a0e1a", dragmode=False)
    
    # Selection trigger
    selected_city = st.selectbox("🎯 Select City for Detailed Forecast", df_map['name'])

with c_panel:
    # 6. DYNAMIC TREND PANEL (Historical vs Forecast)
    st.subheader(f"📈 {selected_city} Trends")
    city_row = df_map[df_map['name'] == selected_city].iloc[0]
    df_trend = city_row['Trend']
    
    # Plotly Trend Graph
    fig_trend = go.Figure()
    
    # Filter columns based on user map selection
    y_col = 'Max' if "Max" in view_option or "Real-time" in view_option else 'Min'
    
    # Historical Line (Solid)
    hist = df_trend[df_trend['Type'] == 'Historical']
    fig_trend.add_trace(go.Scatter(x=hist['Date'], y=hist[y_col], name="Historical", line=dict(color='#3b82f6', width=3)))
    
    # Forecast Line (Dotted)
    fore = df_trend[df_trend['Type'] == 'Forecast']
    # Add last point of hist to fore for a continuous line
    fore_full = pd.concat([hist.tail(1), fore])
    fig_trend.add_trace(go.Scatter(x=fore_full['Date'], y=fore_full[y_col], name="Forecast", line=dict(color='#ef4444', width=3, dash='dot')))
    
    fig_trend.update_layout(
        template="plotly_dark", height=300, 
        margin=dict(l=0,r=0,t=10,b=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        font_family="Verdana"
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    
    # Summary Metrics
    st.metric("Current Temp", f"{city_row['Cur']}°C")
    st.metric("Period Average", f"{round(city_row[color_col], 1)}°C")
