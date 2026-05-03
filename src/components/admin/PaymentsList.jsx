import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { formatDateString } from '../../utils/dateUtils';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import Input from '../common/Input';
import './PaymentsList.css';

const PaymentsList = ({ onDataUpdate }) => {
  const [payments, setPayments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alert, setAlert] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterDateRange, setFilterDateRange] = useState('all');

  useEffect(() => {
    fetchPayments();
  }, []);

  const fetchPayments = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAllPayments();
      setPayments(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
  };

  const handleFilterStatusChange = (value) => {
    setFilterStatus(value);
  };

  const handleDateRangeChange = (value) => {
    setFilterDateRange(value);
  };

  const handleRefundPayment = async (paymentId) => {
    if (!window.confirm('Are you sure you want to refund this payment?')) {
      return;
    }

    try {
      await adminService.refundPayment(paymentId);
      setAlert({ type: 'success', message: 'Payment refunded successfully!' });
      fetchPayments();
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to refund payment.' 
      });
    }
  };

  const filterPaymentsByDate = (payments, range) => {
    if (range === 'all') return payments;
    
    const now = new Date();
    const filterDate = new Date();
    
    switch (range) {
      case 'today':
        filterDate.setHours(0, 0, 0, 0);
        break;
      case 'week':
        filterDate.setDate(now.getDate() - 7);
        break;
      case 'month':
        filterDate.setMonth(now.getMonth() - 1);
        break;
      case 'year':
        filterDate.setFullYear(now.getFullYear() - 1);
        break;
      default:
        return payments;
    }
    
    return payments.filter(payment => 
      new Date(payment.created_at) >= filterDate
    );
  };

  const filteredPayments = payments.filter(payment => {
    const matchesSearch = 
      payment.user.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      payment.user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      payment.project.title.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = filterStatus === 'all' || payment.status === filterStatus;
    
    const matchesDate = filterPaymentsByDate([payment], filterDateRange).length > 0;
    
    return matchesSearch && matchesStatus && matchesDate;
  });

  const totalRevenue = filteredPayments
    .filter(p => p.status === 'completed')
    .reduce((sum, p) => sum + parseFloat(p.amount), 0);

  if (loading) {
    return <Loader text="Loading payments..." />;
  }

  if (error) {
    return (
      <div className="payments-list-error">
        <Alert type="error" message={error} />
        <Button onClick={fetchPayments} variant="primary">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="payments-list">
      <div className="payments-header">
        <h2>Payments Management</h2>
        <div className="payments-stats">
          <span>Total Revenue: ${totalRevenue.toFixed(2)}</span>
          <span>Transactions: {filteredPayments.length}</span>
        </div>
      </div>

      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
          autoClose
        />
      )}

      <div className="payments-filters">
        <Input
          type="text"
          placeholder="Search by client, email, or project..."
          value={searchTerm}
          onChange={handleSearch}
          className="search-input"
        />
        
        <select
          value={filterStatus}
          onChange={(e) => handleFilterStatusChange(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Status</option>
          <option value="pending">Pending</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="refunded">Refunded</option>
        </select>
        
        <select
          value={filterDateRange}
          onChange={(e) => handleDateRangeChange(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Time</option>
          <option value="today">Today</option>
          <option value="week">Last Week</option>
          <option value="month">Last Month</option>
          <option value="year">Last Year</option>
        </select>
      </div>

      <div className="payments-table-container">
        <table className="payments-table">
          <thead>
            <tr>
              <th>Transaction ID</th>
              <th>Client</th>
              <th>Project</th>
              <th>Amount</th>
              <th>Status</th>
              <th>Date</th>
              <th>Payment Method</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredPayments.map((payment) => (
              <tr key={payment.id}>
                <td className="transaction-id">#{payment.transaction_id}</td>
                <td className="client-info">
                  <div className="client-details">
                    <span className="client-name">{payment.user.name}</span>
                    <small className="client-email">{payment.user.email}</small>
                  </div>
                </td>
                <td className="project-title">{payment.project.title}</td>
                <td className="amount">${parseFloat(payment.amount).toFixed(2)}</td>
                <td className="payment-status">
                  <span className={`status-badge ${payment.status}`}>
                    {payment.status}
                  </span>
                </td>
                <td className="payment-date">{formatDateString(payment.created_at)}</td>
                <td className="payment-method">{payment.payment_method || 'Card'}</td>
                <td className="payment-actions">
                  {payment.status === 'completed' && (
                    <Button
                      variant="secondary"
                      size="small"
                      onClick={() => handleRefundPayment(payment.id)}
                    >
                      Refund
                    </Button>
                  )}
                  {payment.status === 'failed' && (
                    <Button
                      variant="primary"
                      size="small"
                      onClick={() => setAlert({ 
                        type: 'info', 
                        message: 'Retry payment functionality would be implemented here' 
                      })}
                    >
                      Retry
                    </Button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredPayments.length === 0 && (
        <div className="no-payments">
          <p>No payments found matching your criteria.</p>
        </div>
      )}

      <div className="payments-summary">
        <h3>Payment Summary</h3>
        <div className="summary-grid">
          <div className="summary-item">
            <label>Total Transactions:</label>
            <span>{filteredPayments.length}</span>
          </div>
          <div className="summary-item">
            <label>Completed:</label>
            <span>{filteredPayments.filter(p => p.status === 'completed').length}</span>
          </div>
          <div className="summary-item">
            <label>Pending:</label>
            <span>{filteredPayments.filter(p => p.status === 'pending').length}</span>
          </div>
          <div className="summary-item">
            <label>Failed:</label>
            <span>{filteredPayments.filter(p => p.status === 'failed').length}</span>
          </div>
          <div className="summary-item">
            <label>Refunded:</label>
            <span>{filteredPayments.filter(p => p.status === 'refunded').length}</span>
          </div>
          <div className="summary-item">
            <label>Total Revenue:</label>
            <span>${totalRevenue.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PaymentsList;
