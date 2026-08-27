import streamlit as st
from utils.model_utils import load_model, MODEL_VERSION

st.set_page_config(page_title="Rossmann Sales & Financing", page_icon="📈", layout="wide")

st.title("📈 Rossmann Sales Forecasting & Revenue-Based Financing")

st.markdown("""
This app turns a trained sales-forecasting model into a working finance
product: a merchant cash advance tool that lends stores money against
their predicted future sales, repaid as a daily percentage of revenue.

**Pages**
- **Single Prediction** — forecast one store's sales for one day
- **Batch Prediction** — upload a CSV of store/date rows, get forecasts for all of them
- **Model Performance** — validation metrics and feature importance
- **Advance Calculator** — turn a 90-day forecast into a financing offer (Phase 3)
- **Risk Dashboard** — review flagged/high-risk applications, audit log (Phase 3–5)

Use the sidebar to navigate.
""")

model, is_demo = load_model()

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
