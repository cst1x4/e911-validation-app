import streamlit as st
import requests
import urllib.parse
import pandas as pd

# --- MASTER SUITE INITIALIZATION ---
st.set_page_config(page_title="E911 Enterprise Automation Suite", layout="wide")

st.title("E911 Location Metadata Automation Suite")
st.subheader("Production-Grade Sandbox: Live GIS Boundary & USPS AMS Validation Engine")
st.markdown("---")

st.markdown(
    """
    **Enterprise Sales Demo Mode:** This platform runs live spatial telemetry and postal database routines. 
    Input any valid United States street address and ZIP code to resolve real-time county assignments, 
    pull live property records, and cross-reference recognized USPS municipal routing sectors.
    """
)

# --- SECURE BACKGROUND STATE VAULT ---
if "gis_is_active" not in st.session_state:
    st.session_state.gis_is_active = False
if "output_county" not in st.session_state:
    st.session_state.output_county = None
if "output_lat" not in st.session_state:
    st.session_state.output_lat = None
if "output_lon" not in st.session_state:
    st.session_state.output_lon = None
if "output_display_name" not in st.session_state:
    st.session_state.output_display_name = ""
if "live_extracted_parcel" not in st.session_state:
    st.session_state.live_extracted_parcel = "NOT_HARVESTED"
if "locked_parcel_value" not in st.session_state:
    st.session_state.locked_parcel_value = ""
if "parcel_label" not in st.session_state:
    st.session_state.parcel_label = "PARCEL ID"
if "usps_standardized_line1" not in st.session_state:
    st.session_state.usps_standardized_line1 = ""
if "usps_primary_city" not in st.session_state:
    st.session_state.usps_primary_city = ""
if "usps_state" not in st.session_state:
    st.session_state.usps_state = ""
if "usps_allowed_municipalities" not in st.session_state:
    st.session_state.usps_allowed_municipalities = []
if "last_searched_street" not in st.session_state:
    st.session_state.last_searched_street = ""
if "last_searched_zip" not in st.session_state:
    st.session_state.last_searched_zip = ""

# --- CRITICAL UI FIX: AUTOMATION FORM RE-KEY TRIGGER ---
# Incrementing this tracking number forces the text boxes to physically wipe their inputs clear
if "form_session_id" not in st.session_state:
    st.session_state.form_session_id = 0

# --- DUAL CONTROL LAYER GRID ---
input_panel, display_panel = st.columns([1, 1], gap="large")

with input_panel:
    st.header("Address Search")
    st.markdown("Enter data fields below. Executing a new search will clear previous states automatically.")
    
    # Passing the form_session_id straight to the form configuration layer
    with st.form(key=f"search_form_instance_{st.session_state.form_session_id}", clear_on_submit=False):
        # Cleaned up and renamed user input fields
        ui_street_str = st.text_input("Street Address", placeholder="e.g., 10545 Pawnee St")
        ui_zip_str = st.text_input("Zip Code", max_chars=5, placeholder="e.g., 80136")
        
        st.markdown(" ")
        
        # Calculation execution anchor
        search_clicked = st.form_submit_button("Execute Live Cross-Reference Validation", type="primary", use_container_width=True)

    # Standalone control button acting as our explicit memory flush mechanism
    reset_clicked = st.button("Reset Engine", type="secondary", use_container_width=True)

    # --- RESET BUTTON ENGINE SYSTEM LOGIC ---
    if reset_clicked:
        # Purge background database variables completely
        st.session_state.gis_is_active = False
        st.session_state.output_county = None
        st.session_state.output_lat = None
        st.session_state.output_lon = None
        st.session_state.output_display_name = ""
        st.session_state.live_extracted_parcel = "NOT_HARVESTED"
        st.session_state.locked_parcel_value = ""
        st.session_state.parcel_label = "PARCEL ID"
        st.session_state.usps_standardized_line1 = ""
        st.session
