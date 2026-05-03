import React from 'react';

const PaymentModal = ({ isOpen, onClose, onPaymentComplete }) => {
  if (!isOpen) return null;

  return (
    <div className="modal">
      <div className="modal-content">
        <h2>Payment</h2>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default PaymentModal;