import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { staffService } from '../../services/staffService';
import Alert from '../common/Alert';
import { formatDateString } from '../../utils/dateUtils';
import './StaffDashboard.css';

/* ══════════════════════════════════════════════════════
   ROOT
══════════════════════════════════════════════════════ */
const StaffDashboard = () => {
  const navigate = useNavigate();

  const [activeView, setActiveView] = useState('dashboard');
  const [theme,      setTheme]      = useState('dark');
  const [time,       setTime]       = useState(new Date());

  const [stats,    setStats]    = useState({ total:0, pending:0, inProgress:0, completed:0 });
  const [profile,  setProfile]  = useState(null);
  const [projects, setProjects] = useState([]);

  const [loadingStats,    setLoadingStats]    = useState(true);
  const [loadingProfile,  setLoadingProfile]  = useState(false);
  const [loadingProjects, setLoadingProjects] = useState(false);
  const [error, setError] = useState(null);
  const [alert, setAlert] = useState(null);

  /* live clock */
  useEffect(() => {
    const id = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  /* initial load */
  useEffect(() => { fetchStats(); }, []);

  /* load on tab change */
  useEffect(() => {
    if (activeView === 'projects' && projects.length === 0) fetchProjects();
    if (activeView === 'profile'  && !profile)             fetchProfile();
  }, [activeView]);

  const fetchStats = async () => {
    try {
      setLoadingStats(true);
      const data = await staffService.getDashboardStats();
      // API returns { stats: {...} } — unwrap whichever shape arrives
      const statsData = data?.stats ?? data?.data ?? data;
      setStats({
        total:      statsData.total_projects     ?? statsData.total      ?? 0,
        pending:    statsData.pending             ?? 0,
        inProgress: statsData.active_projects     ?? statsData.inProgress ?? 0,
        completed:  statsData.completed_projects  ?? statsData.completed  ?? 0,
      });
    } catch (e) { setError(e.message); }
    finally     { setLoadingStats(false); }
  };

  const fetchProjects = async () => {
    try {
      setLoadingProjects(true);
      const data = await staffService.getAssignedProjects();
      // API returns { projects: [...], pagination: {...} }
      const list = Array.isArray(data)              ? data
                 : Array.isArray(data?.projects)    ? data.projects
                 : Array.isArray(data?.data)        ? data.data : [];
      setProjects(list);
    } catch (e) { setError(e.message); }
    finally     { setLoadingProjects(false); }
  };

  const fetchProfile = async () => {
    try {
      setLoadingProfile(true);
      const data = await staffService.getProfile();
      // API returns { staff: {...} } — unwrap whichever shape arrives
      const profileData = data?.staff ?? data?.data ?? data;
      setProfile(profileData);
    } catch (e) { setError(e.message); }
    finally     { setLoadingProfile(false); }
  };

  const greeting = () => {
    const h = time.getHours();
    if (h < 12) return 'Good morning';
    if (h < 17) return 'Good afternoon';
    return 'Good evening';
  };

  const fmt12   = d => d.toLocaleTimeString([], { hour:'2-digit', minute:'2-digit' });
  const fmtDate = d => d.toLocaleDateString([],  { weekday:'short', month:'short', day:'numeric' });

  const completionRate = stats.total
    ? Math.round((stats.completed / stats.total) * 100) : 0;

  const navItems = [
    { id:'dashboard', icon:'⬡', label:'Dashboard' },
    { id:'projects',  icon:'◈', label:'Projects'  },
    { id:'profile',   icon:'◎', label:'Profile'   },
  ];

  return (
    <div className={`sd-root sd-${theme}`}>
      {theme === 'dark' && <>
        <div className="sd-orb sd-orb-1" />
        <div className="sd-orb sd-orb-2" />
        <div className="sd-orb sd-orb-3" />
      </>}

      {/* ── FIXED SIDEBAR ── */}
      <aside className="sd-sidebar">
        <div className="sd-brand">
          <div className="sd-brand-icon">R</div>
          <span className="sd-brand-name">ResearchPro</span>
        </div>

        <nav className="sd-nav">
          {navItems.map(n => (
            <button
              key={n.id}
              className={`sd-nav-btn${activeView === n.id ? ' sd-nav-active' : ''}`}
              onClick={() => setActiveView(n.id)}
            >
              <span className="sd-nav-icon">{n.icon}</span>
              <span>{n.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* ── RIGHT COLUMN (header + scroll area) ── */}
      <div className="sd-body">

        {/* ── FIXED HEADER ── */}
        <header className="sd-header">
          <div className="sd-header-left">
            <span className="sd-page-tag">
              {navItems.find(n => n.id === activeView)?.label}
            </span>
            <span className="sd-header-greeting">{greeting()}</span>
          </div>

          <div className="sd-header-right">
            <div className="sd-clock-block">
              <span className="sd-clock-time">{fmt12(time)}</span>
              <span className="sd-clock-date">{fmtDate(time)}</span>
            </div>

            <button
              className="sd-icon-btn"
              onClick={() => setTheme(t => t === 'dark' ? 'light' : 'dark')}
              title="Toggle theme"
            >
              {theme === 'dark' ? '☀' : '☾'}
            </button>

            <button className="sd-logout-btn" onClick={() => navigate('/')}>
              ⎋ Logout
            </button>

            <div className="sd-avatar">R</div>
          </div>
        </header>

        {/* ── SCROLLABLE MAIN ── */}
        <main className="sd-main">
          {alert && <Alert type={alert.type} message={alert.message} onClose={() => setAlert(null)} />}
          {error && <Alert type="error" message={error} onClose={() => setError(null)} />}

          {activeView === 'dashboard' && (
            <DashboardView
              stats={stats}
              completionRate={completionRate}
              loading={loadingStats}
              onRefresh={fetchStats}
            />
          )}
          {activeView === 'projects' && (
            <ProjectsView
              projects={projects}
              loading={loadingProjects}
              onRefresh={fetchProjects}
              setAlert={setAlert}
            />
          )}
          {activeView === 'profile' && (
            <ProfileView profile={profile} loading={loadingProfile} />
          )}
        </main>
      </div>
    </div>
  );
};

/* ══════════════════════════════════════════════════════
   DASHBOARD VIEW
══════════════════════════════════════════════════════ */
const DashboardView = ({ stats, completionRate, loading, onRefresh }) => {
  if (loading) return <CentreLoader text="Loading dashboard…" />;

  const cards = [
    { label:'Total Assigned', value:stats.total,       icon:'◈', cls:'cyan'   },
    { label:'Pending',        value:stats.pending,     icon:'◷', cls:'amber'  },
    { label:'In Progress',    value:stats.inProgress,  icon:'⟳', cls:'violet' },
    { label:'Completed',      value:stats.completed,   icon:'✓', cls:'mint'   },
  ];

  return (
    <div className="sd-view">
      <div className="sd-view-head">
        <div>
          <h2 className="sd-view-title">Overview</h2>
          <p className="sd-view-sub">Your research workload at a glance</p>
        </div>
        <button className="sd-refresh-btn" onClick={onRefresh}>↺ Refresh</button>
      </div>

      <div className="sd-stats-grid">
        {cards.map((c, i) => (
          <div key={c.label} className={`sd-stat-card sd-stat-${c.cls}`}
               style={{ animationDelay:`${i*60}ms` }}>
            <span className="sd-stat-icon">{c.icon}</span>
            <div className="sd-stat-num">{c.value}</div>
            <div className="sd-stat-label">{c.label}</div>
          </div>
        ))}
      </div>

      <div className="sd-band">
        <div className="sd-band-card sd-completion">
          <div className="sd-blabel">Completion Rate</div>
          <div className="sd-completion-pct">{completionRate}%</div>
          <div className="sd-track">
            <div className="sd-track-fill" style={{ width:`${completionRate}%` }} />
          </div>
          <div className="sd-bsub">{stats.completed} of {stats.total} delivered</div>
        </div>

        <div className="sd-band-card">
          <div className="sd-band-icon">◎</div>
          <div>
            <div className="sd-blabel">Active Workload</div>
            <div className="sd-bval">{stats.inProgress} project{stats.inProgress !== 1 ? 's':''} running</div>
            <div className="sd-bsub">{Math.max(0, 5-(stats.inProgress||0))} slot{(5-(stats.inProgress||0)) !== 1 ? 's':''} remaining</div>
          </div>
        </div>

        <div className="sd-band-card sd-band-accent">
          <div className="sd-band-icon">⬡</div>
          <div>
            <div className="sd-blabel">Quick Tip</div>
            <div className="sd-bval">Upload results as PDF</div>
            <div className="sd-bsub">Only PDF files are accepted</div>
          </div>
        </div>
      </div>
    </div>
  );
};

/* ══════════════════════════════════════════════════════
   PROJECTS VIEW
══════════════════════════════════════════════════════ */
const ProjectsView = ({ projects, loading, onRefresh, setAlert }) => {
  const [statusFilter, setStatusFilter] = useState('all');
  const [dateFrom,     setDateFrom]     = useState('');
  const [dateTo,       setDateTo]       = useState('');
  const [sortOrder,    setSortOrder]    = useState('newest');
  const [selected,     setSelected]     = useState(null);

  const filtered = useMemo(() => {
    let list = [...projects];
    if (statusFilter !== 'all')
      list = list.filter(p => p.status === statusFilter);
    if (dateFrom)
      list = list.filter(p => p.assigned_at && new Date(p.assigned_at) >= new Date(dateFrom));
    if (dateTo)
      list = list.filter(p => p.assigned_at && new Date(p.assigned_at) <= new Date(dateTo + 'T23:59:59'));
    list.sort((a, b) => {
      const da = new Date(a.assigned_at || 0), db = new Date(b.assigned_at || 0);
      return sortOrder === 'newest' ? db - da : da - db;
    });
    return list;
  }, [projects, statusFilter, dateFrom, dateTo, sortOrder]);

  const statusCls = { pending:'s-pending', in_progress:'s-progress', completed:'s-done' };
  const statusTxt = { pending:'Pending',   in_progress:'In Progress', completed:'Completed' };

  if (loading) return <CentreLoader text="Loading projects…" />;

  return (
    <div className="sd-view">
      <div className="sd-view-head">
        <div>
          <h2 className="sd-view-title">Projects</h2>
          <p className="sd-view-sub">{filtered.length} of {projects.length} shown</p>
        </div>
        <button className="sd-refresh-btn" onClick={onRefresh}>↺ Refresh</button>
      </div>

      {/* filters */}
      <div className="sd-filters">
        <div className="sd-fgroup">
          <label className="sd-flabel">Status</label>
          <select className="sd-select" value={statusFilter} onChange={e => setStatusFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
          </select>
        </div>
        <div className="sd-fgroup">
          <label className="sd-flabel">From date</label>
          <input type="date" className="sd-date-input" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
        </div>
        <div className="sd-fgroup">
          <label className="sd-flabel">To date</label>
          <input type="date" className="sd-date-input" value={dateTo} onChange={e => setDateTo(e.target.value)} />
        </div>
        <div className="sd-fgroup">
          <label className="sd-flabel">Sort</label>
          <select className="sd-select" value={sortOrder} onChange={e => setSortOrder(e.target.value)}>
            <option value="newest">Newest first</option>
            <option value="oldest">Oldest first</option>
          </select>
        </div>
        {(statusFilter !== 'all' || dateFrom || dateTo) && (
          <button className="sd-clear-btn"
            onClick={() => { setStatusFilter('all'); setDateFrom(''); setDateTo(''); }}>
            ✕ Clear filters
          </button>
        )}
      </div>

      {filtered.length === 0 ? (
        <div className="sd-empty">
          <div className="sd-empty-icon">📋</div>
          <h3>No projects match</h3>
          <p>Adjust the filters above.</p>
        </div>
      ) : (
        <div className="sd-projects-grid">
          {filtered.map(p => (
            <div key={p.id} className="sd-pcard">
              <div className="sd-pcard-top">
                <h3 className="sd-pcard-title">{p.title}</h3>
                <span className={`sd-badge ${statusCls[p.status] || ''}`}>
                  {statusTxt[p.status] || p.status}
                </span>
              </div>
              <div className="sd-pcard-meta">
                <span>👤 {p.user?.name ?? '—'}</span>
                <span>🔬 {p.research_field ?? '—'}</span>
                <span>📅 {formatDateString(p.assigned_at)}</span>
              </div>
              {p.description?.objectives && (
                <p className="sd-pcard-excerpt">
                  {p.description.objectives.substring(0, 120)}…
                </p>
              )}
              <div className="sd-pcard-foot">
                <button className="sd-btn-primary" onClick={() => setSelected(p)}>
                  {p.status === 'pending' ? '▶ Start Work'
                   : p.status === 'completed' ? '👁 View Details'
                   : '▶ Continue Work'}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {selected && (
        <ProjectWorkspace
          project={selected}
          onClose={() => { setSelected(null); onRefresh(); }}
          setAlert={setAlert}
        />
      )}
    </div>
  );
};

/* ══════════════════════════════════════════════════════
   PROFILE VIEW
══════════════════════════════════════════════════════ */
const ProfileView = ({ profile, loading }) => {
  if (loading) return <CentreLoader text="Loading profile…" />;
  if (!profile) return (
    <div className="sd-view sd-empty">
      <div className="sd-empty-icon">◎</div>
      <h3>Profile unavailable</h3>
    </div>
  );

  const user   = profile.user || {};
  const skills = (() => {
    if (Array.isArray(profile.skills)) return profile.skills;
    try { return JSON.parse(profile.skills || '[]'); } catch { return []; }
  })();

  const rows = [
    ['Full Name',      user.name],
    ['Email',          user.email],
    ['Phone',          user.phone       || '—'],
    ['ID Number',      profile.id_number],
    ['Specialization', profile.specialization || '—'],
    ['Qualification',  profile.qualification  || '—'],
    ['Experience',     profile.experience_years != null ? `${profile.experience_years} yr${profile.experience_years !== 1?'s':''}` : '—'],
    ['Rate / Page',    profile.rate_per_page    != null ? `$${profile.rate_per_page}`    : '—'],
    ['Rate / Chapter', profile.rate_per_chapter != null ? `$${profile.rate_per_chapter}` : '—'],
    ['Availability',   profile.availability ? '✅ Available' : '🔴 Unavailable'],
    ['Rating',         profile.rating != null ? `⭐ ${profile.rating} / 5` : '—'],
    ['Total Projects', profile.total_projects     ?? 0],
    ['Completed',      profile.completed_projects ?? 0],
  ];

  return (
    <div className="sd-view">
      <div className="sd-view-head">
        <h2 className="sd-view-title">My Profile</h2>
        <p className="sd-view-sub">Your staff account details</p>
      </div>

      {/* hero */}
      <div className="sd-profile-hero">
        <div className="sd-profile-avatar">{user.name?.charAt(0).toUpperCase() || 'R'}</div>
        <div className="sd-profile-hero-info">
          <h3 className="sd-profile-name">{user.name}</h3>
          <p className="sd-profile-role">Staff Member · {profile.specialization || 'Researcher'}</p>
          <span className={`sd-avail-pill ${profile.availability ? 'avail-on' : 'avail-off'}`}>
            <span className="sd-avail-dot" />
            {profile.availability ? 'Available for work' : 'Not available'}
          </span>
        </div>
      </div>

      {/* info grid */}
      <div className="sd-info-grid">
        {rows.map(([lbl, val]) => (
          <div key={lbl} className="sd-info-row">
            <span className="sd-info-label">{lbl}</span>
            <span className="sd-info-val">{val}</span>
          </div>
        ))}
      </div>

      {/* skills */}
      {skills.length > 0 && (
        <div className="sd-skills-section">
          <h4 className="sd-section-mini-title">Skills</h4>
          <div className="sd-skills-wrap">
            {skills.map(s => <span key={s} className="sd-skill-chip">{s}</span>)}
          </div>
        </div>
      )}

      {/* bio */}
      {profile.bio && (
        <div className="sd-bio-section">
          <h4 className="sd-section-mini-title">Bio</h4>
          <p className="sd-bio-text">{profile.bio}</p>
        </div>
      )}
    </div>
  );
};

/* ══════════════════════════════════════════════════════
   PROJECT WORKSPACE MODAL
══════════════════════════════════════════════════════ */
const ProjectWorkspace = ({ project, onClose, setAlert }) => {
  const [loadingStatus, setLoadingStatus] = useState(false);
  const [localAlert,    setLocalAlert]    = useState(null);

  const updateStatus = async (newStatus) => {
    try {
      setLoadingStatus(true);
      await staffService.updateProjectStatus(project.id, newStatus);
      setLocalAlert({ type:'success', message:'Status updated!' });
      setTimeout(onClose, 900);
    } catch (e) {
      setLocalAlert({ type:'error', message: e.message || 'Failed to update.' });
    } finally {
      setLoadingStatus(false);
    }
  };

  return (
    <div className="sd-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="sd-modal">
        <div className="sd-modal-head">
          <h2>Project Workspace</h2>
          <button className="sd-modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="sd-modal-body">
          {localAlert && (
            <Alert type={localAlert.type} message={localAlert.message}
                   onClose={() => setLocalAlert(null)} />
          )}

          <div className="sd-modal-info-block">
            <h3>{project.title}</h3>
            <div className="sd-modal-meta-list">
              <span>👤 {project.user?.name} ({project.user?.email})</span>
              <span>🔬 {project.research_field}</span>
              <span>📌 {project.status}</span>
            </div>
          </div>

          {project.description && (
            <div className="sd-modal-desc">
              <h4>Project Details</h4>
              {[
                ['Objectives',        project.description.objectives],
                ['Methodology',       project.description.methodology],
                ['Expected Outcomes', project.description.expected_outcomes],
                ['Timeline',          project.description.timeline],
                ['Budget',            project.description.budget],
                ['Resources',         project.description.resources],
              ].map(([lbl, val]) => val ? (
                <div key={lbl} className="sd-modal-section">
                  <strong>{lbl}</strong>
                  <p>{val}</p>
                </div>
              ) : null)}
            </div>
          )}

          <div className="sd-modal-actions">
            {project.status === 'pending' && (
              <button className="sd-btn-primary" disabled={loadingStatus}
                      onClick={() => updateStatus('in_progress')}>
                {loadingStatus ? '…' : '▶ Start Working'}
              </button>
            )}
            {project.status === 'in_progress' && (
              <ResultUpload projectId={project.id}
                onSuccess={() => {
                  setLocalAlert({ type:'success', message:'Result uploaded!' });
                  setTimeout(onClose, 900);
                }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/* ══════════════════════════════════════════════════════
   RESULT UPLOAD
══════════════════════════════════════════════════════ */
const ResultUpload = ({ projectId, onSuccess }) => {
  const [file,    setFile]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const handle = async () => {
    if (!file)                           return setError('Please select a file');
    if (file.type !== 'application/pdf') return setError('Only PDF files allowed');
    try {
      setLoading(true);
      await staffService.uploadResult(projectId, file);
      onSuccess();
    } catch (e) { setError(e.message); }
    finally     { setLoading(false); }
  };

  return (
    <div className="sd-upload">
      <h4>Upload Result</h4>
      <label className="sd-file-label">
        <input type="file" accept=".pdf"
               onChange={e => { setFile(e.target.files[0]); setError(null); }} />
        {file ? `📄 ${file.name}` : '+ Choose PDF file'}
      </label>
      {error && <p className="sd-upload-err">{error}</p>}
      {file && (
        <button className="sd-btn-primary" onClick={handle} disabled={loading}>
          {loading ? 'Uploading…' : '⬆ Upload Result'}
        </button>
      )}
    </div>
  );
};

/* helpers */
const CentreLoader = ({ text }) => (
  <div className="sd-centre-loader">
    <div className="sd-loader-ring" />
    <p>{text}</p>
  </div>
);

export default StaffDashboard;