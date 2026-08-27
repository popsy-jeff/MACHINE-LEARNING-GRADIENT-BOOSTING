import streamlit as st
import pandas as pd
import plotly.express as px
from utils.audit_log import read_decision_log
from utils.style import inject_css, hero, section_tag, metric_card, plotly_chart, COLORS

st.set_page_config(page_title="Risk Dashboard", page_icon="🛡️", layout="wide")
inject_css()
hero(
    "risk",
    "Ops / Risk Dashboard",
    "Internal review tool for underwriters — every advance decision made by the app, "
    "with high-risk and declined applications flagged for review.",
)

log_df = read_decision_log()

if log_df.empty:
    st.info("No decisions logged yet. Generate an offer on the Advance Calculator page first.")
else:
    section_tag("Overview", "gauge")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card("layers", "Total applications", str(len(log_df)))
    with col2:
        metric_card("check", "Approved", str(int((log_df['eligible'] == True).sum())), color=COLORS["low"])
    with col3:
        metric_card("warn", "Declined", str(int((log_df['eligible'] == False).sum())), color=COLORS["high"])
    with col4:
        metric_card("risk", "High risk", str(int((log_df['risk_tier'] == 'High').sum())), color=COLORS["medium"])

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("##### Risk tier breakdown")
        tier_counts = log_df['risk_tier'].value_counts().reset_index()
        tier_counts.columns = ['risk_tier', 'count']
        tier_color_map = {"Low": COLORS["low"], "Medium": COLORS["medium"], "High": COLORS["high"], "N/A": COLORS["muted"]}
        fig_donut = px.pie(
            tier_counts, names="risk_tier", values="count", hole=0.6,
            color="risk_tier", color_discrete_map=tier_color_map,
        )
        fig_donut.update_traces(textfont_color="#94A3B8", marker=dict(line=dict(color="rgba(0,0,0,0)", width=0)))
        plotly_chart(fig_donut)

    with chart_col2:
        st.markdown("##### Approved vs. declined")
        decision_counts = log_df['eligible'].map({True: "Approved", False: "Declined"}).value_counts().reset_index()
        decision_counts.columns = ['decision', 'count']
        fig_bar = px.bar(
            decision_counts, x="decision", y="count",
            color="decision",
            color_discrete_map={"Approved": COLORS["low"], "Declined": COLORS["high"]},
        )
        fig_bar.update_layout(showlegend=False, xaxis_title="", yaxis_title="Applications")
        plotly_chart(fig_bar)

    section_tag("Flagged for review", "warn")
    flagged = log_df[(log_df['risk_tier'] == 'High') | (log_df['eligible'] == False)]
    if flagged.empty:
        st.success("No applications currently flagged.")
    else:
        st.dataframe(flagged, use_container_width=True)

    section_tag("Full decision log", "layers")
    st.dataframe(log_df, use_container_width=True)

    st.download_button(
        "Download full audit log as CSV",
        data=log_df.to_csv(index=False),
        file_name="decision_log.csv",
        mime="text/csv",
    )
