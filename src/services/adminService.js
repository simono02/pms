import api from './api';

const adminService = {

  // ================================================================
  // DASHBOARD
  // ================================================================

  getDashboardStats: async () => {
    const response = await api.get('/admin/dashboard/stats');
    return response;
  },

  // ================================================================
  // CLIENTS
  // ================================================================

  getAllClients: async () => {
    const response = await api.get('/admin/clients');
    return response;
  },

  getClient: async (clientId) => {
    const response = await api.get(`/admin/clients/${clientId}`);
    return response;
  },

  updateClientStatus: async (clientId, status) => {
    const response = await api.put(`/admin/clients/${clientId}/status`, { status });
    return response;
  },

  deleteClient: async (clientId) => {
    const response = await api.delete(`/admin/clients/${clientId}`);
    return response;
  },

  getClientProjects: async (clientId) => {
    const response = await api.get(`/admin/clients/${clientId}/projects`);
    return response;
  },

  // ================================================================
  // STAFF
  // ================================================================

  getAllStaff: async () => {
    const response = await api.get('/admin/staff');
    return response;
  },

  getStaffMember: async (staffId) => {
    const response = await api.get(`/admin/staff/${staffId}`);
    return response;
  },

  addStaff: async (staffData) => {
    const response = await api.post('/admin/staff', staffData);
    return response;
  },

  updateStaff: async (staffId, staffData) => {
    const response = await api.put(`/admin/staff/${staffId}`, staffData);
    return response;
  },

  updateStaffStatus: async (staffId, status) => {
    const response = await api.put(`/admin/staff/${staffId}/status`, { status });
    return response;
  },

  deleteStaff: async (staffId) => {
    const response = await api.delete(`/admin/staff/${staffId}`);
    return response;
  },

  getStaffPerformance: async (staffId) => {
    const response = await api.get(`/admin/staff/${staffId}/performance`);
    return response;
  },

  // ================================================================
  // PROJECTS
  // ================================================================

  getAllProjects: async () => {
    const response = await api.get('/admin/projects');
    return response;
  },

  getUnassignedProjects: async () => {
    const response = await api.get('/admin/projects/unassigned');
    return response;
  },

  getProject: async (projectId) => {
    const response = await api.get(`/admin/projects/${projectId}`);
    return response;
  },

  allocateProject: async (projectId, staffId) => {
    const response = await api.put(`/admin/projects/${projectId}/allocate`, { staff_id: staffId });
    return response;
  },

  unallocateProject: async (projectId) => {
    const response = await api.put(`/admin/projects/${projectId}/unallocate`);
    return response;
  },

  updateProjectStatus: async (projectId, status) => {
    const response = await api.put(`/admin/projects/${projectId}/status`, { status });
    return response;
  },

  deleteProject: async (projectId) => {
    const response = await api.delete(`/admin/projects/${projectId}`);
    return response;
  },

  // ================================================================
  // PAYMENTS
  // ================================================================

  getAllPayments: async () => {
    const response = await api.get('/admin/payments');
    return response;
  },

  getPayment: async (paymentId) => {
    const response = await api.get(`/admin/payments/${paymentId}`);
    return response;
  },

  refundPayment: async (paymentId) => {
    const response = await api.post(`/admin/payments/${paymentId}/refund`);
    return response;
  },

  getPaymentStats: async () => {
    const response = await api.get('/admin/payments/stats');
    return response;
  },

  // ================================================================
  // ANALYTICS & LOGS
  // ================================================================

  getAnalytics: async (timeRange = 'month') => {
    const response = await api.get(`/admin/analytics?range=${timeRange}`);
    return response;
  },

  getSystemLogs: async () => {
    const response = await api.get('/admin/logs');
    return response;
  },

  // ================================================================
  // SETTINGS & SYSTEM
  // ================================================================

  getSettings: async () => {
    const response = await api.get('/admin/settings');
    return response;
  },

  updateSettings: async (settings) => {
    const response = await api.put('/admin/settings', settings);
    return response;
  },

  getSystemHealth: async () => {
    const response = await api.get('/admin/health');
    return response;
  },

  exportData: async (type, format = 'csv') => {
    const response = await api.get(`/admin/export/${type}?format=${format}`, {
      responseType: 'blob',
    });
    return response;
  },

  backupDatabase: async () => {
    const response = await api.post('/admin/backup');
    return response;
  },

  restoreDatabase: async (backupFile) => {
    const formData = new FormData();
    formData.append('backup', backupFile);
    const response = await api.post('/admin/restore', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response;
  },
};

export { adminService };
export default adminService;