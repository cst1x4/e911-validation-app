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
# We track state execution profiles independently from the interactive UI form elements
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

# --- DUAL CONTROL LAYER GRID ---
input_panel, display_panel = st.columns([1, 1], gap="large")

with input_panel:
    st.header("Address Search")
    st.markdown("Enter data fields below. Executing a new search will clear previous states automatically.")
    
    # --- HARDENED FORM IMPLEMENTATION ---
    # Using clear_on_submit=False for searches, and handling resetting via a targeted block
    with st.form(key="ingestion_search_form", clear_on_submit=False):
        ui_street_str = st.text_input("Street Address String", placeholder="e.g., 10545 Pawnee St")
        ui_zip_str = st.text_input("5-Digit ZIP Code", max_chars=5, placeholder="e.g., 80136")
        
        st.markdown(" ")
        
        # Submitting the form acts as our calculation execution catalyst
        search_clicked = st.form_submit_button("Execute Live Cross-Reference Validation", type="primary", use_container_width=True)

    # Clean, secondary standalone button acting as our explicit memory flush mechanism
    reset_clicked = st.button("Reset Engine", type="secondary", use_container_width=True)

    # --- RESET BUTTON ENGINE SYSTEM LOGIC ---
    if reset_clicked:
        # Purge background database variables
        st.session_state.gis_is_active = False
        st.session_state.output_county = None
        st.session_state.output_lat = None
        st.session_state.output_lon = None
        st.session_state.output_display_name = ""
        st.session_state.live_extracted_parcel = "NOT_HARVESTED"
        st.session_state.locked_parcel_value = ""
        st.session_state.parcel_label = "PARCEL ID"
        st.session_state.usps_standardized_line1 = ""
        st.session_state.usps_primary_city = ""
        st.session_state.usps_state = ""
        st.session_state.usps_allowed_municipalities = []
        st.session_state.last_searched_street = ""
        st.session_state.last_searched_zip = ""
        
        # Streamlit's native way to force a UI reset without breaking widget state boundaries
        st.rerun()
    
    # --- SEARCH COMPONENT SYSTEM LOGIC ---
    if search_clicked:
        if ui_street_str.strip() and ui_zip_str.strip():
            
            # Flush state slots to ensure clean background calculations
            st.session_state.gis_is_active = False
            st.session_state.live_extracted_parcel = "NOT_HARVESTED"
            st.session_state.locked_parcel_value = ""
            
            # Cache inputs inside our state vault safely
            st.session_state.last_searched_street = ui_street_str.strip().upper()
            st.session_state.last_searched_zip = ui_zip_str.strip()
            
            # 1. GIS RESOLUTION CHAIN
            query_string = f"{ui_street_str.strip()}, {ui_zip_str.strip()}"
            api_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query_string)}&format=json&addressdetails=1&countrycodes=us&limit=1"
            headers = {"User-Agent": "CSTerrellART_E911_Automation_Suite/1.0 (contact: support@csterrellart.com)"}
            
            try:
                with st.spinner("Broadcasting coordinate lookup handshakes to global GIS servers..."):
                    response = requests.get(api_url, headers=headers, timeout=10)
                    data = response.json()
                
                if data:
                    res = data[0]
                    address_details = res.get("address", {})
                    
                    raw_county = address_details.get("county")
                    raw_county_district = address_details.get("county_district")
                    raw_region = address_details.get("region")
                    raw_city = address_details.get("city")
                    raw_town = address_details.get("town")
                    raw_village = address_details.get("village")
                    
                    # Consolidated Municipal Overrides
                    if raw_county:
                        final_county = raw_county
                    elif raw_county_district:
                        final_county = raw_county_district
                    elif raw_region and "county" in raw_region.lower():
                        final_county = raw_region
                    elif raw_city == "Denver":
                        final_county = "Denver County"
                    else:
                        local_name = raw_city if raw_city else raw_town if raw_town else raw_village if raw_village else "Unknown"
                        final_county = f"{local_name} County"
                    
                    if final_county and not final_county.lower().endswith("county") and not final_county.lower().endswith("parish"):
                        final_county = f"{final_county} County"
                    
                    # Regional Naming Convention Normalization
                    if "denver" in final_county.lower():
                        st.session_state.parcel_label = "SCHEDULE NUMBER"
                    else:
                        st.session_state.parcel_label = "PARCEL ID"
                    
                    # Store data parameters 
                    st.session_state.output_county = final_county
                    st.session_state.output_lat = res.get("lat")
                    st.session_state.output_lon =
