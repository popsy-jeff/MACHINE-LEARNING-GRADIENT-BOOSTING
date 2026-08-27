import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from utils.model_utils import load_model, MODEL_VERSION
from utils.style import inject_css, hero, section_tag, COLORS, PLOTLY_SEQUENCE

st.set_page_config(page_title="Model Performance", page_icon="📊", layout="wide")
inject_css()
hero("📊 Model Performance", "Validation metrics, hyperparameters, and what the model is actually paying attention to.")

model, is_demo = load_model()

METRICS_PATH = "models/validation_metrics.json"

section_tag("Validation")

if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH) as f:
        metrics = json.load(f)

    gauge_col, kpi_col = st.columns([1, 2])

    with gauge_col:
        rmspe = metrics.get('rmspe', 0)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=rmspe,
            number={"valueformat": ".4f"},
            title={"text": "Validation RMSPE (lower is better)"},
            gauge={
                "axis": {"range": [0, max(0.4, rmspe * 1.5)]},
                "bar": {"color": COLORS["primary"]},
                "steps": [
                    {"range": [0, 0.15], "color": COLORS["low"] + "33"},
                    {"range": [0.15, 0.25], "color": COLORS["medium"] + "33"},
                    {"range": [0.25, max(0.4, rmspe * 1.5)], "color": COLORS["high"] + "33"},
                ],
            },
        ))
        fig_gauge.update_layout(height=260, margin=dict(l=20, r=20, t=50, b=10))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with kpi_col:
        c1, c2 = st.columns(2)
        c1.metric("Model Version", MODEL_VERSION)
        c2.metric("Trials Searched", metrics.get('n_trials', 'N/A'))
        if 'best_params' in metrics:
            st.markdown("##### Best hyperparameters (Optuna search)")
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

    st.markdown("##### Recent search runs (from your notebook)")
    runs = pd.DataFrame([
        {"trials": 20, "rmspe": 0.171487, "max_depth": 9, "n_estimators": 380, "learning_rate": 0.1135},
        {"trials": 20, "rmspe": 0.169938, "max_depth": 10, "n_estimators": 444, "learning_rate": 0.1054},
        {"trials": 30, "rmspe": 0.170200, "max_depth": 9, "n_estimators": 510, "learning_rate": 0.1103},
    ])

    run_col, table_col = st.columns([3, 2])
    with run_col:
        fig_runs = px.line(
            runs.reset_index().rename(columns={"index": "run"}),
            x="run", y="rmspe", markers=True,
            color_discrete_sequence=[COLORS["primary"]],
        )
        fig_runs.update_layout(
            height=300, margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor="white", paper_bgcolor="white",
            yaxis_title="RMSPE", xaxis_title="Search run",
        )
        st.plotly_chart(fig_runs, use_container_width=True)
    with table_col:
        st.dataframe(runs, use_container_width=True)
    st.caption("These three runs converged around RMSPE ≈ 0.170 — a stable performance plateau.")

st.write("")
section_tag("Feature importance")
try:
    importances = model.feature_importances_
    from utils.feature_pipeline import load_feature_cols
    feature_cols = load_feature_cols()
    imp_df = pd.DataFrame({
        "feature": feature_cols[:len(importances)],
        "importance": importances,
    }).sort_values("importance", ascending=True).tail(15)

    fig_imp = px.bar(
        imp_df, x="importance", y="feature", orientation="h",
        color="importance", color_continuous_scale=[COLORS["bg_soft"], COLORS["primary"]],
    )
    fig_imp.update_layout(
        height=460, margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
        coloraxis_showscale=False, yaxis_title="", xaxis_title="Relative importance",
    )
    st.plotly_chart(fig_imp, use_container_width=True)
except Exception as e:
    st.warning(f"Could not compute feature importance: {e}")

if is_demo:
    st.caption("⚠️ Currently showing the demo model's stats, not your real trained model.")
