import streamlit as st
import pandas as pd
import plotly.express as px
from utils.audit_log import read_decision_log
from utils.style import inject_css, hero, section_tag, COLORS, PLOTLY_SEQUENCE

st.set_page_config(page_title="Risk Dashboard", page_icon="🛡️", layout="wide")
inject_css()
hero(
    "🛡️ Ops / Risk Dashboard",
    "Internal review tool for underwriters — every advance decision made by the app, "
    "with high-risk and declined applications flagged for review.",
)

log_df = read_decision_log()

if log_df.empty:
    st.info("No decisions logged yet. Generate an offer on the Advance Calculator page first.")
else:
    section_tag("Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Applications", len(log_df))
    col2.metric("Approved", int((log_df['eligible'] == True).sum()))
    col3.metric("Declined", int((log_df['eligible'] == False).sum()))
    high_risk_count = int((log_df['risk_tier'] == 'High').sum())
    col4.metric("High Risk", high_risk_count)

    st.write("")
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("##### Risk tier breakdown")
        tier_counts = log_df['risk_tier'].value_counts().reset_index()
        tier_counts.columns = ['risk_tier', 'count']
        tier_color_map = {"Low": COLORS["low"], "Medium": COLORS["medium"], "High": COLORS["high"], "N/A": COLORS["text_muted"]}
        fig_donut = px.pie(
            tier_counts, names="risk_tier", values="count", hole=0.55,
            color="risk_tier", color_discrete_map=tier_color_map,
        )
        fig_donut.update_layout(height=320, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        st.markdown("##### Approved vs. declined")
        decision_counts = log_df['eligible'].map({True: "Approved", False: "Declined"}).value_counts().reset_index()
        decision_counts.columns = ['decision', 'count']
        fig_bar = px.bar(
            decision_counts, x="decision", y="count",
            color="decision",
            color_discrete_map={"Approved": COLORS["low"], "Declined": COLORS["high"]},
        )
        fig_bar.update_layout(
            height=320, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            showlegend=False, xaxis_title="", yaxis_title="Applications",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    st.write("")
    section_tag("Flagged for review")
    flagged = log_df[(log_df['risk_tier'] == 'High') | (log_df['eligible'] == False)]
    if flagged.empty:
        st.success("No applications currently flagged.")
    else:
        st.dataframe(flagged, use_container_width=True)

    st.write("")
    section_tag("Full decision log")
    st.dataframe(log_df, use_container_width=True)

    st.download_button(
        "Download full audit log as CSV",
        data=log_df.to_csv(index=False),
        file_name="decision_log.csv",
        mime="text/csv",
    )
