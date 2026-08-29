import { useEffect, useState } from 'react';
import { api } from '../api';
import { KpiCard, GaugeChart, ImportanceBarChart, PageTitle, PAGE_ICONS, Banner } from '../components/Viz';

export default function ModelPerformance() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.modelMetrics().then(setData).catch((e) => setError(e.message));
  }, []);

  if (error) return <div className="main-content"><Banner type="red">{error}</Banner></div>;
  if (!data) return <div className="main-content">Loading…</div>;

  const displayedRmspe = data.metrics?.rmspe ?? data.reference_runs[data.reference_runs.length - 1].rmspe;

  return (
    <div className="main-content">
      <div className="page-header">
        <PageTitle icon={PAGE_ICONS.performance}>Model Performance</PageTitle>
      </div>

      <h3>Validation Metrics</h3>
      <div className="form-grid" style={{ gridTemplateColumns: '1fr 1.4fr' }}>
        <GaugeChart value={displayedRmspe} min={0} max={0.5} title="Validation RMSPE" goodIsLow />
        <div>
          <div className="card-grid" style={{ gridTemplateColumns: '1fr' }}>
            <KpiCard label="Model Version" value={data.model_version} signal="green" />
            <KpiCard label="Trials Searched" value={String(data.metrics?.n_trials ?? data.reference_runs.length)} signal="yellow" />
          </div>
        </div>
      </div>

      {data.metrics?.best_params && (
        <>
          <h3 style={{ marginTop: 24 }}>Best Hyperparameters (from Optuna search)</h3>
          <div className="card mono" style={{ whiteSpace: 'pre-wrap' }}>{JSON.stringify(data.metrics.best_params, null, 2)}</div>
        </>
      )}

      {!data.metrics && (
        <>
          <h3 style={{ marginTop: 24 }}>Recent search runs (from your notebook)</h3>
          <div className="data-table-wrap">
            <table className="data-table">
              <thead>
                <tr><th>Trials</th><th>RMSPE</th><th>Max Depth</th><th>N Estimators</th><th>Learning Rate</th></tr>
              </thead>
              <tbody>
                {data.reference_runs.map((r, i) => (
                  <tr key={i}>
                    <td>{r.trials}</td><td>{r.rmspe.toFixed(6)}</td><td>{r.max_depth}</td>
                    <td>{r.n_estimators}</td><td>{r.learning_rate.toFixed(4)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            These three runs converged around RMSPE ≈ 0.170 — a stable performance plateau.
          </p>
        </>
      )}

      <hr className="divider" />
      <h3>Feature Importance</h3>
      {data.feature_importance.length > 0 ? (
        <ImportanceBarChart data={data.feature_importance} title="Top 15 features" />
      ) : (
        <p style={{ color: 'var(--text-muted)' }}>Could not compute feature importance.</p>
      )}
    </div>
  );
}
