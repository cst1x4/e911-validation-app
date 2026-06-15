import streamlit as st
import pandas as pd
import urllib.parse

# --- MASTER DEMO INITIALIZATION ---
st.set_page_config(page_title="E911 Enterprise Automation Suite", layout="wide", page_icon="🛡️")

st.title("🛡️ E911 Location Metadata Automation Sandbox")
st.subheader("Enterprise Demonstration Portal: Manual Address Search & Verification Routing")
st.markdown("---")

# Production-Grade Sandbox Mock Database
MOCK_COUNTY_REGISTRY = {
    "1560 broadway": {"parcel": "02341-21-009-000", "county": "Denver County", "url": "https://www.denvergov.org/Property"},
    "1699 s colorado blvd": {"parcel": "05213-04-112-000", "county": "Denver County", "url": "https://www.denvergov.org/Property"},
    "5690 greenwood plaza blvd": {"parcel": "2075-16-3-01-002", "county": "Arapahoe County", "url": "https://www.arapahoegov.com/Assessor"}
}

MOCK_USPS_ZIP_MATRIX = {
    "80202": {
        "standardized_street": "1560 BROADWAY",
        "primary_city": "DENVER",
        "allowed_municipalities": ["DENVER", "DOWNTOWN BOXES", "CAPITOL HILL STN"]
    },
    "80222": {
        "standardized_street": "1699 S COLORADO BLVD",
        "primary_city": "DENVER",
        "allowed_municipalities": ["DENVER", "GLENDALE", "CHERRY CREEK"]
    },
    "80111": {
        "standardized_street": "5690 GREENWOOD PLAZA BLVD",
        "primary_city": "GREENWOOD VILLAGE",
        "allowed_municipalities": ["GREENWOOD VILLAGE", "ENGLEWOOD", "CENTENNIAL", "ORCHARD HILLS"]
    }
}

# --- CRITICAL FIX: INITIALIZE PERSISTENT MEMORY SLOTS ---
if "active_street" not in st.session_state:
    st.session_state.active_street = ""
if "active_zip" not in st.session_state:
    st.session_state.active_zip = ""
if "active_unit" not in st.session_state:
    st.session_state.active_unit = ""
if "search_executed" not in st.session_state:
    st.session_state.search_executed = False

# --- DUAL COLUMN DISPLAY ARCHITECTURE ---
input_col, diagnostic_col = st.columns([1, 1], gap="large")

with input_col:
    st.header("📥 Manual Address Ingestion")
    st.markdown("Manually input an address string below to test the deterministic cross-reference engine.")
    
    # Text inputs read from and write to the persistent session state directly
    input_street = st.text_input("Street Address String", value=st.session_state.active_street, placeholder="e.g., 1560 Broadway")
    input_zip = st.text_input("5-Digit ZIP Code", value=st.session_state.active_zip, max_chars=5, placeholder="e.g., 80202")
    input_unit = st.text_input("Unit / Apt / Suite (Optional)", value=st.session_state.active_unit, placeholder="e.g., Suite 300")
    
    st.markdown(" ")
    
    # 🔎 THE SEARCH COMPONENT
    if st.button("🔎 Execute Validation Search", type="primary", use_container_width=True):
        if input_street.strip() and input_zip.strip():
            # Force overwrite the persistent vault memory with the FRESH typed parameters
            st.session_state.active_street = input_street.strip()
            st.session_state.active_zip = input_zip.strip()
            st.session_state.active_unit = input_unit.strip()
            st.session_state.search_executed = True
            
            # Immediately force an internal script rerun so the calculations use the fresh states
            st.rerun()
        else:
            st.error("⚠️ Ingestion Failure: Both a Street Address and a ZIP Code are required to map data registries.")

    st.markdown("---")
    st.markdown("### 🗺️ Registry 1: County Parcel & GIS API Gateway")
    
    # Evaluate calculations strictly out of the locked session state variables
    if st.session_state.search_executed:
        clean_street_key = st.session_state.active_street.lower()
        
        if clean_street_key in MOCK_COUNTY_REGISTRY:
            county_data = MOCK_COUNTY_REGISTRY[clean_street_key]
            st.success(f"🎯 **Official Parcel Identified:** `{
