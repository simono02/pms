import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './SetupPassword.css';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

/* ── SVG Icons ─────────────────────────────────────────────── */
const EyeOpen = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
    <circle cx="12" cy="12" r="3"/>
  </svg>
);

const EyeClosed = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
    <line x1="1" y1="1" x2="23" y2="23"/>
  </svg>
);

const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
);

const ShieldIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    <polyline points="9 12 11 14 15 10"/>
  </svg>
);

/* ── Strength helpers ──────────────────────────────────────── */
const getStrength = (pw) => {
  if (!pw) return 0;
  let s = 0;
  if (pw.length >= 8)           s++;
  if (pw.length >= 12)          s++;
  if (/[A-Z]/.test(pw))         s++;
  if (/[0-9]/.test(pw))         s++;
  if (/[^A-Za-z0-9]/.test(pw))  s++;
  return s;
};

const STRENGTH_META = [
  { label: '',            color: 'var(--seg-empty)' },
  { label: 'Weak',        color: '#f87171' },
  { label: 'Fair',        color: '#fb923c' },
  { label: 'Good',        color: '#facc15' },
  { label: 'Strong',      color: '#4ade80' },
  { label: 'Very Strong', color: '#22d3ee' },
];

const REQUIREMENTS = [
  { label: 'At least 8 characters',  test: pw => pw.length >= 8 },
  { label: 'One uppercase letter',   test: pw => /[A-Z]/.test(pw) },
  { label: 'One number',             test: pw => /[0-9]/.test(pw) },
  { label: 'One special character',  test: pw => /[^A-Za-z0-9]/.test(pw) },
];

/* ── Component ─────────────────────────────────────────────── */
const SetupPassword = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');

  const [formData, setFormData] = useState({ password: '', confirmPassword: '' });
  const [status, setStatus] = useState('idle');
  const [message, setMessage] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    if (!token) {
      setStatus('error');
      setMessage('Invalid or missing token. Please request a new invite link.');
    }
  }, [token]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (status === 'error') setStatus('idle');
  };

  const strength = getStrength(formData.password);
  const meta = STRENGTH_META[strength];
  const passwordsMatch = formData.confirmPassword && formData.password === formData.confirmPassword;
  const passwordsMismatch = formData.confirmPassword && formData.password !== formData.confirmPassword;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password.length < 8) {
      setStatus('error'); setMessage('Password must be at least 8 characters.'); return;
    }
    if (formData.password !== formData.confirmPassword) {
      setStatus('error'); setMessage('Passwords do not match.'); return;
    }
    setStatus('loading'); setMessage('');
    try {
      await axios.post(`${API_BASE}/auth/staff/setup-password`, { token, password: formData.password });
      setStatus('success');
      setMessage('Your account is ready! Redirecting to login…');
      setTimeout(() => navigate('/login'), 3500);
    } catch (err) {
      setStatus('error');
      setMessage(err.response?.data?.error || 'Something went wrong. Please try again.');
    }
  };

  return (
    <div className={`sp-page${mounted ? ' sp-page--in' : ''}`}>

      {/* ── Background ──────────────────────────────────────── */}
      <div className="sp-bg" aria-hidden="true">
        <div className="sp-bg__orb sp-bg__orb--1" />
        <div className="sp-bg__orb sp-bg__orb--2" />
        <div className="sp-bg__orb sp-bg__orb--3" />
        <div className="sp-bg__grid" />
        {/* Decorative floating rings */}
        <div className="sp-bg__ring sp-bg__ring--1" />
        <div className="sp-bg__ring sp-bg__ring--2" />
      </div>

      {/* ── Card ────────────────────────────────────────────── */}
      <div className="sp-card">

        {/* Header */}
        <div className="sp-header">
          <div className="sp-logo">
            <ShieldIcon />
          </div>
          <h1 className="sp-title">
            Activate Your <em>Account</em>
          </h1>
          <p className="sp-subtitle">
            Welcome to the Research Pro team. Create a secure password to get started.
          </p>
        </div>

        {/* ── Success State ────────────────────────────────── */}
        {status === 'success' ? (
          <div className="sp-success">
            <div className="sp-success__icon">
              <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </div>
            <h2 className="sp-success__title">You're all set!</h2>
            <p className="sp-success__text">{message}</p>
            <div className="sp-progress" role="progressbar" aria-label="Redirecting">
              <div className="sp-progress__fill" />
            </div>
          </div>
        ) : (
          <>
            {/* Error banner */}
            {status === 'error' && (
              <div className="sp-error" role="alert">
                <span className="sp-error__icon">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/></svg>
                </span>
                <span>{message}</span>
              </div>
            )}

            {/* Form */}
            <form className="sp-form" onSubmit={handleSubmit} noValidate>

              {/* Password field */}
              <div className="sp-field">
                <label className="sp-label" htmlFor="sp-password">New Password</label>
                <div className="sp-input-wrap">
                  <input
                    id="sp-password"
                    className="sp-input"
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Min. 8 characters"
                    required
                    disabled={status === 'loading' || !token}
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    className={`sp-eye${showPassword ? ' sp-eye--on' : ''}`}
                    onClick={() => setShowPassword(v => !v)}
                    tabIndex={-1}
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeClosed /> : <EyeOpen />}
                  </button>
                </div>

                {/* Strength meter */}
                {formData.password.length > 0 && (
                  <div className="sp-strength">
                    <div className="sp-strength__bar">
                      {[1,2,3,4,5].map(i => (
                        <div
                          key={i}
                          className="sp-strength__seg"
                          style={{ background: i <= strength ? meta.color : 'var(--seg-empty)' }}
                        />
                      ))}
                    </div>
                    <span className="sp-strength__label" style={{ color: meta.color }}>
                      {meta.label}
                    </span>
                  </div>
                )}

                {/* Requirements checklist */}
                {formData.password.length > 0 && (
                  <ul className="sp-reqs">
                    {REQUIREMENTS.map(req => {
                      const ok = req.test(formData.password);
                      return (
                        <li key={req.label} className={`sp-req${ok ? ' sp-req--ok' : ''}`}>
                          <span className="sp-req__icon">{ok ? <CheckIcon /> : null}</span>
                          {req.label}
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>

              {/* Confirm Password field */}
              <div className="sp-field">
                <label className="sp-label" htmlFor="sp-confirm">Confirm Password</label>
                <div className="sp-input-wrap">
                  <input
                    id="sp-confirm"
                    className={`sp-input${passwordsMismatch ? ' sp-input--error' : ''}${passwordsMatch ? ' sp-input--ok' : ''}`}
                    type={showConfirm ? 'text' : 'password'}
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    placeholder="Re-enter your password"
                    required
                    disabled={status === 'loading' || !token}
                    autoComplete="new-password"
                  />
                  <button
                    type="button"
                    className={`sp-eye${showConfirm ? ' sp-eye--on' : ''}`}
                    onClick={() => setShowConfirm(v => !v)}
                    tabIndex={-1}
                    aria-label={showConfirm ? 'Hide password' : 'Show password'}
                  >
                    {showConfirm ? <EyeClosed /> : <EyeOpen />}
                  </button>
                </div>
                {passwordsMismatch && (
                  <p className="sp-mismatch">Passwords do not match</p>
                )}
                {passwordsMatch && (
                  <p className="sp-match">
                    <CheckIcon /> Passwords match
                  </p>
                )}
              </div>

              {/* Submit */}
              <button
                type="submit"
                className={`sp-submit${status === 'loading' ? ' sp-submit--loading' : ''}`}
                disabled={status === 'loading' || !token}
              >
                {status === 'loading' ? (
                  <>
                    <span className="sp-spinner" />
                    <span>Activating your account…</span>
                  </>
                ) : (
                  <>
                    <span>Activate Account</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
                    </svg>
                  </>
                )}
              </button>

            </form>
          </>
        )}

        {/* Footer */}
        <p className="sp-footer">
          Already have an account?{' '}
          <button className="sp-footer__link" onClick={() => navigate('/login')}>
            Sign in
          </button>
        </p>
      </div>
    </div>
  );
};

export default SetupPassword;