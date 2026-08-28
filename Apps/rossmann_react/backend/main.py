"""
main.py — FastAPI backend for the Rossmann sales & financing app.

Wraps the model + business logic in an API (Phase 2 of the workflow doc),
so the React frontend can call it. Every endpoint here corresponds to
one page in the original Streamlit app.
"""

import io
import json
import os
from datetime import date, timedelta

import numpy as np
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from model_utils import load_model, predict_sales, predict_sales_batch, MODEL_VERSION
from feature_pipeline import build_features, build_features_batch, load_feature_cols, REQUIRED_BATCH_COLUMNS
from business_logic import build_advance_offer
from audit_log import log_decision, read_decision_log

app = FastAPI(title="Rossmann Sales & Financing API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's real origin before deploying publicly
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request/response schemas
# ---------------------------------------------------------------------------
class SinglePredictionRequest(BaseModel):
    store_id: int
    forecast_date: date
    is_open: int
    promo: int
    promo2: int
    school_holiday: int
    state_holiday: str
    store_type: str
    assortment: str
    competition_distance: float


class AdvanceRequest(BaseModel):
    store_id: int
    start_date: date
    store_type: str
    assortment: str
    competition_distance: float
    promo: int
    promo2: int
    history_days: int
    trend_pct_90d: float
    is_closing_flagged: bool


# ---------------------------------------------------------------------------
# Health / status
# ---------------------------------------------------------------------------
@app.get("/api/health")
def health():
    model, is_demo = load_model()
    return {"status": "ok", "is_demo": is_demo, "model_version": MODEL_VERSION}


# ---------------------------------------------------------------------------
# Single prediction (Page 1)
# ---------------------------------------------------------------------------
@app.post("/api/predict")
def predict(req: SinglePredictionRequest):
    model, is_demo = load_model()
    feature_cols = load_feature_cols()

    features = build_features(
        store_id=req.store_id,
        forecast_date=req.forecast_date,
        promo=req.promo,
        promo2=req.promo2,
        school_holiday=req.school_holiday,
        state_holiday=req.state_holiday,
        store_type=req.store_type,
        assortment=req.assortment,
        competition_distance=req.competition_distance,
        feature_cols=feature_cols,
    )
    prediction = predict_sales(model, features, is_open=req.is_open)

    return {
        "predicted_sales": prediction,
        "is_demo": is_demo,
        "features": features.iloc[0].to_dict(),
    }


# ---------------------------------------------------------------------------
# Batch prediction (Page 2)
# ---------------------------------------------------------------------------
@app.post("/api/predict/batch")
async def predict_batch(file: UploadFile = File(...)):
    model, is_demo = load_model()
    feature_cols = load_feature_cols()

    contents = await file.read()
    raw_df = pd.read_csv(io.BytesIO(contents))

    missing = [c for c in REQUIRED_BATCH_COLUMNS if c not in raw_df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required columns: {missing}")

    features_df = build_features_batch(raw_df, feature_cols=feature_cols)
    open_flags = raw_df['Open'] if 'Open' in raw_df.columns else None
    predictions = predict_sales_batch(model, features_df, open_flags=open_flags)

    result_df = raw_df.copy()
    result_df['Predicted_Sales'] = predictions

    return {
        "is_demo": is_demo,
        "row_count": len(result_df),
        "total_predicted_revenue": float(result_df['Predicted_Sales'].sum()),
        "average_predicted": float(result_df['Predicted_Sales'].mean()),
        "rows": json.loads(result_df.to_json(orient="records")),
    }


# ---------------------------------------------------------------------------
# Model performance (Page 3)
# ---------------------------------------------------------------------------
@app.get("/api/model/metrics")
def model_metrics():
    metrics_path = "models/validation_metrics.json"
    model, is_demo = load_model()
    feature_cols = load_feature_cols()

    metrics = None
    if os.path.exists(metrics_path):
        with open(metrics_path) as f:
            metrics = json.load(f)

    feature_importance = []
    try:
        importances = model.feature_importances_
        imp_df = pd.DataFrame({
            "feature": feature_cols[:len(importances)],
            "importance": [float(x) for x in importances],
        }).sort_values("importance", ascending=False).head(15)
        feature_importance = imp_df.to_dict(orient="records")
    except Exception:
        pass

    return {
        "is_demo": is_demo,
        "model_version": MODEL_VERSION,
        "metrics": metrics,
        "feature_importance": feature_importance,
        # Reference runs from the actual Optuna search, shown when no real
        # metrics.json has been exported yet
        "reference_runs": [
            {"trials": 20, "rmspe": 0.171487, "max_depth": 9, "n_estimators": 380, "learning_rate": 0.1135},
            {"trials": 20, "rmspe": 0.169938, "max_depth": 10, "n_estimators": 444, "learning_rate": 0.1054},
            {"trials": 30, "rmspe": 0.170200, "max_depth": 9, "n_estimators": 510, "learning_rate": 0.1103},
        ],
    }


# ---------------------------------------------------------------------------
# Advance calculator (Page 4)
# ---------------------------------------------------------------------------
@app.post("/api/advance/offer")
def advance_offer(req: AdvanceRequest):
    model, is_demo = load_model()
    feature_cols = load_feature_cols()

    daily_predictions = []
    daily_dates = []
    for i in range(90):
        forecast_date = req.start_date + timedelta(days=i)
        features = build_features(
            store_id=req.store_id,
            forecast_date=forecast_date,
            promo=req.promo,
            promo2=req.promo2,
            school_holiday=0,
            state_holiday="0",
            store_type=req.store_type,
            assortment=req.assortment,
            competition_distance=req.competition_distance,
            feature_cols=feature_cols,
        )
        # Sundays treated as closed by default, same as the Streamlit version
        is_open = 0 if forecast_date.isoweekday() == 7 else 1
        pred = predict_sales(model, features, is_open=is_open)
        daily_predictions.append(pred)
        daily_dates.append(forecast_date.isoformat())

    offer = build_advance_offer(
        daily_predictions=daily_predictions,
        history_days=req.history_days,
        trend_pct_90d=req.trend_pct_90d,
        is_closing_flagged=req.is_closing_flagged,
        competition_distance=req.competition_distance,
        store_type=req.store_type,
    )

    log_decision(req.store_id, MODEL_VERSION, offer)

    return {
        "is_demo": is_demo,
        "projected_90d_sales": offer.projected_90d_sales,
        "safe_estimate": offer.safe_estimate,
        "max_advance": offer.max_advance,
        "daily_holdback_pct": offer.daily_holdback_pct,
        "risk_tier": offer.risk_tier,
        "eligible": offer.eligibility.eligible,
        "decline_reasons": offer.eligibility.reasons,
        "daily_forecast": [{"date": d, "predicted_sales": p} for d, p in zip(daily_dates, daily_predictions)],
    }


# ---------------------------------------------------------------------------
# Risk dashboard (Page 5)
# ---------------------------------------------------------------------------
@app.get("/api/audit/log")
def audit_log():
    log_df = read_decision_log()
    if log_df.empty:
        return {"rows": [], "summary": None}

    summary = {
        "total": int(len(log_df)),
        "approved": int((log_df['eligible'] == True).sum()),
        "declined": int((log_df['eligible'] == False).sum()),
        "high_risk": int((log_df['risk_tier'] == 'High').sum()),
        "tier_counts": log_df['risk_tier'].value_counts().to_dict(),
    }

    return {"rows": json.loads(log_df.to_json(orient="records")), "summary": summary}


@app.get("/api/audit/log/csv")
def audit_log_csv():
    log_df = read_decision_log()
    stream = io.StringIO()
    log_df.to_csv(stream, index=False)
    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=decision_log.csv"
    return response
