import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import Input from '../common/Input';
import Button from '../common/Button';
import Alert from '../common/Alert';
import './RegisterForm.css';

const RegisterForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [errors, setErrors] = useState({});
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password';
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
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
      await register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        role: 'user' // Always register as 'user' by default
      });
      setAlert({ type: 'success', message: 'Registration successful!' });
      setTimeout(() => {
        navigate('/login');
      }, 1500);
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Registration failed. Please try again.' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="register-form">
      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}
      
      <form onSubmit={handleSubmit}>
        <Input
          label="Full Name"
          type="text"
          name="name"
          value={formData.name}
          onChange={(value) => handleChange('name', value)}
          placeholder="Enter your full name"
          error={errors.name}
          required
        />
        
        <Input
          label="Email"
          type="email"
          name="email"
          value={formData.email}
          onChange={(value) => handleChange('email', value)}
          placeholder="Enter your email"
          error={errors.email}
          required
        />
        
        <Input
          label="Password"
          type="password"
          name="password"
          value={formData.password}
          onChange={(value) => handleChange('password', value)}
          placeholder="Enter your password"
          error={errors.password}
          required
        />
        
        <Input
          label="Confirm Password"
          type="password"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={(value) => handleChange('confirmPassword', value)}
          placeholder="Confirm your password"
          error={errors.confirmPassword}
          required
        />
        
        <Button
          type="submit"
          variant="primary"
          size="large"
          loading={loading}
          disabled={loading}
          className="register-button"
        >
          Register
        </Button>
      </form>
    </div>
  );
};

export default RegisterForm;