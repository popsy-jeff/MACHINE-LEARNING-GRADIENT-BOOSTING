import { useState } from 'react';
import { api } from '../api';
import { KpiCard, ForecastLineChart, PageTitle, PAGE_ICONS, Banner } from '../components/Viz';

export default function BatchPrediction() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.predictBatch(file);
      setResult(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadCsv = () => {
    if (!result) return;
    const rows = result.rows;
    const headers = Object.keys(rows[0]);
    const csv = [headers.join(','), ...rows.map((r) => headers.map((h) => r[h]).join(','))].join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'batch_predictions.csv';
    a.click();
    URL.revokeObjectURL(url);
  };

  const trendData = result?.rows
    ? Object.values(
        result.rows.reduce((acc, r) => {
          const d = r.Date;
          acc[d] = acc[d] || { date: d, predicted_sales: 0 };
          acc[d].predicted_sales += r.Predicted_Sales;
          return acc;
        }, {})
      ).sort((a, b) => a.date.localeCompare(b.date))
    : [];

  return (
    <div className="main-content">
      <div className="page-header">
        <PageTitle icon={PAGE_ICONS.batch}>Batch Sales Prediction</PageTitle>
        <p className="page-subtitle">
          Upload a CSV with columns: Store, Date, Promo, Promo2, SchoolHoliday, StateHoliday,
          StoreType, Assortment, CompetitionDistance (and optionally Open).
        </p>
      </div>

      <form onSubmit={submit} className="card">
        <div className="field">
          <label>CSV file</label>
          <input type="file" accept=".csv" onChange={(e) => setFile(e.target.files[0])} />
        </div>
        <button className="btn-3d" type="submit" disabled={loading || !file}>
          {loading ? 'Predicting…' : 'Run Batch Prediction'}
        </button>
      </form>

      {error && <Banner type="red">{error}</Banner>}

      {result && (
        <>
          <hr className="divider" />
          <div className="card-grid">
            <KpiCard label="Total Predicted Revenue" value={`$${result.total_predicted_revenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="blue" />
            <KpiCard label="Average per Row" value={`$${result.average_predicted.toLocaleString(undefined, { maximumFractionDigits: 0 })}`} signal="orange" />
            <KpiCard label="Rows Predicted" value={result.row_count.toLocaleString()} signal="orange" />
          </div>

          {trendData.length > 1 && (
            <ForecastLineChart data={trendData} title="Predicted sales over time" xKey="date" yKey="predicted_sales" />
          )}

          <div className="data-table-wrap" style={{ marginTop: 20 }}>
            <table className="data-table">
              <thead>
                <tr>{Object.keys(result.rows[0]).map((k) => <th key={k}>{k}</th>)}</tr>
              </thead>
              <tbody>
                {result.rows.slice(0, 50).map((row, i) => (
                  <tr key={i}>{Object.values(row).map((v, j) => <td key={j}>{String(v)}</td>)}</tr>
                ))}
              </tbody>
            </table>
          </div>
          {result.rows.length > 50 && (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>Showing first 50 of {result.rows.length} rows.</p>
          )}

          <button className="btn-3d" style={{ marginTop: 12 }} onClick={downloadCsv}>Download full CSV</button>
        </>
      )}
    </div>
  );
}
