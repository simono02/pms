import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import ClientsView from './views/ClientsView';
import ProjectsView from './views/ProjectsView';
import StaffView from './views/StaffView';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import './AdminDashboard.css';

/* ══════════════════════════════════════════════════════
   ROOT
══════════════════════════════════════════════════════ */
const AdminDashboard = () => {
  const [activeView,       setActiveView]       = useState('dashboard');
  const [stats,            setStats]            = useState({
    users:    { total: 0, staff: 0, active: 0 },
    projects: { total: 0, pending: 0, in_progress: 0, completed: 0 },
    revenue:  0,
  });
  const [loading,          setLoading]          = useState(true);
  const [error,            setError]            = useState(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [theme,            setTheme]            = useState('dark');
  const [time,             setTime]             = useState(new Date());

  /* live clock */
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  useEffect(() => { fetchDashboardStats(); }, []);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const response = await adminService.getDashboardStats();
      setStats(response.stats || {
        users:    { total: 0, staff: 0, active: 0 },
        projects: { total: 0, pending: 0, in_progress: 0, completed: 0 },
        revenue:  0,
      });
      setError(null);
    } catch (e) {
      console.error('Failed to fetch dashboard stats:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleDataUpdate = () => fetchDashboardStats();

  const fmt12   = d => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  const fmtDate = d => d.toLocaleDateString([],  { weekday: 'short', month: 'short', day: 'numeric' });

  const greeting = () => {
    const h = time.getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const sidebarW = sidebarCollapsed ? 72 : 220;

  const navItems = [
    { id: 'dashboard', icon: '⬡', label: 'Dashboard' },
    { id: 'staff',     icon: '◈', label: 'Staff'     },
    { id: 'projects',  icon: '◎', label: 'Projects'  },
    { id: 'clients',   icon: '◷', label: 'Clients'   },
  ];

  if (loading) return (
    <div className="ad-loading-screen">
      <div className="ad-loader-ring" />
      <p>Loading dashboard…</p>
    </div>
  );

  return (
    <div className={`ad-root ad-${theme}`}>
      {/* ambient orbs — dark only */}
      {theme === 'dark' && <>
        <div className="ad-orb ad-orb-1" />
        <div className="ad-orb ad-orb-2" />
        <div className="ad-orb ad-orb-3" />
      </>}

      {/* ── FIXED SIDEBAR ── */}
      <aside className={`ad-sidebar${sidebarCollapsed ? ' ad-sidebar--collapsed' : ''}`}>
        <div className="ad-brand">
          <div className="ad-brand-icon">A</div>
          {!sidebarCollapsed && <span className="ad-brand-name">ResearchPro</span>}
        </div>

        <nav className="ad-nav">
          {navItems.map(n => (
            <button
              key={n.id}
              className={`ad-nav-btn${activeView === n.id ? ' ad-nav-active' : ''}`}
              onClick={() => setActiveView(n.id)}
              title={sidebarCollapsed ? n.label : undefined}
            >
              <span className="ad-nav-icon">{n.icon}</span>
              {!sidebarCollapsed && <span>{n.label}</span>}
            </button>
          ))}
        </nav>

        <button
          className="ad-collapse-btn"
          onClick={() => setSidebarCollapsed(c => !c)}
          title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        >
          {sidebarCollapsed ? '▶' : '◀'}
        </button>
      </aside>

      {/* ── RIGHT COLUMN ── */}
      <div className="ad-body" style={{ marginLeft: sidebarW }}>

        {/* ── FIXED HEADER ── */}
        <header className="ad-header" style={{ left: sidebarW }}>
          <div className="ad-header-left">
            <span className="ad-page-tag">
              {navItems.find(n => n.id === activeView)?.label}
            </span>
            <span className="ad-header-greeting">{greeting()}, Admin</span>
          </div>

          <div className="ad-header-right">
            <div className="ad-clock-block">
              <span className="ad-clock-time">{fmt12(time)}</span>
              <span className="ad-clock-date">{fmtDate(time)}</span>
            </div>

            <button
              className="ad-icon-btn"
              onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
              title="Toggle theme"
            >
              {theme === 'dark' ? '☀' : '☾'}
            </button>

            <button
              className="ad-logout-btn"
              onClick={() => {
                localStorage.removeItem('token');
                localStorage.removeItem('userRole');
                window.location.href = '/login';
              }}
            >
              ⎋ Logout
            </button>

            <div className="ad-avatar">A</div>
          </div>
        </header>

        {/* ── SCROLLABLE MAIN ── */}
        <main className="ad-main">
          {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

          {activeView === 'dashboard' && (
            <DashboardOverview stats={stats} onRefresh={fetchDashboardStats} onNavigate={setActiveView} />
          )}
          {activeView === 'staff'     && <StaffView     onDataUpdate={handleDataUpdate} />}
          {activeView === 'projects'  && <ProjectsView  onDataUpdate={handleDataUpdate} />}
          {activeView === 'clients'   && <ClientsView   onDataUpdate={handleDataUpdate} />}
        </main>
      </div>
    </div>
  );
};

/* ══════════════════════════════════════════════════════
   DASHBOARD OVERVIEW
══════════════════════════════════════════════════════ */
const DashboardOverview = ({ stats, onRefresh, onNavigate }) => {
  const statCards = [
    {
      label:   'Total Clients',
      value:   stats.users?.total    ?? 0,
      sub:     `${stats.users?.active ?? 0} active`,
      icon:    '◷',
      cls:     'amber',
    },
    {
      label:   'Total Projects',
      value:   stats.projects?.total ?? 0,
      sub:     `${stats.projects?.completed ?? 0} completed`,
      icon:    '◈',
      cls:     'cyan',
    },
    {
      label:   'In Progress',
      value:   stats.projects?.in_progress ?? 0,
      sub:     `${stats.projects?.pending ?? 0} pending`,
      icon:    '⟳',
      cls:     'violet',
    },
    {
      label:   'Staff Members',
      value:   stats.users?.staff    ?? 0,
      sub:     'Active staff',
      icon:    '⬡',
      cls:     'mint',
    },
    {
      label:   'Revenue',
      value:   `$${(stats.revenue ?? 0).toFixed(2)}`,
      sub:     'From completed projects',
      icon:    '◎',
      cls:     'rose',
    },
    {
      label:   'Pending',
      value:   stats.projects?.pending ?? 0,
      sub:     'Awaiting assignment',
      icon:    '◇',
      cls:     'amber',
    },
  ];

  const quickActions = [
    { icon: '◈', label: 'Add Staff Member', view: 'staff'    },
    { icon: '◎', label: 'View All Projects', view: 'projects' },
    { icon: '◷', label: 'Manage Clients',    view: 'clients'  },
  ];

  const activity = [
    { icon: '⬡', text: 'System statistics updated',                          time: 'Just now' },
    { icon: '✓', text: `${stats.projects?.completed ?? 0} projects completed`, time: 'Today'    },
    { icon: '◷', text: `${stats.users?.total ?? 0} registered clients`,        time: 'Total'    },
  ];

  return (
    <div className="ad-view">
      <div className="ad-view-head">
        <div>
          <h2 className="ad-view-title">System Overview</h2>
          <p className="ad-view-sub">Monitor your platform statistics and activity</p>
        </div>
        <button className="ad-refresh-btn" onClick={onRefresh}>↺ Refresh</button>
      </div>

      {/* stat cards */}
      <div className="ad-stats-grid">
        {statCards.map((c, i) => (
          <div
            key={c.label}
            className={`ad-stat-card ad-stat-${c.cls}`}
            style={{ animationDelay: `${i * 55}ms` }}
          >
            <span className="ad-stat-icon">{c.icon}</span>
            <div className="ad-stat-num">{c.value}</div>
            <div className="ad-stat-label">{c.label}</div>
            <div className="ad-stat-sub">{c.sub}</div>
          </div>
        ))}
      </div>

      {/* quick actions */}
      <div className="ad-section">
        <h3 className="ad-section-title">Quick Actions</h3>
        <div className="ad-qa-grid">
          {quickActions.map(q => (
            <button key={q.label} className="ad-qa-card" onClick={() => onNavigate(q.view)}>
              <span className="ad-qa-icon">{q.icon}</span>
              <span className="ad-qa-label">{q.label}</span>
              <span className="ad-qa-arrow">→</span>
            </button>
          ))}
        </div>
      </div>

      {/* recent activity */}
      <div className="ad-section">
        <h3 className="ad-section-title">Recent Activity</h3>
        <div className="ad-activity-list">
          {activity.map((a, i) => (
            <div key={i} className="ad-activity-item" style={{ animationDelay: `${i * 80}ms` }}>
              <div className="ad-activity-icon">{a.icon}</div>
              <span className="ad-activity-text">{a.text}</span>
              <span className="ad-activity-time">{a.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;