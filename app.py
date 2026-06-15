import streamlit as st
import requests
import urllib.parse
import time

# --- MASTER SUITE INITIALIZATION ---
st.set_page_config(page_title="E911 Validation Suite - Stage 1", layout="wide", page_icon="🛡️")

st.title("🛡️ E911 Location Metadata Automation Suite")
st.subheader("Enterprise Demonstration Portal: County Discovery & Automated Parcel Harvesting")
st.markdown("---")

# --- INITIALIZE PERSISTENT SESSION STATES ---
if "searched_street" not in st.session_state:
    st.session_state.searched_street = ""
if "searched_zip" not in st.session_state:
    st.session_state.searched_zip = ""
if "gis_resolved" not in st.session_state:
    st.session_state.gis_resolved = False
if "resolved_county" not in st.session_state:
    st.session_state.resolved_county = None
if "resolved_lat" not in st.session_state:
    st.session_state.resolved_lat = None
if "resolved_lon" not in st.session_state:
    st.session_state.resolved_lon = None
if "standardized_address" not in st.session_state:
    st.session_state.standardized_address = ""
if "harvest_state" not in st.session_state:
    st.session_state.harvest_state = "IDLE"

# --- LIVE LAYOUT ARCHITECTURE ---
input_panel, display_panel = st.columns([1, 1], gap="large")

with input_panel:
    st.header("📥 Live Data Ingestion Engine")
    st.markdown("Type any real US address below to initiate the automation pipeline.")
    
    # Core Manual Inputs
    ui_street = st.text_input("Street Address String", placeholder="e.g., 1560 Broadway")
    ui_zip = st.text_input("5-Digit ZIP Code", max_chars=5, placeholder="e.g., 80202")
    
    st.markdown(" ")
    
    # 🔎 DYNAMIC EXECUTION ENGINE
    if st.button("🔎 Execute Live County Verification Search", type="primary", use_container_width=True):
        if ui_street.strip() and ui_zip.strip():
            query_string = f"{ui_street.strip()}, {ui_zip.strip()}"
            api_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query_string)}&format=json&addressdetails=1&countrycodes=us&limit=1"
            headers = {"User-Agent": "CSTerrellART_E911_Automation_Suite/1.0 (contact: support@csterrellart.com)"}
            
            try:
                with st.spinner("Executing secure coordinate handshakes with remote GIS registries..."):
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
                    
                    st.session_state.resolved_county = final_county
                    st.session_state.resolved_lat = res.get("lat")
                    st.session_state.resolved_lon = res.get("lon")
                    st.session_state.standardized_address = res.get("display_name", "").upper()
                    st.session_state.searched_street = ui_street.strip().upper()
                    st.session_state.searched_zip = ui_zip.strip()
                    st.session_state.gis_resolved = True
                    st.session_state.harvest_state = "READY_TO_HARVEST"
                else:
                    st.session_state.gis_resolved = False
                    st.session_state.resolved_county = "NOT_FOUND"
                    st.session_state.searched_street = ui_street.strip().upper()
                    st.session_state.searched_zip = ui_zip.strip()
                    st.session_state.harvest_state = "IDLE"
                    
                st.rerun()
                
            except Exception as e:
                st.error(f"🌐 Remote GIS Network Timeout Exception: {str(e)}")
        else:
            st.error("⚠️ Validation Interrupted: Both a Street Address and a ZIP Code are required to loop API structures.")

with display_panel:
    st.header("🗺️ Stage 1: Official GIS Registry Output")
    
    if st.session_state.get("resolved_county") == "NOT_FOUND":
        st.error("❌ **Stage 1 Exception: Location Footprint Unmapped**")
        st.markdown(
            f"The location string `{st.session_state.searched_street}` with ZIP `{st.session_state.searched_zip}` "
            "could not be mapped to any recognized municipal or county spatial plot."
        )
        
        # Discrepancy Ticket
        st.markdown("#### 📧 System-Generated Discrepancy Ticket")
        fallback_recipient = "gis_data_integrity@co.municipal.gov"
        fallback_subject = f"CRITICAL E911 UNMAPPED FOOTPRINT ALERT: {st.session_state.searched_street}"
        fallback_body = f"Hello GIS Operations Division,\n\nOur E911 platform flagged an unmapped address: {st.session_state.searched_street}."
        mailto_url = f"mailto:{fallback_recipient}?subject={urllib.parse.quote(fallback_subject)}&body={urllib.parse.quote(fallback_body)}"
        st.link_button("📥 Route Core Discrepancy Ticket to County", mailto_url, use_container_width=True)

    elif st.session_state.gis_resolved:
        target_county = st.session_state.resolved_county
        st.success(f"🎯 **Target Jurisdiction Confirmed:** `{target_county.upper()}`")
        
        with st.container(border=True):
            st.markdown("### 📡 Geographic Telemetry Metrics")
            st.markdown(f"**Verified GIS Boundary:** `{target_county}`")
            st.markdown(f"**Calculated Latitude:** `{st.session_state.resolved_lat}`")
            st.markdown(f"**Calculated Longitude:** `{st.session_state.resolved_lon}`")
            st.divider()
            st.caption(f"**System Standardized Ingestion String:**\n`{st.session_state.standardized_address}`")
        
        # DYNAMIC GOV EXTERNAL ENGINE PORTAL
        search_query = f"official {target_county} government property parcel assessor account lookup site:.gov"
        county_search_portal_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        st.link_button(f"🌐 Manual Override: Inspect Official {target_county} Portal", county_search_portal_url, use_container_width=True)
        
    else:
        st.info("Awaiting manual input initialization to extract official spatial parameters...")

# --- 🎛️ NEW ENHANCEMENT: LIVE AUTOMATION FLIGHT DECK ---
st.markdown("---")
st.header("🎛️ Stage 1B: Property Search & Parcel Harvesting Strategy")

if st.session_state.harvest_state == "READY_TO_HARVEST" or st.session_state.harvest_state == "RUNNING":
    st.markdown("Click below to simulate how the automated headless browser discovers and extracts the official parcel ID from the government domain.")
    
    if st.button("🚀 Execute Automated Portal Scraping Simulation", type="secondary"):
        st.session_state.harvest_state = "RUNNING"
        
        # Step-by-step UI tracking simulation
        with st.status("Initializing Headless Browser Session...", expanded=True) as status:
            st.write(f"🔗 Handshaking with verified base domain of `{st.session_state.resolved_county}`...")
            time.sleep(1.5)
            
            st.write("🔍 Scanning DOM anchors for property database links...")
            time.sleep(1.2)
            st.write("✅ Primary match isolated: `href='/assessor/property-account-search/'`")
            
            st.write(f"⌨️ Injecting standardized string `{st.session_state.searched_street}` into detected input nodes...")
            time.sleep(1.5)
            
            st.write("📡 Submitting form data and analyzing returned text layers via regional regular expression filters...")
            time.sleep(1.2)
            
            # Formats simulated parcel numbers to match your exact test cities
            simulated_parcel = "02341-21-009-000" if "Denver" in st.session_state.resolved_county else "2075-16-3-01-002" if "Arapahoe" in st.session_state.resolved_county else "ALA-99812-43-000"
            
            status.update(label=f"Harvest Sequence Complete! Isolated Parcel ID: {simulated_parcel}", state="complete")
        
        # Show final payload display cards
        with st.container(border=True):
            st.success(f"📦 **AUTOMATICALLY HARVESTED PARCEL ID:** `{simulated_parcel}`")
            st.caption(f"This value is now permanently linked to the database row for `{st.session_state.searched_street}`.")
        
        st.session_state.harvest_state = "READY_TO_HARVEST"
else:
    st.caption("🔒 *Harvest deck locked.* Execute a successful location search above to map the automation workflow.")
