import React from 'react';
import './Input.css';

const Input = ({ 
  label, 
  type = 'text', 
  name, 
  value, 
  onChange, 
  placeholder, 
  error, 
  required = false, 
  disabled = false,
  className = '',
  ...props 
}) => {
  const handleChange = (e) => {
    onChange && onChange(e.target.value);
  };

  const inputClasses = [
    'input-field',
    error ? 'input-error' : '',
    disabled ? 'input-disabled' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="input-group">
      {label && (
        <label htmlFor={name} className="input-label">
          {label}
          {required && <span className="input-required">*</span>}
        </label>
      )}
      
      <input
        type={type}
        id={name}
        name={name}
        value={value}
        onChange={handleChange}
        placeholder={placeholder}
        disabled={disabled}
        className={inputClasses}
        {...props}
      />
      
      {error && (
        <span className="input-error-message">{error}</span>
      )}
    </div>
  );
};

export default Input;
