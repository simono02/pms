import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { usePayment } from '../../hooks/usePayment';
import { projectService } from '../../services/projectService';
import Input from '../common/Input';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import './Payment.css';

const Payment = () => {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const { processPayment, loading: paymentLoading } = usePayment();
  const [project, setProject] = useState(null);
  const [formData, setFormData] = useState({
    cardNumber: '',
    cardName: '',
    expiryDate: '',
    cvv: '',
    amount: 0
  });
  const [errors, setErrors] = useState({});
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      setLoading(true);
      const data = await projectService.getProject(projectId);
      
      if (data.status !== 'payment_required') {
        setAlert({ 
          type: 'error', 
          message: 'This project does not require payment.' 
        });
        return;
      }
      
      setProject(data);
      setFormData(prev => ({ ...prev, amount: data.price || 50 }));
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to load project details.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const formatCardNumber = (value) => {
    const cleaned = value.replace(/\s/g, '');
    const chunks = cleaned.match(/.{1,4}/g) || [];
    return chunks.join(' ');
  };

  const formatExpiryDate = (value) => {
    const cleaned = value.replace(/\D/g, '');
    if (cleaned.length >= 2) {
      return cleaned.slice(0, 2) + '/' + cleaned.slice(2, 4);
    }
    return cleaned;
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.cardNumber) {
      newErrors.cardNumber = 'Card number is required';
    } else if (formData.cardNumber.replace(/\s/g, '').length !== 16) {
      newErrors.cardNumber = 'Card number must be 16 digits';
    }
    
    if (!formData.cardName) {
      newErrors.cardName = 'Cardholder name is required';
    }
    
    if (!formData.expiryDate) {
      newErrors.expiryDate = 'Expiry date is required';
    } else if (!/^\d{2}\/\d{2}$/.test(formData.expiryDate)) {
      newErrors.expiryDate = 'Invalid expiry date format (MM/YY)';
    }
    
    if (!formData.cvv) {
      newErrors.cvv = 'CVV is required';
    } else if (!/^\d{3,4}$/.test(formData.cvv)) {
      newErrors.cvv = 'CVV must be 3 or 4 digits';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      setAlert(null);
      await processPayment(projectId, {
        amount: formData.amount,
        card_number: formData.cardNumber.replace(/\s/g, ''),
        card_name: formData.cardName,
        expiry_date: formData.expiryDate,
        cvv: formData.cvv
      });
      
      setAlert({ type: 'success', message: 'Payment successful!' });
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Payment failed. Please try again.' 
      });
    }
  };

  if (loading) {
    return <Loader text="Loading payment details..." />;
  }

  if (!project) {
    return (
      <div className="payment-error">
        <Alert type="error" message="Project not found" />
        <Button onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="payment">
      <div className="payment-header">
        <Button 
          variant="secondary" 
          onClick={() => navigate('/dashboard')}
        >
          ← Back to Dashboard
        </Button>
        <h1>Complete Payment</h1>
      </div>

      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}

      <div className="payment-content">
        <div className="payment-summary">
          <h2>Order Summary</h2>
          <div className="summary-item">
            <span>Project:</span>
            <span>{project.title}</span>
          </div>
          <div className="summary-item">
            <span>Research Field:</span>
            <span>{project.research_field}</span>
          </div>
          <div className="summary-item total">
            <span>Total Amount:</span>
            <span>${formData.amount.toFixed(2)}</span>
          </div>
        </div>

        <div className="payment-form-container">
          <h2>Payment Details</h2>
          
          <form onSubmit={handleSubmit} className="payment-form">
            <Input
              label="Card Number"
              type="text"
              name="cardNumber"
              value={formData.cardNumber}
              onChange={(value) => handleChange('cardNumber', formatCardNumber(value))}
              placeholder="1234 5678 9012 3456"
              error={errors.cardNumber}
              required
              maxLength={19}
            />
            
            <Input
              label="Cardholder Name"
              type="text"
              name="cardName"
              value={formData.cardName}
              onChange={(value) => handleChange('cardName', value)}
              placeholder="John Doe"
              error={errors.cardName}
              required
            />
            
            <div className="form-row">
              <div className="form-group">
                <Input
                  label="Expiry Date"
                  type="text"
                  name="expiryDate"
                  value={formData.expiryDate}
                  onChange={(value) => handleChange('expiryDate', formatExpiryDate(value))}
                  placeholder="MM/YY"
                  error={errors.expiryDate}
                  required
                  maxLength={5}
                />
              </div>
              
              <div className="form-group">
                <Input
                  label="CVV"
                  type="text"
                  name="cvv"
                  value={formData.cvv}
                  onChange={(value) => handleChange('cvv', value.replace(/\D/g, ''))}
                  placeholder="123"
                  error={errors.cvv}
                  required
                  maxLength={4}
                />
              </div>
            </div>
            
            <div className="payment-security">
              <Alert 
                type="info" 
                message="Your payment information is encrypted and secure." 
              />
            </div>
            
            <Button
              type="submit"
              variant="primary"
              size="large"
              loading={paymentLoading}
              disabled={paymentLoading}
              className="payment-button"
            >
              {paymentLoading ? 'Processing...' : `Pay $${formData.amount.toFixed(2)}`}
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Payment;
