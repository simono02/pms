import React from 'react';
import { Link } from 'react-router-dom';
import RegisterForm from '../components/auth/RegisterForm';
import './RegisterPage.css';

const RegisterPage = () => {
  return (
    <div className="register-page">
      <div className="register-page-container">
        <div className="register-page-content">
          <div className="register-page-header">
            <div className="register-page-logo">RM</div>
            <h1 className="register-page-title">Create Account</h1>
            <p className="register-page-subtitle">Join our platform and start managing your research projects</p>
          </div>
          
          <div className="register-page-form">
            <RegisterForm />
          </div>
          
          <div className="register-page-footer">
            <p>Already have an account? <Link to="/login" className="register-page-link">Sign in here</Link></p>
          </div>
        </div>
      </div>
      
      <div className="register-page-background">
        <div className="register-page-shape"></div>
        <div className="register-page-shape"></div>
        <div className="register-page-shape"></div>
      </div>
    </div>
  );
};

export default RegisterPage;