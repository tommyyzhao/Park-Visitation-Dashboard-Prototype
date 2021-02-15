# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import pydeck as pdk
import urllib

st.title("Park Visitation Sample Data Mapping")

PARK_DATA = ('https://raw.githubusercontent.com/ztoms/Park-Visitation-Dashboard/main/data/parks_poi-part1.csv')
PARK_PATTERNS_DATA = "https://raw.githubusercontent.com/ztoms/Park-Visitation-Dashboard/main/data/parks_patterns-part1.csv"

@st.cache
def park_patterns_df():
    return pd.read_csv(PARK_PATTERNS_DATA)

@st.cache
def park_poi_df():
    return pd.read_csv(PARK_DATA).set_index('location_name')


poi_df = park_poi_df()

try:
    parks = st.multiselect("Choose park", list(poi_df.index))
    ALL_LAYERS = {
        "Park Locations": pdk.Layer(
            "ScatterplotLayer",
            PARK_DATA,
            get_position=['lng', 'lat'],
            get_color=[0, 130, 30, 160],
            get_radius=400,
            radius_scale=1,
        ),
        "Parks Visited (9/28/2020 - 10/5/2020)": pdk.Layer(
            "ScatterplotLayer",
            PARK_PATTERNS_DATA,
            get_position=['lng', 'lat'],
            get_color=[200, 30, 0, 160],
            get_radius=['100 + raw_visitor_counts*4'],
            radius_scale=2,
        ),
        "Park Names": pdk.Layer(
            "TextLayer",
            PARK_DATA,
            get_position=["lng", "lat"],
            get_text="location_name",
            get_color=[0, 0, 0, 200],
            get_size=15,
            get_alignment_baseline="'bottom'",
        )
    }

    st.sidebar.markdown('### Map Layers')


    selected_layers = []

    for layer_name, layer in ALL_LAYERS.items():
        if st.sidebar.checkbox(layer_name, True):
            if layer_name == "Park Names":
                pass
            selected_layers.append(layer)

    if selected_layers:
        st.pydeck_chart(pdk.Deck(
            map_style="mapbox://styles/mapbox/light-v9",
            initial_view_state={"latitude": 40.7914,
                                "longitude": -77.8614, "zoom": 11, "pitch": 50},
            layers=selected_layers,
        ))
    else:
        st.error("Please choose at least one layer above.")

except urllib.error.URLError as e:
    st.error("""
        **This demo requires internet access.**
        Connection error: %s
    """ % e.reason)
