import React from 'react';
import { Link } from 'react-router-dom';
import LoginForm from '../components/auth/LoginForm';
import './LoginPage.css';

const LoginPage = () => {
  return (
    <div className="lp">
      {/* Animated background */}
      <div className="lp-bg" aria-hidden="true">
        <div className="lp-bg__orb lp-bg__orb--1" />
        <div className="lp-bg__orb lp-bg__orb--2" />
        <div className="lp-bg__orb lp-bg__orb--3" />
        <div className="lp-bg__grid" />
      </div>

      {/* Floating research decorations */}
      <div className="lp-deco" aria-hidden="true">
        <span className="lp-deco__pill lp-deco__pill--1">Research</span>
        <span className="lp-deco__pill lp-deco__pill--2">Publish</span>
        <span className="lp-deco__pill lp-deco__pill--3">Collaborate</span>
        <span className="lp-deco__pill lp-deco__pill--4">Cite</span>
      </div>

      {/* Card */}
      <div className="lp-card-wrap">
        <div className="lp-card">
          {/* Header */}
          <div className="lp-card__header">
            <div className="lp-logo" aria-hidden="true">
              <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
                <circle cx="16" cy="16" r="14" stroke="white" strokeWidth="2" opacity="0.5"/>
                <circle cx="16" cy="16" r="8"  stroke="white" strokeWidth="2" opacity="0.75"/>
                <circle cx="16" cy="16" r="3"  fill="white"/>
                <line x1="16" y1="2"  x2="16" y2="30" stroke="white" strokeWidth="1.5" opacity="0.4"/>
                <line x1="2"  y1="16" x2="30" y2="16" stroke="white" strokeWidth="1.5" opacity="0.4"/>
              </svg>
            </div>
            <h1 className="lp-card__title">
              Welcome back to <em>Research Pro</em>
            </h1>
            <p className="lp-card__subtitle">
              Sign in to access your workspace, publications, and collaborations.
            </p>
          </div>

          {/* Form */}
          <div className="lp-card__body">
            <LoginForm />
          </div>

          {/* Footer */}
          <div className="lp-card__footer">
            <p>
              New to Research Pro?{' '}
              <Link to="/register" className="lp-link">Create your account</Link>
            </p>
          </div>
        </div>

        {/* Subtle trust badges */}
        <div className="lp-trust" aria-label="Platform statistics">
          <span className="lp-trust__item">
            <strong>120K+</strong> Researchers
          </span>
          <span className="lp-trust__sep" aria-hidden="true">·</span>
          <span className="lp-trust__item">
            <strong>4.8M</strong> Publications
          </span>
          <span className="lp-trust__sep" aria-hidden="true">·</span>
          <span className="lp-trust__item">
            <strong>98%</strong> Uptime
          </span>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;