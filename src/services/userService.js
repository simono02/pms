import api from './api';

const userService = {
  getProfile: async () => {
    const response = await api.get('/user/profile');
    return response;
  },

  updateProfile: async (userData) => {
    const response = await api.put('/user/profile', userData);
    return response;
  },

  getProjects: async () => {
    const response = await api.get('/user/projects');
    return response;
  },

  getProject: async (projectId) => {
    const response = await api.get(`/user/projects/${projectId}`);
    return response;
  },

  updateProject: async (projectId, projectData) => {
    const response = await api.put(`/user/projects/${projectId}`, projectData);
    return response;
  },

  deleteProject: async (projectId) => {
    const response = await api.delete(`/user/projects/${projectId}`);
    return response;
  },

  getProjectHistory: async (projectId) => {
    const response = await api.get(`/user/projects/${projectId}/history`);
    return response;
  },

  getNotifications: async () => {
    const response = await api.get('/user/notifications');
    return response;
  },

  markNotificationAsRead: async (notificationId) => {
    const response = await api.put(`/user/notifications/${notificationId}/read`);
    return response;
  },

  deleteNotification: async (notificationId) => {
    const response = await api.delete(`/user/notifications/${notificationId}`);
    return response;
  },

  getSettings: async () => {
    const response = await api.get('/user/settings');
    return response;
  },

  updateSettings: async (settings) => {
    const response = await api.put('/user/settings', settings);
    return response;
  },

  uploadAvatar: async (file) => {
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await api.post('/user/avatar', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response;
  },

  deleteAccount: async () => {
    const response = await api.delete('/user/account');
    return response;
  }
};

export default userService;
