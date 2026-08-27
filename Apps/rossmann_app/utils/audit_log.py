"""
audit_log.py

Phase 5 of the workflow doc: "Log every decision. Store the inputs,
model version, forecast, and final offer for every application."

Simple CSV-based logger — enough for a portfolio/demo app. In a real
production system this would write to a database instead, but the
schema (what gets logged) stays the same.
"""

import os
import csv
from datetime import datetime

LOG_PATH = "logs/decision_log.csv"

FIELDNAMES = [
    "timestamp", "store_id", "model_version",
    "projected_90d_sales", "safe_estimate", "max_advance",
    "daily_holdback_pct", "risk_tier", "eligible", "decline_reasons",
]


def log_decision(store_id, model_version, offer):
    """Appends one lending decision to the audit log CSV."""
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    file_exists = os.path.exists(LOG_PATH)

    with open(LOG_PATH, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow({
            "timestamp": datetime.utcnow().isoformat(),
            "store_id": store_id,
            "model_version": model_version,
            "projected_90d_sales": offer.projected_90d_sales,
            "safe_estimate": offer.safe_estimate,
            "max_advance": offer.max_advance,
            "daily_holdback_pct": offer.daily_holdback_pct,
            "risk_tier": offer.risk_tier,
            "eligible": offer.eligibility.eligible,
            "decline_reasons": "; ".join(offer.eligibility.reasons),
        })


def read_decision_log():
    """Reads the audit log back as a list of dict rows, for the dashboard page."""
    import pandas as pd
    if not os.path.exists(LOG_PATH):
        return pd.DataFrame(columns=FIELDNAMES)
    return pd.read_csv(LOG_PATH)
