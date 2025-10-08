import streamlit as st
import pandas as pd
import folium
from folium import Marker

def load_airport_data():
    # Load the airport data from the CSV file
    airport_data = pd.read_csv('src/data/AISWEB_Aeroportos.csv')
    return airport_data

def create_map(selected_airports):
    # Create a base map
    m = folium.Map(location=[-14.2350, -51.9253], zoom_start=4)  # Centered on Brazil

    # Add markers for each selected airport
    for airport in selected_airports:
        lat = airport['Latitude']
        lon = airport['Longitude']
        name = airport['Nome']
        icao = airport['ICAO']
        Marker(location=[lat, lon], popup=f"{name} ({icao})").add_to(m)

    return m

def display_map(selected_airports):
    # Create and display the map
    if selected_airports:
        m = create_map(selected_airports)
        st.write(m._repr_html_(), unsafe_allow_html=True)
    else:
        st.warning("Please select at least one airport to display on the map.")