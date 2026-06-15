import streamlit as st
import pandas as pd
import urllib.parse

# --- MASTER DEMO INITIALIZATION ---
st.set_page_config(page_title="E911 Enterprise Automation Suite", layout="wide", page_icon="🛡️")

st.title("🛡️ E911 Location Metadata Automation Suite")
st.subheader("Enterprise Demonstration Portal: Multi-Registry Verification Routing")
st.markdown("---")

# Simulated High-Authority Multi-Registry DB for Demo Responses
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

# --- TWO-COLUMN STAKEHOLDER DISPLAY ---
input_col, diagnostic_col = st.columns([1, 1], gap="large")

with input_col:
    st.header("📥 Live Spatial Address Ingestion")
    st.markdown("Test an address to observe how the engine handles localized routing and fallback automation.")
    
    # Live Interactive Text Inputs
    input_street = st.text_input("Street Address String", placeholder="e.g., 1560 Broadway")
    input_zip = st.text_input("5-Digit ZIP Code", max_chars=5, placeholder="e.g., 80202")
    input_unit = st.text_input("Unit / Apt / Suite (Optional)", placeholder="e.g., Apt 402")

    st.markdown("### 🗺️ Stage 1: County Parcel & GIS API Gateway")
    
    clean_street_key = input_street.strip().lower()
    
    if input_street and input_zip:
        # 1. Evaluate County Registry State
        if clean_street_key in MOCK_COUNTY_REGISTRY:
            county_data = MOCK_COUNTY_REGISTRY[clean_street_key]
            st.success(f"🎯 **Official Parcel Identified:** `{county_data['parcel']}`")
            st.caption(f"Verified via verified secure handshake with **[{county_data['county']}]({county_data['url']})**")
            parcel_found = True
            parcel_number = county_data['parcel']
            assigned_county = county_data['county']
        else:
            st.error("❌ **Stage 1 Exception: Parcel Records Unavailable**")
            st.markdown(
                "👉 *System Status Note:* This address cannot be matched to a local county GIS plot. "
                "In a live deployment, this creates an active routing hazard for emergency services."
            )
            parcel_found = False
            
            # Automated Exception Routing Email Generator
            st.markdown("#### 📧 Automated Discrepancy Routing Queue")
            email_recipient = "gis_data_integrity@co.municipal.gov"
            email_subject = f"E911 Database Discrepancy: Missing Parcel Data for {input_street.upper()}"
            email_body = (
                f"Hello GIS Department,\n\n"
                f"Our E911 Location Integrity engine flagged an unmapped address footprint:\n"
                f"Address: {input_street.upper()}, Suite: {input_unit if input_unit else 'N/A'}, ZIP: {input_zip}\n\n"
                f"Please verify the official parcel assignment and boundary vectors so we can update our emergency routing switches.\n\n"
                f"System Log Signature: CST-E911-AUTO-ERR"
            )
            
            # Construct Mailto Link for Enterprise Ease
            mailto_link = f"mailto:{email_recipient}?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
            st.link_button("📥 Review & Send Discrepancy Email to County", mailto_link, use_container_width=True)
    else:
        st.info("💡 Enter a valid Street Address and ZIP code above to trigger the automated 7-Stage Validation loop.")

with diagnostic_col:
    st.header("📯 Stage 2: USPS AMS Standardization")
    
    if input_street and input_zip:
        # 2. Evaluate USPS Registry State
        if input_zip in MOCK_USPS_ZIP_MATRIX:
            usps_data = MOCK_USPS_ZIP_MATRIX[input_zip]
            
            # Complete Postal Manual Alignment Display
            with st.container(border=True):
                st.markdown("### 📬 Output Standardized Data Payload")
                st.markdown(f"**USPS Standardized Line 1:** `{usps_data['standardized_street']}`")
                if input_unit:
                    st.markdown(f"**USPS Standardized Line 2:** `{input_unit.upper()}`")
                st.markdown(f"**Target Mail Routing City:** `{usps_data['primary_city']}`")
                st.markdown(f"**ZIP + 4 Delivery Indicator:** `{input_zip}-4312`")
            
            # Display Allowed Municipalities from the USPS City State Product Matrix
            st.markdown("### 🏢 Authorized Multi-Municipality Route Index")
            st.caption("The following city names are legally recognized by the USPS AMS database for this specific ZIP code:")
            
            df_municipalities = pd.DataFrame({
                "Authorized Municipal Names": usps_data["allowed_municipalities"],
                "Routing Status": ["PRIMARY" if m == usps_data["primary_city"] else "ACCEPTABLE SECTOR" for m in usps_data["allowed_municipalities"]]
            })
            st.table(df_municipalities)
            
            # Automated Cross-Reference Verification Step
            if parcel_found:
                st.markdown("### 🏁 Cross-Reference Logic State")
                if "Arapahoe" in assigned_county and usps_data['primary_city'] == "DENVER":
                    st.error("🚨 **CRITICAL COUNTY BOUNDARY MISMATCH DETECTED**")
                    st.caption("🚨 *Impact Analyst Warning:* USPS billing lists say 'Denver', but the local GIS database places this location inside Arapahoe County limits. Standard emergency routing vectors will fail.")
                else:
                    st.success("✅ **Cross-Reference Passed:** County records align with USPS postal delivery sectors.")
        else:
            st.warning("⚠️ **USPS System Exception:** Entered ZIP code not found in current local mock database index. Try entering `80202`, `80222`, or `80111` for a complete end-to-end sandbox walkthrough.")
    else:
        st.caption("Awaiting live data stream inputs to map compliance metrics...")
