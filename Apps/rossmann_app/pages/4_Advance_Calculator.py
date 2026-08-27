import streamlit as st
from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
from utils.model_utils import load_model, predict_sales, MODEL_VERSION
from utils.feature_pipeline import build_features, load_feature_cols
from utils.business_logic import build_advance_offer
from utils.audit_log import log_decision
from utils.style import inject_css, hero, section_tag, metric_card, badge, risk_color, plotly_chart, COLORS

st.set_page_config(page_title="Advance Calculator", page_icon="💰", layout="wide")
inject_css()
hero(
    "advance",
    "Revenue-Based Financing — Advance Calculator",
    "Aggregates a 90-day sales forecast for a store, applies a conservative adjustment, "
    "runs eligibility checks, and calculates a merchant cash advance offer.",
)

model, is_demo = load_model()
feature_cols = load_feature_cols()

section_tag("Inputs", "store")
with st.form("advance_form"):
    st.markdown("**Store Details**")
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

    section_tag("Results", "bolt")

    if not offer.eligibility.eligible:
        badge("Not eligible", COLORS["high"], "warn")
        for reason in offer.eligibility.reasons:
            st.write(f"- {reason}")
    else:
        badge("Eligible", COLORS["low"], "check")
        st.write("")

        col1, col2, col3 = st.columns(3)
        with col1:
            metric_card("trend-up", "90-day projected sales", f"${offer.projected_90d_sales:,.0f}")
        with col2:
            metric_card("gauge", "Safe estimate", f"${offer.safe_estimate:,.0f}", "post-haircut")
        with col3:
            metric_card("risk", "Risk tier", offer.risk_tier, color=risk_color(offer.risk_tier))

        col4, col5 = st.columns(2)
        with col4:
            metric_card("coins", "Max advance offer", f"${offer.max_advance:,.0f}", color=COLORS["primary"])
        with col5:
            metric_card("percent", "Daily holdback", f"{offer.daily_holdback_pct:.1%}")

        st.progress(min(offer.daily_holdback_pct, 1.0), text=f"Daily holdback: {offer.daily_holdback_pct:.1%} of daily revenue")

    st.markdown("##### 90-day forecast used for this calculation")
    forecast_dates = [start_date + timedelta(days=i) for i in range(90)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=forecast_dates, y=daily_predictions,
        mode="lines", fill="tozeroy",
        line=dict(color=COLORS["primary"], width=2, shape="spline"),
        fillcolor=COLORS["primary"] + "26",
        name="Predicted Sales",
        hovertemplate="%{x|%b %d}<br>$%{y:,.0f}<extra></extra>",
    ))
    fig.update_layout(yaxis_title="Predicted Sales ($)", xaxis_title="Date")
    plotly_chart(fig, height=340)

    st.caption("This decision has been logged to the audit trail — see Risk Dashboard.")
