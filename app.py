import streamlit as st
import plotly.express as px
from PIL import Image

st.set_page_config(page_title="Agri-Intelligence", layout="centered")

# 1. Load your Static Map
img = Image.open("india_map.png")

# 2. Your 18 City Data
# Note: You'll need to calibrate these X/Y values once to match your specific image
cities = [
    {"name": "Bikaner", "x": 150, "y": 250, "temp": 32, "max": 35, "min": 18},
    {"name": "Nagpur", "x": 350, "y": 480, "temp": 34, "max": 38, "min": 22},
    # Add others here...
]

# 3. Create the Visualization
fig = px.scatter(cities, x="x", y="y", text="name", 
                 hover_data={"temp":True, "max":True, "min":True, "x":False, "y":False})

# Add the image as the background
fig.add_layout_image(
    dict(source=img, xref="x", yref="y", x=0, y=800, # y matches image height
         sizex=600, sizey=800, sizing="stretch", opacity=1, layer="below")
)

# Clean up the axes (hide gridlines)
fig.update_xaxes(showgrid=False, zeroline=False, visible=False, range=[0, 600])
fig.update_yaxes(showgrid=False, zeroline=False, visible=False, range=[0, 800])

# Styling the dots
fig.update_traces(marker=dict(size=12, color='red', line=dict(width=2, color='white')),
                  textposition='top center', textfont=dict(color='black', size=10))

fig.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=700)

st.title("🌾 Wheat Intelligence Hub")
st.plotly_chart(fig, use_container_width=True)

if st.button('🔄 Refresh Live Metrics'):
    st.rerun()
