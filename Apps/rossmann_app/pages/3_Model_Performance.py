import streamlit as st
import pandas as pd
import json
import os
from utils.model_utils import load_model, MODEL_VERSION
from utils.theme import apply_theme, sidebar_brand, sidebar_mode_lock, kpi_card, gauge_chart, styled_bar_chart, section_divider

st.set_page_config(page_title="Model Performance", page_icon="📊", layout="wide")
apply_theme()
sidebar_brand()
sidebar_mode_lock()
st.title("📊 Model Performance")

model, is_demo = load_model()

METRICS_PATH = "models/validation_metrics.json"

st.subheader("Validation Metrics")

if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH) as f:
        metrics = json.load(f)

    gcol, kcol = st.columns([1, 1.4])
    with gcol:
        st.plotly_chart(
            gauge_chart(metrics.get('rmspe', 0), 0, 0.5, "Validation RMSPE", good_is_low=True),
            width='stretch',
        )
    with kcol:
        st.write("")
        kpi_card("Model Version", MODEL_VERSION, signal="green")
        st.write("")
        kpi_card("Trials Searched", str(metrics.get('n_trials', 'N/A')), signal="yellow")

    if 'best_params' in metrics:
        st.subheader("Best Hyperparameters (from Optuna search)")
        st.json(metrics['best_params'])
else:
    st.info(
        "No saved metrics found at `models/validation_metrics.json`. "
        "From your notebook, save your Optuna search results like this:"
    )
    st.code("""
import json

metrics = {
    "rmspe": search.best_value,
    "n_trials": len(search.trials),
    "best_params": search.best_params,
}
with open("validation_metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)
""", language="python")

    # Show your three most recent actual search runs as a placeholder reference
    st.subheader("Recent search runs (from your notebook)")
    runs = pd.DataFrame([
        {"trials": 20, "rmspe": 0.171487, "max_depth": 9, "n_estimators": 380, "learning_rate": 0.1135},
        {"trials": 20, "rmspe": 0.169938, "max_depth": 10, "n_estimators": 444, "learning_rate": 0.1054},
        {"trials": 30, "rmspe": 0.170200, "max_depth": 9, "n_estimators": 510, "learning_rate": 0.1103},
    ])
    gcol, tcol = st.columns([1, 1.4])
    with gcol:
        st.plotly_chart(
            gauge_chart(runs['rmspe'].iloc[-1], 0, 0.5, "Latest run RMSPE", good_is_low=True),
            width='stretch',
        )
    with tcol:
        st.write("")
        st.dataframe(runs, width='stretch')
    st.caption("These three runs converged around RMSPE ≈ 0.170 — a stable performance plateau.")

section_divider()
st.subheader("Feature Importance")
try:
    importances = model.feature_importances_
    from utils.feature_pipeline import load_feature_cols
    feature_cols = load_feature_cols()
    imp_df = pd.DataFrame({
        "feature": feature_cols[:len(importances)],
        "importance": importances,
    }).sort_values("importance", ascending=False).head(15)
    st.plotly_chart(
        styled_bar_chart(imp_df, "feature", "importance", title="Top 15 features"),
        width='stretch',
    )
except Exception as e:
    st.warning(f"Could not compute feature importance: {e}")

if is_demo:
    st.caption("⚠️ Currently showing the demo model's stats, not your real trained model.")
