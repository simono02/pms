import api from './api';

const paymentService = {
  processPayment: async (projectId, paymentData) => {
    const response = await api.post(`/payments/process/${projectId}`, paymentData);
    return response;
  },

  verifyPayment: async (paymentId) => {
    const response = await api.post(`/payments/verify/${paymentId}`);
    return response;
  },

  getPaymentStatus: async (paymentId) => {
    const response = await api.get(`/payments/status/${paymentId}`);
    return response;
  },

  getPaymentHistory: async () => {
    const response = await api.get('/payments/history');
    return response;
  },

  getPayment: async (paymentId) => {
    const response = await api.get(`/payments/${paymentId}`);
    return response;
  },

  refundPayment: async (paymentId, reason) => {
    const response = await api.post(`/payments/${paymentId}/refund`, { reason });
    return response;
  },

  getPaymentMethods: async () => {
    const response = await api.get('/payments/methods');
    return response;
  },

  addPaymentMethod: async (methodData) => {
    const response = await api.post('/payments/methods', methodData);
    return response;
  },

  deletePaymentMethod: async (methodId) => {
    const response = await api.delete(`/payments/methods/${methodId}`);
    return response;
  },

  setDefaultPaymentMethod: async (methodId) => {
    const response = await api.put(`/payments/methods/${methodId}/default`);
    return response;
  },

  getInvoices: async () => {
    const response = await api.get('/payments/invoices');
    return response;
  },

  getInvoice: async (invoiceId) => {
    const response = await api.get(`/payments/invoices/${invoiceId}`);
    return response;
  },

  downloadInvoice: async (invoiceId) => {
    const response = await api.get(`/payments/invoices/${invoiceId}/download`, {
      responseType: 'blob'
    });
    return response;
  },

  calculateProjectPrice: async (projectId) => {
    const response = await api.get(`/payments/calculate/${projectId}`);
    return response;
  },

  applyDiscount: async (paymentId, discountCode) => {
    const response = await api.post(`/payments/${paymentId}/discount`, { discount_code: discountCode });
    return response;
  },

  getDiscounts: async () => {
    const response = await api.get('/payments/discounts');
    return response;
  },

  validateDiscount: async (discountCode, projectId) => {
    const response = await api.post('/payments/validate-discount', { 
      discount_code: discountCode, 
      project_id: projectId 
    });
    return response;
  },

  createSubscription: async (subscriptionData) => {
    const response = await api.post('/payments/subscriptions', subscriptionData);
    return response;
  },

  getSubscriptions: async () => {
    const response = await api.get('/payments/subscriptions');
    return response;
  },

  cancelSubscription: async (subscriptionId) => {
    const response = await api.delete(`/payments/subscriptions/${subscriptionId}`);
    return response;
  },

  getPaymentStats: async () => {
    const response = await api.get('/payments/stats');
    return response;
  }
};

export default paymentService;
