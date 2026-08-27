import streamlit as st
from datetime import date
from utils.model_utils import load_model, predict_sales
from utils.feature_pipeline import build_features, load_feature_cols

st.set_page_config(page_title="Single Prediction", page_icon="🔮")
st.title("🔮 Single Store Sales Prediction")

model, is_demo = load_model()
feature_cols = load_feature_cols()

with st.form("single_prediction_form"):
    col1, col2 = st.columns(2)

    with col1:
        store_id = st.number_input("Store ID", min_value=1, value=1, step=1)
        forecast_date = st.date_input("Forecast date", value=date.today())
        is_open = st.selectbox("Store open that day?", [1, 0], format_func=lambda x: "Open" if x == 1 else "Closed")
        promo = st.selectbox("Running a promo that day?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        school_holiday = st.selectbox("School holiday?", [0, 1], format_func=lambda x: "No" if x == 0 else "Yes")
        state_holiday = st.selectbox("State holiday", ["0", "a", "b", "c"], help="0 = none, a/b/c = holiday types")

    with col2:
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

    st.metric("Predicted Sales", f"${prediction:,.2f}")

    if is_demo:
        st.caption("⚠️ This prediction is from the demo model, not your real trained model.")

    with st.expander("See the exact features sent to the model"):
        st.dataframe(features)
