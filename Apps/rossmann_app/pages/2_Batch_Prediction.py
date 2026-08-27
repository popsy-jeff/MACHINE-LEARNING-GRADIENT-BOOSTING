import streamlit as st
import pandas as pd
import plotly.express as px
from utils.model_utils import load_model, predict_sales_batch
from utils.feature_pipeline import build_features_batch, load_feature_cols, REQUIRED_BATCH_COLUMNS
from utils.style import inject_css, hero, section_tag, metric_card, plotly_chart, COLORS

st.set_page_config(page_title="Batch Prediction", page_icon="📋", layout="wide")
inject_css()
hero("batch", "Batch Sales Prediction", "Upload a CSV with one row per store/date you want a forecast for.")

section_tag("Format", "layers")
st.markdown(f"""
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

        section_tag("Summary", "gauge")
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            metric_card("layers", "Rows", f"{len(result_df):,}")
        with k2:
            metric_card("coins", "Total predicted", f"${result_df['Predicted_Sales'].sum():,.0f}", color=COLORS["primary"])
        with k3:
            metric_card("gauge", "Average / row", f"${result_df['Predicted_Sales'].mean():,.0f}")
        with k4:
            metric_card("trend-up", "Highest", f"${result_df['Predicted_Sales'].max():,.0f}", color=COLORS["accent"])

        chart_col, top_col = st.columns([3, 2])

        with chart_col:
            st.markdown("##### Distribution of predicted sales")
            fig_hist = px.histogram(result_df, x="Predicted_Sales", nbins=30)
            fig_hist.update_traces(marker_color=COLORS["primary"])
            fig_hist.update_layout(xaxis_title="Predicted Sales ($)", yaxis_title="Rows")
            plotly_chart(fig_hist)

        with top_col:
            st.markdown("##### Top 10 by predicted sales")
            top10 = result_df.nlargest(10, "Predicted_Sales")
            y_vals = top10["Store"].astype(str) if "Store" in top10.columns else top10.index.astype(str)
            fig_top = px.bar(
                top10.sort_values("Predicted_Sales"),
                x="Predicted_Sales",
                y=y_vals,
                orientation="h",
            )
            fig_top.update_traces(marker_color=COLORS["accent"])
            fig_top.update_layout(xaxis_title="Predicted Sales ($)", yaxis_title="Store")
            plotly_chart(fig_top)

        section_tag("Full results", "layers")
        st.dataframe(result_df, use_container_width=True)

        st.download_button(
            "Download predictions as CSV",
            data=result_df.to_csv(index=False),
            file_name="sales_predictions.csv",
            mime="text/csv",
        )

        if is_demo:
            st.caption("⚠️ These predictions are from the demo model, not your real trained model.")
