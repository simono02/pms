import api from './api';

const staffService = {
  getProfile: async () => {
    const response = await api.get('/staff/profile');
    return response;
  },

  updateProfile: async (profileData) => {
    const response = await api.put('/staff/profile', profileData);
    return response;
  },

  getAssignedProjects: async () => {
    const response = await api.get('/staff/projects');
    return response;
  },

  getProject: async (projectId) => {
    const response = await api.get(`/staff/projects/${projectId}`);
    return response;
  },

  updateProjectStatus: async (projectId, status) => {
    const response = await api.put(`/staff/projects/${projectId}/status`, { status });
    return response;
  },

  uploadResult: async (projectId, resultData) => {
    const response = await api.post(`/staff/projects/${projectId}/result`, resultData);
    return response;
  },

  updateResult: async (projectId, resultData) => {
    const response = await api.put(`/staff/projects/${projectId}/result`, resultData);
    return response;
  },

  getProjectHistory: async (projectId) => {
    const response = await api.get(`/staff/projects/${projectId}/history`);
    return response;
  },

  getNotifications: async () => {
    const response = await api.get('/staff/notifications');
    return response;
  },

  markNotificationAsRead: async (notificationId) => {
    const response = await api.put(`/staff/notifications/${notificationId}/read`);
    return response;
  },

  getDashboardStats: async () => {
    const response = await api.get('/staff/dashboard/stats');
    return response;
  },

  getPerformanceStats: async () => {
    const response = await api.get('/staff/performance');
    return response;
  },

  getAvailableProjects: async () => {
    const response = await api.get('/staff/available-projects');
    return response;
  },

  requestProject: async (projectId) => {
    const response = await api.post(`/staff/request-project/${projectId}`);
    return response;
  },

  getWorkload: async () => {
    const response = await api.get('/staff/workload');
    return response;
  },

  updateAvailability: async (availability) => {
    const response = await api.put('/staff/availability', { availability });
    return response;
  },

  getSkills: async () => {
    const response = await api.get('/staff/skills');
    return response;
  },

  updateSkills: async (skills) => {
    const response = await api.put('/staff/skills', { skills });
    return response;
  },

  getReviews: async () => {
    const response = await api.get('/staff/reviews');
    return response;
  },

  submitReview: async (projectId, reviewData) => {
    const response = await api.post(`/staff/projects/${projectId}/review`, reviewData);
    return response;
  },

  getEarnings: async () => {
    const response = await api.get('/staff/earnings');
    return response;
  },

  requestPayout: async (amount) => {
    const response = await api.post('/staff/request-payout', { amount });
    return response;
  }
};

export { staffService };
export default staffService;
