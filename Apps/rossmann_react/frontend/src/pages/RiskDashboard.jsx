import { useEffect, useState } from 'react';
import { api } from '../api';
import { KpiCard, DonutChart, GlowPill, PageTitle, PAGE_ICONS, Banner, RiskIcon, EligibilityIcon } from '../components/Viz';

export default function RiskDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.auditLog().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="main-content"><Banner type="red">{error}</Banner></div>;
  if (!data) return <div className="main-content">Loading…</div>;

  if (!data.rows.length) {
    return (
      <div className="main-content">
        <div className="page-header"><PageTitle icon={PAGE_ICONS.risk}>Ops / Risk Dashboard</PageTitle></div>
        <p style={{ color: 'var(--text-muted)' }}>No decisions logged yet — run the Advance Calculator to generate some.</p>
      </div>
    );
  }

  const flagged = data.rows.filter((r) => r.risk_tier === 'High' || r.eligible === false);
  const tierData = Object.entries(data.summary.tier_counts).map(([name, value]) => ({ name, value }));

  return (
    <div className="main-content">
      <div className="page-header"><PageTitle icon={PAGE_ICONS.risk}>Ops / Risk Dashboard</PageTitle></div>

      <div className="form-grid" style={{ gridTemplateColumns: '2fr 1fr' }}>
        <div className="card-grid" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
          <KpiCard label="Total Applications" value={String(data.summary.total)} signal="blue" />
          <KpiCard label="Approved" value={String(data.summary.approved)} signal="green" />
          <KpiCard label="Declined" value={String(data.summary.declined)} signal="red" />
          <KpiCard label="High Risk" value={String(data.summary.high_risk)} signal={data.summary.high_risk ? 'red' : 'green'} />
        </div>
        <DonutChart data={tierData} title="Risk tier mix" />
      </div>

      <hr className="divider" />
      <h3>Flagged for Review</h3>
      {flagged.length === 0 ? (
        <GlowPill label="No applications currently flagged" signal="green" />
      ) : (
        <DecisionTable rows={flagged} />
      )}

      <hr className="divider" />
      <h3>Full Decision Log</h3>
      <DecisionTable rows={data.rows} />

      <a className="btn-3d" style={{ display: 'inline-block', marginTop: 16 }} href={api.auditLogCsvUrl()} download>
        Download full audit log as CSV
      </a>
    </div>
  );
}

function DecisionTable({ rows }) {
  const cols = ['timestamp', 'store_id', 'risk_tier', 'eligible', 'avg_monthly_sales', 'max_advance', 'factor_rate', 'term_months', 'daily_holdback_pct'];
  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead><tr>{cols.map((c) => <th key={c}>{c}</th>)}</tr></thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td>{r.timestamp}</td>
              <td>{r.store_id}</td>
              <td><RiskIcon tier={r.risk_tier} />{r.risk_tier}</td>
              <td><EligibilityIcon eligible={r.eligible} />{r.eligible ? 'Approved' : 'Declined'}</td>
              <td>${Number(r.avg_monthly_sales ?? 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
              <td>${Number(r.max_advance).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
              <td>{r.factor_rate ? Number(r.factor_rate).toFixed(2) : '—'}</td>
              <td>{r.term_months ? `${r.term_months} mo` : '—'}</td>
              <td>{(Number(r.daily_holdback_pct) * 100).toFixed(1)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
