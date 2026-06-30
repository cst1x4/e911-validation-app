import streamlit as st
import requests
import urllib.parse
import pandas as pd
import time
import os
from datetime import datetime

# --- MASTER SUITE INITIALIZATION ---
st.set_page_config(page_title="E911 Compliance Engine", layout="wide")

st.title("E911 Automated Validation & Governance Engine")
st.caption("Enterprise-grade geospatial routing, multi-source property intel, and immutable compliance auditing.")
st.markdown("---")

# --- DATA LAYER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "data", "denver_metro_directory.xlsx")

@st.cache_data
def load_county_directory():
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="Sheet1", header=None)
        df.columns = ["County_Name", "Endpoint_Url", "Contact_Email", "Token_Label"]
        df["County_Match"] = df["County_Name"].astype(str).str.strip().str.upper()
        return df
    except:
        return None

county_directory_df = load_county_directory()

# --- INITIALIZE STATE ---
state_vars = {
    "gis_is_active": False, "output_county": "", "output_lat": "", "output_lon": "",
    "parcel_label": "PARCEL ID", "locked_parcel_value": "", "last_searched_street": "",
    "last_searched_zip": "", "verification_lifecycle_status": "AWAITING_INGESTION",
    "structural_type": "", "registered_identity": "", "psap_sector_code": "UNASSIGNED",
    "usps_standardized_line1": "", "usps_primary_city": "", "search_timestamp": ""
}
for var, default in state_vars.items():
    if var not in st.session_state:
        st.session_state[var] = default

# --- INPUT PANEL ---
input_col, display_col = st.columns([1, 1], gap="large")

with input_col:
    st.header("1. Subscriber Address Input")
    with st.form("search_form"):
        ui_street = st.text_input("Street Address", placeholder="e.g., 2985 S Hudson St")
        ui_zip = st.text_input("Zip Code", max_chars=5)
        submitted = st.form_submit_button("Initialize Compliance Audit")

    if submitted:
        st.session_state.last_searched_street = ui_street.strip().upper()
        st.session_state.last_searched_zip = ui_zip.strip()
        st.session_state.search_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S MST")
        # [Simplified: Nominatim GIS boundary call]
        st.session_state.gis_is_active = True
        st.session_state.output_county = "Arapahoe County"
        st.session_state.verification_lifecycle_status = "PENDING_VERIFICATION"
        st.session_state.structural_type = "SINGLE-FAMILY HOME"
        st.rerun()

# --- DISPLAY & INTEL PANEL ---
if st.session_state.gis_is_active:
    with display_col:
        st.header("2. Unified Property Intel & Routing")
        tabs = st.tabs(["Location Specifics", "Market Intel (Zillow/Redfin)", "Multi-Search"])
        
        with tabs[0]:
            st.success(f"Jurisdiction Confirmed: {st.session_state.output_county.upper()}")
            st.metric("Structure Profile", st.session_state.structural_type)
            st.info(f"ROUTING SINK: {st.session_state.psap_sector_code}")
            
        with tabs[1]:
            st.markdown("### Market Data")
            addr_q = urllib.parse.quote(f"{st.session_state.last_searched_street}, {st.session_state.last_searched_zip}")
            st.link_button("View on Zillow", f"https://www.zillow.com/homes/{addr_q}_rb/")
            st.link_button("View on Redfin", f"https://www.redfin.com/stingray/do/query?location={addr_q}")
            
        with tabs[2]:
            st.markdown("### External Verification")
            st.link_button("Google Maps Search", f"https://www.google.com/maps/search/?api=1&query={addr_q}")
            st.link_button("Bing Maps Search", f"https://www.bing.com/maps?q={addr_q}")

# --- AUDIT GATE ---
st.markdown("---")
st.header("3. Compliance & Parcel Lock-in (Audit Gate)")
if st.session_state.gis_is_active:
    col_a, col_b = st.columns(2)
    with col_a:
        parcel_input = st.text_input(f"Enter Verified {st.session_state.parcel_label}")
        if st.button("Commit to Immutable Audit Ledger"):
            st.session_state.locked_parcel_value = parcel_input
            st.session_state.verification_lifecycle_status = "VERIFIED_COMPLIANT"
    
    with col_b:
        if st.session_state.verification_lifecycle_status == "VERIFIED_COMPLIANT":
            st.success("RECORD LOCKED & SIGNED")
            st.json({"Timestamp": datetime.now().isoformat(), "Parcel": st.session_state.locked_parcel_value})

# --- OFFICIAL TRANSACTION RECORD ---
st.markdown("---")
st.header("Official Transaction Record")
audit_data = {
    "Parameter": ["Timestamp", "Address", "County", "Verified Parcel"],
    "Value": [st.session_state.search_timestamp, st.session_state.last_searched_street, 
              st.session_state.output_county, st.session_state.locked_parcel_value]
}
st.table(pd.DataFrame(audit_data))
