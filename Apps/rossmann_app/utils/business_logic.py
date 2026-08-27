"""
business_logic.py

Implements Phase 3 of the workflow document: turning a raw sales
forecast into a responsible revenue-based financing (merchant cash
advance) decision.

Everything here is transparent, rule-based logic -- no black boxes --
since these numbers are the actual offer shown to a store owner and
need to be explainable and auditable (see Phase 5: "Log every decision").
"""

from dataclasses import dataclass, field
from typing import List


# ------------------------------------------------------------------
# Tunable business parameters — kept in one place so they're easy to
# adjust without hunting through calculation logic.
# ------------------------------------------------------------------
ADVANCE_FACTOR = 0.15          # max advance = safe estimate * this factor
HOLDBACK_BUFFER = 0.02         # extra % added to daily holdback for safety margin
CONSERVATIVE_HAIRCUT = 0.15    # % shaved off the raw forecast before lending against it
MIN_HISTORY_DAYS = 180         # minimum days of sales history required to be eligible
DECLINE_TREND_THRESHOLD = -0.10  # 90-day trend below this % is a red flag


@dataclass
class EligibilityResult:
    eligible: bool
    reasons: List[str] = field(default_factory=list)


@dataclass
class AdvanceOffer:
    projected_90d_sales: float
    safe_estimate: float
    max_advance: float
    daily_holdback_pct: float
    risk_tier: str
    eligibility: EligibilityResult


def aggregate_forecast(daily_predictions: list) -> float:
    """
    Sums daily sales predictions into a single horizon total.
    Per the doc: call the model for the next 90 days, sum into a
    projected 90-day sales total for that store.
    """
    return float(sum(daily_predictions))


def apply_conservative_adjustment(
    projected_total: float,
    forecast_std: float = None,
    haircut: float = CONSERVATIVE_HAIRCUT,
) -> float:
    """
    Shrinks the raw forecast downward before lending against it.

    Two supported approaches, matching the doc's phrasing:
      - if forecast_std is provided (the model's known error margin,
        e.g. from validation residuals), subtract one standard deviation
      - otherwise, fall back to a flat percentage haircut
    """
    if forecast_std is not None:
        safe_estimate = projected_total - forecast_std
    else:
        safe_estimate = projected_total * (1 - haircut)
    return max(0.0, safe_estimate)


def check_eligibility(
    history_days: int,
    trend_pct_90d: float,
    is_closing_flagged: bool,
) -> EligibilityResult:
    """
    Simple rule-based gates, run before any money math — per the doc,
    reject early if any fail, no need to compute an offer at all.
    """
    reasons = []

    if history_days < MIN_HISTORY_DAYS:
        reasons.append(f"Insufficient sales history ({history_days} days, needs {MIN_HISTORY_DAYS}+)")

    if trend_pct_90d < DECLINE_TREND_THRESHOLD:
        reasons.append(f"Sales trending downward ({trend_pct_90d:.1%} over 90 days)")

    if is_closing_flagged:
        reasons.append("Store flagged as closing")

    return EligibilityResult(eligible=(len(reasons) == 0), reasons=reasons)


def calculate_advance_offer(
    safe_estimate: float,
    advance_factor: float = ADVANCE_FACTOR,
    holdback_buffer: float = HOLDBACK_BUFFER,
) -> dict:
    """
    Applies the core lending formulas from the doc:
      max advance     = safe estimate * advance factor
      daily holdback  = (advance / safe estimate) + buffer
    """
    max_advance = safe_estimate * advance_factor
    daily_holdback_pct = (max_advance / safe_estimate + holdback_buffer) if safe_estimate > 0 else 0.0
    return {
        "max_advance": round(max_advance, 2),
        "daily_holdback_pct": round(daily_holdback_pct, 4),
    }


def assign_risk_tier(forecast_volatility: float, competition_distance: float, store_type: str) -> str:
    """
    Combines forecast volatility + store attributes into a risk tier,
    following the doc's "same pattern as the loan app's risk tiering."

    forecast_volatility: coefficient of variation (std / mean) of the
    daily forecasts feeding into the 90-day total — higher = less
    predictable sales, higher risk.
    """
    score = 0

    # Volatility signal
    if forecast_volatility > 0.35:
        score += 2
    elif forecast_volatility > 0.20:
        score += 1

    # Nearby competition signal — very close competitors add uncertainty
    if competition_distance < 500:
        score += 1

    # Store type C/D treated as slightly higher variance in this simple heuristic
    if store_type in ("c", "d"):
        score += 1

    if score >= 3:
        return "High"
    elif score >= 1:
        return "Medium"
    return "Low"


def build_advance_offer(
    daily_predictions: list,
    history_days: int,
    trend_pct_90d: float,
    is_closing_flagged: bool,
    competition_distance: float,
    store_type: str,
    forecast_std: float = None,
) -> AdvanceOffer:
    """End-to-end Phase 3 pipeline: forecast -> safe estimate -> eligibility -> offer -> risk tier."""
    import numpy as np

    projected_total = aggregate_forecast(daily_predictions)
    safe_estimate = apply_conservative_adjustment(projected_total, forecast_std)

    eligibility = check_eligibility(history_days, trend_pct_90d, is_closing_flagged)

    if not eligibility.eligible:
        return AdvanceOffer(
            projected_90d_sales=projected_total,
            safe_estimate=safe_estimate,
            max_advance=0.0,
            daily_holdback_pct=0.0,
            risk_tier="N/A",
            eligibility=eligibility,
        )

    offer = calculate_advance_offer(safe_estimate)

    preds_array = np.array(daily_predictions)
    volatility = float(preds_array.std() / preds_array.mean()) if preds_array.mean() > 0 else 0.0
    risk_tier = assign_risk_tier(volatility, competition_distance, store_type)

    return AdvanceOffer(
        projected_90d_sales=round(projected_total, 2),
        safe_estimate=round(safe_estimate, 2),
        max_advance=offer["max_advance"],
        daily_holdback_pct=offer["daily_holdback_pct"],
        risk_tier=risk_tier,
        eligibility=eligibility,
    )
