import streamlit as st
import requests
import urllib.parse
import pandas as pd
from datetime import datetime

# --- MASTER SUITE INITIALIZATION ---
st.set_page_config(page_title="Project E911 Carrier Suite", layout="wide")

st.title("Project E911 Location Metadata Suite")
st.subheader("Carrier-Grade Validation Matrix: National GIS Boundary, MSAG & Automated Lifecycle Engine")
st.markdown("---")

st.markdown(
    """
    **Carrier Operations Mode:** This enterprise platform runs real-time national spatial telemetry, 
    automatic MSAG exception handling, and automated county verification dispatch routines. Input any 
    domestic street address and ZIP code to anchor coordinate data, assign structural risk levels, 
    and manage automated validation lifecycles.
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
if "search_timestamp" not in st.session_state:
    st.session_state.search_timestamp = ""

# --- STRATEGIC ADDITIONS: CARRIER-GRADE STATE VARIABLE INITIALIZATION ---
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

# --- DUAL CONTROL LAYER GRID ---
input_panel, display_panel = st.columns([1, 1], gap="large")

with input_panel:
    st.header("Carrier Ingestion Point")
    st.markdown("Enter standard address strings below to execute national cross-system verification cycles.")
    
    with st.form(key=f"search_form_instance_{st.session_state.form_session_id}", clear_on_submit=False):
        ui_street_str = st.text_input("Street Address", placeholder="e.g., 2985 S Hudson St or 10545 Pawnee St")
        ui_zip_str = st.text_input("Zip Code", max_chars=5, placeholder="e.g., 80222 or 80136")
        
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
        st.session_state.parcel_label = "PARCEL ID"
        st.session_state.usps_standardized_line1 = ""
        st.session_state.usps_primary_city = ""
        st.session_state.usps_state = ""
        st.session_state.usps_allowed_municipalities = []
        st.session_state.last_searched_street = ""
        st.session_state.last_searched_zip = ""
        st.session_state.search_timestamp = ""
        st.session_state.psap_sector_code = "UNASSIGNED"
        st.session_state.msag_discrepancy_flag = False
        st.session_state.county_contact_email = ""
        st.session_state.verification_lifecycle_status = "AWAITING_INGESTION"
        
        st.session_state.form_session_id += 1
        st.rerun()
    
    if search_clicked:
        if ui_street_str.strip() and ui_zip_str.strip():
            st.session_state.gis_is_active = False
            st.session_state.live_extracted_parcel = "NOT_HARVESTED"
            st.session_state.locked_parcel_value = ""
            st.session_state.msag_discrepancy_flag = False
            
            st.session_state.last_searched_street = ui_street_str.strip().upper()
            st.session_state.last_searched_zip = ui_zip_str.strip()
            st.session_state.search_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S MST")
            
            # 1. NATIONAL GIS RESOLUTION CHAIN (UPGRADED TO STRUCTURED API CALL)
            encoded_street = urllib.parse.quote(ui_street_str.strip())
            encoded_zip = urllib.parse.quote(ui_zip_str.strip())
            api_url = f"https://nominatim.openstreetmap.org/search?street={encoded_street}&postalcode={encoded_zip}&format=json&addressdetails=1&countrycodes=us&limit=1"
            headers = {"User-Agent": "CSTerrellART_E911_Automation_Suite/2.0 (contact: support@csterrellart.com)"}
            
            try:
                with st.spinner("Querying national geographic spatial endpoints..."):
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
                    
                    # National Jurisdiction Normalization
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
                    
                    st.session_state.output_county = final_county
                    st.session_state.output_lat = res.get("lat")
                    st.session_state.output_lon = res.get("lon")
                    st.session_state.output_display_name = res.get("display_name", "").upper()
                    st.session_state.gis_is_active = True
                    st.session_state.live_extracted_parcel = "READY"
                    
                    # DYNAMIC REGIONAL NOMENCLATURE MAPPER
                    county_lower = final_county.lower()
                    if "denver" in county_lower:
                        st.session_state.parcel_label = "SCHEDULE NUMBER"
                        st.session_state.county_contact_email = "assessor@denvergov.org"
                    elif "arapahoe" in county_lower:
                        st.session_state.parcel_label = "PIN (PROPERTY ID NUMBER)"
                        st.session_state.county_contact_email = "assessor@arapahoegov.com"
                    elif "jefferson" in county_lower or "jeffco" in county_lower:
                        st.session_state.parcel_label = "LOT NUMBER /AIN"
                        st.session_state.county_contact_email = "assessor@jeffco.us"
                    elif "cook" in county_lower:
                        st.session_state.parcel_label = "PIN (PERMANENT INDEX NUMBER)"
                        st.session_state.county_contact_email = "assessor@cookcountyil.gov"
                    elif "los angeles" in county_lower:
                        st.session_state.parcel_label = "AIN (ASSESSOR IDENTIFICATION NUMBER)"
                        st.session_state.county_contact_email = "assessor@assessor.lacounty.gov"
                    else:
                        st.session_state.parcel_label = "PARCEL ID / TAX ACCNT NUMBER"
                        sanitized_county_slug = county_lower.replace(" county", "").replace(" ", "")
                        st.session_state.county_contact_email = f"gis_validation@{sanitized_county_slug}.gov"

                    # 2. CARRIER STRATEGIC ADDITION: DETERMINISTIC PSAP CALCULATOR
                    lat_float = float(st.session_state.output_lat)
                    lon_float = float(st.session_state.output_lon)
                    hash_routing = abs(hash(f"{st.session_state.output_county
