import {
  RadialBarChart, RadialBar, PieChart, Pie, Cell, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, Tooltip, LineChart, Line, Area, AreaChart, CartesianGrid,
} from 'recharts';
import {
  Home, Sparkles, ListChecks, BarChart3, Wallet, ShieldCheck,
  CheckCircle2, XCircle, AlertTriangle, AlertCircle, TriangleAlert,
} from 'lucide-react';

export const PAGE_ICONS = {
  home: Home,
  predict: Sparkles,
  batch: ListChecks,
  performance: BarChart3,
  advance: Wallet,
  risk: ShieldCheck,
};

export function PageTitle({ icon: Icon, children }) {
  return (
    <h1 style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
      <Icon size={26} strokeWidth={2.2} color="var(--green)" />
      {children}
    </h1>
  );
}

const RISK_ICON = { Low: CheckCircle2, Medium: AlertTriangle, High: AlertCircle };

export function RiskIcon({ tier, size = 14 }) {
  const Icon = RISK_ICON[tier] || AlertTriangle;
  const color = { Low: '#39E67A', Medium: '#F4C542', High: '#FF5C5C' }[tier] || '#F4C542';
  return <Icon size={size} color={color} style={{ verticalAlign: 'middle', marginRight: 5 }} />;
}

export function EligibilityIcon({ eligible, size = 14 }) {
  const Icon = eligible ? CheckCircle2 : XCircle;
  const color = eligible ? '#39E67A' : '#FF5C5C';
  return <Icon size={size} color={color} style={{ verticalAlign: 'middle', marginRight: 5 }} />;
}

export function Banner({ type = 'yellow', children }) {
  const Icon = type === 'green' ? CheckCircle2 : type === 'red' ? XCircle : TriangleAlert;
  return (
    <div className={`banner banner-${type}`} style={{ display: 'flex', alignItems: 'flex-start', gap: 10 }}>
      <Icon size={18} style={{ flexShrink: 0, marginTop: 1 }} />
      <div>{children}</div>
    </div>
  );
}

const SIGNAL = { green: '#39E67A', yellow: '#F4C542', red: '#FF5C5C' };

export function KpiCard({ label, value, sub, signal = 'green' }) {
  return (
    <div className="kpi-card" style={{ '--kpi-color': SIGNAL[signal] }}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      {sub && <div className="kpi-sub">{sub}</div>}
    </div>
  );
}

export function GlowPill({ label, signal = 'green', dot = true }) {
  return (
    <span className="glow-pill" style={{ '--pill-color': SIGNAL[signal] }}>
      {dot && <span className="glow-dot" style={{ '--pill-color': SIGNAL[signal] }} />}
      {label}
    </span>
  );
}

export function riskSignal(tier) {
  return { Low: 'green', Medium: 'yellow', High: 'red' }[tier] || 'yellow';
}

export function GaugeChart({ value, min = 0, max = 1, title, suffix = '', goodIsLow = true }) {
  const pct = Math.max(0, Math.min(100, ((value - min) / (max - min)) * 100));
  const color = goodIsLow
    ? (pct < 33 ? SIGNAL.green : pct < 66 ? SIGNAL.yellow : SIGNAL.red)
    : (pct < 33 ? SIGNAL.red : pct < 66 ? SIGNAL.yellow : SIGNAL.green);
  const data = [{ name: title, value: pct, fill: color }];

  return (
    <div className="card" style={{ textAlign: 'center' }}>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginBottom: 4 }}>{title}</div>
      <ResponsiveContainer width="100%" height={160}>
        <RadialBarChart
          innerRadius="70%" outerRadius="100%" data={data}
          startAngle={90} endAngle={-270}
        >
          <RadialBar dataKey="value" cornerRadius={20} background={{ fill: 'var(--bg-elevated)' }} />
        </RadialBarChart>
      </ResponsiveContainer>
      <div className="mono" style={{ marginTop: -70, fontSize: '1.4rem', fontWeight: 600, color }}>
        {value.toFixed(suffix === '%' ? 1 : 4)}{suffix}
      </div>
    </div>
  );
}

const TIER_COLORS = { Low: SIGNAL.green, Medium: SIGNAL.yellow, High: SIGNAL.red };

export function DonutChart({ data, title }) {
  // data: [{ name: 'Low', value: 5 }, ...]
  return (
    <div className="card">
      <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.9rem', marginBottom: 8 }}>{title}</div>
      <ResponsiveContainer width="100%" height={220}>
        <PieChart>
          <Pie data={data} dataKey="value" nameKey="name" innerRadius="60%" outerRadius="85%" paddingAngle={2}>
            {data.map((entry) => (
              <Cell key={entry.name} fill={TIER_COLORS[entry.name] || SIGNAL.green} stroke="var(--bg-void)" strokeWidth={2} />
            ))}
          </Pie>
          <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }} />
        </PieChart>
      </ResponsiveContainer>
      <div style={{ display: 'flex', gap: 14, justifyContent: 'center', marginTop: 4 }}>
        {data.map((d) => (
          <div key={d.name} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: TIER_COLORS[d.name] || SIGNAL.green }} />
            {d.name} ({d.value})
          </div>
        ))}
      </div>
    </div>
  );
}

export function ImportanceBarChart({ data, title }) {
  // data: [{ feature, importance }]
  return (
    <div className="card">
      <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.9rem', marginBottom: 8 }}>{title}</div>
      <ResponsiveContainer width="100%" height={380}>
        <BarChart data={data} layout="vertical" margin={{ left: 20, right: 20 }}>
          <CartesianGrid stroke="var(--border)" horizontal={false} />
          <XAxis type="number" tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
          <YAxis type="category" dataKey="feature" width={130} tick={{ fill: 'var(--text-muted)', fontSize: 11 }} />
          <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }} />
          <Bar dataKey="importance" fill={SIGNAL.green} radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export function ForecastLineChart({ data, title, xKey = 'date', yKey = 'predicted_sales' }) {
  return (
    <div className="card">
      <div style={{ color: 'var(--text-primary)', fontWeight: 600, fontSize: '0.9rem', marginBottom: 8 }}>{title}</div>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data} margin={{ left: 0, right: 10, top: 10, bottom: 0 }}>
          <defs>
            <linearGradient id="fillGreen" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={SIGNAL.green} stopOpacity={0.35} />
              <stop offset="95%" stopColor={SIGNAL.green} stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--border)" vertical={false} />
          <XAxis dataKey={xKey} tick={{ fill: 'var(--text-muted)', fontSize: 10 }} minTickGap={30} />
          <YAxis tick={{ fill: 'var(--text-muted)', fontSize: 10 }} />
          <Tooltip contentStyle={{ background: 'var(--bg-elevated)', border: '1px solid var(--border)', borderRadius: 8, color: 'var(--text-primary)' }} />
          <Area type="monotone" dataKey={yKey} stroke={SIGNAL.green} strokeWidth={2} fill="url(#fillGreen)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
