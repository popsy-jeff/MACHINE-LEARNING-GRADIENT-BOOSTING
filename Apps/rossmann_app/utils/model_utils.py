"""
model_utils.py

Loads the trained model (Phase 1/2 of the workflow doc) and exposes a
single predict_sales() function the rest of the app calls.

Per the workflow doc's versioning note: every prediction should be able
to report which model version produced it, so we track that here too.
"""

import os
import numpy as np
import joblib
import streamlit as st

MODEL_PATH = "models/rossmann_sales_model.pkl"
FEATURE_COLS_PATH = "models/feature_cols.pkl"
MODEL_VERSION = "v1.0-demo"   # bump this string each time you swap in a new .pkl


@st.cache_resource
def load_model():
    """
    Loads your real trained model if present. If not (e.g. running this
    scaffold before you've exported your notebook's final_model), falls
    back to a small demo model trained on synthetic data so the app is
    still fully click-through-able.

    Replace this fallback by running, in your notebook:
        import joblib
        joblib.dump(final_model, 'rossmann_sales_model.pkl')
        joblib.dump(feature_cols, 'feature_cols.pkl')
    and dropping both files into this app's models/ folder.
    """
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        is_demo = False
    else:
        model = _build_demo_model()
        is_demo = True
    return model, is_demo


def _build_demo_model():
    """A tiny placeholder model so the app runs end-to-end without your real .pkl yet."""
    from xgboost import XGBRegressor
    from utils.feature_pipeline import DEFAULT_FEATURE_COLS

    rng = np.random.default_rng(42)
    n = 2000
    X = pd.DataFrame(
        {col: rng.integers(0, 2, n) if "_" in col else rng.integers(0, 5000, n)
         for col in DEFAULT_FEATURE_COLS}
    )
    # A rough synthetic relationship, just so demo predictions look sane
    y = 4000 + X.get('Promo', 0) * 1500 + rng.normal(0, 500, n)
    y = np.clip(y, 0, None)

    demo_model = XGBRegressor(random_state=42, n_estimators=50, max_depth=4)
    demo_model.fit(X, np.log1p(y))
    return demo_model


import pandas as pd  # noqa: E402  (placed here to avoid unused-import ordering issues above)


def predict_sales(model, feature_row: pd.DataFrame, is_open: int = 1) -> float:
    """
    Predicts a single day's sales for one store.

    Mirrors the training-time transform: model was trained on
    log1p(Sales), so predictions must be reversed with expm1 and
    clipped at zero. Closed-store days are forced to 0, since the
    model was never trained on closed-store patterns (per your
    earlier data-cleaning step).
    """
    if is_open == 0:
        return 0.0

    raw_pred = model.predict(feature_row)[0]
    sales = np.expm1(raw_pred)
    return float(np.clip(sales, 0, None))


def predict_sales_batch(model, feature_df: pd.DataFrame, open_flags: np.ndarray = None) -> np.ndarray:
    """Batch version of predict_sales(), used by the batch-upload page."""
    raw_preds = model.predict(feature_df)
    sales = np.expm1(raw_preds)
    sales = np.clip(sales, 0, None)
    if open_flags is not None:
        sales = np.where(np.array(open_flags) == 0, 0, sales)
    return sales
