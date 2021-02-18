# -*- coding: utf-8 -*-
import datetime
from io import StringIO
import streamlit as st
import pandas as pd
import pydeck as pdk
import requests
import urllib

st.title("Park Visitation Sample Data Mapping")

PARK_DATA = ('https://raw.githubusercontent.com/ztoms/Park-Visitation-Dashboard/main/data/parks_poi-part1.csv')
PARK_PATTERNS_SAMPLE_DATA = "https://raw.githubusercontent.com/ztoms/Park-Visitation-Dashboard/main/data/parks_patterns-part1.csv"
PARK_PATTERNS_2018_DATA = "https://psu.box.com/shared/static/ke90o1dxe4x3kx40fvgcxqplft3cctqc.csv"


@st.cache
def park_patterns_sample_df():
    return pd.read_csv(PARK_PATTERNS_SAMPLE_DATA)

@st.cache
def park_patterns_2018_df():
    data = pd.read_csv(PARK_PATTERNS_2018_DATA)
    data['date_range_start'] = pd.to_datetime(data['date_range_start'], utc=True, errors='coerce') # convert to tz_naive
    data['date_range_end'] = pd.to_datetime(data['date_range_end'], utc=True, errors='coerce')
    return data

@st.cache
def group_patterns_by_date(df, start, end):
    filtered_by_date = df[df['date_range_start'] > start and df['date_range_start'] < end]
    sum_visits_in_range = filtered_by_date.groupby(['safegraph_place_id', 'location_name']).raw_visitor_counts.agg('sum')
    return sum_visits_in_range

@st.cache
def filter_visitation_by_name(df, park_name):
    filtered_by_name = df[df['location_name'] == park_name]
    indexed_by_date = filtered_by_name.set_index('date_range_start')
    return indexed_by_date

@st.cache
def park_poi_df():
    data = pd.read_csv(PARK_DATA)
    data = data.set_index('location_name')
    return data


poi_df = park_poi_df()
#patterns_2018 = park_patterns_2018_df()

try:
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
            PARK_PATTERNS_SAMPLE_DATA,
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
        
    st.sidebar.markdown('### Time Filters')
    year = st.sidebar.selectbox('Year', ["2018","2019","2020"])
    range_size = st.sidebar.selectbox('Type', ["By Week","By Month"])
    start_date = st.date_input("Start date", datetime.datetime(2018, 1, 1))
    end_date = st.date_input("End date")
    month_selected = st.sidebar.slider('Time Slider', min_value=1, max_value=12)


    park_selected = st.selectbox("Choose park", list(poi_df.index))
        
    # charting
    #selected_park_df = filter_visitation_by_name(poi_df, park_selected)
    #st.line_chart(selected_park_df[['raw_visitor_counts', 'raw_visit_counts']])

except urllib.error.URLError as e:
    st.error("""
        **This demo requires internet access.**
        Connection error: %s
    """ % e.reason)
