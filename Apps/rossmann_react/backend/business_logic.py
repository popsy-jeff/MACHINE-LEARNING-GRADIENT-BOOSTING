"""
business_logic.py

Implements Phase 3 of the workflow document: turning a raw sales forecast
into a revenue-based financing (merchant cash advance / MCA) decision,
using the same mechanics real MCA underwriting uses — not an arbitrary
percentage of revenue.

## How real MCA underwriting works (what this models)

1. **Advance amount** is sized off average MONTHLY revenue, not a flat
   percentage of a forecast total — typically 0.5x-1.5x monthly revenue
   depending on risk.
2. **Pricing uses a factor rate**, not an interest rate. A factor rate of
   1.30 means: borrow $10,000, repay $13,000 total. This is standard MCA
   convention (typically 1.1-1.5).
3. **Daily/weekly holdback %** is derived backwards from the total payback
   and an estimated repayment TERM — it's not picked directly. Real MCA
   holdbacks typically land in an 8%-30% band; anything computed outside
   that is unrealistic and gets clamped.
4. **Risk tier** drives all of the above: better risk = bigger advance
   multiple, lower factor rate, longer term (smaller daily bite).

Everything here is transparent, rule-based logic — no black boxes — since
these numbers are the actual offer shown to a store owner and need to be
explainable and auditable (see Phase 5: "Log every decision").

CAVEAT: the specific numbers below (advance multiples, factor rates,
thresholds) are illustrative and industry-informed, not calibrated on
real underwriting data — a production version of this needs a real
finance/risk team to set them, and in the US, several states (e.g.
California, New York) now require specific MCA cost disclosures, which
this simulator does not implement.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


# ------------------------------------------------------------------
# Tunable business parameters
# ------------------------------------------------------------------
MIN_HISTORY_DAYS = 90              # ~3 months — common MCA minimum time-in-business
MIN_AVG_MONTHLY_REVENUE = 8000.0   # many MCA products require $8k-10k+/month minimum
DECLINE_TREND_THRESHOLD = -0.25    # sustained decline beyond this over 90 days is a hard decline
HIGH_VOLATILITY_WARNING = 0.60     # coefficient of variation above this gets flagged in risk scoring

BUSINESS_DAYS_PER_MONTH = 21.7     # ~5-day work week average, used to convert term -> holdback

# Risk-tier -> pricing table (advance multiple of monthly revenue, factor rate, term in months)
RISK_TIER_TERMS = {
    "Low":    {"advance_multiple": 1.5, "factor_rate": 1.15, "term_months": 9},
    "Medium": {"advance_multiple": 1.0, "factor_rate": 1.30, "term_months": 7},
    "High":   {"advance_multiple": 0.5, "factor_rate": 1.45, "term_months": 5},
}

HOLDBACK_MIN = 0.08   # real MCA agreements are contractually bounded — below this isn't viable for the lender
HOLDBACK_MAX = 0.30   # above this risks starving the merchant's cash flow; most lenders cap here


@dataclass
class EligibilityResult:
    eligible: bool
    reasons: List[str] = field(default_factory=list)


@dataclass
class AdvanceOffer:
    projected_90d_sales: float
    avg_daily_sales: float
    avg_monthly_sales: float
    safe_estimate: float
    volatility: float
    max_advance: float
    factor_rate: float
    total_payback: float
    term_months: int
    daily_holdback_pct: float
    risk_tier: str
    risk_score: int
    eligibility: EligibilityResult


def aggregate_forecast(daily_predictions: list) -> float:
    """Sums daily sales predictions into a single horizon total."""
    return float(sum(daily_predictions))


def compute_volatility(daily_predictions: list) -> float:
    """Coefficient of variation (std / mean) of the daily forecasts — the
    standard way to measure how predictable a revenue stream is. Higher
    means the store's day-to-day sales swing more, which is a real risk
    signal lenders weight heavily (a store with erratic sales is harder
    to collect a reliable daily holdback from)."""
    arr = np.array(daily_predictions, dtype=float)
    if arr.mean() <= 0:
        return 0.0
    return float(arr.std() / arr.mean())


def apply_conservative_adjustment(
    projected_total: float,
    volatility: float,
    model_rmspe: Optional[float] = None,
) -> float:
    """
    Shrinks the raw forecast downward before lending against it — the
    "haircut" a real underwriter applies to a forecast they don't fully
    trust. The haircut itself scales with two independent sources of
    uncertainty:
      - volatility: how erratic this specific store's forecast is
      - model_rmspe: how accurate the forecasting model is in general
        (from your validation results) — a more accurate model earns a
        smaller safety margin; a less accurate one needs a bigger one.
    """
    base_haircut = 0.10
    volatility_penalty = min(volatility, 0.5) * 0.30
    rmspe_penalty = min(model_rmspe, 0.5) * 0.20 if model_rmspe is not None else 0.05

    haircut = min(base_haircut + volatility_penalty + rmspe_penalty, 0.45)
    return max(0.0, projected_total * (1 - haircut))


def check_eligibility(
    history_days: int,
    trend_pct_90d: float,
    is_closing_flagged: bool,
    avg_monthly_sales: float,
) -> EligibilityResult:
    """Rule-based gates, run before any money math — reject early if any
    fail, matching how real MCA underwriting screens applicants before
    pricing an offer."""
    reasons = []

    if history_days < MIN_HISTORY_DAYS:
        reasons.append(f"Insufficient sales history ({history_days} days, needs {MIN_HISTORY_DAYS}+)")

    if avg_monthly_sales < MIN_AVG_MONTHLY_REVENUE:
        reasons.append(
            f"Average monthly revenue (${avg_monthly_sales:,.0f}) is below the "
            f"${MIN_AVG_MONTHLY_REVENUE:,.0f} minimum"
        )

    if trend_pct_90d < DECLINE_TREND_THRESHOLD:
        reasons.append(f"Sales trending downward ({trend_pct_90d:.1%} over 90 days)")

    if is_closing_flagged:
        reasons.append("Store flagged as closing")

    return EligibilityResult(eligible=(len(reasons) == 0), reasons=reasons)


def assign_risk_tier(
    volatility: float,
    trend_pct_90d: float,
    history_days: int,
    competition_distance: float,
    store_type: str,
    model_rmspe: Optional[float] = None,
) -> tuple[str, int]:
    """
    Weighted risk score across the factors a real MCA underwriter looks
    at: how predictable the revenue is, whether it's trending up or down,
    how long the business has operated, local competitive pressure, and
    how much to trust the forecast itself. Returns (tier, raw_score) so
    the score itself can be surfaced for auditability.
    """
    score = 0

    # Revenue predictability — the single biggest real-world MCA risk factor
    if volatility > HIGH_VOLATILITY_WARNING:
        score += 3
    elif volatility > 0.35:
        score += 2
    elif volatility > 0.20:
        score += 1

    # Trend direction
    if trend_pct_90d < -0.10:
        score += 2
    elif trend_pct_90d < 0:
        score += 1

    # Time in business — longer history de-risks the loan
    if history_days < 180:
        score += 1
    if history_days < MIN_HISTORY_DAYS:
        score += 1

    # Nearby competition adds uncertainty to future revenue
    if competition_distance < 500:
        score += 1

    # Store type C/D treated as slightly higher variance in this heuristic
    if store_type in ("c", "d"):
        score += 1

    # Model confidence — an uncertain forecast should not be trusted with
    # the same size advance as a well-validated one
    if model_rmspe is not None:
        if model_rmspe > 0.30:
            score += 2
        elif model_rmspe > 0.20:
            score += 1

    if score >= 6:
        tier = "High"
    elif score >= 3:
        tier = "Medium"
    else:
        tier = "Low"

    return tier, score


def calculate_advance_offer(avg_monthly_sales: float, risk_tier: str) -> dict:
    """
    Real MCA pricing mechanics:
      max_advance      = avg_monthly_sales * advance_multiple (by risk tier)
      total_payback     = max_advance * factor_rate            (by risk tier)
      daily_holdback_pct = total_payback / (avg_daily_sales * term_business_days)

    The holdback is DERIVED from the term, not picked directly — that's
    what makes it "true to the industry" rather than an arbitrary ratio.
    It's then clamped to the realistic 8%-30% band real MCA agreements
    operate within.
    """
    terms = RISK_TIER_TERMS[risk_tier]
    avg_daily_sales = avg_monthly_sales / 30.0

    max_advance = avg_monthly_sales * terms["advance_multiple"]
    total_payback = max_advance * terms["factor_rate"]
    term_business_days = terms["term_months"] * BUSINESS_DAYS_PER_MONTH

    if avg_daily_sales > 0 and term_business_days > 0:
        daily_holdback_pct = total_payback / (avg_daily_sales * term_business_days)
    else:
        daily_holdback_pct = 0.0

    daily_holdback_pct = float(np.clip(daily_holdback_pct, HOLDBACK_MIN, HOLDBACK_MAX))

    return {
        "max_advance": round(max_advance, 2),
        "factor_rate": terms["factor_rate"],
        "total_payback": round(total_payback, 2),
        "term_months": terms["term_months"],
        "daily_holdback_pct": round(daily_holdback_pct, 4),
    }


def build_advance_offer(
    daily_predictions: list,
    history_days: int,
    trend_pct_90d: float,
    is_closing_flagged: bool,
    competition_distance: float,
    store_type: str,
    model_rmspe: Optional[float] = None,
) -> AdvanceOffer:
    """End-to-end Phase 3 pipeline: forecast -> volatility -> safe estimate
    -> eligibility -> risk tier -> priced offer."""
    projected_total = aggregate_forecast(daily_predictions)
    avg_daily_sales = projected_total / len(daily_predictions) if daily_predictions else 0.0
    avg_monthly_sales_raw = avg_daily_sales * 30

    volatility = compute_volatility(daily_predictions)
    safe_estimate = apply_conservative_adjustment(projected_total, volatility, model_rmspe)
    safe_avg_monthly_sales = (safe_estimate / len(daily_predictions) * 30) if daily_predictions else 0.0

    eligibility = check_eligibility(history_days, trend_pct_90d, is_closing_flagged, avg_monthly_sales_raw)

    risk_tier, risk_score = assign_risk_tier(
        volatility, trend_pct_90d, history_days, competition_distance, store_type, model_rmspe
    )

    if not eligibility.eligible:
        return AdvanceOffer(
            projected_90d_sales=round(projected_total, 2),
            avg_daily_sales=round(avg_daily_sales, 2),
            avg_monthly_sales=round(avg_monthly_sales_raw, 2),
            safe_estimate=round(safe_estimate, 2),
            volatility=round(volatility, 4),
            max_advance=0.0,
            factor_rate=0.0,
            total_payback=0.0,
            term_months=0,
            daily_holdback_pct=0.0,
            risk_tier=risk_tier,
            risk_score=risk_score,
            eligibility=eligibility,
        )

    offer = calculate_advance_offer(safe_avg_monthly_sales, risk_tier)

    return AdvanceOffer(
        projected_90d_sales=round(projected_total, 2),
        avg_daily_sales=round(avg_daily_sales, 2),
        avg_monthly_sales=round(avg_monthly_sales_raw, 2),
        safe_estimate=round(safe_estimate, 2),
        volatility=round(volatility, 4),
        max_advance=offer["max_advance"],
        factor_rate=offer["factor_rate"],
        total_payback=offer["total_payback"],
        term_months=offer["term_months"],
        daily_holdback_pct=offer["daily_holdback_pct"],
        risk_tier=risk_tier,
        risk_score=risk_score,
        eligibility=eligibility,
    )
