import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from utils.model_utils import load_model, predict_sales
from utils.feature_pipeline import build_features, load_feature_cols
from utils.style import inject_css, hero, section_tag, COLORS, PLOTLY_SEQUENCE

st.set_page_config(page_title="Single Prediction", page_icon="🔮", layout="wide")
inject_css()
hero("🔮 Single Store Sales Prediction", "Fill in one store's details for one day and get an instant forecast.")

model, is_demo = load_model()
feature_cols = load_feature_cols()

if "single_pred_history" not in st.session_state:
    st.session_state.single_pred_history = []

section_tag("Inputs")
with st.form("single_prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🏬 Store & Date**")
        store_id = st.number_input("Store ID", min_value=1, value=1, step=1)
        forecast_date = st.date_input("Forecast date", value=date.today())
        is_open = st.selectbox("Store open that day?", [1, 0], format_func=lambda x: "Open" if x == 1 else "Closed")
        promo = st.selectbox("Running a promo that day?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        school_holiday = st.selectbox("School holiday?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        state_holiday = st.selectbox("State holiday", ["0", "a", "b", "c"], help="0 = none, a/b/c = holiday types")

    with col2:
        st.markdown("**🧾 Store Profile**")
        store_type = st.selectbox("Store type", ["a", "b", "c", "d"])
        assortment = st.selectbox("Assortment level", ["a", "b", "c"])
        competition_distance = st.number_input("Competition distance (meters)", min_value=0.0, value=500.0)
        promo2 = st.selectbox("Enrolled in Promo2 (ongoing promo)?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")

    submitted = st.form_submit_button("Predict Sales")

if submitted:
    features = build_features(
        store_id=store_id,
        forecast_date=forecast_date,
        promo=promo,
        promo2=promo2,
        school_holiday=school_holiday,
        state_holiday=state_holiday,
        store_type=store_type,
        assortment=assortment,
        competition_distance=competition_distance,
        feature_cols=feature_cols,
    )

    prediction = predict_sales(model, features, is_open=is_open)

    st.session_state.single_pred_history.append(
        {"Store": store_id, "Date": str(forecast_date), "Predicted Sales": prediction}
    )

    st.write("")
    section_tag("Result")
    res_col1, res_col2, res_col3 = st.columns(3)
    res_col1.metric("Predicted Sales", f"${prediction:,.2f}")
    res_col2.metric("Store", f"#{store_id}")
    res_col3.metric("Day of Week", forecast_date.strftime("%A"))

    if is_demo:
        st.caption("⚠️ This prediction is from the demo model, not your real trained model.")

    with st.expander("See the exact features sent to the model"):
        st.dataframe(features, use_container_width=True)

if len(st.session_state.single_pred_history) > 1:
    st.write("")
    section_tag("This session")
    st.markdown("##### Predictions you've made so far")
    hist_df = pd.DataFrame(st.session_state.single_pred_history)

    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=[f"#{r['Store']} · {r['Date']}" for r in st.session_state.single_pred_history],
            y=hist_df["Predicted Sales"],
            marker_color=COLORS["primary"],
        )
    )
    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis_title="Predicted Sales ($)",
        colorway=PLOTLY_SEQUENCE,
    )
    st.plotly_chart(fig, use_container_width=True)

    if st.button("Clear session history"):
        st.session_state.single_pred_history = []
        st.rerun()
