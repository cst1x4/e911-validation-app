import streamlit as st
import requests
import urllib.parse
import pandas as pd
import time
import os
from datetime import datetime

# --- MASTER SUITE INITIALIZATION ---
st.set_page_config(page_title="E911 Automated Validation Tool", layout="wide")

st.title("E911 Automated Validation Tool")
st.caption("Demo model is for Colorado only. The full version will cover the CLECs entire footprint.")
st.markdown("---")

# --- DETECTED REGIONAL DATA DIRECTORY LAYER ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "data", "denver_metro_directory.xlsx")

@st.cache_data
def load_county_directory():
    try:
        df = pd.read_excel(EXCEL_PATH, sheet_name="Sheet1", header=None)
        df.columns = ["County_Name", "Endpoint_Url", "Contact_Email", "Token_Label"]
        df["County_Match"] = df["County_Name"].astype(str).str.strip().str.upper()
        return df
    except Exception as e:
        return None

county_directory_df = load_county_directory()

# --- SECURE BACKGROUND STATE VAULT ---
defaults = {
    "gis_is_active": False, "auditor_notes": "", "usps_allowed_municipalities": [],
    "output_county": None, "output_lat": None, "output_lon": None,
    "live_extracted_parcel": "READY", "locked_parcel_value": "", "parcel_label": "IDENTIFIER",
    "usps_primary_city": "", "last_searched_street": "", "last_searched_zip": "",
    "search_timestamp": "", "structural_type": "", "registered_identity": "UNIDENTIFIED",
    "psap_sector_code": "UNASSIGNED", "msag_discrepancy_flag": False,
    "county_contact_email": "", "verification_lifecycle_status": "AWAITING_INGESTION",
    "form_session_id": 0
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- DUAL CONTROL LAYER GRID ---
input_panel, display_panel = st.columns([1, 1], gap="large")

with input_panel:
    st.header("Subscriber Address")
    with st.form(key=f"search_form_{st.session_state.form_session_id}"):
        ui_street_str = st.text_input("Street Address")
        ui_zip_str = st.text_input("Zip Code", max_chars=5)
        ui_name = st.text_input("Subscriber Name (Optional)")
        search_clicked = st.form_submit_button("Begin Search", type="primary", use_container_width=True)

    if search_clicked:
        st.session_state.last_searched_street = ui_street_str.strip().upper()
        st.session_state.last_searched_zip = ui_zip_str.strip()
        # Identity Improvement
        st.session_state.registered_identity = ui_name.strip() if ui_name.strip() else "UNIDENTIFIED"
        
        # USPS Improvement: Capture Accepted Municipalities
        try:
            usps_res = requests.get(f"https://api.zippopotam.us/us/{ui_zip_str.strip()}", timeout=5).json()
            places = usps_res.get("places", [])
            if places:
                st.session_state.usps_primary_city = places[0].get("place name", "").upper()
                st.session_state.usps_allowed_municipalities = [p.get("place name", "").upper() for p in places]
        except:
            st.session_state.usps_primary_city = "COLORADO MUNICIPALITY"
        
        st.session_state.gis_is_active = True
        st.rerun()

with display_panel:
    st.header("Location Specifics")
    if st.session_state.gis_is_active:
        # --- ADDITIONAL SOURCES ---
        st.markdown("### Additional Sources")
        addr_q = urllib.parse.quote(f"{st.session_state.last_searched_street}, CO {st.session_state.last_searched_zip}")
        col1, col2, col3 = st.columns(3)
        col1.link_button("Bing Maps", f"https://www.bing.com/maps?q={addr_q}", use_container_width=True)
        col2.link_button("Zillow", f"https://www.zillow.com/homes/{addr_q}_rb/", use_container_width=True)
        col3.link_button("Homes.com", f"https://www.homes.com/real-estate/{addr_q}/for-sale/", use_container_width=True)

# --- USPS ROUTING REFERENCE ---
st.markdown("---")
st.header("USPS Routing Reference")
if st.session_state.gis_is_active:
    st.markdown(f"**Standardized City:** `{st.session_state.usps_primary_city}`")
    st.markdown(f"**Accepted Municipalities:** `{', '.join(st.session_state.usps_allowed_municipalities)}`")

# --- AUDITOR NOTES ---
st.markdown("---")
st.header("Auditor Notes")
st.session_state.auditor_notes = st.text_area("Verification findings/discrepancies:", value=st.session_state.auditor_notes)

# --- TRANSACTION RECORD ---
# [Note: Insert your existing logging logic here, including the new 'Auditor Notes' in the audit_data dictionary]
