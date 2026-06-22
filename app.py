import streamlit as st
import requests
import urllib.parse
import pandas as pd
from datetime import datetime

# --- MASTER SUITE INITIALIZATION ---
st.set_page_config(page_title="Project E911 Carrier Suite", layout="wide")

st.title("Project E911 Location Metadata Suite")
st.subheader("Colorado Carrier-Grade Validation Matrix: Local GIS Boundary & MSAG Engine")
st.markdown("---")

st.markdown(
    """
    **Colorado Operational Mode:** This optimized platform runs localized spatial telemetry, 
    automatic MSAG exception handling, and automated validation routine dispatch for Colorado regional grids. 
    Input any Colorado street address and ZIP code to anchor coordinates and extract official county database identifiers.
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
    st.session_state.parcel_label = "IDENTIFIER"
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
if "search_timestamp" not in st.session_state:
    st.session_state.search_timestamp = ""
if "structural_type" not in st.session_state:
    st.session_state.structural_type = ""
if "registered_identity" not in st.session_state:
    st.session_state.registered_identity = ""
if "psap_sector_code" not in st.session_state:
    st.session_state.psap_sector_code = "UNASSIGNED"
if "msag_discrepancy_flag" not in st.session_state:
    st.session_state.msag_discrepancy_flag = False
if "county_contact_email" not in st.session_state:
    st.session_state.county_contact_email = ""
if "verification_lifecycle_status" not in st.session_state:
    st.session_state.verification_lifecycle_status = "AWAITING_INGESTION"
if "form_session_id" not in st.session_state:
    st.session_state.form_session_id = 0
if "source_portal_url" not in st.session_state:
    st.session_state.source_portal_url = ""

# --- DUAL CONTROL LAYER GRID ---
input_panel, display_panel = st.columns([1, 1], gap="large")

with input_panel:
    st.header("Carrier Ingestion Point")
    st.markdown("Enter standard address strings below to execute regional cross-system verification cycles.")
    
    with st.form(key=f"search_form_instance_{st.session_state.form_session_id}", clear_on_submit=False):
        ui_street_str = st.text_input("Street Address", placeholder="e.g., enter any street path")
        ui_zip_str = st.text_input("Zip Code", max_chars=5, placeholder="e.g., enter 5-digit ZIP code")
        
        st.markdown(" ")
        search_clicked = st.form_submit_button("Execute Carrier Validation Cycle", type="primary", use_container_width=True)

    reset_clicked = st.button("Reset Engine", type="secondary", use_container_width=True)

    if reset_clicked:
        st.session_state.gis_is_active = False
        st.session_state.output_county = None
        st.session_state.output_lat = None
        st.session_state.output_lon = None
        st.session_state.output_display_name = ""
        st.session_state.live_extracted_parcel = "NOT_HARVESTED"
        st.session_state.locked_parcel_value = ""
        st.session_state.parcel_label = "IDENTIFIER"
        st.session_state.usps_standardized_line1 = ""
        st.session_state.usps_primary_city = ""
        st.session_state.usps_state = ""
        st.session_state.usps_allowed_municipalities = []
        st.session_state.last_searched_street = ""
        st.session_state.last_searched_zip = ""
        st.session_state.search_timestamp = ""
        st.session_state.psap_sector_code = "UNASSIGNED"
        st.session
