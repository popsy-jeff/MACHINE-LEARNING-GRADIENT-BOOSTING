import streamlit as st
import pandas as pd
from utils.model_utils import load_model, predict_sales_batch
from utils.feature_pipeline import build_features_batch, load_feature_cols, REQUIRED_BATCH_COLUMNS

st.set_page_config(page_title="Batch Prediction", page_icon="📋")
st.title("📋 Batch Sales Prediction")

st.markdown(f"""
Upload a CSV with one row per store/date you want a forecast for.

**Required columns:** `{'`, `'.join(REQUIRED_BATCH_COLUMNS)}`

Optional columns (improves accuracy if provided): `Open`, `CompetitionOpenSinceYear`,
`CompetitionOpenSinceMonth`, `Promo2SinceYear`, `Promo2SinceWeek`
""")

model, is_demo = load_model()
feature_cols = load_feature_cols()

uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

if uploaded_file is not None:
    raw_df = pd.read_csv(uploaded_file)

    missing = [c for c in REQUIRED_BATCH_COLUMNS if c not in raw_df.columns]
    if missing:
        st.error(f"Missing required columns: {missing}")
    else:
        with st.spinner("Building features and predicting..."):
            features_df = build_features_batch(raw_df, feature_cols=feature_cols)
            open_flags = raw_df['Open'] if 'Open' in raw_df.columns else None
            predictions = predict_sales_batch(model, features_df, open_flags=open_flags)

        result_df = raw_df.copy()
        result_df['Predicted_Sales'] = predictions

        st.success(f"Generated {len(result_df)} predictions.")
        st.dataframe(result_df)

        st.download_button(
            "Download predictions as CSV",
            data=result_df.to_csv(index=False),
            file_name="sales_predictions.csv",
            mime="text/csv",
        )

        if is_demo:
            st.caption("⚠️ These predictions are from the demo model, not your real trained model.")
