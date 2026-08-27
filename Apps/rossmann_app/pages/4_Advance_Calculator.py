import streamlit as st
from datetime import date, timedelta
import pandas as pd
from utils.model_utils import load_model, predict_sales, MODEL_VERSION
from utils.feature_pipeline import build_features, load_feature_cols
from utils.business_logic import build_advance_offer
from utils.audit_log import log_decision
from utils.theme import (
    apply_theme, sidebar_brand, sidebar_mode_lock, kpi_card, glow_pill,
    risk_signal, gauge_chart, line_area_chart, section_divider,
)

st.set_page_config(page_title="Advance Calculator", page_icon="💰", layout="wide")
apply_theme()
sidebar_brand()
sidebar_mode_lock()
st.title("💰 Revenue-Based Financing — Advance Calculator")

st.markdown("""
Aggregates a 90-day sales forecast for a store, applies a conservative
adjustment, runs eligibility checks, and calculates a merchant cash
advance offer — following Phase 3 of the workflow.
""")

model, is_demo = load_model()
feature_cols = load_feature_cols()

with st.form("advance_form"):
    st.subheader("Store Details")
    col1, col2 = st.columns(2)

    with col1:
        store_id = st.number_input("Store ID", min_value=1, value=1, step=1)
        start_date = st.date_input("Forecast start date", value=date.today())
        store_type = st.selectbox("Store type", ["a", "b", "c", "d"])
        assortment = st.selectbox("Assortment level", ["a", "b", "c"])
        competition_distance = st.number_input("Competition distance (meters)", min_value=0.0, value=500.0)

    with col2:
        promo = st.selectbox("Promo running during window?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        promo2 = st.selectbox("Enrolled in Promo2?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        history_days = st.number_input("Days of sales history available", min_value=0, value=365, step=30)
        trend_pct_90d = st.slider("Sales trend over last 90 days (%)", -50, 50, 0) / 100
        is_closing_flagged = st.checkbox("Store flagged as closing?", value=False)

    submitted = st.form_submit_button("Generate Advance Offer")

if submitted:
    with st.spinner("Forecasting next 90 days..."):
        daily_predictions = []
        for i in range(90):
            forecast_date = start_date + timedelta(days=i)
            features = build_features(
                store_id=store_id,
                forecast_date=forecast_date,
                promo=promo,
                promo2=promo2,
                school_holiday=0,
                state_holiday="0",
                store_type=store_type,
                assortment=assortment,
                competition_distance=competition_distance,
                feature_cols=feature_cols,
            )
            # Sundays (day_of_week == 7) treated as closed by default, adjust as needed
            is_open = 0 if forecast_date.isoweekday() == 7 else 1
            pred = predict_sales(model, features, is_open=is_open)
            daily_predictions.append(pred)

    offer = build_advance_offer(
        daily_predictions=daily_predictions,
        history_days=history_days,
        trend_pct_90d=trend_pct_90d,
        is_closing_flagged=is_closing_flagged,
        competition_distance=competition_distance,
        store_type=store_type,
    )

    log_decision(store_id, MODEL_VERSION, offer)

    section_divider()
    st.subheader("Results")

    if not offer.eligibility.eligible:
        glow_pill("Not eligible for an advance", signal="red")
        for reason in offer.eligibility.reasons:
            st.write(f"- {reason}")
    else:
        glow_pill("Eligible", signal="green")
        st.write("")
        col1, col2, col3 = st.columns(3)
        with col1:
            kpi_card("90-Day Projected Sales", f"${offer.projected_90d_sales:,.0f}", signal="green")
        with col2:
            kpi_card("Safe Estimate (post-haircut)", f"${offer.safe_estimate:,.0f}", signal="yellow")
        with col3:
            kpi_card("Risk Tier", offer.risk_tier, signal=risk_signal(offer.risk_tier))

        st.write("")
        col4, col5, col6 = st.columns([1, 1, 1])
        with col4:
            kpi_card("Max Advance Offer", f"${offer.max_advance:,.0f}", signal="green")
        with col5:
            kpi_card("Daily Holdback %", f"{offer.daily_holdback_pct:.1%}", signal="yellow")
        with col6:
            st.plotly_chart(
                gauge_chart(
                    {"Low": 20, "Medium": 55, "High": 90}.get(offer.risk_tier, 55),
                    0, 100, "Risk Score", good_is_low=True,
                ),
                width='stretch',
            )

    with st.expander("See daily forecast used for this calculation", expanded=True):
        chart_df = pd.DataFrame({
            "Date": [start_date + timedelta(days=i) for i in range(90)],
            "Predicted Sales": daily_predictions,
        })
        st.plotly_chart(
            line_area_chart(chart_df, "Date", "Predicted Sales", title="90-day sales forecast"),
            width='stretch',
        )

    st.caption("This decision has been logged to the audit trail — see Risk Dashboard.")
