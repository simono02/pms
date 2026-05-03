import React from 'react';
import './Alert.css';

const Alert = ({ 
  type = 'info', 
  message, 
  onClose, 
  autoClose = false, 
  duration = 5000 
}) => {
  React.useEffect(() => {
    if (autoClose && onClose) {
      const timer = setTimeout(() => {
        onClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [autoClose, onClose, duration]);

  if (!message) return null;

  return (
    <div className={`alert alert-${type}`}>
      <div className="alert-content">
        <span className="alert-message">{message}</span>
        {onClose && (
          <button className="alert-close" onClick={onClose}>
            &times;
          </button>
        )}
      </div>
    </div>
  );
};

export default Alert;
