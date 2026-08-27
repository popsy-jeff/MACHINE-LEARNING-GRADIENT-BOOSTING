import streamlit as st
import pandas as pd
from utils.model_utils import load_model, predict_sales_batch
from utils.feature_pipeline import build_features_batch, load_feature_cols, REQUIRED_BATCH_COLUMNS
from utils.theme import apply_theme, sidebar_brand, sidebar_mode_lock, kpi_card, section_divider, line_area_chart

st.set_page_config(page_title="Batch Prediction", page_icon="📋", layout="wide")
apply_theme()
sidebar_brand()
sidebar_mode_lock()
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

        section_divider()
        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_card("Total Predicted Revenue", f"${result_df['Predicted_Sales'].sum():,.0f}", signal="green")
        with c2:
            kpi_card("Average per Row", f"${result_df['Predicted_Sales'].mean():,.0f}", signal="green")
        with c3:
            kpi_card("Rows Predicted", f"{len(result_df):,}", signal="yellow")

        if 'Date' in result_df.columns:
            trend_df = result_df.groupby('Date', as_index=False)['Predicted_Sales'].sum().sort_values('Date')
            st.plotly_chart(
                line_area_chart(trend_df, 'Date', 'Predicted_Sales', title="Predicted sales over time"),
                width='stretch',
            )

        st.dataframe(result_df, width='stretch')

        st.download_button(
            "Download predictions as CSV",
            data=result_df.to_csv(index=False),
            file_name="sales_predictions.csv",
            mime="text/csv",
        )

        if is_demo:
            st.caption("⚠️ These predictions are from the demo model, not your real trained model.")
