# Create the map object first
m = folium.Map(
    location=[22.5937, 78.9629], 
    zoom_start=5, 
    tiles='cartodbpositron',
    zoom_control=False,
    scrollWheelZoom=False
)

# STABLE CSS INJECTION
# This targets the map container and applies the Midnight Blue filter
dark_css = """
<style>
    .leaflet-container { background: #0a0e1a !important; }
    .leaflet-tile-pane { 
        filter: brightness(0.6) invert(1) contrast(3) hue-rotate(200deg) saturate(0.3) brightness(0.5); 
    }
</style>
"""
m.get_root().header.add_child(folium.Element(dark_css))
