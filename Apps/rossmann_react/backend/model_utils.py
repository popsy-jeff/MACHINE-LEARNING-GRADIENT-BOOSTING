"""
model_utils.py

Loads the trained model and exposes predict_sales() / predict_sales_batch().
Ported from the Streamlit app — same logic, st.cache_resource replaced with
a plain module-level cache (a FastAPI process only needs to load once anyway).
"""

import os
import json
import numpy as np
import pandas as pd
import joblib

MODEL_PATH = "models/rossmann_sales_model.pkl"
FEATURE_COLS_PATH = "models/feature_cols.pkl"
METRICS_PATH = "models/validation_metrics.json"


def _model_version() -> str:
    """Builds a version label from the real model's validation metrics when
    one is present, so the UI never shows a stale "-demo" label just because
    that word happened to be baked into a hardcoded constant. Falls back to
    a demo label only when there's genuinely no trained model on disk."""
    if os.path.exists(MODEL_PATH) and os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH) as f:
                metrics = json.load(f)
            rmspe = metrics.get("rmspe")
            if rmspe is not None:
                return f"v1.0 (rmspe={rmspe:.4f})"
            return "v1.0"
        except Exception:
            return "v1.0"
    return "v1.0-demo"


MODEL_VERSION = _model_version()

_cached_model = None
_cached_is_demo = None


def load_model():
    global _cached_model, _cached_is_demo
    if _cached_model is not None:
        return _cached_model, _cached_is_demo

    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        is_demo = False
    else:
        model = _build_demo_model()
        is_demo = True

    _cached_model, _cached_is_demo = model, is_demo
    return model, is_demo


BINARY_COLS = {'Promo', 'Promo2', 'SchoolHoliday'}


def _build_demo_model():
    """A tiny placeholder model so the API runs end-to-end without a real .pkl yet."""
    from xgboost import XGBRegressor
    from feature_pipeline import DEFAULT_FEATURE_COLS

    rng = np.random.default_rng(42)
    n = 2000
    X = pd.DataFrame({
        col: rng.integers(0, 2, n) if ("_" in col or col in BINARY_COLS) else rng.integers(0, 5000, n)
        for col in DEFAULT_FEATURE_COLS
    })
    y = 4000 + X.get('Promo', 0) * 1500 + rng.normal(0, 500, n)
    y = np.clip(y, 0, None)

    demo_model = XGBRegressor(random_state=42, n_estimators=50, max_depth=4)
    demo_model.fit(X, np.log1p(y))
    return demo_model


def _safe_sales(value: float) -> float:
    """Guard against inf/NaN ever leaving this function — Python's json module
    serializes those as the literal tokens Infinity/NaN, which are not valid
    JSON and break strict parsers (including the browser's JSON.parse)."""
    if not np.isfinite(value):
        return 0.0
    return float(value)


# Bound applied to the model's raw (log-space) output before exponentiating.
# np.expm1(20) is already ~485 million — far beyond any real single-day sales
# figure — so clipping here can only ever affect a genuinely broken
# prediction, never a legitimate one. This turns "silently returns $0" into
# "returns an obviously-too-large number", which is far easier to notice and
# debug than a fake-looking zero.
RAW_LOG_PRED_BOUND = 20.0


def predict_sales(model, feature_row: pd.DataFrame, is_open: int = 1) -> dict:
    """Returns both the final dollar prediction and the raw log-space value,
    so the API can surface the raw number for debugging when something looks
    wrong (e.g. a scale mismatch between how the model was trained and what
    the backend is feeding it)."""
    if is_open == 0:
        return {"predicted_sales": 0.0, "raw_log_prediction": None, "clipped": False}

    raw_pred = float(model.predict(feature_row)[0])
    clipped = abs(raw_pred) > RAW_LOG_PRED_BOUND
    bounded_pred = float(np.clip(raw_pred, -RAW_LOG_PRED_BOUND, RAW_LOG_PRED_BOUND))

    sales = np.expm1(bounded_pred)
    sales = np.clip(sales, 0, None)
    return {
        "predicted_sales": _safe_sales(sales),
        "raw_log_prediction": raw_pred,
        "clipped": clipped,
    }


def predict_sales_batch(model, feature_df: pd.DataFrame, open_flags=None) -> np.ndarray:
    raw_preds = model.predict(feature_df)
    bounded = np.clip(raw_preds, -RAW_LOG_PRED_BOUND, RAW_LOG_PRED_BOUND)
    sales = np.expm1(bounded)
    sales = np.clip(sales, 0, None)
    sales = np.where(np.isfinite(sales), sales, 0.0)
    if open_flags is not None:
        sales = np.where(np.array(open_flags) == 0, 0, sales)
    return sales