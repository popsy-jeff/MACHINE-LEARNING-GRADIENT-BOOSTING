import { useEffect, useState } from 'react';
import { api } from '../api';
import { KpiCard, PageTitle, PAGE_ICONS, Banner } from '../components/Viz';
import { Sparkles, ListChecks, BarChart3, Wallet, ShieldCheck } from 'lucide-react';

export default function Home() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.health().then(setHealth).catch((e) => setError(e.message));
  }, []);

  return (
    <div className="main-content">
      <div className="page-header">
        <PageTitle icon={PAGE_ICONS.home}>Rossmann Sales Forecasting &amp; Revenue-Based Financing</PageTitle>
        <p className="page-subtitle">
          This app turns a trained sales-forecasting model into a working finance product:
          a merchant cash advance tool that lends stores money against their predicted
          future sales, repaid as a daily percentage of revenue.
        </p>
      </div>

      <div className="card-grid">
        <KpiCard
          label="Model Status"
          value={health ? (health.is_demo ? 'Demo Model' : 'Trained Model') : '…'}
          sub={health ? `version ${health.model_version}` : ''}
          signal={health?.is_demo ? 'yellow' : 'green'}
        />
        <KpiCard label="Pipeline Stage" value="Phase 3" sub="Business logic layer active" signal="blue" />
        <KpiCard label="Pages Available" value="5" sub="Prediction → Financing → Ops" signal="orange" />
      </div>

      <hr className="divider" />

      <h3>Navigate</h3>
      <div className="form-grid">
        <ul style={{ color: 'var(--text-primary)', lineHeight: 2, listStyle: 'none', padding: 0 }}>
          <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}><Sparkles size={16} color="var(--green)" /> <b>Single Prediction</b> — forecast one store's sales for one day</li>
          <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}><ListChecks size={16} color="var(--green)" /> <b>Batch Prediction</b> — upload a CSV, get forecasts for every row</li>
          <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}><BarChart3 size={16} color="var(--green)" /> <b>Model Performance</b> — validation metrics and feature importance</li>
        </ul>
        <ul style={{ color: 'var(--text-primary)', lineHeight: 2, listStyle: 'none', padding: 0 }}>
          <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}><Wallet size={16} color="var(--green)" /> <b>Advance Calculator</b> — 90-day forecast → financing offer (Phase 3)</li>
          <li style={{ display: 'flex', alignItems: 'center', gap: 10 }}><ShieldCheck size={16} color="var(--green)" /> <b>Risk Dashboard</b> — flagged applications, audit log (Phase 3–5)</li>
        </ul>
      </div>

      <hr className="divider" />

      {error && <Banner type="red">Could not reach the API: {error}. Is the backend running?</Banner>}
      {health && health.is_demo && (
        <Banner type="yellow">
          No trained model found on the backend — running with a <b>demo model</b> trained
          on synthetic data so the app is fully click-through-able. Export your real model and
          drop <code>rossmann_sales_model.pkl</code> + <code>feature_cols.pkl</code> into the
          backend's <code>models/</code> folder to get real predictions.
        </Banner>
      )}
      {health && !health.is_demo && (
        <Banner type="green">Loaded trained model — version {health.model_version}</Banner>
      )}
    </div>
  );
}
