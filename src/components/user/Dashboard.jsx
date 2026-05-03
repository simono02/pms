import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import './Dashboard.css';

// ─── API BASE ─────────────────────────────────────────────────────────────────
const API = async (path, options = {}) => {
  const token = localStorage.getItem('access_token');
  const res = await fetch(`/api${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || 'Request failed');
  return data;
};

// ─── HELPERS ──────────────────────────────────────────────────────────────────
const fmtMoney    = (n)  => `KES ${Number(n || 0).toLocaleString()}`;
const fmtDate     = (ds) => ds ? new Date(ds).toLocaleDateString('en-US', { year:'numeric', month:'short', day:'numeric' }) : '—';
const fmtDT       = (ds) => ds ? new Date(ds).toLocaleString('en-US', { day:'numeric', month:'short', year:'numeric', hour:'2-digit', minute:'2-digit' }) : '—';
const fmtLiveTime = (date) => {
  const days   = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat'];
  const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
  let h = date.getHours(), m = date.getMinutes().toString().padStart(2,'0');
  const ap = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  const ord = (n) => { const s=['th','st','nd','rd'],v=n%100; return n+(s[(v-20)%10]||s[v]||s[0]); };
  return `${days[date.getDay()]} ${ord(date.getDate())} ${months[date.getMonth()]} · ${h}:${m} ${ap}`;
};
const typeIcon = (t) => ({
  'Research Paper':'📄','Dissertation':'🎓','Thesis':'📖',
  'Essay':'✍️','Literature Review':'📚','Case Study':'🔬',
  'research':'📄','thesis':'📖','dissertation':'🎓',
  'literature-review':'📚','case-study':'🔬','other':'📝',
}[t] || '📝');

// ─── SPINNER ──────────────────────────────────────────────────────────────────
const Spinner = () => (
  <div className="rp-spinner-wrap">
    <div className="rp-spinner" />
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
const Dashboard = () => {
  const { user: authUser, logout } = useAuth();

  // ── UI ────────────────────────────────────────────────────────────────────
  const [activePage,      setActivePage]      = useState('projects');
  const [darkMode,        setDarkMode]        = useState(false);
  const [sidebarOpen,     setSidebarOpen]     = useState(false);
  const [activeTab,       setActiveTab]       = useState('all');
  const [currentDateTime, setCurrentDateTime] = useState(new Date());

  // ── Data ──────────────────────────────────────────────────────────────────
  const [profile,      setProfile]      = useState(null);
  const [stats,        setStats]        = useState(null);
  const [projects,     setProjects]     = useState([]);
  const [projectsPage, setProjectsPage] = useState({ total:0, pages:1, page:1 });
  const [payments,     setPayments]     = useState([]);
  const [paymentsPage, setPaymentsPage] = useState({ total:0, pages:1, page:1 });
  const [loading,      setLoading]      = useState({ profile:false, projects:false, payments:false });
  const [error,        setError]        = useState({ profile:null, projects:null, payments:null });

  // ── Modals ────────────────────────────────────────────────────────────────
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);
  const [showPaymentModal,    setShowPaymentModal]    = useState(false);
  const [selectedFile,        setSelectedFile]        = useState(null);
  const [submitting,          setSubmitting]          = useState(false);

  const [projectFormData, setProjectFormData] = useState({
    projectType:'', pages:'', chapters:'', description:'', researchQuestion:'',
    academicLevel:'', citationStyle:'', methodology:'', specificRequirements:'',
    keywords:'', pricingType:'per-page', descriptionFile:null,
  });

  const [paymentData, setPaymentData] = useState({
    paymentMethod:'mpesa', mpesaNumber:'', cardNumber:'', cardName:'',
    expiryDate:'', cvv:'', totalAmount:0, depositAmount:0,
  });

  // ── Theme ─────────────────────────────────────────────────────────────────
  useEffect(() => {
    document.documentElement.setAttribute('data-rp-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // ── Clock ─────────────────────────────────────────────────────────────────
  useEffect(() => {
    const t = setInterval(() => setCurrentDateTime(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  // ── Pricing calc ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (projectFormData.pricingType === 'per-page' && projectFormData.pages) {
      const total = parseInt(projectFormData.pages) * 370;
      setPaymentData(p => ({ ...p, totalAmount: total, depositAmount: total / 2 }));
    } else if (projectFormData.pricingType === 'per-chapter' && projectFormData.chapters) {
      const total = parseInt(projectFormData.chapters) * 2000;
      setPaymentData(p => ({ ...p, totalAmount: total, depositAmount: total / 2 }));
    }
  }, [projectFormData.pricingType, projectFormData.pages, projectFormData.chapters]);

  // ── FETCH PROFILE ─────────────────────────────────────────────────────────
  const fetchProfile = useCallback(async () => {
    setLoading(l => ({ ...l, profile: true }));
    setError(e => ({ ...e, profile: null }));
    try {
      const data = await API('/user/profile');
      setProfile(data.user);
    } catch (err) {
      setError(e => ({ ...e, profile: err.message }));
    } finally {
      setLoading(l => ({ ...l, profile: false }));
    }
  }, []);

  // ── FETCH STATS ───────────────────────────────────────────────────────────
  const fetchStats = useCallback(async () => {
    try {
      const data = await API('/user/stats');
      setStats(data.stats);
    } catch {}
  }, []);

  // ── FETCH PROJECTS ────────────────────────────────────────────────────────
  const fetchProjects = useCallback(async (page = 1, statusFilter = null) => {
    setLoading(l => ({ ...l, projects: true }));
    setError(e => ({ ...e, projects: null }));
    try {
      let url = `/user/projects?page=${page}&per_page=10`;
      if (statusFilter && statusFilter !== 'all') {
        const map = { pending: 'pending,in_progress,payment_required', completed: 'completed' };
        url += `&status=${map[statusFilter] || statusFilter}`;
      }
      const data = await API(url);
      setProjects(data.projects || []);
      setProjectsPage(data.pagination || { total:0, pages:1, page:1 });
    } catch (err) {
      setError(e => ({ ...e, projects: err.message }));
    } finally {
      setLoading(l => ({ ...l, projects: false }));
    }
  }, []);

  // ── FETCH PAYMENTS ────────────────────────────────────────────────────────
  const fetchPayments = useCallback(async (page = 1) => {
    setLoading(l => ({ ...l, payments: true }));
    setError(e => ({ ...e, payments: null }));
    try {
      const data = await API(`/payments/history?page=${page}&per_page=15`);
      setPayments(data.payments || []);
      setPaymentsPage(data.pagination || { total:0, pages:1, page:1 });
    } catch (err) {
      setError(e => ({ ...e, payments: err.message }));
    } finally {
      setLoading(l => ({ ...l, payments: false }));
    }
  }, []);

  // ── Initial loads ─────────────────────────────────────────────────────────
  useEffect(() => { fetchProfile(); fetchStats(); }, [fetchProfile, fetchStats]);
  useEffect(() => {
    if (activePage === 'projects') fetchProjects(1, activeTab);
    if (activePage === 'payments') fetchPayments(1);
  }, [activePage, activeTab, fetchProjects, fetchPayments]);

  // ── PROJECT SUBMIT — no API call, just open payment modal ─────────────────
  const handleProjectSubmit = (e) => {
    e.preventDefault();
    setShowNewProjectModal(false);
    setShowPaymentModal(true);
  };

  // ── PAYMENT SUBMIT ────────────────────────────────────────────────────────
  // Step 1: POST /api/payments/deposit  →  Step 2 (on success): POST /api/projects/
  const handlePaymentSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      // Step 1 — process the deposit payment
      const paymentResult = await API('/payments/deposit', {
        method: 'POST',
        body: JSON.stringify({
          ...paymentData,
          projectFormData,
        }),
      });

      // Step 2 — create the project, linking the confirmed payment reference
      await API('/projects/', {
        method: 'POST',
        body: JSON.stringify({
          ...projectFormData,
          paymentReference: paymentResult.transaction_id || paymentResult.reference || null,
          depositAmount:    paymentData.depositAmount,
          totalAmount:      paymentData.totalAmount,
        }),
      });

      alert(`Deposit of ${fmtMoney(paymentData.depositAmount)} processed successfully! Your project has been created.`);
      setShowPaymentModal(false);
      resetForms();
      fetchProjects(1, activeTab);
      fetchStats();
      fetchPayments(1);
    } catch (err) {
      alert(err.message || 'Payment or project creation failed. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  // ── RESET ─────────────────────────────────────────────────────────────────
  const resetForms = () => {
    setProjectFormData({
      projectType:'', pages:'', chapters:'', description:'', researchQuestion:'',
      academicLevel:'', citationStyle:'', methodology:'', specificRequirements:'',
      keywords:'', pricingType:'per-page', descriptionFile:null,
    });
    setPaymentData({
      paymentMethod:'mpesa', mpesaNumber:'', cardNumber:'', cardName:'',
      expiryDate:'', cvv:'', totalAmount:0, depositAmount:0,
    });
    setSelectedFile(null);
  };

  // ── FORM HANDLERS ─────────────────────────────────────────────────────────
  const handleProjectFormChange = (e) => {
    const { name, value } = e.target;
    setProjectFormData(p => ({ ...p, [name]: value }));
  };
  const handlePaymentInputChange = (e) => {
    const { name, value } = e.target;
    setPaymentData(p => ({ ...p, [name]: value }));
  };
  const handleFileSelect = (e) => {
    const f = e.target.files[0];
    if (f) { setSelectedFile(f); setProjectFormData(p => ({ ...p, descriptionFile: f.name })); }
  };

  // ── DERIVED ───────────────────────────────────────────────────────────────
  const user      = profile || authUser || {};
  const firstName = user.name?.split(' ')[0] || 'Scholar';
  const initials  = (user.name || 'R').split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);

  const isPendingProject = (p) => ['pending','in_progress','payment_required'].includes(p.status);

  const filteredProjects = projects.filter(p => {
    if (activeTab === 'pending')   return isPendingProject(p);
    if (activeTab === 'completed') return p.status === 'completed';
    return true;
  });

  const navItems = [
    { id:'projects', label:'My Projects', icon:'📋' },
    { id:'payments', label:'Payments',    icon:'💳' },
    { id:'profile',  label:'Profile',     icon:'👤' },
  ];

  // ─────────────────────────────────────────────────────────────────────────
  return (
    <div className="rp-root">

      {sidebarOpen && <div className="rp-overlay" onClick={() => setSidebarOpen(false)} />}

      {/* ═══════════ SIDEBAR ═══════════ */}
      <aside className={`rp-sidebar ${sidebarOpen ? 'open' : ''}`}>
        <div className="rp-brand">
          <span className="rp-brand-dot" />
          Research<span className="rp-brand-accent">Pro</span>
        </div>

        <nav className="rp-nav">
          <div className="rp-nav-label">Workspace</div>
          {navItems.map(item => (
            <button
              key={item.id}
              className={`rp-nav-item ${activePage === item.id ? 'active' : ''}`}
              onClick={() => { setActivePage(item.id); setSidebarOpen(false); }}
            >
              <span className="rp-nav-icon">{item.icon}</span>
              {item.label}
            </button>
          ))}
        </nav>

        <div className="rp-sidebar-foot">
          <div className="rp-user-chip">
            <div className="rp-avatar-sm">{initials}</div>
            <div>
              <div className="rp-chip-name">{firstName}</div>
              <div className="rp-chip-role">{user.role || 'researcher'}</div>
            </div>
          </div>
        </div>
      </aside>

      {/* ═══════════ MAIN ═══════════ */}
      <main className="rp-main">

        {/* TOPBAR */}
        <header className="rp-topbar">
          <div className="rp-topbar-l">
            <button className="rp-hamburger" onClick={() => setSidebarOpen(!sidebarOpen)}>
              <span /><span /><span />
            </button>
            <div className="rp-topbar-time">
              <span className="rp-live-dot" />
              {fmtLiveTime(currentDateTime)}
            </div>
          </div>
          <div className="rp-topbar-r">
            <button className="rp-theme-btn" onClick={() => setDarkMode(!darkMode)} title="Toggle theme">
              {darkMode ? '☀️' : '🌙'}
            </button>
            <button className="rp-new-btn" onClick={() => setShowNewProjectModal(true)}>
              <span className="rp-plus">+</span>
              <span>New Project</span>
            </button>
            <button className="rp-signout-btn" onClick={logout}>
              ↪ Sign Out
            </button>
          </div>
        </header>

        {/* ═══════════ PAGE BODY ═══════════ */}
        <div className="rp-body">

          {/* ══════ PROJECTS PAGE ══════ */}
          {activePage === 'projects' && (
            <div className="rp-page">

              <div className="rp-welcome">
                <div className="rp-welcome-text">
                  <div className="rp-eyebrow">Research Pro · Dashboard</div>
                  <h1 className="rp-welcome-title">Hello, <em>{firstName}</em> 👋</h1>
                  <p className="rp-welcome-sub">
                    {stats
                      ? <>You have <strong>{stats.in_progress_projects + stats.pending_projects}</strong> active and <strong>{stats.completed_projects}</strong> completed projects.</>
                      : 'Welcome back to your research workspace.'}
                  </p>
                </div>
                <div className="rp-welcome-deco">
                  <div className="rp-deco-ring r1" />
                  <div className="rp-deco-ring r2" />
                  <span className="rp-deco-glyph">🔬</span>
                </div>
              </div>

              <div className="rp-stats-grid">
                {[
                  { icon:'📋', label:'Total',    value: stats?.total_projects ?? '—', color:'blue'   },
                  { icon:'⏳', label:'Active',    value: stats ? (stats.in_progress_projects + stats.pending_projects) : '—', color:'amber' },
                  { icon:'✅', label:'Completed', value: stats?.completed_projects ?? '—', color:'green'  },
                  { icon:'💰', label:'Invested',  value: stats ? `KES ${((stats.total_spent||0)/1000).toFixed(1)}k` : '—', color:'purple' },
                ].map(s => (
                  <div key={s.label} className={`rp-stat rp-stat-${s.color}`}>
                    <span className="rp-stat-icon">{s.icon}</span>
                    <span className="rp-stat-value">{s.value}</span>
                    <span className="rp-stat-label">{s.label}</span>
                  </div>
                ))}
              </div>

              <div className="rp-panel">
                <div className="rp-panel-hdr">
                  <div className="rp-panel-title">
                    <h2>My Projects</h2>
                    <span className="rp-count-pill">{projectsPage.total}</span>
                  </div>
                  <div className="rp-tabs">
                    {[['all','All'],['pending','Active'],['completed','Done']].map(([k,l]) => (
                      <button
                        key={k}
                        className={`rp-tab ${activeTab===k?'active':''}`}
                        onClick={() => { setActiveTab(k); fetchProjects(1, k); }}
                      >
                        {l}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="rp-scroll-area">
                  {loading.projects ? <Spinner /> : error.projects ? (
                    <div className="rp-error-msg">
                      <span>⚠</span> {error.projects}
                      <button onClick={() => fetchProjects(1, activeTab)}>Retry</button>
                    </div>
                  ) : filteredProjects.length === 0 ? (
                    <div className="rp-empty">
                      <div className="rp-empty-icon">📭</div>
                      <h3>No projects found</h3>
                      <p>Click "New Project" to get started</p>
                      <button className="rp-new-btn" onClick={() => setShowNewProjectModal(true)}>
                        <span className="rp-plus">+</span> Start a Project
                      </button>
                    </div>
                  ) : (
                    <>
                      {filteredProjects.map(project => {
                        const isActive = isPendingProject(project);
                        return (
                          <div key={project.id} className={`rp-card ${isActive ? 'rp-card-active' : 'rp-card-done'}`}>
                            <div className="rp-card-stripe" />
                            <div className="rp-card-head">
                              <div className="rp-card-icon">{typeIcon(project.project_type || project.type)}</div>
                              <div className="rp-card-meta">
                                <div className="rp-card-type">{project.project_type || project.type}</div>
                                <h3 className="rp-card-title">{project.title}</h3>
                                <div className="rp-card-pills">
                                  {project.academic_level && <span className="rp-pill rp-pill-a">{project.academic_level}</span>}
                                  {project.citation_style && <span className="rp-pill rp-pill-b">{project.citation_style}</span>}
                                  {(project.pages || project.chapters) && (
                                    <span className="rp-pill rp-pill-c">
                                      {project.pages ? `${project.pages} pages` : `${project.chapters} chapters`}
                                    </span>
                                  )}
                                </div>
                              </div>
                              <div>
                                <span className={`rp-status rp-status-${(project.status||'').replace('_','-')}`}>
                                  <span className="rp-status-dot" />
                                  {project.status?.replace(/_/g,' ')}
                                </span>
                              </div>
                            </div>

                            <div className="rp-card-body">
                              {isActive && (
                                <div className="rp-progress-wrap">
                                  <div className="rp-progress-hdr">
                                    <span>Progress</span>
                                    <span className="rp-progress-pct">{project.progress || 0}%</span>
                                  </div>
                                  <div className="rp-track">
                                    <div className="rp-fill" style={{ width:`${project.progress || 0}%` }} />
                                  </div>
                                </div>
                              )}
                              <div className="rp-info-row">
                                {isActive ? (
                                  <>
                                    <div className="rp-info-block">
                                      <div className="rp-ilab">Deadline</div>
                                      <div className="rp-ival rp-amber">{fmtDate(project.deadline)}</div>
                                    </div>
                                    <div className="rp-info-block">
                                      <div className="rp-ilab">Deposit Paid</div>
                                      <div className="rp-ival rp-green">{fmtMoney(project.deposit_amount)}</div>
                                    </div>
                                    <div className="rp-info-block">
                                      <div className="rp-ilab">Balance</div>
                                      <div className="rp-ival rp-red">{fmtMoney(project.balance_amount)}</div>
                                    </div>
                                    <div className="rp-info-block">
                                      <div className="rp-ilab">Total</div>
                                      <div className="rp-ival">{fmtMoney(project.total_price)}</div>
                                    </div>
                                  </>
                                ) : (
                                  <>
                                    <div className="rp-info-block">
                                      <div className="rp-ilab">Completed</div>
                                      <div className="rp-ival">{fmtDate(project.completed_at)}</div>
                                    </div>
                                    <div className="rp-info-block">
                                      <div className="rp-ilab">Total Paid</div>
                                      <div className="rp-ival rp-green">{fmtMoney(project.total_price)}</div>
                                    </div>
                                  </>
                                )}
                              </div>
                            </div>

                            <div className="rp-card-foot">
                              <button className="rp-btn rp-btn-ghost">👁 View</button>
                              {project.status === 'payment_required'
                                ? <button className="rp-btn rp-btn-pay">💳 Pay Balance</button>
                                : project.status === 'completed'
                                ? <button className="rp-btn rp-btn-dl">⬇ Download</button>
                                : null
                              }
                            </div>
                          </div>
                        );
                      })}

                      {projectsPage.pages > 1 && (
                        <div className="rp-pagination">
                          <button className="rp-page-btn" disabled={projectsPage.page <= 1} onClick={() => fetchProjects(projectsPage.page - 1, activeTab)}>← Prev</button>
                          <span className="rp-page-info">Page {projectsPage.page} of {projectsPage.pages}</span>
                          <button className="rp-page-btn" disabled={projectsPage.page >= projectsPage.pages} onClick={() => fetchProjects(projectsPage.page + 1, activeTab)}>Next →</button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ══════ PAYMENTS PAGE ══════ */}
          {activePage === 'payments' && (
            <div className="rp-page">
              <div className="rp-page-hero">
                <div className="rp-eyebrow">Research Pro · Payments</div>
                <h1 className="rp-page-title">Payment History</h1>
                <p className="rp-page-sub">All your transactions across projects.</p>
              </div>

              <div className="rp-panel">
                <div className="rp-panel-hdr">
                  <div className="rp-panel-title">
                    <h2>Transactions</h2>
                    <span className="rp-count-pill">{paymentsPage.total}</span>
                  </div>
                </div>

                <div className="rp-scroll-area">
                  {loading.payments ? <Spinner /> : error.payments ? (
                    <div className="rp-error-msg">
                      <span>⚠</span> {error.payments}
                      <button onClick={() => fetchPayments(1)}>Retry</button>
                    </div>
                  ) : payments.length === 0 ? (
                    <div className="rp-empty">
                      <div className="rp-empty-icon">💳</div>
                      <h3>No payments yet</h3>
                      <p>Your transactions will appear here once you create a project.</p>
                    </div>
                  ) : (
                    <>
                      {payments.map(pay => (
                        <div key={pay.id} className="rp-pay-row">
                          <div className="rp-pay-icon">{pay.payment_method === 'mpesa' ? '📱' : '💳'}</div>
                          <div className="rp-pay-info">
                            <div className="rp-pay-project">{pay.project_title || `Project #${pay.project_id}`}</div>
                            <div className="rp-pay-meta">
                              <span className={`rp-pill ${pay.payment_type === 'deposit' ? 'rp-pill-b' : 'rp-pill-a'}`}>
                                {pay.payment_type === 'deposit' ? 'Deposit' : 'Balance'}
                              </span>
                              <span className="rp-pay-txn">{pay.transaction_id}</span>
                              <span className="rp-pay-date">{fmtDT(pay.created_at)}</span>
                            </div>
                          </div>
                          <div className="rp-pay-right">
                            <div className="rp-pay-amount rp-green">{fmtMoney(pay.amount)}</div>
                            <span className={`rp-status rp-status-${pay.status}`}>
                              <span className="rp-status-dot" />{pay.status}
                            </span>
                          </div>
                        </div>
                      ))}

                      {paymentsPage.pages > 1 && (
                        <div className="rp-pagination">
                          <button className="rp-page-btn" disabled={paymentsPage.page <= 1} onClick={() => fetchPayments(paymentsPage.page - 1)}>← Prev</button>
                          <span className="rp-page-info">Page {paymentsPage.page} of {paymentsPage.pages}</span>
                          <button className="rp-page-btn" disabled={paymentsPage.page >= paymentsPage.pages} onClick={() => fetchPayments(paymentsPage.page + 1)}>Next →</button>
                        </div>
                      )}
                    </>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* ══════ PROFILE PAGE ══════ */}
          {activePage === 'profile' && (
            <div className="rp-page">
              <div className="rp-page-hero">
                <div className="rp-eyebrow">Research Pro · Account</div>
                <h1 className="rp-page-title">My Profile</h1>
                <p className="rp-page-sub">Your account details and research statistics.</p>
              </div>

              {loading.profile ? <Spinner /> : error.profile ? (
                <div className="rp-error-msg">
                  <span>⚠</span> {error.profile}
                  <button onClick={fetchProfile}>Retry</button>
                </div>
              ) : (
                <div className="rp-profile-layout">

                  {/* Profile Card */}
                  <div className="rp-profile-card">
                    <div className="rp-profile-avatar">{initials}</div>
                    <div className="rp-profile-name">{user.name || '—'}</div>
                    <div className="rp-profile-email">{user.email || '—'}</div>
                    {/* Role badge shown only on the card, not in the details grid */}
                    <span className={`rp-role-badge ${user.role === 'admin' ? 'admin' : user.role === 'staff' ? 'staff' : ''}`}>
                      {user.role === 'admin' ? '🛡 Admin' : user.role === 'staff' ? '🔧 Staff' : '🎓 Researcher'}
                    </span>
                    <div className="rp-profile-since">Member since {fmtDate(user.created_at)}</div>

                    <div className="rp-profile-divider" />

                    <div className="rp-profile-mini-stats">
                      <div className="rp-mini-stat">
                        <div className="rp-mini-val">{user.project_count ?? stats?.total_projects ?? 0}</div>
                        <div className="rp-mini-lab">Projects</div>
                      </div>
                      <div className="rp-mini-stat">
                        <div className="rp-mini-val">{stats?.completed_projects ?? 0}</div>
                        <div className="rp-mini-lab">Done</div>
                      </div>
                      <div className="rp-mini-stat">
                        <div className="rp-mini-val">{paymentsPage.total}</div>
                        <div className="rp-mini-lab">Payments</div>
                      </div>
                    </div>
                  </div>

                  {/* Details */}
                  <div className="rp-profile-details">
                    <div className="rp-panel">
                      <div className="rp-panel-hdr">
                        <div className="rp-panel-title"><h2>Account Information</h2></div>
                      </div>
                      <div className="rp-info-grid">
                        {[
                          // ── Role intentionally excluded from this grid ──
                          { label:'Full Name',      value: user.name },
                          { label:'Email',          value: user.email },
                          { label:'Phone',          value: user.phone || '—' },
                          { label:'Account Status', value: user.status ? (user.status.charAt(0).toUpperCase() + user.status.slice(1)) : '—' },
                          { label:'Email Verified', value: user.email_verified ? '✅ Verified' : '⚠ Not Verified' },
                          { label:'Member Since',   value: fmtDate(user.created_at) },
                          { label:'Last Updated',   value: fmtDT(user.updated_at) },
                          { label:'Last Login',     value: fmtDT(user.last_login) },
                        ].map(row => (
                          <div key={row.label} className="rp-info-item">
                            <div className="rp-info-item-label">{row.label}</div>
                            <div className="rp-info-item-val">{row.value}</div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="rp-panel">
                      <div className="rp-panel-hdr">
                        <div className="rp-panel-title"><h2>Research Statistics</h2></div>
                      </div>
                      <div className="rp-scroll-area rp-profile-stats-scroll">
                        {[
                          { icon:'📋', label:'Total Projects',        value: stats?.total_projects ?? 0,            color:'blue'   },
                          { icon:'⏳', label:'Pending',                value: stats?.pending_projects ?? 0,          color:'amber'  },
                          { icon:'🔄', label:'In Progress',            value: stats?.in_progress_projects ?? 0,      color:'amber'  },
                          { icon:'💳', label:'Payment Required',       value: stats?.payment_required_projects ?? 0, color:'red'    },
                          { icon:'✅', label:'Completed',              value: stats?.completed_projects ?? 0,        color:'green'  },
                          { icon:'💰', label:'Total Spent',            value: fmtMoney(stats?.total_spent),          color:'green'  },
                        ].map(s => (
                          <div key={s.label} className={`rp-pstat rp-pstat-${s.color}`}>
                            <span className="rp-pstat-icon">{s.icon}</span>
                            <span className="rp-pstat-label">{s.label}</span>
                            <span className="rp-pstat-val">{s.value}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                </div>
              )}
            </div>
          )}

        </div>
      </main>

      {/* ═══════════ NEW PROJECT MODAL ═══════════ */}
      {showNewProjectModal && (
        <div className="rp-modal-overlay" onClick={() => setShowNewProjectModal(false)}>
          <div className="rp-modal" onClick={e => e.stopPropagation()}>
            <div className="rp-modal-hdr">
              <div>
                <div className="rp-eyebrow">Research Pro</div>
                <h2 className="rp-modal-title">Create New Project</h2>
              </div>
              <button className="rp-modal-close" onClick={() => setShowNewProjectModal(false)}>✕</button>
            </div>

            <form onSubmit={handleProjectSubmit} className="rp-form">
              <div className="rp-form-row">
                <div className="rp-fg">
                  <label>Project Type <span className="rp-req">*</span></label>
                  <select name="projectType" value={projectFormData.projectType} onChange={handleProjectFormChange} required>
                    <option value="">Select type</option>
                    <option value="research">Research Paper</option>
                    <option value="thesis">Thesis</option>
                    <option value="dissertation">Dissertation</option>
                    <option value="literature-review">Literature Review</option>
                    <option value="case-study">Case Study</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div className="rp-fg">
                  <label>Academic Level <span className="rp-req">*</span></label>
                  <select name="academicLevel" value={projectFormData.academicLevel} onChange={handleProjectFormChange} required>
                    <option value="">Select level</option>
                    <option value="undergraduate">Undergraduate</option>
                    <option value="masters">Master's</option>
                    <option value="phd">PhD/Doctoral</option>
                    <option value="professional">Professional</option>
                  </select>
                </div>
              </div>

              <div className="rp-form-row">
                <div className="rp-fg">
                  <label>Pricing Type <span className="rp-req">*</span></label>
                  <select name="pricingType" value={projectFormData.pricingType} onChange={handleProjectFormChange} required>
                    <option value="per-page">Per Page — KES 370/page</option>
                    <option value="per-chapter">Per Chapter — KES 2,000/chapter</option>
                  </select>
                </div>
                <div className="rp-fg">
                  <label>{projectFormData.pricingType === 'per-page' ? 'Pages' : 'Chapters'} <span className="rp-req">*</span></label>
                  {projectFormData.pricingType === 'per-page'
                    ? <input type="number" name="pages" placeholder="e.g. 20" value={projectFormData.pages} onChange={handleProjectFormChange} min="1" required />
                    : <input type="number" name="chapters" placeholder="e.g. 5" value={projectFormData.chapters} onChange={handleProjectFormChange} min="1" required />
                  }
                </div>
              </div>

              <div className="rp-fg">
                <label>Research Question / Objective <span className="rp-req">*</span></label>
                <textarea name="researchQuestion" placeholder="Main research question or objective..." value={projectFormData.researchQuestion} onChange={handleProjectFormChange} rows="2" required />
              </div>

              <div className="rp-fg">
                <label>Project Description <span className="rp-req">*</span></label>
                <textarea name="description" placeholder="Detailed description of your topic, background and scope..." value={projectFormData.description} onChange={handleProjectFormChange} rows="4" required />
              </div>

              <div className="rp-form-row">
                <div className="rp-fg">
                  <label>Citation Style <span className="rp-req">*</span></label>
                  <select name="citationStyle" value={projectFormData.citationStyle} onChange={handleProjectFormChange} required>
                    <option value="">Select style</option>
                    <option value="apa">APA (7th Edition)</option>
                    <option value="mla">MLA</option>
                    <option value="chicago">Chicago</option>
                    <option value="harvard">Harvard</option>
                    <option value="ieee">IEEE</option>
                    <option value="vancouver">Vancouver</option>
                  </select>
                </div>
                <div className="rp-fg">
                  <label>Methodology</label>
                  <select name="methodology" value={projectFormData.methodology} onChange={handleProjectFormChange}>
                    <option value="">Select (optional)</option>
                    <option value="qualitative">Qualitative</option>
                    <option value="quantitative">Quantitative</option>
                    <option value="mixed">Mixed Methods</option>
                    <option value="theoretical">Theoretical</option>
                    <option value="experimental">Experimental</option>
                  </select>
                </div>
              </div>

              <div className="rp-fg">
                <label>Keywords</label>
                <input type="text" name="keywords" placeholder="e.g. climate change, AI (comma-separated)" value={projectFormData.keywords} onChange={handleProjectFormChange} />
              </div>

              <div className="rp-fg">
                <label>Specific Requirements</label>
                <textarea name="specificRequirements" placeholder="Any formatting, structure or special requirements..." value={projectFormData.specificRequirements} onChange={handleProjectFormChange} rows="3" />
              </div>

              <div className="rp-fg">
                <label>Upload Description File (Optional)</label>
                <div className="rp-file-drop">
                  <label htmlFor="rp-file-input">
                    {selectedFile
                      ? <><span>📄</span><span>{selectedFile.name}</span></>
                      : <><span>📎</span><span>Click to upload</span><span className="rp-file-hint">.pdf .doc .docx .txt</span></>
                    }
                  </label>
                  <input id="rp-file-input" type="file" onChange={handleFileSelect} style={{ display:'none' }} accept=".pdf,.doc,.docx,.txt" />
                </div>
              </div>

              {(projectFormData.pages || projectFormData.chapters) && (
                <div className="rp-price-box">
                  <div className="rp-price-row">
                    <span>Total Amount</span>
                    <span className="rp-price-val">{fmtMoney(paymentData.totalAmount)}</span>
                  </div>
                  <div className="rp-price-row rp-price-dep">
                    <span>50% Deposit Required</span>
                    <span className="rp-price-val rp-accent-text">{fmtMoney(paymentData.depositAmount)}</span>
                  </div>
                </div>
              )}

              <div className="rp-modal-foot">
                <button type="button" className="rp-btn rp-btn-ghost" onClick={() => setShowNewProjectModal(false)}>Cancel</button>
                <button type="submit" className="rp-btn rp-btn-primary">
                  Proceed to Payment →
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* ═══════════ PAYMENT MODAL ═══════════ */}
      {showPaymentModal && (
        <div className="rp-modal-overlay" onClick={() => setShowPaymentModal(false)}>
          <div className="rp-modal rp-modal-sm" onClick={e => e.stopPropagation()}>
            <div className="rp-modal-hdr">
              <div>
                <div className="rp-eyebrow">Secure Checkout</div>
                <h2 className="rp-modal-title">Pay Deposit</h2>
              </div>
              <button className="rp-modal-close" onClick={() => setShowPaymentModal(false)}>✕</button>
            </div>

            <div className="rp-pay-summary">
              <div className="rp-prow"><span>Total Project Cost</span><span>{fmtMoney(paymentData.totalAmount)}</span></div>
              <div className="rp-prow rp-prow-hl"><span>Deposit (50%) — Due Now</span><span>{fmtMoney(paymentData.depositAmount)}</span></div>
              <div className="rp-prow rp-prow-dim"><span>Balance on Completion</span><span>{fmtMoney(paymentData.depositAmount)}</span></div>
            </div>

            <form onSubmit={handlePaymentSubmit} className="rp-form">
              <div className="rp-fg">
                <label>Payment Method <span className="rp-req">*</span></label>
                <div className="rp-pay-methods">
                  {[{ value:'mpesa', icon:'📱', label:'M-Pesa' }, { value:'card', icon:'💳', label:'Card' }].map(m => (
                    <label key={m.value} className={`rp-pay-method ${paymentData.paymentMethod===m.value?'active':''}`}>
                      <input type="radio" name="paymentMethod" value={m.value} checked={paymentData.paymentMethod===m.value} onChange={handlePaymentInputChange} style={{ display:'none' }} />
                      <span>{m.icon}</span><span>{m.label}</span>
                    </label>
                  ))}
                </div>
              </div>

              {paymentData.paymentMethod === 'mpesa' && (
                <div className="rp-fg">
                  <label>M-Pesa Number <span className="rp-req">*</span></label>
                  <input type="tel" name="mpesaNumber" placeholder="07XX XXX XXX" value={paymentData.mpesaNumber} onChange={handlePaymentInputChange} required pattern="[0-9]{10}" />
                  <span className="rp-hint">Enter your M-Pesa registered number</span>
                </div>
              )}

              {paymentData.paymentMethod === 'card' && (
                <>
                  <div className="rp-fg">
                    <label>Cardholder Name <span className="rp-req">*</span></label>
                    <input type="text" name="cardName" placeholder="John Doe" value={paymentData.cardName} onChange={handlePaymentInputChange} required />
                  </div>
                  <div className="rp-fg">
                    <label>Card Number <span className="rp-req">*</span></label>
                    <input type="text" name="cardNumber" placeholder="1234 5678 9012 3456" value={paymentData.cardNumber} onChange={handlePaymentInputChange} maxLength="16" required />
                  </div>
                  <div className="rp-form-row">
                    <div className="rp-fg">
                      <label>Expiry <span className="rp-req">*</span></label>
                      <input type="text" name="expiryDate" placeholder="MM/YY" value={paymentData.expiryDate} onChange={handlePaymentInputChange} maxLength="5" required />
                    </div>
                    <div className="rp-fg">
                      <label>CVV <span className="rp-req">*</span></label>
                      <input type="text" name="cvv" placeholder="123" value={paymentData.cvv} onChange={handlePaymentInputChange} maxLength="3" required />
                    </div>
                  </div>
                </>
              )}

              <div className="rp-secure-note">🔒 Your payment is encrypted and secure</div>

              <div className="rp-modal-foot">
                <button type="button" className="rp-btn rp-btn-ghost" onClick={() => setShowPaymentModal(false)}>Cancel</button>
                <button type="submit" className="rp-btn rp-btn-primary" disabled={submitting}>
                  {submitting ? 'Processing…' : `Pay ${fmtMoney(paymentData.depositAmount)} →`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

    </div>
  );
};

export default Dashboard;