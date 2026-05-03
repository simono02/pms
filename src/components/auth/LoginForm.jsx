import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Input from '../common/Input';
import Button from '../common/Button';
import './LoginForm.css';

const EyeIcon = ({ open }) => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    {open ? (
      <>
        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
        <circle cx="12" cy="12" r="3"/>
      </>
    ) : (
      <>
        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
        <line x1="1" y1="1" x2="23" y2="23"/>
      </>
    )}
  </svg>
);

const AlertBanner = ({ alert, onClose }) => {
  if (!alert) return null;
  const isSuccess = alert.type === 'success';
  return (
    <div className={`lf-alert lf-alert--${alert.type}`} role="alert">
      <span className="lf-alert__icon">{isSuccess ? '✓' : '!'}</span>
      <span className="lf-alert__message">{alert.message}</span>
      <button className="lf-alert__close" onClick={onClose} aria-label="Close">×</button>
    </div>
  );
};

const LoginForm = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [errors, setErrors] = useState({});
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const validateForm = () => {
    const newErrors = {};
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validateForm()) return;
    setLoading(true);
    setAlert(null);
    try {
      const response = await login(formData.email, formData.password);
      const userRole = response.user.role;
      setAlert({ type: 'success', message: 'Login successful! Redirecting…' });
      setTimeout(() => {
        switch (userRole) {
          case 'admin': navigate('/admin/dashboard'); break;
          case 'staff': navigate('/staff/dashboard'); break;
          default: navigate('/dashboard');
        }
      }, 1200);
    } catch (error) {
      setAlert({ type: 'error', message: error.message || 'Invalid credentials. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className={`lf${loading ? ' lf--loading' : ''}`} onSubmit={handleSubmit} noValidate>
      <AlertBanner alert={alert} onClose={() => setAlert(null)} />

      <div className="lf-field">
        <label className="lf-label" htmlFor="email">Email Address</label>
        <div className="lf-input-wrap">
          <input
            id="email"
            className={`lf-input${errors.email ? ' lf-input--error' : ''}`}
            type="email"
            value={formData.email}
            onChange={e => handleChange('email', e.target.value)}
            placeholder="you@institution.edu"
            required
            autoComplete="email"
          />
        </div>
        {errors.email && <p className="lf-error-msg">{errors.email}</p>}
      </div>

      <div className="lf-field">
        <label className="lf-label" htmlFor="password">Password</label>
        <div className="lf-input-wrap lf-input-wrap--password">
          <input
            id="password"
            className={`lf-input lf-input--has-toggle${errors.password ? ' lf-input--error' : ''}`}
            type={showPassword ? 'text' : 'password'}
            value={formData.password}
            onChange={e => handleChange('password', e.target.value)}
            placeholder="Enter your password"
            required
            autoComplete="current-password"
          />
          <button
            type="button"
            className={`lf-eye-btn${showPassword ? ' lf-eye-btn--active' : ''}`}
            onClick={() => setShowPassword(v => !v)}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
            tabIndex={-1}
          >
            <EyeIcon open={showPassword} />
          </button>
        </div>
        {errors.password && <p className="lf-error-msg">{errors.password}</p>}
      </div>

      <div className="lf-options">
        <label className="lf-remember">
          <input type="checkbox" className="lf-checkbox" />
          <span className="lf-checkbox-label">Remember me</span>
        </label>
        <a href="/forgot-password" className="lf-forgot">Forgot password?</a>
      </div>

      <button type="submit" className="lf-submit" disabled={loading}>
        {loading ? (
          <span className="lf-spinner" />
        ) : (
          <>
            <span>Sign In</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
            </svg>
          </>
        )}
      </button>
    </form>
  );
};

export default LoginForm;