import streamlit as st
import folium
import leafmap.foliumap as leafmap
import geopandas as gpd
import matplotlib.pyplot as plt


st.set_page_config(page_title="Dashboard", layout="wide")

st.title('National Highway Dashboard')

st.sidebar.title("About")
st.sidebar.info('Explore the Roads')
        
filename = 'karnataka.gpkg'

@st.cache
def get_data(layer):
    gdf = gpd.read_file(filename, layer=layer)
    return gdf

districts_gdf = get_data('karnataka_districts')
roads_gdf = get_data('karnataka_major_roads')


@st.cache
def get_roads_by_district(roads_gdf, districts_gdf):

    def get_category(row):
        ref = str(row['ref'])
        if 'NH' in ref:
            return 'NH'
        elif 'SH' in ref:
            return 'SH'
        else:
            return 'Others'
    
    roads_gdf['category'] = roads_gdf.apply(get_category, axis=1)
    roads_reprojected = roads_gdf.to_crs('EPSG:32643')
    roads_reprojected['length'] = roads_reprojected['geometry'].length
    districts_reprojected = districts_gdf.to_crs('EPSG:32643')
    joined = gpd.sjoin(roads_reprojected, districts_reprojected, how='left', op='intersects')
    length_by_type = joined.groupby(['DISTRICT', 'category']).length.sum()/1000
    return length_by_type.unstack().reset_index()

districts = districts_gdf.DISTRICT.values
district = st.sidebar.selectbox('Select a District', districts)

lengths_df = get_roads_by_district(roads_gdf.copy(), districts_gdf)
district_lengths = lengths_df[lengths_df['DISTRICT'] == district]

fig, ax = plt.subplots(1, 1)
district_lengths.plot(kind='bar', ax=ax, color=['blue', 'red', 'gray'], ylabel='Kilometers')
stats = st.sidebar.pyplot(fig)

m = leafmap.Map(
    layers_control=True,
    draw_control=False,
    measure_control=False,
    fullscreen_control=False,
)

m.add_gdf(
    gdf=districts_gdf,
    layer_name='districts',
    zoom_to_layer=True,
    info_mode='on_click',
    style={'color': 'black', 'fillOpacity': 0.3, 'weight': 0.5},
    )

selected_gdf = districts_gdf[districts_gdf['DISTRICT'] == district]

m.add_gdf(
    gdf=selected_gdf,
    layer_name='selected',
    zoom_to_layer=False,
    info_mode=None,
    style={'color': 'yellow', 'fill': None, 'weight': 2}
 )

m_streamlit = m.to_streamlit(800, 800)
