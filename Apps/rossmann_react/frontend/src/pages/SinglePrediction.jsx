import { useState } from 'react';
import { api } from '../api';
import { KpiCard, GlowPill, PageTitle, PAGE_ICONS, Banner } from '../components/Viz';

const today = new Date().toISOString().slice(0, 10);

export default function SinglePrediction() {
  const [form, setForm] = useState({
    store_id: 1,
    forecast_date: today,
    is_open: 1,
    promo: 0,
    school_holiday: 0,
    state_holiday: '0',
    store_type: 'a',
    assortment: 'a',
    competition_distance: 500,
    promo2: 0,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const update = (key, value) => setForm((f) => ({ ...f, [key]: value }));

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.predict({
        ...form,
        store_id: Number(form.store_id),
        is_open: Number(form.is_open),
        promo: Number(form.promo),
        school_holiday: Number(form.school_holiday),
        competition_distance: Number(form.competition_distance),
        promo2: Number(form.promo2),
      });
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="main-content">
      <div className="page-header">
        <PageTitle icon={PAGE_ICONS.predict}>Single Store Sales Prediction</PageTitle>
      </div>

      <form onSubmit={submit} className="card">
        <div className="form-grid">
          <div>
            <div className="field">
              <label>Store ID</label>
              <input type="number" min={1} value={form.store_id} onChange={(e) => update('store_id', e.target.value)} />
            </div>
            <div className="field">
              <label>Forecast date</label>
              <input type="date" value={form.forecast_date} onChange={(e) => update('forecast_date', e.target.value)} />
            </div>
            <div className="field">
              <label>Store open that day?</label>
              <select value={form.is_open} onChange={(e) => update('is_open', e.target.value)}>
                <option value={1}>Open</option>
                <option value={0}>Closed</option>
              </select>
            </div>
            <div className="field">
              <label>Running a promo that day?</label>
              <select value={form.promo} onChange={(e) => update('promo', e.target.value)}>
                <option value={0}>No</option>
                <option value={1}>Yes</option>
              </select>
            </div>
            <div className="field">
              <label>School holiday?</label>
              <select value={form.school_holiday} onChange={(e) => update('school_holiday', e.target.value)}>
                <option value={0}>No</option>
                <option value={1}>Yes</option>
              </select>
            </div>
            <div className="field">
              <label>State holiday</label>
              <select value={form.state_holiday} onChange={(e) => update('state_holiday', e.target.value)}>
                <option value="0">0 = none</option>
                <option value="a">a</option>
                <option value="b">b</option>
                <option value="c">c</option>
              </select>
            </div>
          </div>
          <div>
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
            <div className="field">
              <label>Enrolled in Promo2 (ongoing promo)?</label>
              <select value={form.promo2} onChange={(e) => update('promo2', e.target.value)}>
                <option value={0}>No</option>
                <option value={1}>Yes</option>
              </select>
            </div>
          </div>
        </div>
        <button className="btn-3d" type="submit" disabled={loading}>
          {loading ? 'Predicting…' : 'Predict Sales'}
        </button>
      </form>

      {error && <Banner type="red">{error}</Banner>}

      {result && (
        <>
          <hr className="divider" />
          <div className="card-grid" style={{ gridTemplateColumns: '1.3fr 1fr 1fr' }}>
            <KpiCard
              label="Predicted Sales"
              value={`$${result.predicted_sales.toLocaleString(undefined, { maximumFractionDigits: 2 })}`}
              sub={`Store #${form.store_id} · ${form.forecast_date}`}
              signal="blue"
            />
            <div className="card">
              <div className="kpi-label" style={{ marginBottom: 8 }}>Store status</div>
              <GlowPill label={Number(form.is_open) === 1 ? 'Open' : 'Closed'} signal={Number(form.is_open) === 1 ? 'green' : 'red'} />
            </div>
            <div className="card">
              <div className="kpi-label" style={{ marginBottom: 8 }}>Promo</div>
              <GlowPill label={Number(form.promo) === 1 ? 'Running' : 'None'} signal={Number(form.promo) === 1 ? 'green' : 'yellow'} />
            </div>
          </div>

          {result.is_demo && <Banner type="yellow">This prediction is from the demo model, not your real trained model.</Banner>}

          <details style={{ marginTop: 16 }}>
            <summary style={{ cursor: 'pointer', color: 'var(--text-muted)' }}>See the exact features sent to the model</summary>
            <div className="data-table-wrap" style={{ marginTop: 10 }}>
              <table className="data-table">
                <thead><tr><th>Feature</th><th>Value</th></tr></thead>
                <tbody>
                  {Object.entries(result.features).map(([k, v]) => (
                    <tr key={k}><td>{k}</td><td className="mono">{String(v)}</td></tr>
                  ))}
                </tbody>
              </table>
            </div>
          </details>
        </>
      )}
    </div>
  );
}
