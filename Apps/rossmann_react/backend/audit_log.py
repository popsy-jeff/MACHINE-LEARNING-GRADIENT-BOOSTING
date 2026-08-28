"""
audit_log.py

Logs every lending decision (Phase 5 of the workflow doc). Same schema
and CSV storage as the Streamlit version, unchanged.
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
    import pandas as pd
    if not os.path.exists(LOG_PATH):
        return pd.DataFrame(columns=FIELDNAMES)
    return pd.read_csv(LOG_PATH)
