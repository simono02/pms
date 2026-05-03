import React from 'react';
import './Button.css';

const Button = ({ 
  children, 
  onClick, 
  type = 'button', 
  variant = 'primary', 
  size = 'medium', 
  disabled = false, 
  loading = false,
  className = '',
  ...props 
}) => {
  const baseClasses = 'btn';
  const variantClasses = `btn-${variant}`;
  const sizeClasses = `btn-${size}`;
  const disabledClasses = disabled ? 'btn-disabled' : '';
  const loadingClasses = loading ? 'btn-loading' : '';
  
  const classes = [
    baseClasses,
    variantClasses,
    sizeClasses,
    disabledClasses,
    loadingClasses,
    className
  ].filter(Boolean).join(' ');

  return (
    <button
      type={type}
      className={classes}
      onClick={onClick}
      disabled={disabled || loading}
      {...props}
    >
      {loading ? (
        <>
          <span className="btn-spinner"></span>
          {children}
        </>
      ) : (
        children
      )}
    </button>
  );
};

export default Button;
