"""
model_utils.py

Loads the trained model and exposes predict_sales() / predict_sales_batch().
Ported from the Streamlit app — same logic, st.cache_resource replaced with
a plain module-level cache (a FastAPI process only needs to load once anyway).
"""

import os
import numpy as np
import pandas as pd
import joblib

MODEL_PATH = "models/rossmann_sales_model.pkl"
FEATURE_COLS_PATH = "models/feature_cols.pkl"
MODEL_VERSION = "v1.0-demo"

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

def _safe_sales(value: float) -> float:
    """Guard against inf/NaN ever leaving this function."""
    if not np.isfinite(value):
        return 0.0
    return float(value)


def predict_sales(model, feature_row: pd.DataFrame, is_open: int = 1) -> float:
    if is_open == 0:
        return 0.0
    raw_pred = model.predict(feature_row)[0]
    sales = np.expm1(raw_pred)
    sales = np.clip(sales, 0, None)
    return _safe_sales(sales)


def predict_sales_batch(model, feature_df: pd.DataFrame, open_flags=None) -> np.ndarray:
    raw_preds = model.predict(feature_df)
    sales = np.expm1(raw_preds)
    sales = np.clip(sales, 0, None)
    sales = np.where(np.isfinite(sales), sales, 0.0)
    if open_flags is not None:
        sales = np.where(np.array(open_flags) == 0, 0, sales)
    return sales