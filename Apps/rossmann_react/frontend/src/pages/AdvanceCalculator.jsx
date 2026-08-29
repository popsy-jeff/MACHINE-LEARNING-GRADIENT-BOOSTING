import { useState } from 'react';
import { api } from '../api';
import { KpiCard, GlowPill, riskSignal, GaugeChart, ForecastLineChart, PageTitle, PAGE_ICONS, Banner } from '../components/Viz';
import Modal from '../components/Modal';

const today = new Date().toISOString().slice(0, 10);

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
  const [modalOpen, setModalOpen] = useState(false);

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
      // Surface a decision modal automatically for outcomes that need
      // attention — declined (red) or approved-but-high-risk (orange).
      if (!res.eligible || res.risk_tier === 'High') setModalOpen(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const modalType = offer ? (!offer.eligible ? 'red' : 'orange') : 'red';

  return (
    <div className="main-content">
      <div className="page-header">
        <PageTitle icon={PAGE_ICONS.advance}>Revenue-Based Financing — Advance Calculator</PageTitle>
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

      {error && <Banner type="red">{error}</Banner>}

      {offer && (
        <>
          <hr className="divider" />
          <h3>Results</h3>

          {!offer.eligible ? (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                <GlowPill label="Not eligible for an advance" signal="red" />
                <button type="button" className="btn-3d" style={{ color: 'var(--red)', borderColor: 'var(--red-dim)' }} onClick={() => setModalOpen(true)}>
                  View decline reasons
                </button>
              </div>
              <ul style={{ color: 'var(--text-primary)', marginTop: 12 }}>
                {offer.decline_reasons.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                Risk tier for reference: {offer.risk_tier} (score {offer.risk_score})
              </p>
            </>
          ) : (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
                <GlowPill label="Eligible" signal="green" />
                {offer.risk_tier === 'High' && (
                  <button type="button" className="btn-3d" style={{ color: 'var(--orange)', borderColor: 'var(--orange-dim)' }} onClick={() => setModalOpen(true)}>
                    View risk flag
                  </button>
                )}
              </div>

              <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 14, marginBottom: 6 }}>Forecast summary</p>
              <div className="card-grid">
                <KpiCard label="90-Day Projected Sales" value={`$${offer.projected_90d_sales.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="blue" />
                <KpiCard label="Avg Monthly Revenue" value={`$${offer.avg_monthly_sales.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="blue" />
                <KpiCard label="Safe Estimate (post-haircut)" value={`$${offer.safe_estimate.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="yellow" />
                <KpiCard label="Revenue Volatility" value={`${(offer.volatility * 100).toFixed(0)}%`} sub="coefficient of variation" signal={offer.volatility > 0.35 ? 'red' : offer.volatility > 0.2 ? 'yellow' : 'green'} />
              </div>

              <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 20, marginBottom: 6 }}>Offer terms (MCA pricing)</p>
              <div className="card-grid">
                <KpiCard label="Max Advance" value={`$${offer.max_advance.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="green" />
                <KpiCard label="Factor Rate" value={offer.factor_rate.toFixed(2)} sub={`total payback $${offer.total_payback.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="orange" />
                <KpiCard label="Term" value={`${offer.term_months} mo`} signal="blue" />
                <KpiCard label="Daily Holdback %" value={`${(offer.daily_holdback_pct * 100).toFixed(1)}%`} sub="of daily card/bank sales" signal="orange" />
              </div>

              <div className="form-grid" style={{ gridTemplateColumns: '1fr 1fr', marginTop: 20 }}>
                <KpiCard label="Risk Tier" value={offer.risk_tier} sub={`risk score: ${offer.risk_score}`} signal={riskSignal(offer.risk_tier)} />
                <GaugeChart value={offer.risk_score} min={0} max={10} title="Risk Score (0-10)" goodIsLow />
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

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        type={modalType}
        title={offer && !offer.eligible ? 'Application declined' : 'High risk — approved with caution'}
      >
        {offer && !offer.eligible && (
          <>
            <p>This application did not meet the eligibility criteria for an advance:</p>
            <ul style={{ margin: 0, paddingLeft: 18 }}>
              {offer.decline_reasons.map((r, i) => <li key={i}>{r}</li>)}
            </ul>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 10 }}>
              Risk tier: {offer.risk_tier} (score {offer.risk_score})
            </p>
          </>
        )}
        {offer && offer.eligible && offer.risk_tier === 'High' && (
          <>
            <p>This store is approved, but landed in the <b>High</b> risk tier (score {offer.risk_score}/10).</p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
              Consider a smaller advance amount or a shorter term before finalizing this offer.
            </p>
          </>
        )}
      </Modal>
    </div>
  );
}
