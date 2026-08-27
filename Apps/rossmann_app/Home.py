import streamlit as st
from utils.model_utils import load_model, MODEL_VERSION
from utils.style import inject_css, hero, section_tag, metric_card, badge, nav_card, footer, COLORS

st.set_page_config(page_title="Rossmann Sales & Financing", page_icon="📈", layout="wide")
inject_css()

hero(
    "trend-up",
    "Rossmann Sales Forecasting & Revenue-Based Financing",
    "A gradient-boosted forecasting model, wrapped in a working finance product: "
    "a merchant cash advance tool that lends stores money against their predicted "
    "future sales, repaid as a daily percentage of revenue.",
)

model, is_demo = load_model()

status_col, version_col, algo_col = st.columns(3)
with status_col:
    if is_demo:
        metric_card("flask", "Model status", "Demo mode", "Synthetic data, click-through only", COLORS["medium"])
    else:
        metric_card("check", "Model status", "Live", "Serving real predictions", COLORS["low"])
with version_col:
    metric_card("bolt", "Model version", MODEL_VERSION)
with algo_col:
    metric_card("gauge", "Algorithm", "XGBoost", "Gradient Boosting")

if is_demo:
    st.warning(
        "No trained model found at `models/rossmann_sales_model.pkl` — running with a "
        "**demo model** trained on synthetic data so the app is fully click-through-able. "
        "Export your real model with `joblib.dump(final_model, 'rossmann_sales_model.pkl')` "
        "and `joblib.dump(feature_cols, 'feature_cols.pkl')`, then drop both files into "
        "this app's `models/` folder to get real predictions."
    )

section_tag("Get around the app", "layers")

row1 = st.columns(3)
row2 = st.columns(2)

pages = [
    ("single", "Single Prediction", "Forecast one store's sales for one day.", "pages/1_Single_Prediction.py"),
    ("batch", "Batch Prediction", "Upload a CSV of store/date rows, get forecasts for all of them.", "pages/2_Batch_Prediction.py"),
    ("performance", "Model Performance", "Validation metrics and feature importance.", "pages/3_Model_Performance.py"),
    ("advance", "Advance Calculator", "Turn a 90-day forecast into a financing offer.", "pages/4_Advance_Calculator.py"),
    ("risk", "Risk Dashboard", "Review flagged / high-risk applications and the audit log.", "pages/5_Risk_Dashboard.py"),
]

slots = row1 + row2
for (icon, title, desc, target), slot in zip(pages, slots):
    with slot:
        nav_card(icon, title, desc)
        st.page_link(target, label=f"Open {title}")

footer(
    'Built by Jeff Mulele · Gradient Boosting portfolio project · '
    '<a href="https://github.com/popsy-jeff/MACHINE-LEARNING-GRADIENT-BOOSTING" target="_blank">View source on GitHub</a>'
)
