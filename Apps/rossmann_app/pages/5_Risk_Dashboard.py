import streamlit as st
import pandas as pd
from utils.audit_log import read_decision_log
from utils.theme import (
    apply_theme, sidebar_brand, sidebar_mode_lock, kpi_card, glow_pill_html,
    donut_chart, section_divider,
)

st.set_page_config(page_title="Risk Dashboard", page_icon="🛡️", layout="wide")
apply_theme()
sidebar_brand()
sidebar_mode_lock()
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
    approved_count = int((log_df['eligible'] == True).sum())
    declined_count = int((log_df['eligible'] == False).sum())
    high_risk_count = int((log_df['risk_tier'] == 'High').sum())

    kcol, dcol = st.columns([2, 1])
    with kcol:
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            kpi_card("Total Applications", str(len(log_df)), signal="green")
        with c2:
            kpi_card("Approved", str(approved_count), signal="green")
        with c3:
            kpi_card("Declined", str(declined_count), signal="red")
        with c4:
            kpi_card("High Risk", str(high_risk_count), signal="red" if high_risk_count else "green")
    with dcol:
        tier_counts = log_df['risk_tier'].value_counts()
        st.plotly_chart(
            donut_chart(tier_counts.index.tolist(), tier_counts.values.tolist(), title="Risk tier mix"),
            width='stretch',
        )

    section_divider()
    st.subheader("Flagged for Review")
    flagged = log_df[(log_df['risk_tier'] == 'High') | (log_df['eligible'] == False)]
    if flagged.empty:
        st.markdown(glow_pill_html("No applications currently flagged", signal="green"), unsafe_allow_html=True)
    else:
        st.dataframe(flagged, width='stretch')

    section_divider()
    st.subheader("Full Decision Log")
    display_df = log_df.copy()
    display_df['risk_tier'] = display_df['risk_tier'].apply(
        lambda t: {"Low": "🟢 Low", "Medium": "🟡 Medium", "High": "🔴 High"}.get(t, t)
    )
    display_df['eligible'] = display_df['eligible'].apply(lambda e: "🟢 Approved" if e else "🔴 Declined")
    st.dataframe(display_df, width='stretch')

    st.download_button(
        "Download full audit log as CSV",
        data=log_df.to_csv(index=False),
        file_name="decision_log.csv",
        mime="text/csv",
    )
