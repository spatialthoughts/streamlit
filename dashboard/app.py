import streamlit as st
import leafmap.foliumap as leafmap
import geopandas as gpd

st.title('National Highway Dashboard')

filename = 'karnataka.gpkg'

@st.cache
def get_data(layer):
    gdf = gpd.read_file(filename, layer=layer)
    return gdf

districts_gdf = get_data('karnataka_districts')

districts = districts_gdf.DISTRICT.values
district = st.selectbox('Select a District', districts)

m = leafmap.Map()

districts_gdf.explore(
    m=m,
    color='black', 
    style_kwds={'fillOpacity': 0.3, 'weight': 0.5},
    tiles='Stamen Terrain',
    name='districts')

bounds = districts_gdf.total_bounds
sw = bounds[1], bounds[0]
ne = bounds[3], bounds[2]
m.fit_bounds([sw, ne]) 

m.to_streamlit(800, 800)