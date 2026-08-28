import { useState } from 'react';
import { api } from '../api';
import { KpiCard, GlowPill, riskSignal, GaugeChart, ForecastLineChart } from '../components/Viz';

const today = new Date().toISOString().slice(0, 10);

const RISK_SCORE = { Low: 20, Medium: 55, High: 90 };

export default function AdvanceCalculator() {
  const [form, setForm] = useState({
    store_id: 1,
    start_date: today,
    store_type: 'a',
    assortment: 'a',
    competition_distance: 500,
    promo: 0,
    promo2: 0,
    history_days: 365,
    trend_pct_90d: 0,
    is_closing_flagged: false,
  });
  const [offer, setOffer] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const update = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.advanceOffer({
        ...form,
        store_id: Number(form.store_id),
        competition_distance: Number(form.competition_distance),
        promo: Number(form.promo),
        promo2: Number(form.promo2),
        history_days: Number(form.history_days),
        trend_pct_90d: Number(form.trend_pct_90d),
      });
      setOffer(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-content">
      <div className="page-header">
        <h1>💰 Revenue-Based Financing — Advance Calculator</h1>
      </div>

      <form onSubmit={submit} className="card">
        <div className="form-grid">
          <div>
            <div className="field">
              <label>Store ID</label>
              <input type="number" min={1} value={form.store_id} onChange={(e) => update('store_id', e.target.value)} />
            </div>
            <div className="field">
              <label>Forecast start date</label>
              <input type="date" value={form.start_date} onChange={(e) => update('start_date', e.target.value)} />
            </div>
            <div className="field">
              <label>Store type</label>
              <select value={form.store_type} onChange={(e) => update('store_type', e.target.value)}>
                {['a', 'b', 'c', 'd'].map((v) => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Assortment level</label>
              <select value={form.assortment} onChange={(e) => update('assortment', e.target.value)}>
                {['a', 'b', 'c'].map((v) => <option key={v} value={v}>{v}</option>)}
              </select>
            </div>
            <div className="field">
              <label>Competition distance (meters)</label>
              <input type="number" min={0} value={form.competition_distance} onChange={(e) => update('competition_distance', e.target.value)} />
            </div>
          </div>
          <div>
            <div className="field">
              <label>Currently running Promo?</label>
              <select value={form.promo} onChange={(e) => update('promo', e.target.value)}>
                <option value={0}>No</option><option value={1}>Yes</option>
              </select>
            </div>
            <div className="field">
              <label>Enrolled in Promo2?</label>
              <select value={form.promo2} onChange={(e) => update('promo2', e.target.value)}>
                <option value={0}>No</option><option value={1}>Yes</option>
              </select>
            </div>
            <div className="field">
              <label>Days of sales history on record</label>
              <input type="number" min={0} value={form.history_days} onChange={(e) => update('history_days', e.target.value)} />
            </div>
            <div className="field">
              <label>90-day sales trend (%, negative = declining)</label>
              <input type="number" step="0.01" value={form.trend_pct_90d} onChange={(e) => update('trend_pct_90d', e.target.value)} />
            </div>
            <div className="field">
              <label>Flagged as potentially closing?</label>
              <select value={form.is_closing_flagged} onChange={(e) => update('is_closing_flagged', e.target.value === 'true')}>
                <option value="false">No</option><option value="true">Yes</option>
              </select>
            </div>
          </div>
        </div>
        <button className="btn-3d" type="submit" disabled={loading}>
          {loading ? 'Calculating…' : 'Calculate Offer'}
        </button>
      </form>

      {error && <div className="banner banner-red">⚠️ {error}</div>}

      {offer && (
        <>
          <hr className="divider" />
          <h3>Results</h3>

          {!offer.eligible ? (
            <>
              <GlowPill label="Not eligible for an advance" signal="red" />
              <ul style={{ color: 'var(--text-primary)', marginTop: 12 }}>
                {offer.decline_reasons.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </>
          ) : (
            <>
              <GlowPill label="Eligible" signal="green" />
              <div className="card-grid" style={{ marginTop: 16 }}>
                <KpiCard label="90-Day Projected Sales" value={`$${offer.projected_90d_sales.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="green" />
                <KpiCard label="Safe Estimate (post-haircut)" value={`$${offer.safe_estimate.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="yellow" />
                <KpiCard label="Risk Tier" value={offer.risk_tier} signal={riskSignal(offer.risk_tier)} />
              </div>
              <div className="form-grid" style={{ gridTemplateColumns: '1fr 1fr 1fr', marginTop: 16 }}>
                <KpiCard label="Max Advance Offer" value={`$${offer.max_advance.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="green" />
                <KpiCard label="Daily Holdback %" value={`${(offer.daily_holdback_pct * 100).toFixed(1)}%`} signal="yellow" />
                <GaugeChart value={RISK_SCORE[offer.risk_tier] ?? 55} min={0} max={100} title="Risk Score" goodIsLow />
              </div>
            </>
          )}

          <div style={{ marginTop: 20 }}>
            <ForecastLineChart data={offer.daily_forecast} title="90-day sales forecast" xKey="date" yKey="predicted_sales" />
          </div>

          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 10 }}>
            This decision has been logged to the audit trail — see Risk Dashboard.
          </p>
        </>
      )}
    </div>
  );
}
