import { NavLink } from 'react-router-dom';
import {
  Search, Home, Sparkles, ListChecks, BarChart3, Wallet, ShieldCheck,
} from 'lucide-react';
import ThemeToggle from './ThemeToggle';
import './Sidebar.css';

const NAV_ITEMS = [
  { to: '/', label: 'Overview', icon: Home, end: true },
  { to: '/predict', label: 'Single Prediction', icon: Sparkles },
  { to: '/batch', label: 'Batch Prediction', icon: ListChecks },
  { to: '/performance', label: 'Model Performance', icon: BarChart3 },
  { to: '/advance', label: 'Advance Calculator', icon: Wallet },
  { to: '/risk', label: 'Risk Dashboard', icon: ShieldCheck },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-badge">RS</div>
        <div>
          <div className="sidebar-brand-name">Rossmann Finance</div>
          <div className="sidebar-brand-sub">AI Sales &amp; Lending</div>
        </div>
      </div>

      <div className="sidebar-search">
        <Search size={16} />
        <input type="text" placeholder="Search store ID…" />
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => `sidebar-nav-item${isActive ? ' active' : ''}`}
          >
            <Icon size={18} strokeWidth={2} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <ThemeToggle />
      </div>
    </aside>
  );
}
