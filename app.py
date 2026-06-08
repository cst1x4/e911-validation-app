import streamlit as st
import pandas as pd
from data.mock_data import MOCK_SUBSCRIBER_RECORDS, MOCK_MUNICIPAL_GIS
from core.validator import execute_7_stage_validation

st.set_page_config(page_title="E911 Automation Sandbox", layout="wide")

st.title("🛡️ E911 Location Metadata Automation Sandbox")
st.subheader("7-Stage Deterministic Integrity & QA Validation Engine")
st.markdown("---")

left_col, right_col = st.columns([1, 2])

with left_col:
    st.header("📥 Ingested Mismatched Billing Records")
    df_records = pd.DataFrame(MOCK_SUBSCRIBER_RECORDS)
    selected_tn = st.selectbox("Active Telephone Number (TN) Queue", df_records["tn"])

    record = next(r for r in MOCK_SUBSCRIBER_RECORDS if r["tn"] == selected_tn)

    with st.container(border=True):
        st.write(f"**Raw Ingested Phone Line:** {record['tn']}")
        st.write(f"**Street Address String:** {record['street_address']}")
        st.write(f"**Input City/State:** {record['city']}, {record['state']}")
        st.write(f"**Unit/Apt Value:** '{record['unit'] if record['unit'] else 'NULL'}'")
        st.caption(f"Metadata Diagnostic Note: {record['notes']}")

trace_log = execute_7_stage_validation(record, MOCK_MUNICIPAL_GIS)

with right_col:
    st.header("🎛️ Automation Flight Deck Inspection")

    status = trace_log["validation_status"]
    if status == "VALIDATED_AUTOMATICALLY_CLOSED":
        st.success(f"**CURRENT DISPOSITION:** {status}")
    elif status == "ACTION_REQUIRED_FLAGGED_FOR_MANUAL_OVERRIDE":
        st.warning(f"**CURRENT DISPOSITION:** {status}")
    else:
        st.error(f"**CURRENT DISPOSITION:** {status}")

    st.markdown("### Verification Checklist State Execution:")
    stages = trace_log["stages_completed"]
    errors = trace_log["error_flags_detected"]

    if "STAGE_1_COUNTY_GIS_PARCEL_MATCH" in stages:
        st.markdown("✅ **Stage 1: County GIS API Gateway** — Clean match found in local geographic maps.")
    else:
        st.markdown("❌ **Stage 1: County GIS API Gateway** — Aborted. Address record not recognized in spatial maps.")

    if "STAGE_2_TELEMETRY_COORDINATE_VERIFICATION" in stages:
        st.markdown("✅ **Stage 2: Telemetry Verification** — Spatial vectors and GPS lat/lon strings locked.")

    if "STAGE_3_USPS_POSTAL_STANDARDIZATION" in stages:
        st.markdown("✅ **Stage 3: USPS Postal Manual Alignment** — Address character array standardized.")

    if errors:
        st.markdown("### ⚠️ Active Diagnostic Infrastructure Alerts:")
        for err in errors:
            st.error(f"**System Exception Logged:** {err}")
            if err == "OMISSION_ERROR_MISSING_UNIT_OR_APT":
                st.caption("👉 *Impact Analyst Note:* The underlying GIS footprint contains multiple occupant points. The ingestion record is missing its required sub-address identifier, generating a life-safety deployment hazard.")
            if err == "CRITICAL_COUNTY_BOUNDARY_MISMATCH":
                st.caption("👉 *Impact Analyst Note:* Emergency routing boundaries split precisely along this street. Billing file says Denver, but geographic deployment is in Arapahoe County. Standard routing parameters will fail.")

    st.markdown("### 📦 Engineered Data Payload Extract (JSON Structure)")
    st.json(trace_log)
