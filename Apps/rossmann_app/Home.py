import streamlit as st
from utils.model_utils import load_model, MODEL_VERSION
from utils.theme import apply_theme, sidebar_brand, sidebar_mode_lock, kpi_card, section_divider

st.set_page_config(page_title="Rossmann Sales & Financing", page_icon="📈", layout="wide")
apply_theme()
sidebar_brand()
sidebar_mode_lock()

st.title("📈 Rossmann Sales Forecasting & Revenue-Based Financing")

st.markdown("""
This app turns a trained sales-forecasting model into a working finance
product: a merchant cash advance tool that lends stores money against
their predicted future sales, repaid as a daily percentage of revenue.
""")

model, is_demo = load_model()

col1, col2, col3 = st.columns(3)
with col1:
    kpi_card("Model Status", "Demo Model" if is_demo else "Trained Model",
              sub=f"version {MODEL_VERSION}", signal="yellow" if is_demo else "green")
with col2:
    kpi_card("Pipeline Stage", "Phase 3", sub="Business logic layer active", signal="green")
with col3:
    kpi_card("Pages Available", "5", sub="Prediction → Financing → Ops", signal="green")

section_divider()

st.markdown("#### Navigate")
p1, p2 = st.columns(2)
with p1:
    st.markdown("""
    - 🔮 **Single Prediction** — forecast one store's sales for one day
    - 📋 **Batch Prediction** — upload a CSV, get forecasts for every row
    - 📊 **Model Performance** — validation metrics and feature importance
    """)
with p2:
    st.markdown("""
    - 💰 **Advance Calculator** — 90-day forecast → financing offer (Phase 3)
    - 🛡️ **Risk Dashboard** — flagged applications, audit log (Phase 3–5)
    """)

section_divider()

if is_demo:
    st.warning(
        "⚠️ No trained model found at `models/rossmann_sales_model.pkl` — running with a "
        "**demo model** trained on synthetic data so the app is fully click-through-able. "
        "Export your real model with `joblib.dump(final_model, 'rossmann_sales_model.pkl')` "
        "and `joblib.dump(feature_cols, 'feature_cols.pkl')`, then drop both files into "
        "this app's `models/` folder to get real predictions."
    )
else:
    st.success(f"✅ Loaded trained model — version `{MODEL_VERSION}`")
