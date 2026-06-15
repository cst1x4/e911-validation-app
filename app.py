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

# --- INITIALIZE PERSISTENT MEMORY SLOTS ---
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
    
    # Text inputs binded to parameters
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
            st.success(f"🎯 **Official Parcel Identified:** `{county_data['parcel']}`")
            st.caption(f"Secure handshake verified via **[{county_data['county']}]({county_data['url']})**")
            parcel_found = True
            assigned_county = county_data['county']
        else:
            st.error("❌ **Stage 1 Exception: Parcel Records Unavailable**")
            st.markdown(
                f"👉 *System Status Note:* The address `{st.session_state.active_street.upper()}` cannot be matched to a local county GIS plot. "
                "In a live deployment, this creates an active routing hazard for emergency services."
            )
            parcel_found = False
            
            # Automated Exception Routing Email Generator
            st.markdown("#### 📧 Automated Discrepancy Routing Queue")
            email_recipient = "gis_data_integrity@co.municipal.gov"
            email_subject = f"E911 Database Discrepancy: Missing Parcel Data for {st.session_state.active_street.upper()}"
            email_body = (
                f"Hello GIS Department,\n\n"
                f"Our E911 Location Integrity engine flagged an unmapped address footprint:\n"
                f"Address: {st.session_state.active_street.upper()}, Suite: {st.session_state.active_unit if st.session_state.active_unit else 'N/A'}, ZIP: {st.session_state.active_zip}\n\n"
                f"Please verify the official parcel assignment and boundary vectors so we can update our emergency routing switches.\n\n"
                f"System Log Signature: CST-E911-AUTO-ERR"
            )
            
            mailto_link = f"mailto:{email_recipient}?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
            st.link_button("📥 Open Discrepancy Email Ticket to County", mailto_link, use_container_width=True)
    else:
        st.info("Awaiting manual input initialization...")

with diagnostic_col:
    st.header("📯 Registry 2: USPS AMS Standardization")
    
    # Process Registry 2 strictly out of the locked session state variables
    if st.session_state.search_executed:
        active_zip_str = st.session_state.active_zip
        
        if active_zip_str in MOCK_USPS_ZIP_MATRIX:
            usps_data = MOCK_USPS_ZIP_MATRIX[active_zip_str]
            
            # Complete Postal Manual Alignment Display
            with st.container(border=True):
                st.markdown("### 📬 Output Standardized Data Payload")
                st.markdown(f"**USPS Standardized Line 1:** `{usps_data['standardized_street']}`")
                if st.session_state.active_unit:
                    st.markdown(f"**USPS Standardized Line 2:** `{st.session_state.active_unit.upper()}`")
                st.markdown(f"**Target Mail Routing City:** `{usps_data['primary_city']}`")
                st.markdown(f"**ZIP + 4 Delivery Indicator:** `{active_zip_str}-4312`")
            
            # Display Allowed Municipalities from the USPS City State Product Matrix
            st.markdown("### 🏢 Authorized Multi-Municipality Route Index")
            st.caption("The following city names are legally recognized by the USPS AMS database for this specific ZIP code:")
            
            df_municipalities = pd.DataFrame({
                "Authorized Municipal Names": usps_data["allowed_municipalities"],
                "Routing Status": ["PRIMARY" if m == usps_data["primary_city"] else "ACCEPTABLE SECTOR" for m in usps_data["allowed_municipalities"]]
            })
            st.table(df_municipalities)
            
            # Automated Cross-Reference Verification Step
            if 'parcel_found' in locals() and parcel_found:
                st.markdown("### 🏁 Cross-Reference Logic State")
                if "Arapahoe" in assigned_county and usps_data['primary_city'] == "DENVER":
                    st.error("🚨 **CRITICAL COUNTY BOUNDARY MISMATCH DETECTED**")
                    st.caption("🚨 *Impact Analyst Warning:* USPS billing lists say 'Denver', but the local GIS database places this location inside Arapahoe County limits. Standard emergency routing vectors will fail.")
                else:
                    st.success("✅ **Cross-Reference Passed:** County records align with USPS postal delivery sectors.")
        else:
            st.warning(f"⚠️ **USPS System Exception:** The ZIP code `{active_zip_str}` is outside the active demonstration index. Try testing `80202`, `80222`, or `80111` to show a successful registry mapping.")
    else:
        st.caption("Awaiting live data stream inputs to map compliance metrics...")
