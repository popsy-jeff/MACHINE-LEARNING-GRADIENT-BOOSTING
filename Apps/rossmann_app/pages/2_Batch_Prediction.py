import streamlit as st
import pandas as pd
import plotly.express as px
from utils.model_utils import load_model, predict_sales_batch
from utils.feature_pipeline import build_features_batch, load_feature_cols, REQUIRED_BATCH_COLUMNS
from utils.style import inject_css, hero, section_tag, COLORS, PLOTLY_SEQUENCE

st.set_page_config(page_title="Batch Prediction", page_icon="📋", layout="wide")
inject_css()
hero("📋 Batch Sales Prediction", "Upload a CSV with one row per store/date you want a forecast for.")

section_tag("Format")
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

        st.write("")
        section_tag("Summary")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Rows", f"{len(result_df):,}")
        k2.metric("Total Predicted Sales", f"${result_df['Predicted_Sales'].sum():,.0f}")
        k3.metric("Average per Row", f"${result_df['Predicted_Sales'].mean():,.0f}")
        k4.metric("Highest Prediction", f"${result_df['Predicted_Sales'].max():,.0f}")

        st.write("")
        chart_col, top_col = st.columns([3, 2])

        with chart_col:
            st.markdown("##### Distribution of predicted sales")
            fig_hist = px.histogram(
                result_df, x="Predicted_Sales", nbins=30,
                color_discrete_sequence=[COLORS["primary"]],
            )
            fig_hist.update_layout(
                height=320, margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis_title="Predicted Sales ($)", yaxis_title="Rows",
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with top_col:
            st.markdown("##### Top 10 by predicted sales")
            top10 = result_df.nlargest(10, "Predicted_Sales")
            label_col = "Store" if "Store" in top10.columns else top10.index.name or top10.columns[0]
            fig_top = px.bar(
                top10.sort_values("Predicted_Sales"),
                x="Predicted_Sales",
                y=top10["Store"].astype(str) if "Store" in top10.columns else top10.index.astype(str),
                orientation="h",
                color_discrete_sequence=[COLORS["accent"]],
            )
            fig_top.update_layout(
                height=320, margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor="white", paper_bgcolor="white",
                xaxis_title="Predicted Sales ($)", yaxis_title="Store",
            )
            st.plotly_chart(fig_top, use_container_width=True)

        st.write("")
        section_tag("Full results")
        st.dataframe(result_df, use_container_width=True)

        st.download_button(
            "Download predictions as CSV",
            data=result_df.to_csv(index=False),
            file_name="sales_predictions.csv",
            mime="text/csv",
        )

        if is_demo:
            st.caption("⚠️ These predictions are from the demo model, not your real trained model.")
