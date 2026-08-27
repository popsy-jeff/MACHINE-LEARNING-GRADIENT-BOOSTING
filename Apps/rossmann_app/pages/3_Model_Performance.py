import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from utils.model_utils import load_model, MODEL_VERSION
from utils.style import inject_css, hero, section_tag, metric_card, plotly_chart, COLORS

st.set_page_config(page_title="Model Performance", page_icon="📊", layout="wide")
inject_css()
hero("performance", "Model Performance", "Validation metrics, hyperparameters, and what the model is actually paying attention to.")

model, is_demo = load_model()
METRICS_PATH = "models/validation_metrics.json"

section_tag("Validation", "gauge")

if os.path.exists(METRICS_PATH):
    with open(METRICS_PATH) as f:
        metrics = json.load(f)

    gauge_col, kpi_col = st.columns([1, 2])

    with gauge_col:
        rmspe = metrics.get('rmspe', 0)
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=rmspe,
            number={"valueformat": ".4f", "font": {"color": "#94A3B8"}},
            title={"text": "Validation RMSPE (lower is better)", "font": {"color": "#94A3B8", "size": 13}},
            gauge={
                "axis": {"range": [0, max(0.4, rmspe * 1.5)], "tickcolor": "#94A3B8"},
                "bar": {"color": COLORS["primary"]},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 0.15], "color": COLORS["low"] + "26"},
                    {"range": [0.15, 0.25], "color": COLORS["medium"] + "26"},
                    {"range": [0.25, max(0.4, rmspe * 1.5)], "color": COLORS["high"] + "26"},
                ],
            },
        ))
        plotly_chart(fig_gauge, height=260)

    with kpi_col:
        c1, c2 = st.columns(2)
        with c1:
            metric_card("bolt", "Model version", MODEL_VERSION)
        with c2:
            metric_card("layers", "Trials searched", str(metrics.get('n_trials', 'N/A')))
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
        )
        fig_runs.update_traces(line_color=COLORS["primary"], marker_color=COLORS["primary"])
        fig_runs.update_layout(yaxis_title="RMSPE", xaxis_title="Search run")
        plotly_chart(fig_runs, height=300)
    with table_col:
        st.dataframe(runs, use_container_width=True)
    st.caption("These three runs converged around RMSPE ≈ 0.170 — a stable performance plateau.")

section_tag("Feature importance", "trend-up")
try:
    importances = model.feature_importances_
    from utils.feature_pipeline import load_feature_cols
    feature_cols = load_feature_cols()
    imp_df = pd.DataFrame({
        "feature": feature_cols[:len(importances)],
        "importance": importances,
    }).sort_values("importance", ascending=True).tail(15)

    fig_imp = px.bar(imp_df, x="importance", y="feature", orientation="h", color="importance")
    fig_imp.update_traces(marker_colorscale=[[0, "#312E81"], [1, COLORS["primary"]]])
    fig_imp.update_layout(coloraxis_showscale=False, yaxis_title="", xaxis_title="Relative importance")
    plotly_chart(fig_imp, height=460)
except Exception as e:
    st.warning(f"Could not compute feature importance: {e}")

if is_demo:
    st.caption("⚠️ Currently showing the demo model's stats, not your real trained model.")
