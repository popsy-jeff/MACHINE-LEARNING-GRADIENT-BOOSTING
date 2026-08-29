"""
feature_pipeline.py

Rebuilds the EXACT feature set the model was trained on, starting from
raw, human-entered inputs (store details + a date).

Ported from the Streamlit app version — the transformation logic is
identical, only the Streamlit dependency was removed.
"""

import pandas as pd
from datetime import date
import os
import joblib

DEFAULT_FEATURE_COLS = [
    'Store', 'Promo', 'Promo2', 'SchoolHoliday', 'CompetitionDistance',
    'Year', 'Month', 'Day', 'WeekOfYear', 'CompetitionOpen',
    'Promo2Open', 'IsPromo2Month',
    'StateHoliday_0', 'StateHoliday_a', 'StateHoliday_b', 'StateHoliday_c',
    'StoreType_a', 'StoreType_b', 'StoreType_c', 'StoreType_d',
    'Assortment_a', 'Assortment_b', 'Assortment_c',
    'DayOfWeek_1', 'DayOfWeek_2', 'DayOfWeek_3', 'DayOfWeek_4',
    'DayOfWeek_5', 'DayOfWeek_6', 'DayOfWeek_7',
]


def load_feature_cols(path="models/feature_cols.pkl"):
    if os.path.exists(path):
        return joblib.load(path)
    return DEFAULT_FEATURE_COLS


_cached_scaler = None
_cached_scaler_cols = None
_scaler_loaded = False


def load_scaler(scaler_path="models/scaler.pkl", cols_path="models/scaler_cols.pkl"):
    """Loads the MinMaxScaler fitted on numeric columns during training, plus
    the exact list of columns it was fit on. Returns (None, None) if either
    file is missing (e.g. the demo model, or an older export that predates
    the scaler) — callers should skip scaling in that case rather than error.
    """
    global _cached_scaler, _cached_scaler_cols, _scaler_loaded
    if _scaler_loaded:
        return _cached_scaler, _cached_scaler_cols

    if os.path.exists(scaler_path) and os.path.exists(cols_path):
        _cached_scaler = joblib.load(scaler_path)
        _cached_scaler_cols = joblib.load(cols_path)
    else:
        _cached_scaler, _cached_scaler_cols = None, None

    _scaler_loaded = True
    return _cached_scaler, _cached_scaler_cols


def _one_hot(value, categories, prefix):
    return {f"{prefix}_{c}": int(value == c) for c in categories}


def build_features(
    store_id: int,
    forecast_date: date,
    promo: int,
    promo2: int,
    school_holiday: int,
    state_holiday: str,
    store_type: str,
    assortment: str,
    competition_distance: float,
    competition_open_since_year: int = None,
    competition_open_since_month: int = None,
    promo2_since_year: int = None,
    promo2_since_week: int = None,
    promo_interval_months: list = None,
    feature_cols: list = None,
) -> pd.DataFrame:
    if feature_cols is None:
        feature_cols = DEFAULT_FEATURE_COLS

    year = forecast_date.year
    month = forecast_date.month
    day = forecast_date.day
    week_of_year = forecast_date.isocalendar()[1]
    day_of_week = forecast_date.isoweekday()

    if competition_open_since_year and competition_open_since_month:
        competition_open = max(
            0,
            (year - competition_open_since_year) * 12
            + (month - competition_open_since_month),
        )
    else:
        competition_open = 0

    if promo2 and promo2_since_year and promo2_since_week:
        promo2_open = max(
            0,
            (year - promo2_since_year) * 52 + (week_of_year - promo2_since_week),
        )
    else:
        promo2_open = 0

    is_promo2_month = int(bool(promo2 == 1 and promo_interval_months and month in promo_interval_months))

    row = {
        'Store': store_id,
        'Promo': promo,
        'Promo2': promo2,
        'SchoolHoliday': school_holiday,
        'CompetitionDistance': competition_distance,
        'Year': year,
        'Month': month,
        'Day': day,
        'WeekOfYear': week_of_year,
        'CompetitionOpen': competition_open,
        'Promo2Open': promo2_open,
        'IsPromo2Month': is_promo2_month,
    }

    row.update(_one_hot(state_holiday, ['0', 'a', 'b', 'c'], 'StateHoliday'))
    row.update(_one_hot(store_type, ['a', 'b', 'c', 'd'], 'StoreType'))
    row.update(_one_hot(assortment, ['a', 'b', 'c'], 'Assortment'))
    row.update(_one_hot(day_of_week, [1, 2, 3, 4, 5, 6, 7], 'DayOfWeek'))

    df = pd.DataFrame([row])

    # Apply the SAME MinMaxScaler fit during training to the same numeric
    # columns. The model's tree splits were learned in this scaled range —
    # skipping this step (or scaling differently) makes predictions
    # meaningless, even though the model still returns a number.
    scaler, scaler_cols = load_scaler()
    if scaler is not None and scaler_cols is not None:
        present = [c for c in scaler_cols if c in df.columns]
        df[present] = scaler.transform(df[present])

    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0
    df = df[feature_cols]

    return df


def build_features_batch(raw_df: pd.DataFrame, feature_cols: list = None) -> pd.DataFrame:
    if feature_cols is None:
        feature_cols = DEFAULT_FEATURE_COLS

    rows = []
    for _, r in raw_df.iterrows():
        f_date = pd.to_datetime(r['Date']).date()
        row_df = build_features(
            store_id=int(r['Store']),
            forecast_date=f_date,
            promo=int(r.get('Promo', 0)),
            promo2=int(r.get('Promo2', 0)),
            school_holiday=int(r.get('SchoolHoliday', 0)),
            state_holiday=str(r.get('StateHoliday', '0')),
            store_type=str(r.get('StoreType', 'a')),
            assortment=str(r.get('Assortment', 'a')),
            competition_distance=float(r.get('CompetitionDistance', 0)),
            competition_open_since_year=r.get('CompetitionOpenSinceYear'),
            competition_open_since_month=r.get('CompetitionOpenSinceMonth'),
            promo2_since_year=r.get('Promo2SinceYear'),
            promo2_since_week=r.get('Promo2SinceWeek'),
            promo_interval_months=None,
            feature_cols=feature_cols,
        )
        rows.append(row_df)
    return pd.concat(rows, ignore_index=True)


REQUIRED_BATCH_COLUMNS = [
    'Store', 'Date', 'Promo', 'Promo2', 'SchoolHoliday', 'StateHoliday',
    'StoreType', 'Assortment', 'CompetitionDistance',
]
