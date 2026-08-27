import streamlit as st
import pandas as pd
from utils.audit_log import read_decision_log

st.set_page_config(page_title="Risk Dashboard", page_icon="🛡️", layout="wide")
st.title("🛡️ Ops / Risk Dashboard")

st.markdown("""
Internal review tool for underwriters — shows every advance decision made
by the app, with high-risk and declined applications flagged for review.
This is the audit trail described in Phase 5 of the workflow.
""")

log_df = read_decision_log()

if log_df.empty:
    st.info("No decisions logged yet. Generate an offer on the Advance Calculator page first.")
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", len(log_df))
    col2.metric("Approved", int((log_df['eligible'] == True).sum()))
    col3.metric("Declined", int((log_df['eligible'] == False).sum()))
    high_risk_count = int((log_df['risk_tier'] == 'High').sum())
    col4.metric("High Risk", high_risk_count)

    st.subheader("Flagged for Review")
    flagged = log_df[(log_df['risk_tier'] == 'High') | (log_df['eligible'] == False)]
    if flagged.empty:
        st.success("No applications currently flagged.")
    else:
        st.dataframe(flagged, use_container_width=True)

    st.subheader("Full Decision Log")
    st.dataframe(log_df, use_container_width=True)

    st.download_button(
        "Download full audit log as CSV",
        data=log_df.to_csv(index=False),
        file_name="decision_log.csv",
        mime="text/csv",
    )
