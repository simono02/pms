import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  const [theme, setTheme] = useState('light');
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    document.documentElement.setAttribute('data-theme', savedTheme);
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  return (
    <div className="home-page">
      {/* Custom Navigation */}
      <nav className={`main-nav ${scrolled ? 'scrolled' : ''}`}>
        <div className="nav-container">
          <div className="nav-brand">
            <span className="brand-icon">🎓</span>
            <span className="brand-text">ResearchPro</span>
          </div>
          <div className="nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#pricing">Pricing</a>
            <Link to="/login" className="nav-btn login-btn">Sign In</Link>
            <Link to="/register" className="nav-btn register-btn">Get Started</Link>
          </div>
          <button className="theme-toggle-btn" onClick={toggleTheme}>
            {theme === 'light' ? '🌙' : '☀️'}
          </button>
        </div>
      </nav>

      {/* Animated Background */}
      <div className="animated-bg">
        <div className="gradient-orb orb-1"></div>
        <div className="gradient-orb orb-2"></div>
        <div className="gradient-orb orb-3"></div>
        <div className="floating-particles">
          {[...Array(30)].map((_, i) => (
            <div 
              key={i} 
              className="particle" 
              style={{
                left: `${Math.random() * 100}%`,
                animationDelay: `${Math.random() * 5}s`,
                animationDuration: `${5 + Math.random() * 10}s`
              }}
            ></div>
          ))}
        </div>
      </div>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <div className="hero-content">
            <div className="hero-badge">
              <span className="pulse-indicator"></span>
              <span>Trusted by 15,000+ Researchers Worldwide</span>
            </div>
            
            <h1 className="hero-title">
              Elevate Your <span className="highlight-text">Research</span>
              <br />To Academic Excellence
            </h1>
            
            <p className="hero-description">
              Professional research management platform that transforms your academic projects 
              into publication-ready work. Upload, track, collaborate, and achieve excellence 
              with complete transparency and expert support.
            </p>
            
            <div className="hero-buttons">
              <Link to="/register" className="btn btn-primary">
                <span>Start Your Project</span>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M7.5 15L12.5 10L7.5 5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </Link>
              <Link to="/login" className="btn btn-secondary">
                <span>View Demo</span>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path d="M10 5V10L13 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                  <circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="2"/>
                </svg>
              </Link>
            </div>

            {/* Trust Indicators */}
            <div className="trust-badges">
              <div className="trust-item">
                <div className="trust-icon">✓</div>
                <span>100% Confidential</span>
              </div>
              <div className="trust-item">
                <div className="trust-icon">⚡</div>
                <span>Fast Turnaround</span>
              </div>
              <div className="trust-item">
                <div className="trust-icon">🏆</div>
                <span>Expert Team</span>
              </div>
            </div>
          </div>

          {/* Hero Visual */}
          <div className="hero-visual">
            <div className="research-card main-card">
              <div className="card-header-bar">
                <div className="status-pill active">
                  <span className="status-dot"></span>
                  Project Active
                </div>
                <span className="card-date">Feb 2026</span>
              </div>
              
              <div className="research-stats">
                <div className="circular-progress">
                  <svg viewBox="0 0 100 100">
                    <circle className="progress-bg" cx="50" cy="50" r="45"/>
                    <circle className="progress-bar" cx="50" cy="50" r="45" 
                            style={{'--progress': '85'}}/>
                  </svg>
                  <div className="progress-value">85%</div>
                </div>
                <div className="stats-info">
                  <div className="stat-row">
                    <span className="stat-label">Completion</span>
                    <span className="stat-value">85%</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Quality Score</span>
                    <span className="stat-value">9.8/10</span>
                  </div>
                  <div className="stat-row">
                    <span className="stat-label">Timeline</span>
                    <span className="stat-value">On Track</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Floating Mini Cards */}
            <div className="mini-card card-1">
              <div className="mini-icon">📊</div>
              <div className="mini-content">
                <div className="mini-title">Data Analysis</div>
                <div className="mini-status success">Complete</div>
              </div>
            </div>

            <div className="mini-card card-2">
              <div className="mini-icon">📝</div>
              <div className="mini-content">
                <div className="mini-title">Literature Review</div>
                <div className="mini-status progress">In Progress</div>
              </div>
            </div>

            <div className="mini-card card-3">
              <div className="mini-icon">✅</div>
              <div className="mini-content">
                <div className="mini-title">Peer Review</div>
                <div className="mini-status pending">Pending</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section" id="features">
        <div className="container">
          <div className="section-header">
            <span className="section-tag">Why Choose Us</span>
            <h2 className="section-title">Everything You Need for Research Excellence</h2>
            <p className="section-subtitle">Comprehensive tools and expert support to transform your research journey</p>
          </div>

          <div className="features-grid">
            <div className="feature-box">
              <div className="feature-icon-wrapper purple">
                <span className="feature-icon">🚀</span>
              </div>
              <h3 className="feature-title">Fast Turnaround</h3>
              <p className="feature-text">Get your research processed quickly without compromising on quality. Average delivery in 3-5 days.</p>
            </div>

            <div className="feature-box">
              <div className="feature-icon-wrapper blue">
                <span className="feature-icon">🔒</span>
              </div>
              <h3 className="feature-title">100% Confidential</h3>
              <p className="feature-text">Your research is protected with enterprise-grade security. We never share your work.</p>
            </div>

            <div className="feature-box">
              <div className="feature-icon-wrapper green">
                <span className="feature-icon">👁️</span>
              </div>
              <h3 className="feature-title">Preview Before Payment</h3>
              <p className="feature-text">Review the complete work before making payment. 100% satisfaction guaranteed.</p>
            </div>

            <div className="feature-box">
              <div className="feature-icon-wrapper orange">
                <span className="feature-icon">🎓</span>
              </div>
              <h3 className="feature-title">Expert Researchers</h3>
              <p className="feature-text">PhD-level experts in your field ensure the highest quality standards.</p>
            </div>

            <div className="feature-box">
              <div className="feature-icon-wrapper pink">
                <span className="feature-icon">📊</span>
              </div>
              <h3 className="feature-title">Real-Time Tracking</h3>
              <p className="feature-text">Monitor your project's progress at every stage with live updates.</p>
            </div>

            <div className="feature-box">
              <div className="feature-icon-wrapper teal">
                <span className="feature-icon">💬</span>
              </div>
              <h3 className="feature-title">24/7 Support</h3>
              <p className="feature-text">Get instant help whenever you need it. Our team is always available.</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="how-it-works" id="how-it-works">
        <div className="container">
          <div className="section-header">
            <span className="section-tag">Simple Process</span>
            <h2 className="section-title">How It Works</h2>
            <p className="section-subtitle">Four simple steps to research excellence</p>
          </div>

          <div className="steps-container">
            <div className="step-item">
              <div className="step-number">1</div>
              <div className="step-content">
                <div className="step-icon">📤</div>
                <h3 className="step-title">Upload Project</h3>
                <p className="step-description">Submit your research document, requirements, and deadline through our secure platform.</p>
              </div>
            </div>

            <div className="step-connector"></div>

            <div className="step-item">
              <div className="step-number">2</div>
              <div className="step-content">
                <div className="step-icon">👨‍🔬</div>
                <h3 className="step-title">Expert Assignment</h3>
                <p className="step-description">We match your project with a qualified researcher in your specific field.</p>
              </div>
            </div>

            <div className="step-connector"></div>

            <div className="step-item">
              <div className="step-number">3</div>
              <div className="step-content">
                <div className="step-icon">🔍</div>
                <h3 className="step-title">Review & Approve</h3>
                <p className="step-description">Preview the completed work and request revisions if needed before payment.</p>
              </div>
            </div>

            <div className="step-connector"></div>

            <div className="step-item">
              <div className="step-number">4</div>
              <div className="step-content">
                <div className="step-icon">⬇️</div>
                <h3 className="step-title">Download Results</h3>
                <p className="step-description">Get your publication-ready research with full documentation and support.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="pricing-section" id="pricing">
        <div className="container">
          <div className="section-header">
            <span className="section-tag">Transparent Pricing</span>
            <h2 className="section-title">Choose Your Plan</h2>
            <p className="section-subtitle">No hidden fees. Pay only for what you need.</p>
          </div>

          <div className="pricing-grid">
            <div className="pricing-card">
              <div className="pricing-header">
                <h3 className="plan-name">Starter</h3>
                <div className="plan-price">
                  <span className="currency">$</span>
                  <span className="amount">299</span>
                  <span className="period">/project</span>
                </div>
              </div>
              <ul className="plan-features">
                <li>✓ Basic Research Support</li>
                <li>✓ 7-Day Turnaround</li>
                <li>✓ 1 Revision Round</li>
                <li>✓ Email Support</li>
                <li>✓ Quality Guarantee</li>
              </ul>
              <Link to="/register" className="plan-button">Get Started</Link>
            </div>

            <div className="pricing-card featured">
              <div className="popular-badge">Most Popular</div>
              <div className="pricing-header">
                <h3 className="plan-name">Professional</h3>
                <div className="plan-price">
                  <span className="currency">$</span>
                  <span className="amount">599</span>
                  <span className="period">/project</span>
                </div>
              </div>
              <ul className="plan-features">
                <li>✓ Advanced Research Support</li>
                <li>✓ 5-Day Turnaround</li>
                <li>✓ Unlimited Revisions</li>
                <li>✓ Priority Support</li>
                <li>✓ Plagiarism Report</li>
                <li>✓ Statistical Analysis</li>
              </ul>
              <Link to="/register" className="plan-button featured-button">Get Started</Link>
            </div>

            <div className="pricing-card">
              <div className="pricing-header">
                <h3 className="plan-name">Enterprise</h3>
                <div className="plan-price">
                  <span className="amount-text">Custom</span>
                </div>
              </div>
              <ul className="plan-features">
                <li>✓ Full Research Partnership</li>
                <li>✓ Custom Timelines</li>
                <li>✓ Unlimited Revisions</li>
                <li>✓ Dedicated Manager</li>
                <li>✓ Advanced Analytics</li>
                <li>✓ Team Collaboration</li>
              </ul>
              <Link to="/register" className="plan-button">Contact Sales</Link>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <h2 className="cta-title">Ready to Transform Your Research?</h2>
            <p className="cta-text">Join thousands of researchers who trust us with their academic success</p>
            <div className="cta-buttons">
              <Link to="/register" className="btn btn-white">
                Start Your First Project
              </Link>
              <Link to="/login" className="btn btn-outline">
                Sign In to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="main-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <div className="footer-logo">
                <span className="brand-icon">🎓</span>
                <span className="brand-text">ResearchPro</span>
              </div>
              <p className="footer-description">
                Professional research management platform empowering academics worldwide.
              </p>
            </div>

            <div className="footer-links">
              <div className="footer-column">
                <h4>Product</h4>
                <a href="#features">Features</a>
                <a href="#how-it-works">How It Works</a>
                <a href="#pricing">Pricing</a>
              </div>

              <div className="footer-column">
                <h4>Company</h4>
                <a href="#about">About Us</a>
                <a href="#team">Our Team</a>
                <a href="#careers">Careers</a>
              </div>

              <div className="footer-column">
                <h4>Support</h4>
                <a href="#help">Help Center</a>
                <a href="#contact">Contact Us</a>
                <a href="#faq">FAQ</a>
              </div>
            </div>
          </div>

          <div className="footer-bottom">
            <p>&copy; 2026 ResearchPro. All rights reserved.</p>
            <div className="footer-legal">
              <a href="#privacy">Privacy Policy</a>
              <span>•</span>
              <a href="#terms">Terms of Service</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;